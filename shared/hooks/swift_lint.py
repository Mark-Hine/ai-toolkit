#!/usr/bin/env python3
"""PostToolUse Swift lint shared by the ai-toolkit layers. Canonical source: shared/hooks/swift_lint.py.

Runs SwiftFormat --lint and SwiftLint on edited .swift files, only when the nearest enclosing
directory of the file (up to the git root) carries the tool's config and the binary is installed.
Never rewrites files. Usage: swift_lint.py [--agent claude|codex|antigravity]
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

TOTAL_BUDGET = 45
PER_TOOL_BUDGET = 10
CHECKS = [('swiftformat', '.swiftformat', ['--lint', '--quiet', '--config']),
          ('swiftlint', '.swiftlint.yml', ['lint', '--quiet', '--config'])]


def tool_args(event):
    call = event.get('toolCall') if isinstance(event, dict) else None
    args = call.get('args', {}) if isinstance(call, dict) else event.get('tool_input', {})
    if isinstance(args, str):
        args = {'command': args}
    return args if isinstance(args, dict) else {}


def changed_swift_files(event):
    args = tool_args(event)
    paths = [args.get('TargetFile', ''), args.get('file_path', '')]
    patch = args.get('patch', args.get('command', ''))
    if isinstance(patch, str):
        paths += re.findall(r'^\*\*\* (?:Add File|Update File|Move to): (.+)$', patch, re.M)
    cwd = Path(event.get('cwd') or Path.cwd())
    return sorted({(cwd / path).resolve() for path in paths
                   if isinstance(path, str) and path.endswith('.swift') and (cwd / path).is_file()})


def git_root(path):
    repo = subprocess.run(['git', '-C', str(path.parent), 'rev-parse', '--show-toplevel'],
                          text=True, capture_output=True, timeout=5, check=False)
    return Path(repo.stdout.strip()) if repo.returncode == 0 and repo.stdout.strip() else None


def nearest_config(path, root, config):
    """The config file closest to the edited file, searching upwards and stopping at the git root."""
    for directory in [path.parent, *path.parent.parents]:
        candidate = directory / config
        if candidate.is_file():
            return candidate
        if directory == root:
            break
    return None


def classify(output):
    """SwiftLint prints `file:line:col: error|warning: ...`. Anything else counts as an error."""
    errors, warnings = [], []
    for line in output.splitlines():
        (warnings if re.search(r': warning: ', line) else errors).append(line)
    return errors, warnings


def findings(event):
    """Return (errors, warnings). Errors block on Claude, warnings are context only."""
    errors, warnings = [], []
    deadline = time.monotonic() + TOTAL_BUDGET
    for path in changed_swift_files(event):
        try:
            root = git_root(path)
            if root is None:
                continue
            for tool, config, flags in CHECKS:
                binary = shutil.which(tool)
                config_path = nearest_config(path, root, config)
                if config_path is None or not binary:
                    continue
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    warnings.append('Swift lint hook reached its time limit; remaining files are Unverified.')
                    return errors, warnings
                result = subprocess.run([binary, *flags, str(config_path), str(path)], cwd=config_path.parent,
                                        text=True, capture_output=True, timeout=min(PER_TOOL_BUDGET, remaining), check=False)
                output = (result.stdout + result.stderr).strip()
                if not (result.returncode or output):
                    continue
                if tool == 'swiftlint':
                    tool_errors, tool_warnings = classify(output)
                else:
                    tool_errors, tool_warnings = [output or 'Exited with code ' + str(result.returncode)], []
                if tool_errors:
                    errors.append(f'{tool} findings in {path}:\n' + '\n'.join(tool_errors))
                if tool_warnings:
                    warnings.append(f'{tool} warnings in {path}:\n' + '\n'.join(tool_warnings))
        except (OSError, subprocess.TimeoutExpired) as error:
            warnings.append(f'Swift lint Unverified for {path}: {error}')
    return errors, warnings


def render(agent, errors, warnings):
    if agent == 'antigravity':
        if errors or warnings:
            sys.stderr.write('\n'.join(errors + warnings) + '\n')
        return json.dumps({})
    if not (errors or warnings):
        return ''
    context = '\n\n'.join(errors + warnings) + '\nFix applicable findings without disabling rules.'
    out = {'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': context}}
    if errors:
        out['decision'] = 'block'
        out['reason'] = context
    return json.dumps(out)


def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--agent', choices=['claude', 'codex', 'antigravity'], default='codex')
    try:
        opts = parser.parse_args(argv)
    except SystemExit:
        opts = argparse.Namespace(agent='codex')
    try:
        raw = (stdin or sys.stdin).read()
        event = json.loads(raw) if raw.strip() else {}
        errors, warnings = findings(event)
    except (ValueError, TypeError, AttributeError) as error:
        errors, warnings = [], [f'Swift lint hook could not inspect the edit: {type(error).__name__}']
    output = render(opts.agent, errors, warnings)
    if output:
        print(output)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
