#!/usr/bin/env python3
"""Post a pr-review findings.json to a pull request on Azure DevOps or GitHub.

Stdlib-only. Reads the canonical findings.json (references/output.md), posts one anchored thread
per Blocker, Question and Major, and keeps one summary that carries the verdict, the scope
statement, a severity legend, an index linking every finding, the nits and the credit list. Nits
live only in the summary, so they never add a thread that a comment-resolution policy would make
the author resolve. Re-runs are idempotent: each thread ends with a readable footer such as
`_pr-review M1 · ..._`, so an existing thread is updated (resolved when the finding is fixed,
reactivated on regression) instead of duplicated. The legacy `[pr-review:M1]` marker is still
recognised.

A thread a human resolved as won't fix or by design is never reopened, and a human-resolved
Question thread counts as answered and stops gating the vote.

The core (findings -> intended actions) is host-neutral. Each host adapter maps its own thread
statuses onto `active`, `bot_resolved` and `human_resolved`, and the neutral vote onto its own.
--host auto picks the host from findings.json `scope.host`, then the CI environment, then the
`origin` remote URL. --dry-run prints every write unsent, and --emit-threads writes the intended
threads as JSON so another client, such as an MCP server, can post identical content.
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

# Severity wording shared by thread headers, the summary legend and the index.
SEVERITY = {
    "blocker": ("Blocker", "fix before merge"),
    "question": ("Question", "answer before merge, then resolve this thread"),
    "major": ("Major", "please ticket, does not block the merge"),
    "nit": ("Nit", "optional"),
}
FOOTER = "_pr-review {id} · see the review summary on this PR for every finding_"
REPLY_FOOTER = "_pr-review {id}_"
SUMMARY_FOOTER = "_pr-review summary_"
SUMMARY_ID = "summary"
# The footer is wrapped in underscores for italics, so the ID ends at any non-alphanumeric.
MARKER_RE = re.compile(r"pr-review (summary|[BQMN]\d+)(?![A-Za-z0-9])")
LEGACY_MARKER_RE = re.compile(r"\[pr-review:([^\]]+)\]")

# Finding statuses that still count against the PR. A regressed or partial fix gates like an open one.
GATING = {"open", "regressed", "partial"}
STATUSES = GATING | {"fixed", "retracted"}
# Neutral thread statuses every adapter maps onto.
ACTIVE, BOT_RESOLVED, HUMAN_RESOLVED = "active", "bot_resolved", "human_resolved"
NEUTRAL_VOTES = ("approve", "approve_with_suggestions", "waiting_for_author", "reject")


# ---------------------------------------------------------------------------------------------
# Core: bodies, markers, validation, vote, reconciliation. Host-neutral.
# ---------------------------------------------------------------------------------------------

def marker_of(content):
    """Return the finding ID or 'summary' a comment is tagged with, or None."""
    m = MARKER_RE.search(content or "") or LEGACY_MARKER_RE.search(content or "")
    return m.group(1) if m else None


def index_threads(threads):
    """Map marker ID -> normalised thread, scanning every comment for a marker."""
    out = {}
    for t in threads:
        for content in t.get("comments", []):
            mid = marker_of(content)
            if mid:
                out.setdefault(mid, t)
                break
    return out


def thread_mentions(thread, text):
    return any(text in (c or "") for c in thread.get("comments", []))


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def finding_body(f):
    label, action = SEVERITY[f["severity"]]
    parts = [f"**{label}** ({action}) · **{f['id']}**: {f.get('title', '')}".rstrip(": "), "",
             f["pr_comment"]]
    extra = []
    if f.get("root_cause"):
        extra.append(f"**Why:** {f['root_cause']}")
    if f.get("symptom_sites"):
        extra.append("**Also at:** " + ", ".join(f"`{s}`" for s in f["symptom_sites"]))
    if f.get("verify_fixed_when"):
        extra.append(f"**Verified fixed when:** {f['verify_fixed_when']}")
    if extra:
        parts += [""] + ["\n\n".join(extra)]
    parts += ["", FOOTER.format(id=f["id"])]
    return "\n".join(parts)


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def scope_statement(doc):
    s = doc.get("scope") or {}
    rng = f"`{s.get('merge_base', '?')[:12]}..{s.get('source_head', '?')[:12]}`"
    counts = []
    if isinstance(s.get("commits"), int):
        counts.append(plural(s["commits"], "commit"))
    if isinstance(s.get("files"), int):
        counts.append(plural(s["files"], "file"))
    counted = f" ({', '.join(counts)})" if counts else ""
    target = s.get("target", "the target branch")
    if doc.get("mode") == "promotion":
        return (f"This review and any approval cover only the {s.get('source', 'source')} to {target} "
                f"delta, commits {rng}{counted}. They are not technical sign-off of the pre-existing "
                f"{target} baseline, acceptance of the release for production, or closure of any "
                f"standing register finding.")
    return f"This review covers the PR delta only, commits {rng} against `{target}`{counted}."


def summary_body(doc, threads_by_id=None, outside=()):
    threads_by_id = threads_by_id or {}
    outside_ids = {f["id"] for f in outside}
    verdict = doc["verdict"].replace("_", " ").capitalize()
    lines = [f"**Verdict: {verdict}.** {scope_statement(doc)}", "",
             "Severity: " + " · ".join(f"**{label}** {action}" for label, action in SEVERITY.values()), ""]

    threaded = [f for f in doc["findings"] if f["severity"] != "nit"]
    if threaded:
        lines += ["| ID | Severity | Finding | Where | Status |", "|---|---|---|---|---|"]
        for f in threaded:
            t = threads_by_id.get(f["id"])
            fid = f"[{f['id']}]({t['url']})" if t and t.get("url") else f["id"]
            where = f"`{f.get('file', '')}:{f.get('line', '')}`"
            if f["id"] in outside_ids:
                where += " (outside the diff, see below)"
            lines.append(f"| {fid} | {SEVERITY[f['severity']][0]} | {cell(f.get('title', ''))} "
                         f"| {cell(where)} | {f.get('status', 'open')} |")
        lines.append("")
    else:
        lines += ["No blockers, questions or majors.", ""]

    open_outside = [f for f in outside if f.get("status", "open") in GATING]
    if open_outside:
        lines.append("**Outside the diff.** The host could not anchor these at their line:")
        lines += [f"- **{f['id']}** {f.get('title', '')}, `{f.get('file', '')}:{f.get('line', '')}`. "
                  f"{f['pr_comment']}" for f in open_outside]
        lines.append("")

    nits = [f for f in doc["findings"] if f["severity"] == "nit" and f.get("status", "open") in GATING]
    if nits:
        lines.append("**Nits** (optional, no thread to resolve):")
        lines += [f"- **{f['id']}** {f.get('title', '')}, `{f.get('file', '')}:{f.get('line', '')}`. "
                  f"{f['pr_comment']}" for f in nits]
        lines.append("")

    good = doc.get("genuinely_good") or []
    if good:
        lines.append("**Good in this delta:**")
        lines += [f"- {g}" for g in good]
        lines.append("")

    lines.append(SUMMARY_FOOTER)
    return "\n".join(lines)


def validate(doc):
    """Reject a document the poster cannot act on safely. Returns a list of problems."""
    problems = []
    for f in doc.get("findings", []):
        if f.get("severity") not in SEVERITY:
            problems.append(f"{f.get('id', '?')}: unknown severity {f.get('severity')!r}")
        if f.get("status", "open") not in STATUSES:
            problems.append(f"{f.get('id', '?')}: unknown status {f.get('status')!r}")
    gating_blockers = [f["id"] for f in doc.get("findings", [])
                       if f.get("severity") == "blocker" and f.get("status", "open") in GATING]
    if gating_blockers and doc.get("verdict") != "request_changes":
        problems.append(f"verdict {doc.get('verdict')!r} but blockers still gate: {', '.join(gating_blockers)}")
    return problems


def compute_vote(doc, by_marker, reject):
    """Return the neutral vote: approve, approve_with_suggestions, waiting_for_author or reject."""
    gating = False
    suggestions = False
    for f in doc["findings"]:
        status = f.get("status", "open")
        if status not in GATING:
            continue
        if f["severity"] == "blocker":
            gating = True  # a human disposition on the thread never lifts a Blocker
        elif f["severity"] == "question":
            t = by_marker.get(f["id"])
            answered = status == "open" and t is not None and t.get("status") in (BOT_RESOLVED, HUMAN_RESOLVED)
            gating = gating or not answered  # an unanswered Q gates, a resolved thread answers it
        else:
            suggestions = True
    if gating:
        return "reject" if reject else "waiting_for_author"
    return "approve_with_suggestions" if suggestions else "approve"


def reconcile(host, doc, by_marker):
    """Create, reply to, resolve or reactivate one thread per threaded finding. Idempotent.

    Returns (threads_by_id, outside): every finding's thread, existing or new, and the findings the
    host could not anchor at their line.
    """
    head = (doc.get("scope") or {}).get("source_head", "")[:12]
    threads_by_id, outside = {}, []
    for f in doc["findings"]:
        t = by_marker.get(f["id"])
        status = f.get("status", "open")
        tag = REPLY_FOOTER.format(id=f["id"])
        if t is None:
            # Nits live in the summary only. Fixed or retracted findings that never had a thread need none.
            if status in GATING and f["severity"] != "nit":
                t = host.create_thread(finding_body(f), f.get("file"), f.get("line"))
                if t is None:
                    outside.append(f)
                else:
                    threads_by_id[f["id"]] = t
            continue
        threads_by_id[f["id"]] = t
        tstatus = t.get("status")
        if tstatus == HUMAN_RESOLVED:
            if status in ("regressed", "partial") and not thread_mentions(t, f"Marked {status}"):
                host.reply(t, f"Marked {status} at `{head}`. Left as the reviewer disposed it. {tag}")
            continue  # a human closed this conversation; never reopen it
        if status == "open" and tstatus == BOT_RESOLVED and f["severity"] != "question":
            host.reply(t, f"Still open at `{head}`, re-verified against its criterion. {tag}")
            host.set_status(t, "active")
        elif status in ("regressed", "partial") and tstatus == BOT_RESOLVED:
            host.reply(t, f"{status.capitalize()} at `{head}`. The fix no longer holds. {tag}")
            host.set_status(t, "active")
        elif status == "fixed" and tstatus == ACTIVE:
            host.reply(t, f"Verified fixed at `{head}` (criterion met). {tag}")
            host.set_status(t, "resolved")
        elif status == "retracted" and tstatus == ACTIVE:
            host.reply(t, f"Retracted. This finding was wrong, see the review document for the correction. {tag}")
            host.set_status(t, "closed")
    return threads_by_id, outside


# ---------------------------------------------------------------------------------------------
# HTTP and auth helpers.
# ---------------------------------------------------------------------------------------------

class HostError(Exception):
    def __init__(self, status, message):
        super().__init__(f"{status} {message}")
        self.status = status


class Http:
    """JSON over urllib. Dry-run prints writes unsent; GETs still run when a token is present."""

    def __init__(self, auth_header, dry_run, extra_headers=None):
        self.auth_header = auth_header
        self.dry_run = dry_run
        self.extra_headers = extra_headers or {}

    def call(self, method, url, body=None, content_type="application/json", read_only=False):
        # A GraphQL query is a POST that writes nothing, so it passes `read_only` to run in a dry-run.
        if self.dry_run and ((method != "GET" and not read_only) or not self.auth_header):
            print(f"DRY-RUN {method} {url}")
            if body is not None:
                print("  " + json.dumps(body, indent=2, ensure_ascii=False).replace("\n", "\n  "))
            return None
        headers = {"Content-Type": content_type, **self.extra_headers}
        if self.auth_header:
            headers["Authorization"] = self.auth_header
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, method=method, headers=headers, data=data)
        try:
            with urllib.request.urlopen(req) as resp:
                payload = resp.read()
                return json.loads(payload) if payload else {}
        except urllib.error.HTTPError as e:
            raise HostError(e.code, f"{method} {url}: {e.read().decode(errors='replace')[:500]}")


def is_jwt(token):
    return token.startswith("eyJ") and token.count(".") == 2


def read_token_file(path):
    with open(os.path.expanduser(path)) as fh:
        return fh.read().strip()


def first_env(*names):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return None


# ---------------------------------------------------------------------------------------------
# Azure DevOps adapter.
# ---------------------------------------------------------------------------------------------

class AzureDevOps:
    API = "7.1"
    STATUS_IN = {"active": ACTIVE, "pending": ACTIVE, "fixed": BOT_RESOLVED, "closed": BOT_RESOLVED,
                 "wontFix": HUMAN_RESOLVED, "byDesign": HUMAN_RESOLVED}
    STATUS_OUT = {"active": "active", "resolved": "fixed", "closed": "closed"}
    VOTE = {"approve": 10, "approve_with_suggestions": 5, "waiting_for_author": -5, "reject": -10}

    def __init__(self, org_url, project, repo, pr, token, dry_run):
        self.org_url = org_url.rstrip("/")
        self.project, self.repo, self.pr = project, repo, pr
        self.base = (f"{self.org_url}/{urllib.parse.quote(project)}/_apis/git/repositories/"
                     f"{urllib.parse.quote(repo)}/pullRequests/{pr}")
        if not token:
            auth = None
        elif is_jwt(token):
            auth = f"Bearer {token}"  # an Entra access token, such as one from `az account get-access-token`
        else:
            auth = "Basic " + base64.b64encode(f":{token}".encode()).decode()
        self.http = Http(auth, dry_run)

    def thread_url(self, thread_id):
        return (f"{self.org_url}/{urllib.parse.quote(self.project)}/_git/{urllib.parse.quote(self.repo)}"
                f"/pullrequest/{self.pr}?discussionId={thread_id}")

    def _normalise(self, raw):
        return {"id": raw["id"], "status": self.STATUS_IN.get(raw.get("status"), ACTIVE),
                "comments": [c.get("content") or "" for c in raw.get("comments", [])],
                "url": self.thread_url(raw["id"]), "raw_status": raw.get("status")}

    def threads(self):
        data = self.http.call("GET", f"{self.base}/threads?api-version={self.API}") or {}
        return [self._normalise(t) for t in data.get("value", []) if not t.get("isDeleted")]

    def create_thread(self, body, path=None, line=None, status="active"):
        payload = {"comments": [{"parentCommentId": 0, "content": body, "commentType": "text"}],
                   "status": status}
        if path:
            ln = max(int(line or 1), 1)
            payload["threadContext"] = {"filePath": "/" + path.lstrip("/"),
                                        "rightFileStart": {"line": ln, "offset": 1},
                                        "rightFileEnd": {"line": ln, "offset": 1}}
        raw = self.http.call("POST", f"{self.base}/threads?api-version={self.API}", payload)
        if not raw:
            return {"id": None, "status": ACTIVE, "comments": [body], "url": None}
        return self._normalise(raw)

    def reply(self, thread, body):
        self.http.call("POST", f"{self.base}/threads/{thread['id']}/comments?api-version={self.API}",
                       {"parentCommentId": 1, "content": body, "commentType": "text"})

    def set_status(self, thread, status):
        self.http.call("PATCH", f"{self.base}/threads/{thread['id']}?api-version={self.API}",
                       {"status": self.STATUS_OUT[status]})

    def upsert_summary(self, body, existing):
        if existing is None:
            self.create_thread(body)
        else:
            # Edit the summary in place so the PR keeps one current summary.
            self.http.call("PATCH", f"{self.base}/threads/{existing['id']}/comments/1?api-version={self.API}",
                           {"content": body})

    def vote(self, neutral):
        data = self.http.call("GET", f"{self.org_url}/_apis/connectionData?api-version={self.API}-preview") or {}
        rid = (data.get("authenticatedUser") or {}).get("id")
        if not rid:
            print(f"{'DRY-RUN' if self.http.dry_run else 'WARN'}: vote={neutral} not cast "
                  f"(reviewer identity not resolved)")
            return
        self.http.call("PUT", f"{self.base}/reviewers/{rid}?api-version={self.API}",
                       {"vote": self.VOTE[neutral], "id": rid})


# ---------------------------------------------------------------------------------------------
# GitHub adapter. REST for comments and reviews, GraphQL for listing and resolving threads,
# because REST cannot resolve a review thread.
# ---------------------------------------------------------------------------------------------

class GitHub:
    # Supported until 2028-03-10 per GitHub's REST API versions page.
    API_VERSION = "2022-11-28"
    EVENT = {"approve": "APPROVE", "approve_with_suggestions": "APPROVE",
             "waiting_for_author": "REQUEST_CHANGES", "reject": "REQUEST_CHANGES"}
    # The poster's own status replies. A resolved thread whose latest poster reply resolved it was
    # resolved by the poster. Otherwise a human resolved it. This avoids asking GitHub who the
    # token is, which an Actions GITHUB_TOKEN cannot always answer.
    RESOLVING = ("Verified fixed at", "Retracted.")
    REOPENING = ("Still open at", "Regressed at", "Partial at")
    THREADS_QUERY = """
