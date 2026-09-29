#!/usr/bin/env python3
"""Post a pr-review findings.json to an Azure DevOps pull request.

Stdlib-only. Reads the canonical findings.json (references/output.md), posts one comment thread
per finding anchored at file:line, maintains a summary thread, and casts a reviewer vote. Re-runs
are idempotent: each thread carries a stateless marker `[pr-review:<ID>]`, so an existing thread
is updated (resolved when the finding is fixed, reactivated on regression) instead of duplicated.

A Question thread resolved by a human in the ADO UI counts as answered and stops gating the vote.

Auth: SYSTEM_ACCESSTOKEN (pipeline) or AZURE_DEVOPS_EXT_PAT. Org/project/repo/PR default to the
ADO predefined variables; all overridable by flag. --dry-run prints every REST call unsent.

The internals split into a generic core (findings -> intended actions) and an ADO adapter
(actions -> REST calls) so another host's adapter can be added without touching the core.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "7.1"
MARKER = "[pr-review:{id}]"
SEVERITY_LABEL = {"blocker": "**BLOCKER**", "question": "**QUESTION**",
                  "major": "**MAJOR**", "minor": "**NIT**", "nit": "**NIT**"}
# ADO thread statuses that mean a human considers the conversation settled.
RESOLVED_STATUSES = {"fixed", "closed", "wontFix", "byDesign"}
VOTE = {"approve": 10, "approve_with_suggestions": 5, "none": 0,
        "waiting_for_author": -5, "reject": -10}


def env(*names, default=None):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


class Ado:
    def __init__(self, org_url, project, repo, pr, token, dry_run):
        self.base = f"{org_url.rstrip('/')}/{urllib.parse.quote(project)}/_apis/git/repositories/{urllib.parse.quote(repo)}/pullRequests/{pr}"
        self.org_url = org_url.rstrip("/")
        self.auth = "Basic " + base64.b64encode(f":{token}".encode()).decode()
        self.has_token = bool(token)
        self.dry_run = dry_run

    def call(self, method, url, body=None):
        # Dry-run sends nothing; GETs still run when a token is available so a dry-run against a
        # live PR shows the real thread reconciliation.
        if self.dry_run and (method != "GET" or not self.has_token):
            print(f"DRY-RUN {method} {url}")
            if body is not None:
                print("  " + json.dumps(body, indent=2).replace("\n", "\n  "))
            return {}
        req = urllib.request.Request(url, method=method,
                                     headers={"Authorization": self.auth,
                                              "Content-Type": "application/json"})
        data = json.dumps(body).encode() if body is not None else None
        try:
            with urllib.request.urlopen(req, data=data) as resp:
                payload = resp.read()
                return json.loads(payload) if payload else {}
        except urllib.error.HTTPError as e:
            sys.exit(f"ADO {method} {url} failed: {e.code} {e.read().decode()[:500]}")

    def threads(self):
        return self.call("GET", f"{self.base}/threads?api-version={API}").get("value", [])

    def create_thread(self, content, path=None, line=None, status="active"):
        body = {"comments": [{"parentCommentId": 0, "content": content, "commentType": "text"}],
                "status": status}
        if path:
            body["threadContext"] = {
                "filePath": "/" + path.lstrip("/"),
                "rightFileStart": {"line": max(int(line or 1), 1), "offset": 1},
                "rightFileEnd": {"line": max(int(line or 1), 1), "offset": 1}}
        return self.call("POST", f"{self.base}/threads?api-version={API}", body)

    def reply(self, thread_id, content):
        return self.call("POST", f"{self.base}/threads/{thread_id}/comments?api-version={API}",
                         {"parentCommentId": 1, "content": content, "commentType": "text"})

    def set_status(self, thread_id, status):
        return self.call("PATCH", f"{self.base}/threads/{thread_id}?api-version={API}",
                         {"status": status})

    def my_id(self):
        data = self.call("GET", f"{self.org_url}/_apis/connectionData?api-version={API}-preview")
        return (data.get("authenticatedUser") or {}).get("id")

    def vote(self, value):
        rid = self.my_id()
        if not rid:
            if self.dry_run:
                print(f"DRY-RUN vote={value} (reviewer identity not resolved)")
            else:
                print("WARN: could not resolve reviewer identity; skipping vote")
            return
        self.call("PUT", f"{self.base}/reviewers/{rid}?api-version={API}",
                  {"vote": value, "id": rid})


def finding_body(f):
    parts = [f"{SEVERITY_LABEL.get(f['severity'], f['severity'])} `{f['id']}` — {f.get('title', '')}".rstrip(" —"),
             "", f["pr_comment"]]
    if f.get("verify_fixed_when"):
        parts += ["", f"**Verified fixed when:** {f['verify_fixed_when']}"]
    parts += ["", MARKER.format(id=f["id"])]
    return "\n".join(parts)


def summary_body(doc):
    s = doc.get("scope", {})
    blockers = [f for f in doc["findings"] if f["severity"] == "blocker" and f.get("status") == "open"]
    lines = [f"**Verdict: {doc['verdict'].replace('_', ' ')}** — "
             f"`{s.get('merge_base', '?')[:12]}..{s.get('source_head', '?')[:12]}` "
             f"({s.get('commits', '?')} commits, {s.get('files', '?')} files).", ""]
    if blockers:
        lines.append(f"{len(blockers)} blocker(s):")
        lines += [f"- `{f['id']}` {f.get('title', '')} — `{f['file']}:{f['line']}`" for f in blockers]
    else:
        lines.append("No open blockers.")
    questions = [f for f in doc["findings"] if f["severity"] == "question" and f.get("status") == "open"]
    if questions:
        lines.append(f"{len(questions)} question(s) gate approval until answered "
                     f"(resolving a question's thread lifts the gate):")
        lines += [f"- `{f['id']}` {f.get('title', '')}" for f in questions]
    lines += ["", MARKER.format(id="summary")]
    return "\n".join(lines)


def index_threads(threads):
    """Map marker id -> thread, scanning every comment for the marker."""
    out = {}
    for t in threads:
        for c in t.get("comments", []):
            content = c.get("content") or ""
            if "[pr-review:" in content:
                mid = content.split("[pr-review:", 1)[1].split("]", 1)[0]
                out.setdefault(mid, t)
    return out


def compute_vote(doc, by_marker, reject):
    gating = False
    for f in doc["findings"]:
        if f.get("status") != "open":
            continue
        if f["severity"] == "blocker":
            gating = True
        elif f["severity"] == "question":
            t = by_marker.get(f["id"])
            if not (t and t.get("status") in RESOLVED_STATUSES):
                gating = True  # unanswered Q gates approval, unless a human resolved its thread
    if gating:
        return VOTE["reject"] if reject else VOTE["waiting_for_author"]
    open_rest = [f for f in doc["findings"] if f.get("status") == "open"]
    return VOTE["approve_with_suggestions"] if open_rest else VOTE["approve"]


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("findings", help="path to findings.json")
    p.add_argument("--org-url", default=env("SYSTEM_COLLECTIONURI"))
    p.add_argument("--project", default=env("SYSTEM_TEAMPROJECT"))
    p.add_argument("--repo", default=env("BUILD_REPOSITORY_NAME", "BUILD_REPOSITORY_ID"))
    p.add_argument("--pr", default=env("SYSTEM_PULLREQUEST_PULLREQUESTID"))
    p.add_argument("--dry-run", action="store_true", help="print REST calls without sending")
    p.add_argument("--no-vote", action="store_true")
    p.add_argument("--vote-reject", action="store_true",
                   help="use Rejected (-10) instead of Waiting for Author (-5) when gated")
    p.add_argument("--fail-on-verdict", action="store_true",
                   help="exit 1 when the computed vote is negative (for pipeline gating)")
    args = p.parse_args()

    token = env("SYSTEM_ACCESSTOKEN", "AZURE_DEVOPS_EXT_PAT")
    missing = [n for n, v in [("org-url", args.org_url), ("project", args.project),
                              ("repo", args.repo), ("pr", args.pr),
                              ("token (SYSTEM_ACCESSTOKEN / AZURE_DEVOPS_EXT_PAT)", token)] if not v]
    if missing and not args.dry_run:
        sys.exit("Missing: " + ", ".join(missing))

    with open(args.findings) as fh:
        doc = json.load(fh)
    if doc.get("schema") != "pr-review/v1":
        sys.exit(f"Unsupported schema: {doc.get('schema')!r} (want pr-review/v1)")

    ado = Ado(args.org_url or "https://dev.azure.com/ORG/", args.project or "PROJECT",
              args.repo or "REPO", args.pr or "0", token or "", args.dry_run)
    by_marker = index_threads(ado.threads())

    head = (doc.get("scope") or {}).get("source_head", "")[:12]
    for f in doc["findings"]:
        t = by_marker.get(f["id"])
        status = f.get("status", "open")
        if t is None:
            if status == "open":
                ado.create_thread(finding_body(f), f.get("file"), f.get("line"))
            continue  # nothing to post for a non-open finding that never had a thread
        tid, tstatus = t["id"], t.get("status")
        if status == "open" and tstatus in RESOLVED_STATUSES and f["severity"] != "question":
            ado.reply(tid, f"Still open at `{head}` — re-verified against its criterion. {MARKER.format(id=f['id'])}")
            ado.set_status(tid, "active")
        elif status == "fixed" and tstatus not in RESOLVED_STATUSES:
            ado.reply(tid, f"Verified fixed at `{head}` (criterion met). {MARKER.format(id=f['id'])}")
            ado.set_status(tid, "fixed")
        elif status == "regressed":
            ado.reply(tid, f"Regressed at `{head}` — the fix no longer holds. {MARKER.format(id=f['id'])}")
            ado.set_status(tid, "active")
        elif status == "retracted" and tstatus not in RESOLVED_STATUSES:
            ado.reply(tid, f"Retracted — this finding was wrong; see the review document for the correction. {MARKER.format(id=f['id'])}")
            ado.set_status(tid, "closed")

    summary = by_marker.get("summary")
    if summary is None:
        ado.create_thread(summary_body(doc), status="active")
    else:
        ado.reply(summary["id"], summary_body(doc))

    vote = compute_vote(doc, by_marker, args.vote_reject)
    if not args.no_vote:
        ado.vote(vote)
    print(f"vote={vote} verdict={doc['verdict']} findings={len(doc['findings'])}")
    if args.fail_on_verdict and vote < 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
