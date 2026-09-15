#!/usr/bin/env python3
"""Codex PreToolUse guards. Advisory command parsing is not a shell sandbox."""
import json
from pathlib import PurePosixPath
import re
import shlex
import sys


def shell_source(command):
    """Remove literal heredoc bodies before checking executable shell text."""
    lines = command.splitlines(keepends=True)
    result = []
    pending = []
    header = ''
    for line in lines:
        if pending:
            delimiter, strip_tabs, literal = pending[0]
            candidate = line.lstrip('\t') if strip_tabs else line
            if candidate.rstrip('\r\n') == delimiter:
                pending.pop(0)
                result.append('\n')
            else:
                result.append('\n' if literal else line)
            continue
        result.append(line)
        header += line
        try:
            lexer = shlex.shlex(header, posix=False, punctuation_chars=';&|()<>')
            lexer.whitespace_split = True
            tokens = list(lexer)
        except ValueError:
            continue
        header = ''
        for i, token in enumerate(tokens[:-1]):
            if token != '<<':
                continue
            word = tokens[i + 1]
            strip_tabs = word.startswith('-')
            if strip_tabs:
                word = word[1:]
                if not word and i + 2 < len(tokens):
                    word = tokens[i + 2]
            try:
                delimiter = shlex.split(word)
            except ValueError:
                continue
            if len(delimiter) == 1:
                pending.append((delimiter[0], strip_tabs, any(c in word for c in "'\"\\")))
    return command if pending else ''.join(result)


def timeout_command(tokens):
    """Recognize the wrapper in command positions, excluding ordinary arguments."""
    command_start = True
    redirect_target = False
    wrapper_option = False
    for token in tokens:
        if re.fullmatch(r'[;&|()\n]+', token):
            command_start = True
            redirect_target = False
            wrapper_option = False
            continue
        if re.fullmatch(r'[<>]+', token):
            redirect_target = True
            continue
        if redirect_target:
            redirect_target = False
            continue
        if not command_start:
            continue
        if wrapper_option:
            wrapper_option = False
            continue
        if re.match(r'[A-Za-z_][A-Za-z_0-9]*=', token):
            continue
        if token in {'!', 'if', 'then', 'elif', 'else', 'while', 'until', 'do', '{'}:
            continue
        executable = token.rsplit('/', 1)[-1]
        if executable == 'timeout':
            return True
        if executable in {'sudo', 'env', 'command', 'exec', 'nohup'}:
            continue
        if token.startswith('-'):
            wrapper_option = token in {'-u', '-g', '-h', '-p', '-C', '-T', '--user',
                                       '--group', '--host', '--prompt', '--chdir', '--unset'}
            continue
        command_start = False
    return False


def protected(path):
    p = PurePosixPath(path)
    return (p.name in {'google-services.json', 'GoogleService-Info.plist', 'secrets.properties',
                       'local.properties', 'network_security_config.xml', '.env'}
            or p.name.startswith('.env.')
            or p.suffix in {'.jks', '.keystore', '.p12', '.pem', '.key', '.mobileprovision', '.cer'}
            or (p.suffix in {'.aar', '.jar'} and '/app/libs/' in '/' + str(p))
            or str(p).endswith('gradle/wrapper/gradle-wrapper.jar'))


def shell_reason(command):
    command = shell_source(command)
    # Tokenize literal commands, including quoted refs and git -C/-c options.
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|()<>\n')
        lexer.whitespace = ' \t\r'
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return None  # The shell itself handles invalid syntax.
    if timeout_command(tokens):
        return 'Use tool execution and polling controls instead of timeout.'
    for i, token in enumerate(tokens):
        if token.rsplit('/', 1)[-1] != 'git':
            continue
        args = []
        for arg in tokens[i + 1:]:
            if re.fullmatch(r'[;&|()<>\n]+', arg):
                break
            args.append(arg)
        while args and args[0].startswith('-'):
            opt = args.pop(0)
            if opt in {'-C', '-c', '--git-dir', '--work-tree', '--namespace'} and args:
                args.pop(0)
        if not args:
            continue
        op, rest = args[0], args[1:]
        if op == 'push':
            if any(x.startswith(('--force', '--mirror')) or x == '-f' or x.startswith('+') for x in rest):
                return 'Force pushes and mirror pushes are blocked.'
            if any(re.search(r'(^|:)(refs/heads/)?(main|master|develop|release/[^\s]*)$', x) for x in rest):
                return 'Push a feature branch and open a PR. Protected branch pushes are blocked.'
            # Require an explicit remote and feature ref. Implicit pushes depend on local git config.
            positional = [x for x in rest if not x.startswith('-')]
            if len(positional) != 2 or any(x in {'--all', '--branches', '--delete', '--prune'} for x in rest):
                return 'Push with an explicit remote and feature refspec so the destination can be checked.'
            if any(c in positional[-1] for c in '$`*;|&'):
                return 'Use a literal feature refspec so the destination can be checked.'
        if op == 'reset' and '--hard' in rest:
            return 'Destructive git reset is blocked.'
        if op == 'clean' and any(x == '--force' or (x.startswith('-') and 'f' in x[1:]) for x in rest):
            return 'Destructive git clean is blocked.'
        if op == 'checkout' and '--' in rest and '.' in rest:
            return 'Discarding the working tree is blocked.'
        if op == 'restore' and ('.' in rest or ':/' in rest):
            return 'Discarding the working tree is blocked.'
    # Only shell command arguments contain nested shell source.
    for i, token in enumerate(tokens):
        for substitution in re.finditer(r'\$\(([^()]*)\)|`([^`]*)`', token):
            reason = shell_reason(substitution.group(1) or substitution.group(2) or '')
            if reason:
                return reason
        if token.rsplit('/', 1)[-1] not in {'sh', 'bash', 'zsh', 'dash', 'ksh'}:
            continue
        for j in range(i + 1, len(tokens) - 1):
            option = tokens[j]
            if not option.startswith('-'):
                break
            if 'c' in option[1:] and not option.startswith('--'):
                reason = shell_reason(tokens[j + 1])
                if reason:
                    return reason
                break
    return None


