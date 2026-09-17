#!/usr/bin/env python3
"""Report Swift lint findings after edits, only for repositories that opt in."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


def changed_swift_files(event):
    args = event.get('tool_input', {})
    if isinstance(args, str):
        args = {'command': args}
    if not isinstance(args, dict):
        return []
    paths = [args.get('file_path', '')]
    patch = args.get('patch', args.get('command', ''))
    if isinstance(patch, str):
        paths += re.findall(r'^\*\*\* (?:Add File|Update File|Move to): (.+)$', patch, re.M)
    cwd = Path(event.get('cwd') or Path.cwd())
    return sorted({(cwd / path).resolve() for path in paths
                   if isinstance(path, str) and path.endswith('.swift') and (cwd / path).is_file()})


def findings(event):
    messages = []
    deadline = time.monotonic() + 45
    for path in changed_swift_files(event):
        try:
            repo = subprocess.run(['git', '-C', str(path.parent), 'rev-parse', '--show-toplevel'],
                                  text=True, capture_output=True, timeout=5, check=False)
            if repo.returncode:
                continue
            root = Path(repo.stdout.strip())
            checks = [('swiftformat', '.swiftformat', ['--lint', '--quiet', '--config']),
                      ('swiftlint', '.swiftlint.yml', ['lint', '--quiet', '--config'])]
            for tool, config, flags in checks:
                binary = shutil.which(tool)
                if not (root / config).is_file() or not binary:
                    continue
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return messages + ['Swift lint hook reached its time limit; remaining files are Unverified.']
                result = subprocess.run([binary, *flags, str(root / config), str(path)], cwd=root,
                                        text=True, capture_output=True, timeout=min(10, remaining), check=False)
                output = (result.stdout + result.stderr).strip()
                if result.returncode or output:
                    messages.append(f'{tool} findings in {path}:\n{output or "Exited with code " + str(result.returncode)}')
        except (OSError, subprocess.TimeoutExpired) as error:
            messages.append(f'Swift lint Unverified for {path}: {error}')
    return messages


def main():
    try:
        messages = findings(json.load(sys.stdin))
    except (ValueError, TypeError, AttributeError) as error:
        messages = [f'Swift lint hook could not inspect the edit: {type(error).__name__}']
    if messages:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PostToolUse',
              'additionalContext': '\n\n'.join(messages) + '\nFix applicable findings without disabling rules.'}}))


if __name__ == '__main__':
    main()
