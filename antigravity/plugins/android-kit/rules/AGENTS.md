# Android and Kotlin Rules

These rules apply when working with Android and Kotlin code in this repository.

## Subagents and Specialist Delegation

- Delegate current platform research to `android-researcher` (`model: flash`, read-only).
- Delegate non-trivial diff review to `android-reviewer` (`model: pro`, read-only).
- Delegate test execution and emulator verification to `android-verifier` (`model: flash`, workspace writes enabled).
- When specialists are not yet defined, configure them with `define_subagent` using the specifications in `agents/` and invoke them with `invoke_subagent`.

## Kotlin Style

- Formatting follows the repo's `.editorconfig` (4-space indent for `.kt`/`.kts`, LF, no star imports, final newline). Match surrounding code by hand if the formatter is unavailable.
- Use `when` as an expression over sealed types and keep it exhaustive; no `else` branch that hides a missing case. Prefer guard conditions and early returns to nested `if`.
- Structured concurrency: no stored `CoroutineScope` in classes other than ViewModels (`viewModelScope`) and lifecycle owners (`lifecycleScope`); no `GlobalScope`; no `runBlocking` outside tests; inject dispatchers rather than hardcoding `Dispatchers.IO`.
- State to the UI is `StateFlow` updated with `update {}`; one-shot events go through `Channel(BUFFERED).receiveAsFlow()` collected lifecycle-aware. Do not introduce new `LiveData`.
- Wrap primitive identifiers and amounts in `@JvmInline value class` where a `data class` would hold one field.
- Nullability: no `!!` in production code; use `requireNotNull`/`checkNotNull` with an explanatory message or handle the null gracefully.
- Match existing file style when editing legacy files; avoid reformatting unrelated lines.

## Jetpack Compose

- Theme: screen roots wrapped in the project's theme (named in project `AGENTS.md`); colours/type from design tokens, never raw hex or bare `MaterialTheme` defaults; project components before raw Material widgets; no new `androidx.compose.material.*` (M2) imports.
- Split screen-level composables into a stateful `XScreen(viewModel)` that collects state and a stateless `XContent(uiState, onEvent)` that renders. Previews target the stateless component using shared preview annotations.
- State: `remember { mutableStateOf() }` only for UI-local state; hoist everything else to ViewModel `StateFlow` collected with `collectAsStateWithLifecycle()`.
- Side effects in `LaunchedEffect`/`DisposableEffect` with real keys, never `Unit` to mask changing inputs.
- Stability: `@Immutable`/`@Stable` on UI state classes; avoid raw `List` parameters where a `kotlinx.collections.immutable` type or a wrapper fits; remember lambdas passed to list items.
- Modifiers: a single `modifier: Modifier = Modifier` parameter first among optional params, applied to the root element once.
- Callbacks: leaf composables take individual lambdas. Above five callbacks on a screen/section composable, bundle them in an `XActions` data class of function types (`{}` defaults) built once in the ViewModel, and pass single lambdas down. Never build `XActions` inside composition; never put state in it.
- Parameters are values, not `State<T>`/`LiveData`; compute derived booleans in `UiState` within the ViewModel.
- Insets: content honours system bars via `WindowInsets`/`Scaffold` padding.
- Large screens: no orientation locks (ignored on sw600dp+ from target 36); verify layout on tablet emulator.

## One-Shot ViewModel to UI Events

- **Screen state** is one `StateFlow<UiState>` where `UiState` is a sealed interface (`Loading` / `Loaded(...)` / `Error(...)`). Update it synchronously with `MutableStateFlow.update {}`; never inside `launch` unless following real asynchronous work.
- **Navigation events**: per-screen sealed `XNavigationEvent` through `Channel(BUFFERED)` exposed via `receiveAsFlow()`; handled in an extracted `onXNavigationEvent(host…, event)` function with an exhaustive `when`. ViewModels never import navigation libraries; host maps events to navigators.
- **Snackbars and toasts are app-scoped**: the ViewModel calls an injected `SnackbarPresenter` and the root `Scaffold` collects it.
- **Collect lifecycle-aware**: `LaunchedEffect(events, lifecycle) { lifecycle.repeatOnLifecycle(STARTED) { events.collect { … } } }` with handlers wrapped in `rememberUpdatedState`.
- **Never**: `MutableSharedFlow(replay = 0)` for events; sticky `StateFlow` sentinels as triggers; `LaunchedEffect(Unit)` capturing navigators; `context as? Activity` (use `LocalActivity.current`).

## Tests and Verification

- Unit test ViewModel, use case, and repository changes in the same module. New or changed screens require Compose UI-behaviour tests or previews plus an emulator journey.
- Bug fixes require a failing test first, then the fix, then verified green. Quote both runs.
- Test stack: JUnit 5, Kotest assertions, MockK, `kotlinx-coroutines-test` (`runTest`, injected `TestDispatcher`). Fakes over mocks for repositories and data sources; MockK only at true boundaries. No `Thread.sleep` or `runBlocking`.
- Never `@Ignore`, delete, or loosen an assertion to pass. Report pre-existing failures listed in project `AGENTS.md`.
- Run targeted tests first (`./gradlew :<module>:test<Variant>UnitTest --tests '<FQCN>'`).
- End-to-end journeys live under `journeys/<feature>.xml`. Hand verification off to `android-verifier`.
