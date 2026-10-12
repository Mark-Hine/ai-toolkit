"""Template rendering for the agent-neutral sources under src/.

A source is Markdown with two additions. Tokens such as `{@project_file}` or `{@invoke web-kit/run-app}`
render to each target's wording. Line-level blocks keep text for some targets only:

    <!-- if: plan_mode -->
    text for targets with the plan_mode capability
    <!-- else -->
    text for the others
    <!-- end -->

A condition is a comma-separated list, true when any item is. An item is a capability flag (`plan_mode`),
a negated flag (`!plan_mode`), or a key and value (`target=codex`, `ci_cli=agy`). Blocks do not nest.
"""
import json
import re

TOKEN = re.compile(r'\{@([a-z_]+)(?: ([^{}\n]+))?\}')
IF = re.compile(r'^\s*<!-- if: (.+?) -->\s*$')
ELSE = re.compile(r'^\s*<!-- else -->\s*$')
END = re.compile(r'^\s*<!-- end -->\s*$')

# Literal agent wording that belongs behind a token or inside a block. The source lint fails on these.
AGENT_LITERALS = [
    re.compile(r'~/\.(claude|codex|gemini)\b'),
    re.compile(r'\b(CLAUDE|GEMINI)\.md\b'),
    re.compile(r'(?<![\w.-])AGENTS\.md\b'),
    re.compile(r'(?<![\w-])/(android|ios|web|design)-kit:'),
    re.compile(r'\b(android|ios|web|design)-kit:standards\b'),
    re.compile(r'\$(android|ios|web|design|toolkit)-[a-z]'),
    re.compile(r'\$pr-review\b'),
    re.compile(r'\$\{CLAUDE_[A-Z_]+\}'),
]


class RenderError(Exception):
    pass


def condition_holds(expr, target):
    for item in (part.strip() for part in expr.split(',')):
        if not item:
            raise RenderError(f'empty condition item in "{expr}"')
        if '=' in item:
            key, value = (s.strip() for s in item.split('=', 1))
            target.check_value(key, value)
            if str(target.value(key)) == value:
                return True
        elif item.startswith('!'):
            if not target.flag(item[1:]):
                return True
        elif target.flag(item):
            return True
    return False


def apply_blocks(text, target, source='<source>'):
    out = []
    state = None  # None outside a block, else (keep_current_branch, seen_else)
    for number, line in enumerate(text.split('\n'), 1):
        if IF.match(line):
            if state is not None:
                raise RenderError(f'{source}:{number}: nested if block')
            state = (condition_holds(IF.match(line).group(1), target), False)
            continue
        if ELSE.match(line):
            if state is None or state[1]:
                raise RenderError(f'{source}:{number}: else without an open if')
            state = (not state[0], True)
            continue
        if END.match(line):
            if state is None:
                raise RenderError(f'{source}:{number}: end without an open if')
            state = None
            continue
        if state is None or state[0]:
            out.append(line)
    if state is not None:
        raise RenderError(f'{source}: if block is not closed')
    return '\n'.join(out)


def apply_tokens(text, target, source='<source>'):
    def replace(match):
        name, arg = match.group(1), match.group(2)
        try:
            return target.token(name, arg)
        except KeyError:
            raise RenderError(f'{source}: unknown token {match.group(0)} for target {target.name}') from None
    return TOKEN.sub(replace, text)


def render(text, target, source='<source>'):
    return apply_tokens(apply_blocks(text, target, source), target, source)


def lint(text, source='<source>'):
    """Literal agent wording outside blocks, as (line number, line) pairs."""
    problems = []
    inside = False
    for number, line in enumerate(text.split('\n'), 1):
        if IF.match(line):
            inside = True
            continue
        if END.match(line):
            inside = False
            continue
        if inside or ELSE.match(line):
            continue
        if any(pattern.search(line) for pattern in AGENT_LITERALS):
            problems.append((number, line.strip()))
    return problems


def split_frontmatter(text):
    """(frontmatter block without fences, body). The block is '' when the text has none."""
    if text.startswith('---\n'):
        end = text.find('\n---\n', 4)
        if end != -1:
            return text[4:end], text[end + 5:]
    return '', text


def parse_frontmatter(block):
    """Ordered (key, raw) pairs. `raw` keeps the value text and any indented continuation lines verbatim, so
    folded scalars, lists and nested maps survive a round trip. A YAML subset, not a YAML parser."""
    entries = []
    for line in block.split('\n'):
        if line and not line[0].isspace() and ':' in line:
            key, rest = line.split(':', 1)
            entries.append([key.strip(), rest.strip()])
        elif entries:
            entries[-1][1] += '\n' + line
        elif line.strip():
            raise RenderError(f'frontmatter line before any key: {line!r}')
    return [tuple(entry) for entry in entries]


def scalar(raw):
    """The string value of a one-line or folded scalar."""
    first, _, rest = raw.partition('\n')
    if first in ('>-', '>', '|', '|-'):
        lines = [line.strip() for line in rest.split('\n') if line.strip()]
        return ' '.join(lines) if first.startswith('>') else '\n'.join(lines)
    if rest.strip():
        raise RenderError(f'expected a scalar, got a block: {raw!r}')
    if first.startswith('"'):
        return json.loads(first)
    if first.startswith("'") and first.endswith("'"):
        return first[1:-1].replace("''", "'")
    return first


def string_list(raw):
    """A flow list `[a, b]` or a block list of `- item` lines."""
    raw = raw.strip()
    if raw.startswith('['):
        return [item.strip() for item in raw[1:-1].split(',') if item.strip()]
    return [line.strip()[2:].strip() for line in raw.split('\n') if line.strip().startswith('- ')]


def paths_of(text):
    """The `paths:` globs of a rule, for the Antigravity scope line."""
    block, _ = split_frontmatter(text)
    match = re.search(r'^paths:\s*\n((?:\s+-\s+.*\n?)+)', block + '\n', re.M)
    return re.findall(r'^\s+-\s+"?([^"\n]+)"?\s*$', match.group(1), re.M) if match else []
