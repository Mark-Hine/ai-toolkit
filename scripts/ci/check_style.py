#!/usr/bin/env python3
"""Writing-style lint for tracked prose. Fails on em dashes, en dashes and banned words.

Scope: every tracked .md file, the developer_instructions strings in codex/agents/*.toml, and string
literals in tracked .py files. Fenced code blocks, inline code spans, URLs and YAML frontmatter are
skipped. scripts/ci/style-exceptions.txt lists `path: substring` pairs that are allowed, one per line,
for quoted source text and for the files that define the banned words.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXCEPTIONS = ROOT / 'scripts/ci/style-exceptions.txt'
BANNED = re.compile(r'\b(honestly|load-bearing|crux|delve|delves|delving|robust|robustly|seamless|seamlessly|leverage|leverages|leveraged|leveraging|genuinely)\b', re.I)
DASHES = re.compile('[–—]')
INLINE_CODE = re.compile(r'`[^`]*`')
URL = re.compile(r'https?://\S+')


def tracked(patterns):
    out = subprocess.run(['git', 'ls-files', *patterns], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.split()]


def load_exceptions():
    rules = []
    if EXCEPTIONS.exists():
        for line in EXCEPTIONS.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            path, _, needle = line.partition(': ')
            rules.append((path.strip(), needle.strip()))
    return rules


def excepted(rel, line, rules):
    return any(rel.startswith(path) and (needle == '*' or needle in line) for path, needle in rules)


def prose_lines_md(text):
    """Yield (lineno, prose) for lines outside fences and frontmatter, with code spans and URLs removed."""
    in_fence = False
    lines = text.splitlines()
    start = 0
    if lines and lines[0] == '---':
        try:
            start = lines.index('---', 1) + 1
        except ValueError:
            start = 0
    for i, line in enumerate(lines[start:], start + 1):
        if line.strip().startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield i, URL.sub('', INLINE_CODE.sub('', line))


def prose_lines_toml(text):
    """Only the developer_instructions strings carry prose."""
    for m in re.finditer(r'developer_instructions\s*=\s*(?:"""(.*?)"""|"((?:[^"\\]|\\.)*)")', text, re.S):
        body = m.group(1) if m.group(1) is not None else m.group(2).encode().decode('unicode_escape')
        base = text[:m.start()].count('\n') + 1
        for i, line in enumerate(body.splitlines()):
            yield base + i, URL.sub('', INLINE_CODE.sub('', line))


def prose_lines_py(text):
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(r'["\']', line) and not line.lstrip().startswith('#'):
            yield i, line


def check(path, lines, rules, problems):
    rel = path.relative_to(ROOT).as_posix()
    for lineno, prose in lines:
        for kind, found in (('dash', DASHES.search(prose)), ('banned word', BANNED.search(prose))):
            if found and not excepted(rel, prose, rules):
                problems.append(f'{rel}:{lineno}: {kind} {found.group(0)!r}')


def main():
    rules = load_exceptions()
    problems = []
    for path in tracked(['*.md']):
        check(path, prose_lines_md(path.read_text(errors='replace')), rules, problems)
    for path in tracked(['codex/agents/*.toml']):
        check(path, prose_lines_toml(path.read_text(errors='replace')), rules, problems)
    for path in tracked(['*.py']):
        check(path, prose_lines_py(path.read_text(errors='replace')), rules, problems)
    for problem in problems:
        print(f'::error::{problem}')
    if problems:
        print(f'check_style: {len(problems)} problems')
        return 1
    print('check_style: no dashes or banned words in tracked prose')
    return 0


if __name__ == '__main__':
    sys.exit(main())
