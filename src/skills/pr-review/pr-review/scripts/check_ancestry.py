#!/usr/bin/env python3
"""Check that every commit a review cites is an ancestor of the ref it is published against.

Stdlib-only. Implements protocol.md §19. Pass the SHAs as arguments, or pass --file to scan a review
document for backticked 7 to 40 character hex SHAs outside fenced code blocks.

Verdicts:
  ok          an ancestor of --ref
  off-branch  in the repository and reachable from another ref, but not from --ref
  orphaned    in the repository but reachable from no ref, usually after a rebase or an amend
  missing     not in the repository

Exit 0 when every SHA is ok, 1 when any is not, and 2 on a usage error.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# A SHA needs at least one digit and one letter, so plain numbers and hex-looking words are skipped.
SHA_RE = re.compile(r"`(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])([0-9a-f]{7,40})`")
BARE_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def git(repo, *args, stdin=None):
    return subprocess.run(["git", *args], cwd=repo, input=stdin, capture_output=True, text=True)


def shas_in(text):
    """Backticked SHAs in document order, skipping fenced code blocks."""
    found, inside = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            inside = not inside
            continue
        if not inside:
            found.extend(s for s in SHA_RE.findall(line) if s not in found)
    return found


def check(repo, ref, shas):
    """Return [(sha, verdict)] for each SHA, judged against ref."""
    target = git(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if target.returncode != 0:
        raise ValueError("ref %r does not resolve to a commit" % ref)
    target = target.stdout.strip()
    batch = git(repo, "cat-file", "--batch-check=%(objectname) %(objecttype)",
                stdin="".join(s + "\n" for s in shas))
    results = []
    for sha, line in zip(shas, batch.stdout.splitlines()):
        parts = line.split()
        full = parts[0] if len(parts) == 2 and parts[1] == "commit" else None
        if full is None:
            verdict = "missing"
        elif git(repo, "merge-base", "--is-ancestor", full, target).returncode == 0:
            verdict = "ok"
        elif git(repo, "for-each-ref", "--contains", full, "--count=1",
                 "--format=%(refname)").stdout.strip():
            verdict = "off-branch"
        else:
            verdict = "orphaned"
        results.append((sha, verdict))
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check cited commits against the ref a review is published against.")
    ap.add_argument("shas", nargs="*", help="commit SHAs to check")
    ap.add_argument("--ref", required=True, help="the branch or commit the review is published against")
    ap.add_argument("--repo", default=".", help="repository to check in (default: the current directory)")
    ap.add_argument("--file", help="scan this review document for backticked SHAs")
    ap.add_argument("--json", action="store_true", help="print the verdicts as JSON")
    args = ap.parse_args(argv)

    shas = list(args.shas)
    bad = [s for s in shas if not BARE_SHA_RE.match(s)]
    if bad:
        print("not a commit SHA: %s" % ", ".join(bad), file=sys.stderr)
        return 2
    if args.file:
        shas.extend(s for s in shas_in(Path(args.file).read_text(encoding="utf-8")) if s not in shas)
    if not shas:
        print("no SHAs to check", file=sys.stderr)
        return 2
    if git(args.repo, "rev-parse", "--git-dir").returncode != 0:
        print("%s is not a git repository" % args.repo, file=sys.stderr)
        return 2
    try:
        results = check(args.repo, args.ref, shas)
    except ValueError as err:
        print(err, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([{"sha": s, "verdict": v} for s, v in results], indent=2))
    else:
        for sha, verdict in results:
            print("%-10s %s" % (verdict, sha))
    return 0 if all(v == "ok" for _, v in results) else 1


if __name__ == "__main__":
    sys.exit(main())
