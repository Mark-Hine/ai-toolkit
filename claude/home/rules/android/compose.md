---
verified: 2026-09-29
sources:
  - https://developer.android.com/develop/ui/compose/performance/stability/strongskipping
  - https://developer.android.com/develop/ui/compose/performance/stability/fix
  - https://developer.android.com/guide/navigation/navigation-3
  - https://developer.android.com/guide/navigation/navigation-3/migration-guide
  - https://developer.android.com/develop/ui/compose/state-hoisting
  - https://developer.android.com/about/versions/16/behavior-changes-16
paths:
  - "**/compose/**/*.kt"
  - "**/*Screen.kt"
  - "**/*Composable*.kt"
  - "**/*Content.kt"
---

# Jetpack Compose (Android repos)

- Theme: screen roots wrapped in the project's theme (named in its `CLAUDE.md`). Colours/type come from its tokens, never hex
  or bare `MaterialTheme` defaults. Project components come before raw Material widgets, and no new `androidx.compose.material.*` (M2) imports.
- Split screen-level composables into a stateful `XScreen(viewModel)` that collects state and a stateless
  `XContent(uiState, onEvent)` that renders. Previews target the stateless one using the project's shared preview annotations.
  Skills: `compose-state-holder-ui-split`, `compose-state-hoisting`.
- State: `remember { mutableStateOf() }` only for UI-local state. Everything else is hoisted to the ViewModel
  `StateFlow` and collected with `collectAsStateWithLifecycle()`. Skill: `compose-state-authoring`.
- Side effects in `LaunchedEffect`/`DisposableEffect` with real keys, never `Unit` to hide a changing input. Skill: `compose-side-effects`.
- Stability: strong skipping is the default from Kotlin 2.0.20. Unstable parameters no longer stop a composable from skipping, and the compiler memoizes lambdas. Do not add `@Immutable`, `@Stable`, `kotlinx.collections.immutable` types or remembered lambdas by default. Fix stability only when compiler metrics or recomposition counts show a problem, and prefer making the class stable without an annotation. `@Stable` still helps when a source such as Room emits new but equal instances, because stable parameters compare with `equals` and unstable ones with `===`.
  Skills: `compose-stability-diagnostics`, `compose-recomposition-performance`.
- Modifiers: a single `modifier: Modifier = Modifier` parameter first among optional params, applied to the
  root element once. Skill: `compose-modifier-and-layout-style`.
- Callbacks: leaves and reusable components take individual lambdas. Above five callbacks on a screen/section composable,
  bundle them in an `XActions` data class of function types (`{}` defaults), built once in the ViewModel from method
  references, and pass single lambdas down from it. Never build it in composition, and never put state in it.
  Reference: `android-kit:standards` → `references/ui-events.md` §Actions holder.
- Parameters are values, not `State<T>`/`LiveData`. Derived booleans/predicates are computed into `UiState` in the ViewModel.
- Insets: content honours system bars via `WindowInsets`/`Scaffold` padding. Use the `edge-to-edge` skill when
  touching screen roots. Large screens: no orientation locks (ignored on sw600dp+ from target 36). Check layout on the tablet AVD (`adaptive` skill).
- Navigation (house policy): new Compose-only apps and new Compose navigation hosts use Navigation 3 (`navigation-3` skill). Existing Navigation 2 graphs stay on Navigation 2 with type-safe `@Serializable` routes. Moving a graph to Navigation 3 is its own ticket, because the migration guide needs one atomic change, compileSdk 36, composable destinations and typed routes. Apps with Fragment or Activity destinations stay on Navigation 2.
- Reference shape for a design system and theming: JetSnack (`android-kit:standards` skill, `references/jetsnack.md`).
- Follow `~/.claude/rules/design-standards.md` for design rules and their tiers. Screens design loading, loaded, empty and error, plus partial only where they show cached or offline data. Touch targets are at least 48 by 48 dp. Delegate UI diff reviews to `ui-reviewer`.
