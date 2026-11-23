#!/usr/bin/env python3
"""Measure Claude Code session health from local transcripts and the global setup.

Reads `~/.claude/projects/**/*.jsonl` and prints one JSON document of counts. It never prints
transcript text, so the output is safe to keep beside the dated scorecards in `docs/health/`.
`--alias` replaces project folder names with stable hashes for a report that will be committed.
Standard library only, Python 3.11 or later.
"""
import argparse
import hashlib
import json
import re
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

EVAL_SLUG = re.compile(r'trigger-eval|eval-project|evalproj|-tmp-smoke', re.I)
READ_TOOLS = {'grep', 'rg', 'cat', 'sed', 'head', 'tail', 'awk', 'find', 'ls'}
SHELL_SEARCH = {'grep', 'rg', 'cat', 'sed', 'head', 'tail', 'awk'}
TEST_PATH = re.compile(r'/(test|androidTest|tests|__tests__)/|Tests?\.(kt|swift|java)$|\.(test|spec)\.[jt]sx?$|/test_[^/]+\.py$')
CODE_PATH = re.compile(r'\.(kt|kts|swift|java|ts|tsx|js|jsx|py)$')
TEST_FUNC = re.compile(r'@Test\b|^\s*func test\w*\(|^\s*(?:it|test)\(\s*[\'"`]|^\s*def test_\w+\(|withData\(', re.M)
GRADLE_TEST = re.compile(r'gradlew\b[^|;&]*?(?<![\w-])(?::[\w:-]+:)?(test\w*|connected\w*Test|check)(?![\w-])')
FENCE = re.compile(r'```.*?```', re.S)
INLINE_CODE = re.compile(r'`[^`\n]*`')
OFFER = re.compile(r'(want me to|would you like|let me know if|shall i|should i)[^.?!\n]*\?\s*$', re.I)

# Order matters. The first matching category wins.
ERROR_CATEGORIES = [
    ('worktree_guard', re.compile(r'worktree', re.I)),
    ('hook_block', re.compile(r'hook.{0,40}(block|denied|deny)|blocked by.{0,20}hook|PreToolUse', re.I)),
    ('user_rejected', re.compile(r"user doesn't want to proceed|user rejected|tool use was rejected", re.I)),
    ('permission_denied', re.compile(r'permission.{0,30}(denied|not granted)|auto.?mode.{0,40}(denied|blocked)', re.I)),
    ('edit_before_read', re.compile(r'has not been read yet|read it first', re.I)),
    ('edit_no_match', re.compile(r'string to replace not found|found \d+ matches', re.I)),
    ('agent_type_missing', re.compile(r'agent type .{0,60}not found', re.I)),
    ('mcp_auth', re.compile(r'not logged in|unauthori[sz]ed|\b401\b|\b403\b|forbidden', re.I)),
    ('input_validation', re.compile(r'InputValidationError', re.I)),
    ('missing_binary', re.compile(r'command not found', re.I)),
    ('git_fatal', re.compile(r'^fatal: ', re.M)),
    ('nonzero_exit', re.compile(r'exit code \d+', re.I)),
]


def classify_error(text):
    for name, pattern in ERROR_CATEGORIES:
        if pattern.search(text):
            return name
    return 'other'


def first_words(command):
    """The executable of each simple command in a shell line, ignoring env assignments."""
    words = []
    for part in re.split(r'&&|\|\||[;|\n]', command):
        tokens = [t for t in part.strip().split() if not re.fullmatch(r'\w+=\S*', t)]
        while tokens and tokens[0] in ('do', 'then', 'else', 'while', 'until', 'if', '!', '(', '{'):
            tokens = tokens[1:]
        if tokens:
            words.append(tokens[0].rsplit('/', 1)[-1])
    return words


def bash_facts(command):
    words = first_words(command)
    facts = Counter()
    if words and words[0] in SHELL_SEARCH:
        facts['shell_for_read_or_search'] += 1
    if re.search(r'(cat|tee)\s*>+\s*\S|<<\s*[\'"]?\w+', command) and re.search(r'>\s*[\w./~$"]', command):
        facts['shell_file_write'] += 1
    if 'sleep' in words:
        facts['sleep'] += 1
        if re.search(r'\b(while|until|for)\b', command):
            facts['polling_loop'] += 1
    if 'timeout' in words:
        facts['timeout_binary'] += 1
    if GRADLE_TEST.search(command):
        facts['gradle_test_runs'] += 1
        if '--tests' not in command:
            facts['gradle_test_unfiltered'] += 1
            if not re.search(r'gradlew\b[^|;&]*\s:[\w:-]+:(test|connected)', command):
                facts['gradle_test_whole_project'] += 1
    if re.search(r'xcodebuild\b[^|;&]*\btest\b', command):
        facts['xcodebuild_test_runs'] += 1
        if '-only-testing' not in command:
            facts['xcodebuild_test_unfiltered'] += 1
    return facts


