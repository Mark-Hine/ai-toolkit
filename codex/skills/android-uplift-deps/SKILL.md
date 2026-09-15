---
name: android-uplift-deps
description: "Toolchain/dependency uplift playbook for Android apps: one axis per commit, release-note research, dependency diffs, review."
---

Read the project AGENTS.md and applicable global guidance first. If AGENTS.md is absent, read CLAUDE.md as migration fallback. Discover optional skills before invoking them. If `using-chrisbanes-skills`, `android-cli`, or an official Android skill is unavailable, use the bundled android-standards references and current official documentation. Do not invent commands or claim that an absent skill ran. Use installed Android SDK tools when the optional Android CLI is missing. Commit and push only when the user has requested that action.


# Dependency uplift: the user request

Repo facts (modules, compile/assemble commands, catalog vs Groovy scripts, deliberate opt-outs) come from the project's
`AGENTS.md` and its `gradle-deps` rule if present. Write the step 4 plan before editing dependency versions. Existing authorization to perform the uplift is sufficient.

1. **Baseline.** Clean `git status` on `feature/<ticket>-<slug>`. Run the project's compile checks and
   `./gradlew :app:dependencies --configuration <debugVariant>RuntimeClasspath > <scratchpad>/deps-before.txt`. Quote results.
2. **Inventory.** List the in-scope entries with current versions (version catalog, or `build.gradle` files in Groovy repos).
   Note any `gradle.properties` opt-outs and convention plugins the uplift touches.
3. **Research.** Ask `android-researcher` for the latest stable of each item, its release notes, and compatibility
   (AGP↔Gradle↔JDK, Kotlin↔KSP↔Compose compiler). For AGP majors also load `agp-9-upgrade`.
4. **Plan.** One commit per axis, ordered Gradle → AGP → Kotlin/KSP → Compose BOM/AndroidX → third-party. Name the variants
   you will build and the tests you will run. Proceed within the user-authorized scope. Ask only about unresolved scope or consequential choices.
5. **Apply each axis.** Edit versions only where the project declares them. Rebuild all compile checks; for
   AGP/Kotlin/Gradle also one release assemble (R8 path) and one debug assemble. Run the unit tests that passed at baseline.
   Diff `deps-after.txt` against `deps-before.txt`; list transitive changes.
6. **Runtime check** when native or vendored code is involved: `$android-run-app` on the 16 KB AVD, then the
   `android-verifier` agent runs the baseline tests and a smoke journey and returns the evidence.
7. **Review.** `android-reviewer`. Fix Blockers/Majors.
8. **Commit, only if asked** per axis: `chore(<ticket>): bump <thing> <old> -> <new>`; body: up to 3 lines naming release-note items that
   affect this app. Do not push unless asked.
9. **Report** table: item, old, new, build result, test result, notable transitive changes, follow-ups.
