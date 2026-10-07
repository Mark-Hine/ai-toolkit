---
verified: 2026-10-07
sources: inline
---

# Companions

Maintained skills that android-kit names at a specific playbook step. android-kit never installs them. When one is missing, tell the user once how to install it, continue with the bundled standards references, and mark the check it would have made Unverified. The project instructions and the installed house rules win over any companion.

## Official Android skills

Google publishes these through the Android CLI. Install one with `android skills add <id>`, or all with `android skills add --all`. `android skills list` shows what is installed.

| Skill | Named in | What it adds |
| --- | --- | --- |
| `android-cli` | run-app, android-verifier | Commands for devices, emulators, screenshots, layout dumps and the SDK |
| `edge-to-edge` | feature step 7 | Insets for system bars, the IME and display cutouts |
| `adaptive` | feature step 7 | Layouts for window size classes, foldables and large screens |
| `agp-9-upgrade` | uplift-deps step 3 | The AGP 9 migration procedure |
| `navigation-3` | standards | Navigation 3 setup and patterns |
| `migrate-xml-views-to-jetpack-compose` | standards | The XML to Compose migration procedure |

## Chris Banes skills

`using-chrisbanes-skills` routes Kotlin and Compose work to focused skills on state, side effects, layout, stability, Flow and coroutines. feature step 3 names it. Source: https://github.com/chrisbanes/skills

| Agent | Install |
| --- | --- |
| Claude Code | `/plugin marketplace add chrisbanes/skills`, then `/plugin install chrisbanes-skills@chrisbanes-skills` |
| Codex | `codex plugin marketplace add chrisbanes/skills --ref main`, then `codex plugin add chrisbanes-skills@chrisbanes-skills` |
| Other agents | `npx skills add chrisbanes/skills` |