def prose(text):
    return INLINE_CODE.sub(' ', FENCE.sub(' ', text))


def reply_facts(text):
    body = prose(text)
    return {
        'words': len(body.split()),
        'dashes': len(re.findall(r'[\u2013\u2014]', body)),
        'semicolons': body.count(';'),
        'bold': 1 if re.search(r'\*\*[^*\n]+\*\*', body) else 0,
        'offer': 1 if OFFER.search(text.strip()) else 0,
    }


def result_text(block):
    content = block.get('content')
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(item.get('text', '') for item in content if isinstance(item, dict))
    return ''


def is_prompt(event):
    """A message the person typed, as opposed to a tool result or a harness note."""
    if event.get('type') != 'user' or event.get('isMeta') or event.get('isSidechain'):
        return False
    content = event.get('message', {}).get('content')
    if isinstance(content, str):
        return not content.lstrip().startswith('<')
    return isinstance(content, list) and any(
        block.get('type') == 'text' and not block.get('text', '').lstrip().startswith('<')
        for block in content if isinstance(block, dict)) and not any(
        block.get('type') == 'tool_result' for block in content if isinstance(block, dict))


def scan(path, totals, replies, since=''):
    """Fold one transcript's events from `since` (an ISO timestamp) into `totals`.

    Returns (tool calls, prompts). File modified times are unreliable, so each event's own timestamp decides.
    """
    calls = prompts = 0
    names = {}
    last_text, stamp = None, ''
    with open(path, errors='replace') as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            kind = event.get('type')
            stamp = event.get('timestamp') or stamp
            if stamp and stamp < since:
                continue
            if kind == 'system' and 'compact' in str(event.get('subtype', '')):
                totals['compactions'] += 1
            if kind not in ('assistant', 'user'):
                continue
            if is_prompt(event):
                prompts += 1
                if last_text:
                    replies.append(reply_facts(last_text))
                last_text = None
            content = event.get('message', {}).get('content')
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get('type')
                if kind == 'assistant' and btype == 'text' and not event.get('isSidechain'):
                    last_text = block.get('text', '')
                elif btype == 'tool_use':
                    calls += 1
                    name, args = block.get('name', '?'), block.get('input') or {}
                    names[block.get('id')] = name
                    totals['tool:' + name] += 1
                    if name.startswith('mcp__'):
                        totals['mcp:' + name.split('__')[1]] += 1
                    if name == 'Bash':
                        for fact, count in bash_facts(str(args.get('command', ''))).items():
                            totals[fact] += count
                    elif name == 'Agent':
                        totals['agent_spawns'] += 1
                        if not args.get('model') and args.get('subagent_type') != 'fork':
                            totals['agent_spawns_without_model'] += 1
                    elif name in ('Write', 'Edit'):
                        target = str(args.get('file_path', ''))
                        added = str(args.get('content') or args.get('new_string') or '')
                        if TEST_PATH.search(target):
                            totals['test_functions_added'] += len(TEST_FUNC.findall(added))
                        elif CODE_PATH.search(target):
                            totals['production_lines_written'] += added.count('\n') + 1
                elif btype == 'tool_result' and block.get('is_error'):
                    totals['tool_errors'] += 1
                    totals['error:' + classify_error(result_text(block))] += 1
                    totals['error_tool:' + names.get(block.get('tool_use_id'), '?')] += 1
    if last_text:
        replies.append(reply_facts(last_text))
    return calls, prompts


def alias(name):
    return 'proj-' + hashlib.sha1(name.encode()).hexdigest()[:6]


def percentile(values, share):
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(share * len(ordered)))]


def setup_facts(home):
    """Sizes of what loads into every session, and housekeeping counts."""
    facts = {}
    always = []
    for path in [home / 'CLAUDE.md', home / 'machine.md', *sorted((home / 'rules').glob('*.md'))]:
        if not path.is_file():
            continue
        text = path.read_text(errors='replace')
        head = text.split('---', 2)[1] if text.startswith('---') and text.count('---') >= 2 else ''
        if path.parent.name == 'rules' and re.search(r'^paths:', head, re.M):
            continue
        always.append((path.name, len(text)))
    facts['always_loaded_chars'] = sum(size for _, size in always)
    facts['always_loaded_files'] = dict(always)
    indexes = sorted(((p.stat().st_size, p.parent.parent.name) for p in (home / 'projects').glob('*/memory/MEMORY.md')),
                     reverse=True)
    facts['largest_memory_index_bytes'] = indexes[0][0] if indexes else 0
    facts['memory_indexes_over_3000_bytes'] = sum(1 for size, _ in indexes if size > 3000)
    folders = [p.name for p in (home / 'projects').iterdir() if p.is_dir()] if (home / 'projects').is_dir() else []
    facts['project_folders'] = len(folders)
    facts['eval_leftover_folders'] = sum(1 for name in folders if EVAL_SLUG.search(name))
    try:
        settings = json.loads((home / 'settings.json').read_text())
    except (OSError, ValueError):
        settings = {}
    facts['cleanup_period_days'] = settings.get('cleanupPeriodDays')
    facts['allow_rules'] = len(settings.get('permissions', {}).get('allow', []))
    facts['user_prompt_hooks'] = len(settings.get('hooks', {}).get('UserPromptSubmit', []))
    facts['local_skills'] = sum(1 for p in (home / 'skills').iterdir()) if (home / 'skills').is_dir() else 0
    return facts


