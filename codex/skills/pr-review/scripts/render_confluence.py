#!/usr/bin/env python3
"""Render a pr-review Markdown document as a Confluence page, and publish it.

Stdlib-only. `render` converts the Markdown subset that references/template.md emits into
Confluence storage format:

- the blockquote before the first `##` heading becomes an info panel (the verdict),
- severity and status markers such as `🔴 Blocker` or `✅ Fixed` become status lozenges,
- a fenced block after a `**PR comment**` label becomes a code block titled "PR comment", whose
  copy button gives the exact Markdown to paste into the PR,
- a paragraph that starts `**Evidence.**` becomes a collapsed expand section,
- `<a id="...">` anchors and heading slugs become anchor macros, so `[B1](#b1)` links resolve.
- tables span the full page width, to match the full-width page `publish` sets.

`publish` creates a page or updates one through the Confluence REST v2 API and sets it to full
width. An update names the version it expects to replace (`--expect-version`). If the live page
is newer, someone edited it by hand, so the script refuses rather than overwrite the edit.

Credentials come from CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL and CONFLUENCE_TOKEN, or
--token-file for the token. The token is never printed.
"""

import argparse
import base64
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

# Marker -> (lozenge colour, lozenge text). The markers are the template's vocabulary.
MARKERS = [
    ("🔴", "Blocker", "Red"), ("🟣", "Question", "Purple"), ("🟠", "Major", "Yellow"),
    ("⚪", "Nit", "Grey"), ("🆕", "New", "Blue"), ("☐", "Open", "Grey"),
    ("⚠", "Partial", "Yellow"), ("✅", "Fixed", "Green"), ("❌", "Regressed", "Red"),
]
MARKER_RE = re.compile(
    "(" + "|".join(re.escape(e) for e, _, _ in MARKERS) + ")️?[  ]+("
    + "|".join(w for _, w, _ in MARKERS) + r")\b")
MARKER_COLOUR = {(e, w): c for e, w, c in MARKERS}

ANCHOR_RE = re.compile(r'<a id="([^"]+)"></a>\s*')

# Pages are published full width, and the editor otherwise draws tables at its narrow default.
TABLE_WIDTH = 1800


def lozenge(colour, title):
    return ('<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">'
            f'{colour}</ac:parameter><ac:parameter ac:name="title">{html.escape(title)}'
            '</ac:parameter></ac:structured-macro>')


def anchor(name):
    return ('<ac:structured-macro ac:name="anchor"><ac:parameter ac:name="">'
            f'{html.escape(name)}</ac:parameter></ac:structured-macro>')


def slug(text):
    text = re.sub(r"<[^>]+>|[`*_]", "", text).lower()
    return re.sub(r"[^a-z0-9 -]", "", text).strip().replace(" ", "-")


