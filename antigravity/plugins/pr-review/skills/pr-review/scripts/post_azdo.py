#!/usr/bin/env python3
"""Post a pr-review findings.json to an Azure DevOps pull request.

Kept so existing pipelines keep working. It runs `post_review.py --host azure` with the same
arguments. New pipelines call post_review.py directly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import post_review  # noqa: E402

if __name__ == "__main__":
    sys.exit(post_review.main(["--host", "azure", *sys.argv[1:]]))