query($o:String!,$n:String!,$pr:Int!,$after:String){
  repository(owner:$o,name:$n){ pullRequest(number:$pr){
    reviewThreads(first:100, after:$after){
      pageInfo{hasNextPage endCursor}
      nodes{ id isResolved path line
        comments(first:100){ nodes{ databaseId body url } } } } } } }"""

    def __init__(self, owner, name, pr, token, head_sha, dry_run, api_url="https://api.github.com"):
        self.owner, self.name, self.pr = owner, name, int(pr)
        self.head_sha = head_sha
        self.api = api_url.rstrip("/")
        self.repo_api = f"{self.api}/repos/{owner}/{name}"
        self.http = Http(f"Bearer {token}" if token else None, dry_run,
                         {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": self.API_VERSION})

    @classmethod
    def from_args(cls, args, doc):
        repo = args.repo or first_env("GITHUB_REPOSITORY")
        pr = args.pr or cls._pr_from_actions()
        token = first_env("GITHUB_TOKEN", "GH_TOKEN")
        if not token and (args.token_file or first_env("GITHUB_TOKEN_FILE")):
            token = read_token_file(args.token_file or first_env("GITHUB_TOKEN_FILE"))
        if not token:
            token = cls._gh_cli_token()
        head = (doc.get("scope") or {}).get("source_head", "")
        missing = []
        if not repo or "/" not in repo:
            missing.append("repo (--repo owner/name or GITHUB_REPOSITORY)")
        if not pr:
            missing.append("pr (--pr or the Actions pull_request event)")
        if not head:
            missing.append("scope.source_head in findings.json")
        if not token:
            missing.append("token (GITHUB_TOKEN, GH_TOKEN, --token-file, or a signed-in `gh` CLI)")
        owner, _, name = (repo or "OWNER/REPO").partition("/")
        return cls(owner, name, pr or 0, token or "", head, args.dry_run,
                   first_env("GITHUB_API_URL") or "https://api.github.com"), missing

    @staticmethod
    def _pr_from_actions():
        path = first_env("GITHUB_EVENT_PATH")
        if path and os.path.exists(path):
            with open(path) as fh:
                number = (json.load(fh).get("pull_request") or {}).get("number")
            if number:
                return str(number)
        m = re.match(r"refs/pull/(\d+)/", first_env("GITHUB_REF") or "")
        return m.group(1) if m else None

    @staticmethod
    def _gh_cli_token():
        try:
            return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True,
                                  check=True).stdout.strip() or None
        except (OSError, subprocess.CalledProcessError):
            return None

    def _graphql(self, query, variables, read_only):
        data = self.http.call("POST", f"{self.api}/graphql", {"query": query, "variables": variables},
                              read_only=read_only)
        if data and data.get("errors"):
            raise HostError(200, f"GraphQL: {data['errors']}")
        return (data or {}).get("data") or {}

    def _status(self, node, bodies):
        if not node.get("isResolved"):
            return ACTIVE
        for body in reversed(bodies):
            if any(p in body for p in self.RESOLVING) and marker_of(body):
                return BOT_RESOLVED
            if any(p in body for p in self.REOPENING) and marker_of(body):
                break
        return HUMAN_RESOLVED

    def threads(self):
        out, after = [], None
        while True:
            data = self._graphql(self.THREADS_QUERY, {"o": self.owner, "n": self.name, "pr": self.pr,
                                                      "after": after}, read_only=True)
            conn = ((data.get("repository") or {}).get("pullRequest") or {}).get("reviewThreads") or {}
            for node in conn.get("nodes") or []:
                comments = (node.get("comments") or {}).get("nodes") or []
                bodies = [c.get("body") or "" for c in comments]
                out.append({"id": node["id"], "status": self._status(node, bodies), "comments": bodies,
                            "url": comments[0]["url"] if comments else None,
                            "first_comment": comments[0]["databaseId"] if comments else None})
            page = conn.get("pageInfo") or {}
            if not page.get("hasNextPage"):
                return out
            after = page.get("endCursor")

    def create_thread(self, body, path=None, line=None, status="active"):
        payload = {"body": body, "commit_id": self.head_sha, "path": path.lstrip("/"),
                   "line": max(int(line or 1), 1), "side": "RIGHT"}
        try:
            raw = self.http.call("POST", f"{self.repo_api}/pulls/{self.pr}/comments", payload)
        except HostError as e:
            if e.status == 422:
                return None  # GitHub anchors review comments only on lines inside the diff
            raise
        if not raw:
            return {"id": None, "status": ACTIVE, "comments": [body], "url": None, "first_comment": None}
        # The GraphQL thread ID is not in the REST response. A later run finds the thread by its footer.
        return {"id": None, "status": ACTIVE, "comments": [body], "url": raw.get("html_url"),
                "first_comment": raw.get("id")}

    def reply(self, thread, body):
        self.http.call("POST", f"{self.repo_api}/pulls/{self.pr}/comments/{thread['first_comment']}/replies",
                       {"body": body})

    def set_status(self, thread, status):
        mutation = "unresolveReviewThread" if status == "active" else "resolveReviewThread"
        self._graphql(f"mutation($t:ID!){{{mutation}(input:{{threadId:$t}}){{thread{{id isResolved}}}}}}",
                      {"t": thread["id"]}, read_only=False)

    def _summary_comment(self):
        page = 1
        while True:
            batch = self.http.call("GET", f"{self.repo_api}/issues/{self.pr}/comments?per_page=100&page={page}")
            if not batch:
                return None
            for c in batch:
                if marker_of(c.get("body")) == SUMMARY_ID:
                    return c
            if len(batch) < 100:
                return None
            page += 1

    def upsert_summary(self, body, existing):
        # The summary is a PR conversation comment, not a review thread, so look it up here.
        current = self._summary_comment()
        if current is None:
            self.http.call("POST", f"{self.repo_api}/issues/{self.pr}/comments", {"body": body})
        else:
            self.http.call("PATCH", f"{self.repo_api}/issues/comments/{current['id']}", {"body": body})

    def vote(self, neutral):
        event = self.EVENT[neutral]
        body = f"pr-review vote: {neutral.replace('_', ' ')}. The review summary comment lists every finding."
        try:
            self.http.call("POST", f"{self.repo_api}/pulls/{self.pr}/reviews", {"event": event, "body": body})
        except HostError as e:
            if e.status not in (403, 422):
                raise
            # GitHub refuses approval or change requests on the author's own PR, and for an Actions
            # token unless the repository allows it. Leave a comment review instead.
            print(f"WARN: GitHub refused {event} ({e.status}); posting a comment review instead")
            self.http.call("POST", f"{self.repo_api}/pulls/{self.pr}/reviews", {"event": "COMMENT", "body": body})


# ---------------------------------------------------------------------------------------------
# Host selection, emit mode and the entry point.
# ---------------------------------------------------------------------------------------------

def origin_url():
    try:
        return subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def detect_host(requested, doc, environ=None, remote=None):
    """Resolve --host auto: findings.json scope.host, then the CI environment, then the origin URL."""
    if requested and requested != "auto":
        return requested
    environ = os.environ if environ is None else environ
    scope_host = (doc.get("scope") or {}).get("host")
    if scope_host in HOSTS:
        return scope_host
    if environ.get("SYSTEM_COLLECTIONURI") or environ.get("TF_BUILD"):
        return "azure"
    if environ.get("GITHUB_ACTIONS"):
        return "github"
    remote = origin_url() if remote is None else remote
    if "dev.azure.com" in remote or "visualstudio.com" in remote:
        return "azure"
    if "github.com" in remote:
        return "github"
    raise SystemExit("Cannot tell the PR host. Pass --host azure or --host github.")


class Recorder:
    """A host stand-in for --emit-threads: records the threads the live run would write."""

    def __init__(self, existing=()):
        self.existing = list(existing)
        self.actions = []

    def threads(self):
        return self.existing

    def create_thread(self, body, path=None, line=None, status="active"):
        self.actions.append({"action": "create_thread", "path": path, "line": line, "status": status, "body": body})
        return {"id": None, "status": ACTIVE, "comments": [body], "url": None}

    def reply(self, thread, body):
        self.actions.append({"action": "reply", "thread_id": thread.get("id"), "body": body})

    def set_status(self, thread, status):
        self.actions.append({"action": "set_status", "thread_id": thread.get("id"), "status": status})

    def upsert_summary(self, body, existing):
        self.actions.append({"action": "summary", "thread_id": existing and existing.get("id"), "body": body})

    def vote(self, neutral):
        self.actions.append({"action": "vote", "vote": neutral})


def build_host(name, args, doc):
    if name == "azure":
        token = first_env("SYSTEM_ACCESSTOKEN", "AZURE_DEVOPS_EXT_PAT")
        token_file = args.token_file or first_env("AZURE_DEVOPS_TOKEN_FILE")
        if not token and token_file:
            token = read_token_file(token_file)
        cfg = {"org-url": args.org_url or first_env("SYSTEM_COLLECTIONURI"),
               "project": args.project or first_env("SYSTEM_TEAMPROJECT"),
               "repo": args.repo or first_env("BUILD_REPOSITORY_NAME", "BUILD_REPOSITORY_ID"),
               "pr": args.pr or first_env("SYSTEM_PULLREQUEST_PULLREQUESTID")}
        missing = [k for k, v in cfg.items() if not v]
        if not token:
            missing.append("token (SYSTEM_ACCESSTOKEN, AZURE_DEVOPS_EXT_PAT, --token-file, or an Entra "
                           "token from `az account get-access-token` in AZURE_DEVOPS_EXT_PAT)")
        return AzureDevOps(cfg["org-url"] or "https://dev.azure.com/ORG/", cfg["project"] or "PROJECT",
                           cfg["repo"] or "REPO", cfg["pr"] or "0", token or "", args.dry_run), missing
    if name == "github":
        return GitHub.from_args(args, doc)
    raise SystemExit(f"Unknown host {name!r}")


HOSTS = {"azure", "github"}


def run(host, doc, args):
    by_marker = index_threads(host.threads())
    threads_by_id, outside = reconcile(host, doc, by_marker)
    host.upsert_summary(summary_body(doc, threads_by_id, outside), by_marker.get(SUMMARY_ID))
    vote = compute_vote(doc, by_marker, args.vote_reject)
    if not args.no_vote:
        host.vote(vote)
    return vote


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("findings", help="path to findings.json")
    p.add_argument("--host", choices=["auto", "azure", "github"], default="auto")
    p.add_argument("--org-url", help="Azure DevOps organisation URL")
    p.add_argument("--project", help="Azure DevOps project")
    p.add_argument("--repo", help="Azure DevOps repository name, or GitHub owner/name")
    p.add_argument("--pr", help="pull request number")
    p.add_argument("--token-file", help="file holding the token, read and never echoed")
    p.add_argument("--dry-run", action="store_true", help="print every write without sending it")
    p.add_argument("--emit-threads", metavar="FILE",
                   help="write the intended threads as JSON and send nothing, for posting by another client")
    p.add_argument("--no-vote", action="store_true")
    p.add_argument("--vote-reject", action="store_true",
                   help="reject instead of waiting for author when gated (Azure DevOps -10 rather than -5)")
    p.add_argument("--fail-on-verdict", action="store_true",
                   help="exit 1 when the computed vote is negative (for pipeline gating)")
    args = p.parse_args(argv)

    with open(args.findings) as fh:
        doc = json.load(fh)
    if doc.get("schema") != "pr-review/v1":
        raise SystemExit(f"Unsupported schema: {doc.get('schema')!r} (want pr-review/v1)")
    problems = validate(doc)
    if problems:
        raise SystemExit("findings.json rejected:\n  " + "\n  ".join(problems))

    name = detect_host(args.host, doc)
    if args.emit_threads:
        recorder = Recorder()
        vote = run(recorder, doc, args)
        with open(args.emit_threads, "w") as fh:
            json.dump({"host": name, "actions": recorder.actions}, fh, indent=2, ensure_ascii=False)
        print(f"host={name} vote={vote} actions={len(recorder.actions)} written to {args.emit_threads}")
        return 0

    host, missing = build_host(name, args, doc)
    if missing and not args.dry_run:
        raise SystemExit(f"Missing for {name}: " + ", ".join(missing))
    try:
        vote = run(host, doc, args)
    except HostError as e:
        raise SystemExit(f"{name}: {e}")
    print(f"host={name} vote={vote} verdict={doc['verdict']} findings={len(doc['findings'])}")
    if args.fail_on_verdict and vote in ("waiting_for_author", "reject"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
