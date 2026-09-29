#!/usr/bin/env python3
"""Minimal frontmatter reader for the `verified:` and `sources:` stamps. Standard library only.

Handles `key: scalar` lines and `key:` followed by `  - item` lines, which covers every stamped file
in this repo. It is not a YAML parser.
"""
import re
from datetime import date
from pathlib import Path

URL = re.compile(r'https?://[^\s<>\]`"\'|]+')
TRAILING = '.,;:'


def frontmatter(text):
    """(fields, body). fields maps key to a string or a list of strings."""
    if not text.startswith('---\n'):
        return {}, text
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}, text
    fields, current = {}, None
    for line in text[4:end].splitlines():
        if line.startswith('  - ') and current:
            fields.setdefault(current, []).append(line[4:].strip())
        elif line and not line.startswith(' ') and ':' in line:
            key, _, value = line.partition(':')
            current = key.strip()
            fields[current] = value.strip() or []
    return fields, text[end + 5:]


def stamp(path):
    """(verified date or None, sources) for a file. sources is a list of URLs, or 'inline', or 'house'."""
    fields, _ = frontmatter(Path(path).read_text(errors='replace'))
    raw = fields.get('verified')
    verified = None
    if isinstance(raw, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw):
        verified = date.fromisoformat(raw)
    return verified, fields.get('sources', [])


def body_urls(text):
    """Every URL in a document, code fences included, with trailing punctuation removed."""
    seen = []
    for match in URL.finditer(text):
        url, end = match.group(0), match.end()
        if end < len(text) and text[end] == '<':
            continue  # a pattern such as https://host/path/<page>.json, not a link
        url = url.rstrip(TRAILING)
        while url.endswith(')') and url.count(')') > url.count('('):
            url = url[:-1].rstrip(TRAILING)  # the closing bracket of a markdown link, not part of the URL
        if url not in seen:
            seen.append(url)
    return seen
