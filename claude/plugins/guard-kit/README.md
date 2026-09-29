# guard-kit

One PreToolUse hook, shared with the Codex and Antigravity layers of this repo, that runs before every `Bash`, `Edit`, `Write` and `NotebookEdit` call. `android-kit` and `ios-kit` depend on it, so installing either installs this plugin.

## What it blocks

| Area | Blocked |
| --- | --- |
| Pushes | Any push to `main`, `master`, `develop` or `release/*`, in any refspec form. Force, mirror and `+ref` pushes. Bare `git push`, remote-only pushes, `HEAD` or `@` as the destination, branch deletion (`--delete`, `-d`, `:branch`), `--all`, `--tags` with a refspec, `--prune`. A push needs exactly one remote and one literal feature refspec |
| Working tree | `git reset --hard`, `git clean -f*`, `git checkout .`, `git restore .` (staged-only restores are allowed) |
| `timeout` | The `timeout` wrapper in command position, including behind `sudo`, `env`, `time`, `xargs`, `nice`, `caffeinate`, `eval`, `sh -c` and command substitution. macOS has no `timeout` binary |
| Files | Secrets (`.env`, `.envrc`, `.env.*` except `.env.example` and friends, `secrets.properties`, `keystore.properties`, `local.properties`, `*Secrets*.swift|plist|xcconfig`), signing material (`.jks`, `.keystore`, `.p12`, `.p8`, `.pem`, `.key`, `.mobileprovision`, `.cer`, `.entitlements`, `ExportOptions.plist`), Firebase and network-security config, `app/libs/*.aar|jar`, `gradle-wrapper.jar`, `Podfile.lock`, `Package.resolved`, anything under `.git/` |
| CI definitions | `.github/workflows/*` and `azure-pipelines*.yml` prompt for confirmation instead of blocking, because they run with pipeline credentials |
| Agents | When the hook fires inside `android-researcher`, `android-verifier`, `ios-researcher` or `ios-verifier` (read from `agent_type` in the hook input), the command must be one of that agent's documented read-only or evidence commands, and edits are refused |

Nested shells (`sh -c`, `eval`, `$(...)`, backticks), `git -C` and quoted refs are parsed. Literal heredoc bodies are ignored. It is not a sandbox and does not parse scripts, aliases or computed commands.

## Failure mode

If `python3` is missing or the guard crashes, the call is blocked with a message, never allowed. A block is final. Do not work around it.

## Source and tests

The canonical module is `shared/hooks/guard.py`. This copy is kept identical by `scripts/ci/check_parity.py`. Unit tests are in `shared/tests/test_guard.py`, and `claude/tests/test-guards.sh` runs the real `hooks.json` command.