def inline(text):
    """Convert one line of inline Markdown. Code spans and links are parked behind sentinels
    first, so escaping and marker matching never touch their contents."""
    parked = []

    def park(fragment):
        parked.append(fragment)
        return f"\x00{len(parked) - 1}\x00"

    text = ANCHOR_RE.sub(lambda m: park(anchor(m.group(1))), text)
    text = re.sub(r"`([^`]+)`", lambda m: park(f"<code>{html.escape(m.group(1))}</code>"), text)

    def link(m):
        label, target = m.group(1), m.group(2)
        body = inline(label)
        if target.startswith("#"):
            return park(f'<ac:link ac:anchor="{html.escape(target[1:])}"><ac:link-body>{body}'
                        "</ac:link-body></ac:link>")
        return park(f'<a href="{html.escape(target)}">{body}</a>')

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"(?<![\"=])(https?://[^\s)<]+)",
                  lambda m: park(f'<a href="{html.escape(m.group(1))}">{html.escape(m.group(1))}</a>'),
                  text)
    text = MARKER_RE.sub(
        lambda m: park(lozenge(MARKER_COLOUR[(m.group(1), m.group(2))], m.group(2).upper())), text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    while "\x00" in text:
        text = re.sub(r"\x00(\d+)\x00", lambda m: parked[int(m.group(1))], text)
    return text


def split_row(line):
    cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [c.strip().replace("\\|", "|") for c in cells]


def is_separator(line):
    return re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$", line) is not None


def render_list(items):
    """items: [(indent, start, text)] -> nested <ul>/<ol>. start is None for a bullet, else the item's
    number, so a numbered list that resumes after other content keeps counting."""
    out, stack = [], []
    for indent, start, text in items:
        while stack and stack[-1][0] > indent:
            out.append(f"</li></{stack.pop()[1]}>")
        if stack and stack[-1][0] == indent:
            out.append("</li>")
        else:
            tag = "ul" if start is None else "ol"
            stack.append((indent, tag))
            out.append(f'<ol start="{start}">' if start not in (None, 1) else f"<{tag}>")
        out.append(f"<li>{inline(text)}")
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "".join(out)


def paragraph(lines):
    parts = []
    for i, line in enumerate(lines):
        hard_break = line.endswith("  ") and i < len(lines) - 1
        parts.append(inline(line.strip()) + ("<br/>" if hard_break else ""))
    return "<p>" + " ".join(parts).replace("<br/> ", "<br/>") + "</p>"


def render(md):
    lines = md.split("\n")
    out, i, seen_heading, label = [], 0, False, None
    list_re = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            i += 1
            continue
        if line.startswith(">"):
            block = []
            while i < len(lines) and lines[i].startswith(">"):
                block.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            paras, cur = [], []
            for b in block + [""]:
                if b.strip():
                    cur.append(b)
                elif cur:
                    paras.append(paragraph(cur))
                    cur = []
            body = "".join(paras)
            if not seen_heading:
                out.append('<ac:structured-macro ac:name="info"><ac:rich-text-body>'
                           f"{body}</ac:rich-text-body></ac:structured-macro>")
            else:
                out.append(f"<blockquote>{body}</blockquote>")
            continue
        if line.startswith("```"):
            lang = line[3:].strip()
            body, i = [], i + 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            params = ""
            if lang and lang != "text":
                params += f'<ac:parameter ac:name="language">{html.escape(lang)}</ac:parameter>'
            if label:
                params += f'<ac:parameter ac:name="title">{html.escape(label)}</ac:parameter>'
                label = None
            out.append(f'<ac:structured-macro ac:name="code">{params}<ac:plain-text-body>'
                       "<![CDATA[" + "\n".join(body).replace("]]>", "]]]]><![CDATA[>")
                       + "]]></ac:plain-text-body></ac:structured-macro>")
            continue
        m = re.match(r"^(#{2,4})\s+(.*)$", line)
        if m:
            seen_heading = True
            level, text = len(m.group(1)), m.group(2)
            ids = ANCHOR_RE.findall(text)
            text = ANCHOR_RE.sub("", text)
            anchors = "".join(anchor(a) for a in ids + [slug(text)])
            out.append(f"<h{level}>{anchors}{inline(text)}</h{level}>")
            i += 1
            continue
        if line.strip() == "---":
            out.append("<hr/>")
            i += 1
            continue
        if line.lstrip().startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            head = split_row(line)
            rows, i = [], i + 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            cells = "".join(f"<th>{inline(c)}</th>" for c in head)
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                           for r in rows)
            out.append(f'<table data-table-width="{TABLE_WIDTH}" data-layout="default"><tbody>'
                       f"<tr>{cells}</tr>{body}</tbody></table>")
            continue
        if list_re.match(line):
            items = []
            while i < len(lines) and list_re.match(lines[i]):
                lm = list_re.match(lines[i])
                marker = lm.group(2)
                items.append((len(lm.group(1)), int(marker[:-1]) if marker[0].isdigit() else None, lm.group(3)))
                i += 1
            out.append(render_list(items))
            continue
        para = []
        while (i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", ">", "```", "|"))
               and not list_re.match(lines[i]) and lines[i].strip() != "---"):
            para.append(lines[i])
            i += 1
        text = " ".join(p.strip() for p in para)
        label_m = re.fullmatch(r"\*\*(PR comment)\*\*(?:\s*\(.*\))?", text)
        if label_m and i < len(lines) and next((l for l in lines[i:] if l.strip()), "").startswith("```"):
            label = label_m.group(1)
            continue
        evidence = re.match(r"^\*\*Evidence\.\*\*\s*(.*)$", text)
        if evidence:
            out.append('<ac:structured-macro ac:name="expand"><ac:parameter ac:name="title">'
                       f"Evidence</ac:parameter><ac:rich-text-body>{paragraph([evidence.group(1)])}"
                       "</ac:rich-text-body></ac:structured-macro>")
            continue
        out.append(paragraph(para))
    return "\n".join(out)


class Confluence:
    def __init__(self, base, email, token):
        self.base = base.rstrip("/")
        self.auth = "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()

    def call(self, method, path, body=None):
        req = urllib.request.Request(
            f"{self.base}/api/v2{path}", method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": self.auth, "Accept": "application/json",
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors="replace")[:500]
            raise SystemExit(f"{method} {path} failed: HTTP {err.code} {detail}")

    def set_full_width(self, page_id):
        existing = {p["key"]: p for p in self.call("GET", f"/pages/{page_id}/properties")["results"]}
        for key in ("content-appearance-published", "content-appearance-draft"):
            prop = existing.get(key)
            if prop is None:
                self.call("POST", f"/pages/{page_id}/properties", {"key": key, "value": "full-width"})
            elif prop["value"] != "full-width":
                self.call("PUT", f"/pages/{page_id}/properties/{prop['id']}",
                          {"key": key, "value": "full-width",
                           "version": {"number": prop["version"]["number"] + 1}})


def publish(args):
    base = args.base_url or os.environ.get("CONFLUENCE_BASE_URL")
    email = args.email or os.environ.get("CONFLUENCE_EMAIL")
    token = os.environ.get("CONFLUENCE_TOKEN")
    if args.token_file:
        with open(os.path.expanduser(args.token_file)) as fh:
            token = fh.read().strip()
    if not (base and email and token):
        raise SystemExit("set CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL and CONFLUENCE_TOKEN "
                         "(or --base-url, --email and --token-file)")
    api = Confluence(base, email, token)
    with open(args.xhtml) as fh:
        storage = fh.read()
    body = {"representation": "storage", "value": storage}
    if args.page_id:
        live = api.call("GET", f"/pages/{args.page_id}")
        live_version = live["version"]["number"]
        if args.expect_version is None:
            raise SystemExit(f"page {args.page_id} is at version {live_version}. Pass "
                             "--expect-version with the version you last published.")
        if live_version != args.expect_version:
            raise SystemExit(f"page {args.page_id} is at version {live_version}, not "
                             f"{args.expect_version}. Someone edited it. Compare the live page "
                             "with yours and carry the edits over before publishing again.")
        version = {"number": live_version + 1}
        if args.message:
            version["message"] = args.message
        page = api.call("PUT", f"/pages/{args.page_id}",
                        {"id": args.page_id, "status": "current",
                         "title": args.title or live["title"], "body": body, "version": version})
    else:
        if not (args.title and args.space_id):
            raise SystemExit("a new page needs --title and --space-id")
        request = {"spaceId": args.space_id, "status": "current", "title": args.title, "body": body}
        if args.parent_id:
            request["parentId"] = args.parent_id
        page = api.call("POST", "/pages", request)
    api.set_full_width(page["id"])
    link = page.get("_links", {})
    url = (link.get("base") or base) + link.get("webui", "")
    print(json.dumps({"id": page["id"], "version": page["version"]["number"], "url": url}))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("render", help="convert a review .md into Confluence storage XHTML")
    r.add_argument("markdown")
    r.add_argument("--out", help="output path (default: stdout)")
    p = sub.add_parser("publish", help="create or update a Confluence page from rendered XHTML")
    p.add_argument("xhtml")
    p.add_argument("--page-id", help="update this page")
    p.add_argument("--expect-version", type=int, help="the live version this update replaces")
    p.add_argument("--title", help="page title (required for a new page)")
    p.add_argument("--space-id", help="space for a new page")
    p.add_argument("--parent-id", help="parent page or folder for a new page")
    p.add_argument("--message", help="version message")
    p.add_argument("--base-url")
    p.add_argument("--email")
    p.add_argument("--token-file")
    args = parser.parse_args()
    if args.command == "render":
        with open(args.markdown) as fh:
            storage = render(fh.read())
        if args.out:
            with open(args.out, "w") as fh:
                fh.write(storage)
        else:
            sys.stdout.write(storage)
    else:
        publish(args)


if __name__ == "__main__":
    main()
