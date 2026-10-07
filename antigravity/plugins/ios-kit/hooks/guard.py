#!/usr/bin/env python3
"""PreToolUse guard shared by the Claude Code, Codex and Antigravity layers of ai-toolkit.

Canonical source: shared/hooks/guard.py. The copies inside the plugins and under codex/hooks are
kept byte-identical by scripts/ci/check_parity.py. Advisory command parsing is not a shell sandbox.

Usage: guard.py [--agent claude|codex|antigravity] [role]
  stdin   the hook event as JSON
  role    a toolkit agent name; when absent it is read from the event's agent_type or role
  stdout  the host's decision object, or nothing when there is no objection
The guard never exits non-zero on a valid run. Any crash is reported as a deny, so a guard that
cannot run still blocks the call.
"""
import argparse
import json
from pathlib import PurePosixPath
import re
import shlex
import sys

TOOLKIT_ROLES = {'android-researcher', 'android-reviewer', 'android-verifier',
                 'ios-researcher', 'ios-reviewer', 'ios-verifier',
                 'web-researcher', 'web-reviewer', 'web-verifier', 'ui-reviewer'}
SHELL_LIMITED_ROLES = {'android-researcher', 'android-verifier', 'ios-researcher', 'ios-verifier',
                       'web-researcher', 'web-verifier'}
# Commands that set up a checkout. The calling session runs them, so a verifier gets a path instead.
SETUP_COMMANDS = {'git', 'pod', 'swift', 'carthage', 'bundle', 'npm', 'pnpm', 'yarn', 'bun'}
SETUP_REASON = ('Verifier agents do not run git or dependency installers. '
                'Ask the calling session to prepare the checkout and pass its path.')
SHELL_TOOLS = {'Bash', 'shell', 'shell_command', 'exec_command', 'run_command'}
EDIT_TOOLS = {'apply_patch', 'Edit', 'Write', 'NotebookEdit',
              'write_to_file', 'replace_file_content', 'multi_replace_file_content'}
SHELLS = {'sh', 'bash', 'zsh', 'dash', 'ksh'}
# Wrappers that run another command. The value is the set of options that take an argument.
WRAPPERS = {'sudo': {'-u', '-g', '-h', '-p', '-C', '-T', '--user', '--group', '--host', '--prompt', '--chdir', '--unset'},
            'env': {'-u', '-C', '-S', '--unset', '--chdir', '--split-string'},
            'command': set(), 'exec': {'-a'}, 'nohup': set(), 'time': set(),
            'xargs': {'-n', '-I', '-P', '-L', '-s', '-E', '-d', '-a'},
            'nice': {'-n'}, 'caffeinate': {'-t', '-w'}}


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
    wrapper_options = set()
    for token in tokens:
        if re.fullmatch(r'[;&|()\n]+', token):
            command_start = True
            redirect_target = False
            wrapper_option = False
            wrapper_options = set()
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
        if executable in WRAPPERS:
            wrapper_options = WRAPPERS[executable]
            continue
        if token.startswith('-'):
            wrapper_option = token in wrapper_options
            continue
        command_start = False
    return False


ENV_TEMPLATES = {'.env.example', '.env.sample', '.env.template', '.env.dist'}


def protected(path):
    """Secrets, signing material, generated binaries and lock files. Never edited by an agent."""
    p = PurePosixPath(path)
    return (p.name in {'google-services.json', 'GoogleService-Info.plist', 'secrets.properties',
                       'keystore.properties', 'local.properties', 'network_security_config.xml',
                       '.env', '.envrc', 'ExportOptions.plist', 'Podfile.lock', 'Package.resolved'}
            or (p.name.startswith('.env.') and p.name not in ENV_TEMPLATES)
            or p.suffix in {'.jks', '.keystore', '.p12', '.p8', '.pem', '.key', '.mobileprovision', '.cer', '.entitlements'}
            or '.git' in p.parts
            or re.search(r'[Ss]ecrets(?:\.swift|\.plist|[^/]*\.xcconfig)$', p.name) is not None
            or (p.suffix in {'.aar', '.jar'} and '/app/libs/' in '/' + str(p))
            or str(p).endswith('gradle/wrapper/gradle-wrapper.jar'))


