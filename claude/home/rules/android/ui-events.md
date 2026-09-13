---
paths:
  - "**/*ViewModel.kt"
  - "**/*Screen.kt"
  - "**/*Event.kt"
  - "**/*Events.kt"
  - "**/*UiState.kt"
  - "**/*Effect.kt"
---

# One-shot ViewModel → UI events

Canonical code and rationale: `android-kit:standards` skill, `references/ui-events.md`.

- **Screen state** is one `StateFlow<UiState>` where `UiState` is a sealed interface (`Loading` / `Loaded(...)` / `Error(...)`,
  with `Error` itself sealed when there are distinct kinds). Update it synchronously with `MutableStateFlow.update {}`;
  never inside `launch` unless the update follows real async work.
- **Navigation events** (go to screen, open URL, finish): per-screen sealed `XNavigationEvent` through
  `Channel(BUFFERED)` exposed via `receiveAsFlow()`; handled in an extracted `onXNavigationEvent(host…, event)` function
  with an exhaustive `when`. The ViewModel never imports a navigation library; the host maps events to `startActivity`,
  `FragmentManager` or a navigator.
- **Snackbars/toasts are not events**: app-scoped, so the ViewModel calls an injected `SnackbarPresenter` and the root
  `Scaffold` collects it. No marker interface; scope decides.
- **Collect lifecycle-aware**: `LaunchedEffect(events, lifecycle) { lifecycle.repeatOnLifecycle(STARTED) { events.collect { … } } }`;
  handler via `rememberUpdatedState`. In Views, `repeatOnLifecycle(STARTED)` inside `lifecycleScope.launch`.
- **Never**: `MutableSharedFlow(replay = 0)` for events; sticky `LiveData`/`StateFlow` sentinels as triggers;
  `LaunchedEffect(Unit)` capturing a navigator/context; `delayInMillis` parameters on base-class helpers;
  `context as? Activity` (use `LocalActivity.current` or a host `onFinish`).

Skills: `kotlin-flow-state-event-modeling`, `compose-side-effects`.