def collect(home, days, use_alias=False, now=None):
    cutoff = (now or time.time()) - days * 86400
    since = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(cutoff))
    totals, replies = Counter(), []
    sessions, per_project, skipped_eval = [], Counter(), 0
    root = home / 'projects'
    for project in sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []:
        files = [f for f in project.rglob('*.jsonl') if f.stat().st_mtime >= cutoff]
        if EVAL_SLUG.search(project.name):
            skipped_eval += len(files)
            continue
        for path in files:
            is_sub = 'subagents' in path.parts
            calls, prompts = scan(path, totals, replies if not is_sub else [], since)
            if not calls and not prompts:
                continue
            if is_sub:
                totals['subagent_transcripts'] += 1
            else:
                sessions.append((calls, prompts))
                per_project[alias(project.name) if use_alias else project.name] += 1
    tool_calls = sum(v for k, v in totals.items() if k.startswith('tool:'))
    words = sum(r['words'] for r in replies) or 1
    count = len(replies) or 1

    def group(prefix):
        return dict(Counter({k[len(prefix):]: v for k, v in totals.items() if k.startswith(prefix)}).most_common())

    gradle = totals['gradle_test_runs'] or 1
    produced = totals['production_lines_written'] or 1
    return {
        'window_days': days,
        'sessions': len(sessions),
        'subagent_transcripts': totals['subagent_transcripts'],
        'eval_transcripts_skipped': skipped_eval,
        'sessions_by_project': dict(per_project.most_common()),
        'prompts_median': statistics.median([p for _, p in sessions]) if sessions else 0,
        'tool_calls': tool_calls,
        'tool_calls_median': statistics.median([c for c, _ in sessions]) if sessions else 0,
        'tool_calls_p90': percentile([c for c, _ in sessions], 0.9),
        'tool_errors': totals['tool_errors'],
        'tool_error_rate': round(totals['tool_errors'] / (tool_calls or 1), 4),
        'errors_by_category': group('error:'),
        'errors_by_tool': group('error_tool:'),
        'workarounds': {key: totals[key] for key in (
            'shell_for_read_or_search', 'shell_file_write', 'sleep', 'polling_loop', 'timeout_binary')},
        'shell_for_read_share': round(totals['shell_for_read_or_search'] / (tool_calls or 1), 4),
        'tests': {
            'test_functions_added': totals['test_functions_added'],
            'production_lines_written': totals['production_lines_written'],
            'tests_per_100_production_lines': round(100 * totals['test_functions_added'] / produced, 2),
            'gradle_test_runs': totals['gradle_test_runs'],
            'gradle_test_unfiltered': totals['gradle_test_unfiltered'],
            'gradle_test_whole_project': totals['gradle_test_whole_project'],
            'gradle_unfiltered_share': round(totals['gradle_test_unfiltered'] / gradle, 4),
            'xcodebuild_test_runs': totals['xcodebuild_test_runs'],
            'xcodebuild_test_unfiltered': totals['xcodebuild_test_unfiltered'],
        },
        'replies': {
            'count': len(replies),
            'median_words': statistics.median([r['words'] for r in replies]) if replies else 0,
            'p90_words': percentile([r['words'] for r in replies], 0.9),
            'dashes_per_1000_words': round(1000 * sum(r['dashes'] for r in replies) / words, 2),
            'semicolons_per_1000_words': round(1000 * sum(r['semicolons'] for r in replies) / words, 2),
            'share_with_bold': round(sum(r['bold'] for r in replies) / count, 4),
            'share_ending_in_offer': round(sum(r['offer'] for r in replies) / count, 4),
        },
        'subagents': {'spawns': totals['agent_spawns'], 'spawns_without_model': totals['agent_spawns_without_model']},
        'compactions': totals['compactions'],
        'mcp_calls_by_server': group('mcp:'),
        'top_tools': dict(list(group('tool:').items())[:12]),
        'setup': setup_facts(home),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--home', type=Path, default=Path.home() / '.claude')
    parser.add_argument('--days', type=int, default=14)
    parser.add_argument('--alias', action='store_true', help='hash project names for a committed report')
    parser.add_argument('--out', type=Path, help='write the JSON here instead of stdout')
    args = parser.parse_args(argv)
    text = json.dumps(collect(args.home, args.days, args.alias), indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + '\n')
    else:
        print(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
