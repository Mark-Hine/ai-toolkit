---
paths:
  - "app/src/main/java/**/compose/**"
  - "**/*Screen.kt"
  - "**/*Composable*.kt"
  - "**/*Content.kt"
---

# Jetpack Compose (Android repos)

- Theme: screen roots wrapped in the project's theme (named in its `AGENTS.md`); colours/type from its tokens, never hex
  or bare `MaterialTheme` defaults; project components before raw Material widgets; no new `androidx.compose.material.*` (M2) imports.
- Split screen-level composables into a stateful `XScreen(viewModel)` that collects state and a stateless
  `XContent(uiState, onEvent)` that renders. Previews target the stateless one using the project's shared preview annotations.
  Skills: `compose-state-holder-ui-split`, `compose-state-hoisting`.
- State: `remember { mutableStateOf() }` only for UI-local state; everything else hoisted to the ViewModel
  `StateFlow` and collected with `collectAsStateWithLifecycle()`. Skill: `compose-state-authoring`.
- Side effects in `LaunchedEffect`/`DisposableEffect` with real keys, never `Unit` to hide a changing input. Skill: `compose-side-effects`.
- Stability: `@Immutable`/`@Stable` on UI state classes; no `List` parameters where a
  `kotlinx.collections.immutable` type or a wrapper fits; lambdas passed to lists are remembered.
  Skills: `compose-stability-diagnostics`, `compose-recomposition-performance`.
- Modifiers: a single `modifier: Modifier = Modifier` parameter first among optional params, applied to the
  root element once. Skill: `compose-modifier-and-layout-style`.
- Callbacks: leaves and reusable components take individual lambdas. Above five callbacks on a screen/section composable,
  bundle them in an `XActions` data class of function types (`{}` defaults), built once in the ViewModel from method
  references, and pass single lambdas down from it. Never build it in composition; never put state in it.
  Reference: `android-standards` → `references/ui-events.md` §Actions holder.
- Parameters are values, not `State<T>`/`LiveData`; derived booleans/predicates are computed into `UiState` in the ViewModel.
- Insets: content honours system bars via `WindowInsets`/`Scaffold` padding; use the `edge-to-edge` skill when
  touching screen roots. Large screens: no orientation locks (ignored on sw600dp+ from target 36); check layout on the tablet AVD (`adaptive` skill).
- Reference shape for a design system and theming: JetSnack (`android-standards` skill, `references/jetsnack.md`).