def read_command(tokens):
    """The shell equivalents of Claude's Read/Grep/Glob tools."""
    if not tokens:
        return False
    if tokens[0] in {'cat', 'ls', 'pwd'}:
        return True
    if tokens[0] == 'rg':
        # These ripgrep flags execute an external command, unlike normal searches.
        return not any(arg == flag or arg.startswith(flag + '=')
                       for arg in tokens[1:] for flag in {'--pre', '--hostname-bin'})
    if tokens[0] == 'sed':
        args = tokens[1:]
        while args and args[0] in {'-n', '-E', '-e'}:
            args = args[1:]
        # Permit only printing an optional line range; never sed's write/execute commands.
        return bool(len(args) >= 2
                    and re.fullmatch(r'(?:\d+(?:,(?:\d+|\$))?|\$)?p', args[0])
                    and not any(arg.startswith('-') for arg in args[1:]))
    return False


def gradle_reason(args):
    reason = 'Verifier Gradle commands may contain compile, assemble and test tasks with reporting flags only.'
    task_count = 0
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in {'--tests', '--console'}:
            i += 1
            if i == len(args) or args[i].startswith('-'):
                return reason
            if arg == '--console' and args[i] not in {'plain', 'auto', 'rich', 'verbose'}:
                return reason
        elif arg in {'-q', '--offline', '--no-daemon', '--stacktrace', '--info', '--rerun-tasks'}:
            pass
        elif arg.startswith('--console=') and arg.partition('=')[2] in {'plain', 'auto', 'rich', 'verbose'}:
            pass
        elif re.fullmatch(r':?(?:[\w-]+:)*(test|connected|compile|assemble)[\w]*', arg):
            task_count += 1
        else:
            return reason
        i += 1
    return None if task_count else reason


def role_reason(role, command):
    if role not in {'android-researcher', 'android-verifier'}:
        return None
    if re.search(r'[;&|<>`\n]|\$\(', command):
        return 'Specialist agents use single commands without shell chaining, redirection or substitution.'
    try:
        tokens = shlex.split(command)
    except ValueError:
        return 'Specialist command could not be parsed.'
    if read_command(tokens):
        return None
    if role == 'android-verifier' and tokens and tokens[0] == './gradlew':
        return gradle_reason(tokens[1:])
    if role == 'android-researcher':
        allowed = r'android\s+(docs\s+(search|fetch)|sdk\s+list)(\s|$)'
    else:
        allowed = (r'(android\s+(layout|screen|emulator\s+list|info|docs)(\s|$)'
                   r'|adb(?:\s+-s\s+\S+)?\s+(devices|logcat|shell\s+(input|dumpsys|am\s+start|monkey|pm\s+list))(\s|$)'
                   r'|sleep\s+[\d.]+$)')
    if not re.match(allowed, command.strip()):
        return 'This specialist only runs its documented research or verification commands.'
    if role == 'android-verifier' and tokens and tokens[0] == 'adb':
        adb_args = tokens[3:] if tokens[1:2] == ['-s'] else tokens[1:]
        if adb_args[:1] == ['logcat'] and any(
                arg.startswith(('-f', '--file', '--output')) for arg in adb_args[1:]):
            return 'Verifier logcat output must go to the tool response, not a workspace file.'
    return None


def check(event, role=''):
    name = event.get('tool_name', '')
    args = event.get('tool_input', {})
    if not isinstance(args, dict):
        args = {'command': args} if isinstance(args, str) else {}
    command = args.get('command', args.get('cmd', ''))
    if isinstance(command, list):
        command = shlex.join(command)
    if name in {'Bash', 'shell', 'shell_command', 'exec_command'}:
        return shell_reason(command) or role_reason(role, command)
    if name in {'apply_patch', 'Edit', 'Write', 'NotebookEdit'}:
        if role:
            return 'Specialist agents do not edit source, tests or journeys.'
        paths = [args.get('file_path', ''), args.get('notebook_path', '')]
        patch = args.get('patch', command)
        paths += re.findall(r'^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$', patch, re.M)
        if any(protected(p) for p in paths if p):
            return 'Editing secrets, signing/network configuration or generated binaries is blocked.'
    return None


if __name__ == '__main__':
    try:
        reason = check(json.load(sys.stdin), sys.argv[1] if len(sys.argv) > 1 else '')
    except (ValueError, TypeError, AttributeError) as exc:
        reason = 'Guard could not validate the tool input: ' + type(exc).__name__
    if reason:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
              'permissionDecision': 'deny', 'permissionDecisionReason': reason}}))
