# Now in Android as a blueprint

Repo: https://github.com/android/nowinandroid
Read first: `docs/ArchitectureLearningJourney.md`, `docs/ModularizationLearningJourney.md`.
Pragmatism guardrails: https://github.com/android/nowinandroid/discussions/1273

## What to borrow for Android repos
- **Unidirectional data flow**: `Repository` exposes `Flow`; ViewModel maps to a single `UiState` sealed interface
  (`Loading`/`Success`/`Error`) via `stateIn(viewModelScope, WhileSubscribed(5_000), Loading)`; UI collects with
  `collectAsStateWithLifecycle`. Map this onto the data module → app ViewModels.
- **Convention plugins** in `build-logic/convention` with one plugin per concern (`AndroidApplicationConventionPlugin`,
  `AndroidLibraryConventionPlugin`, compose, hilt). Add plugins rather than inlining config per module.
- **Version catalog as the only source of versions**, including plugins.
- **Testing**: fakes over mocks for repositories (NIA `core/testing`), `runTest` + `TestDispatcher`, Turbine-style
  flow assertions only if the dependency is added deliberately.
- **Offline-first**: local source of truth (Room/DataStore) with sync; relevant only if a feature needs caching.
- **Feature modules** (`feature:x` depends on `core:*`, never on another feature). Aspirational for many app repos, which are
  a few modules plus a toolkit. Do not propose a module split inside a feature ticket.

## What not to copy
- Interfaces on every use case, a mandatory domain layer, per-layer Hilt modules: discussion #1273 says these are
  optional. Recommend them only when a concrete reuse or test need exists.
- NIA's `core:designsystem` theming is Material3-only; many legacy apps carry a Material2 surface. See `jetsnack.md`.
- Baseline profiles, Compose compiler metrics and benchmark modules: valuable, but each is a task, not a side effect.