def needs_approval(path):
    """CI definitions. Editing one is legitimate but changes what runs with credentials, so a person confirms it."""
    p = PurePosixPath(path)
    return ('.github' in p.parts and 'workflows' in p.parts) or re.fullmatch(r'azure-pipelines.*\.ya?ml', p.name) is not None


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
                # The lexer splits 2>&1 into 2, >& and 1, so a digit just before a redirect is a file descriptor.
                if re.search(r'[<>]', arg) and args and args[-1].isdigit():
                    args.pop()
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
            if any(x.startswith(('--force', '--mirror', '+')) or re.fullmatch(r'-[A-Za-z]*f[A-Za-z]*', x) for x in rest):
                return 'Force pushes and mirror pushes are blocked.'
            if any(re.search(r'(^|:)(refs/heads/)?(main|master|develop|release/[^\s]*)$', x) for x in rest):
                return 'Push a feature branch and open a PR. Protected branch pushes are blocked.'
            if any(x in {'--all', '--branches', '--tags', '--delete', '-d', '--prune'} for x in rest):
                return 'Branch deletion and bulk pushes are blocked. Delete or prune branches from the host UI.'
            # Require an explicit remote and feature ref. Implicit pushes depend on local git config.
            positional = [x for x in rest if not x.startswith('-')]
            if len(positional) != 2:
                return 'Push with an explicit remote and feature refspec so the destination can be checked.'
            refspec = positional[-1]
            if any(c in refspec for c in '$`*;|&'):
                return 'Use a literal feature refspec so the destination can be checked.'
            if refspec.startswith(':'):
                return 'Branch deletion pushes are blocked. Delete branches from the host UI.'
            destination = refspec.rsplit(':', 1)[-1]
            if destination in {'HEAD', '@'}:
                return 'Name the destination branch explicitly instead of HEAD so the guard can check it.'
        if op == 'reset' and '--hard' in rest:
            return 'Destructive git reset is blocked.'
        if op == 'clean' and any(x == '--force' or (x.startswith('-') and 'f' in x[1:]) for x in rest):
            return 'Destructive git clean is blocked.'
        if op == 'checkout' and ('.' in rest or ':/' in rest):
            return 'Discarding the working tree is blocked.'
        if op == 'restore' and ('.' in rest or ':/' in rest):
            staged_only = ('--staged' in rest or '-S' in rest) and not ('--worktree' in rest or '-W' in rest)
            if not staged_only:
                return 'Discarding the working tree is blocked.'
    # Only shell command arguments contain nested shell source.
    for i, token in enumerate(tokens):
        for substitution in re.finditer(r'\$\(([^()]*)\)|`([^`]*)`', token):
            reason = shell_reason(substitution.group(1) or substitution.group(2) or '')
            if reason:
                return reason
        executable = token.rsplit('/', 1)[-1]
        if executable == 'eval':
            nested = []
            for arg in tokens[i + 1:]:
                if re.fullmatch(r'[;&|()<>\n]+', arg):
                    break
                nested.append(arg)
            reason = shell_reason(' '.join(nested))
            if reason:
                return reason
            continue
        if executable not in SHELLS:
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


def xcodebuild_allowed(args, research=False):
    """Allow documented query/test options, excluding unrelated build actions."""
    value_flags = {'-workspace', '-project', '-scheme', '-configuration', '-sdk', '-destination'}
    toggles = {'-quiet', '-json'}
    operations = {'-version', '-showsdks', '-list', '-showBuildSettings', '-showdestinations'} if research else {
        'test', 'test-without-building'}
    if not research:
        value_flags |= {'-derivedDataPath', '-resultBundlePath', '-testPlan', '-parallel-testing-enabled',
                        '-maximum-concurrent-test-simulator-destinations'}
    found = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in operations:
            found.append(arg)
        elif arg in value_flags:
            i += 1
            if i == len(args) or args[i].startswith('-'):
                return False
            if arg == '-resultBundlePath' and not args[i].endswith('.xcresult'):
                return False
        elif arg in toggles:
            pass
        elif not research and (re.fullmatch(r'-(?:only|skip)-testing:.+', arg)
                               or arg == 'CODE_SIGNING_ALLOWED=NO'):
            pass
        else:
            return False
        i += 1
    return len(found) == 1


def ios_command_allowed(tokens, research=False):
    if not tokens:
        return False
    executable, args = tokens[0].rsplit('/', 1)[-1], tokens[1:]
    if executable == 'xcodebuild':
        return xcodebuild_allowed(args, research)
    if research:
        if executable == 'swift':
            return args == ['--version'] or args in [
                ['package', query] for query in ('describe', 'show-dependencies', 'dump-package')]
        if executable == 'pod':
            return args in [['--version'], ['outdated']]
    if executable == 'sleep' and not research:
        return len(args) == 1 and re.fullmatch(r'\d+(?:\.\d+)?', args[0]) is not None
    if executable != 'xcrun' or not args:
        return False
    if research and args in [[flag] for flag in ('--show-sdk-version', '--show-sdk-path', '--show-sdk-platform-version')]:
        return True
    if args[0] == 'xcodebuild':
        return xcodebuild_allowed(args[1:], research)
    if not research and args[:3] == ['xcresulttool', 'get', 'test-results']:
        return (len(args) == 6 and args[3] in {'summary', 'tests', 'activities', 'metrics'}
                and args[4] == '--path' and args[5].endswith('.xcresult'))
    if args[0] != 'simctl' or len(args) < 2:
        return False
    operation, rest = args[1], args[2:]
    if operation == 'list':
        return all(arg in {'devices', 'runtimes', 'devicetypes', 'pairs', 'available', '-j', '--json'} for arg in rest)
    if research:
        return False
    if operation in {'launch', 'openurl'}:
        return len(rest) == 2
    if operation == 'listapps':
        return len(rest) == 1
    if operation == 'bootstatus':
        return len(rest) == 1 or (len(rest) == 2 and rest[1] == '-b')
    if operation == 'get_app_container':
        return len(rest) in {2, 3}
    if operation == 'io':
        return len(rest) == 3 and rest[1] == 'screenshot' and rest[2].endswith('.png')
    if operation == 'ui':
        return len(rest) in {2, 3} and rest[1] in {'appearance', 'content_size'}
    if operation == 'spawn' and rest[1:3] == ['log', 'show']:
        flags = rest[3:]
        return (len(rest) >= 3 and len(flags) % 2 == 0
                and all(flag in {'--last', '--predicate', '--style'} for flag in flags[::2]))
    return False


PACKAGE_MANAGERS = {'npm', 'pnpm', 'yarn', 'bun'}
# Script names a verifier may run. The repo's CLAUDE.md or AGENTS.md names which of them exist.
WEB_SCRIPT = re.compile(r'(test|lint|typecheck|type-check|check-types)(:[\w-]+)*')
# Flags that rewrite files: lint autofix and snapshot updates.
WEB_WRITE_FLAGS = {'--fix', '-u', '--update', '--updateSnapshot', '--update-snapshots', '--write'}


def web_tool_allowed(tool, args):
    """A test, lint, type-check or capture tool run directly, without flags that write to the workspace."""
    if any(arg in WEB_WRITE_FLAGS or arg.startswith(('--fix=', '--update-snapshots=')) for arg in args):
        return False
    if tool in {'vitest', 'jest', 'eslint'}:
        return True
    if tool == 'tsc':
        return '--noEmit' in args
    if tool == 'playwright':
        # A screenshot writes only the PNG it names.
        return bool(args) and (args[0] in {'test', '--version'}
                               or (args[0] == 'screenshot' and args[-1].endswith('.png')))
    return False


def web_command_allowed(tokens, research=False):
    if not tokens:
        return False
    executable, args = tokens[0].rsplit('/', 1)[-1], tokens[1:]
    if executable == 'node':
        return args == ['--version']
    if executable == 'sleep':
        return not research and len(args) == 1 and re.fullmatch(r'\d+(?:\.\d+)?', args[0]) is not None
    if executable not in PACKAGE_MANAGERS | {'npx'} or not args:
        return False
    if executable == 'npx' or (args[0] == 'exec' and executable != 'bun'):
        rest = args if executable == 'npx' else args[1:]
        rest = [arg for arg in rest if arg not in {'--', '--no-install', '--offline'}]
        return not research and bool(rest) and web_tool_allowed(rest[0], rest[1:])
    if research:
        return args[0] in {'view', 'info', 'outdated', 'ls', 'list', 'why', '--version'}
    if any(arg in WEB_WRITE_FLAGS for arg in args):
        return False
    if args[0] == 'test' or (args[0] == 'run' and len(args) > 1 and WEB_SCRIPT.fullmatch(args[1])):
        return True
    # pnpm, yarn and bun run a package script by name without `run`. `bun test` is bun's own runner.
    return executable != 'npm' and WEB_SCRIPT.fullmatch(args[0]) is not None


def role_reason(role, command):
    if role not in SHELL_LIMITED_ROLES:
        return None
    if re.search(r'[;&|<>`\n]|\$\(', command):
        return 'Specialist agents use single commands without shell chaining, redirection or substitution.'
    try:
        tokens = shlex.split(command)
    except ValueError:
        return 'Specialist command could not be parsed.'
    if read_command(tokens):
        return None
    # The web verifier runs package-manager scripts, so its allowlist is checked before the setup message.
    setup = role.endswith('-verifier') and bool(tokens) and tokens[0].rsplit('/', 1)[-1] in SETUP_COMMANDS
    if role.startswith('web-'):
        if web_command_allowed(tokens, role == 'web-researcher'):
            return None
        return SETUP_REASON if setup else (
            'This web specialist only runs its documented package queries or test, lint, type-check and capture commands.')
    if setup:
        return SETUP_REASON
    if role.startswith('ios-'):
        return None if ios_command_allowed(tokens, role == 'ios-researcher') else (
            'This iOS specialist only runs its documented read-only queries or test/simulator evidence commands.')
    if role == 'android-verifier' and tokens and tokens[0] == './gradlew':
        return gradle_reason(tokens[1:])
    if role == 'android-researcher':
        allowed = r'android\s+(docs\s+(search|fetch)|sdk\s+list)(\s|$)'
    else:
        allowed = (r'(android\s+(layout|screen|emulator\s+list|info|docs)(\s|$)'
                   r'|adb(?:\s+-s\s+\S+)?\s+(devices|logcat|shell\s+(input|dumpsys|am\s+start|monkey|pm\s+list))(\s|$)'
                   # Configuration captures read, set and restore only these two display settings.
                   r'|adb(?:\s+-s\s+\S+)?\s+shell\s+settings\s+(get\s+system\s+font_scale|put\s+system\s+font_scale\s+\d+(\.\d+)?)$'
                   r'|adb(?:\s+-s\s+\S+)?\s+shell\s+cmd\s+uimode\s+night(\s+(yes|no))?$'
                   r'|sleep\s+[\d.]+$)')
    if not re.match(allowed, command.strip()):
        return 'This specialist only runs its documented research or verification commands.'
    if role == 'android-verifier' and tokens and tokens[0] == 'adb':
        adb_args = tokens[3:] if tokens[1:2] == ['-s'] else tokens[1:]
        if adb_args[:1] == ['logcat'] and any(
                arg.startswith(('-f', '--file', '--output')) for arg in adb_args[1:]):
            return 'Verifier logcat output must go to the tool response, not a workspace file.'
    return None


def tool_call(event):
    """Normalise the three hosts' event shapes to (tool name, argument dict)."""
    call = event.get('toolCall') if isinstance(event, dict) else None
    if isinstance(call, dict):  # Antigravity
        name, args = call.get('name', ''), call.get('args', {})
    else:  # Claude Code and Codex
        name, args = event.get('tool_name', ''), event.get('tool_input', {})
    if not isinstance(args, dict):
        args = {'command': args} if isinstance(args, str) else {}
    return name, args


def resolve_role(event, explicit=''):
    """A toolkit agent name from argv, else from the event. Anything else means no role."""
    candidates = [explicit]
    if isinstance(event, dict):
        candidates += [event.get('agent_type', ''), event.get('role', '')]
    for candidate in candidates:
        if not isinstance(candidate, str) or not candidate:
            continue
        name = candidate.rsplit(':', 1)[-1]  # plugin-scoped names such as android-kit:android-researcher
        if name in TOOLKIT_ROLES:
            return name
    return ''


def evaluate(event, role=''):
    """Return ('deny' | 'ask', reason) or None when there is no objection."""
    name, args = tool_call(event)
    command = args.get('CommandLine', args.get('command', args.get('cmd', '')))
    if isinstance(command, list):
        command = shlex.join(command)
    if name in SHELL_TOOLS:
        reason = shell_reason(command) or role_reason(role, command)
        return ('deny', reason) if reason else None
    if name in EDIT_TOOLS:
        if role:
            return ('deny', 'Specialist agents do not edit source, tests or journeys.')
        paths = [args.get('TargetFile', ''), args.get('file_path', ''), args.get('notebook_path', '')]
        patch = args.get('patch', args.get('CodeContent', args.get('ReplacementContent', command)))
        if isinstance(patch, str):
            paths += re.findall(r'^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$', patch, re.M)
        paths = [p for p in paths if isinstance(p, str) and p]
        if any(protected(p) for p in paths):
            return ('deny', 'Editing secrets, signing/network configuration or generated binaries is blocked.')
        if any(needs_approval(p) for p in paths):
            return ('ask', 'This edits a CI definition. Confirm it before it runs with pipeline credentials.')
    return None


def check(event, role=''):
    """The reason an event is not plainly allowed, or None. Kept for tests and callers that only need a yes or no."""
    verdict = evaluate(event, role)
    return verdict[1] if verdict else None


def render(agent, verdict):
    """The host-specific stdout for a verdict. An empty string means no objection."""
    if agent == 'antigravity':
        # `decision` is required. `ask` keeps the normal permission prompt and its Always Allow cache.
        # An empty object is treated as a denial, and `allow` would skip the prompt entirely.
        if verdict is None:
            return json.dumps({'decision': 'ask'})
        return json.dumps({'decision': verdict[0] if verdict[0] in ('deny', 'ask') else 'deny', 'reason': verdict[1]})
    if verdict is None:
        return ''
    decision, reason = verdict
    if decision == 'ask' and agent == 'codex':
        decision = 'deny'  # Codex hooks cannot prompt
    return json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                       'permissionDecision': decision, 'permissionDecisionReason': reason}})


def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--agent', choices=['claude', 'codex', 'antigravity'], default='codex')
    parser.add_argument('role', nargs='?', default='')
    try:
        opts = parser.parse_args(argv)
    except SystemExit:
        opts = argparse.Namespace(agent='codex', role='')
    try:
        raw = (stdin or sys.stdin).read()
        event = json.loads(raw) if raw.strip() else {}
        verdict = evaluate(event, resolve_role(event, opts.role))
    except BaseException as exc:  # noqa: BLE001 - a guard that cannot run must block, not fail open
        verdict = ('deny', 'Guard could not validate the tool input: ' + type(exc).__name__)
    output = render(opts.agent, verdict)
    if output:
        print(output)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
