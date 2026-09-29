---
verified: 2026-09-29
sources: house
---

# JetSnack as a design-system blueprint

Repo: https://github.com/android/compose-samples/tree/main/Jetsnack
Companion doc: https://developer.android.com/develop/ui/compose/designsystems/custom

House standard. JetSnack is the design-system blueprint this toolkit endorses. Reviewers grade drift from the shape below as a finding.

## Shape to mirror in the project's theme package
- `JetsnackTheme` = `CompositionLocalProvider(LocalJetsnackColors provides colors) { MaterialTheme(...) }`. Colours
  are an `@Immutable` class with `mutableStateOf` fields updated via `update()`, exposed through
  `JetsnackTheme.colors`. The project theme should follow this. Keep new tokens there, not in composables.
- Components live in one package, take `modifier: Modifier = Modifier`, expose slot content (`content: @Composable () -> Unit`)
  rather than many boolean flags (`compose-slot-api-pattern` skill).
- Gradient buttons and surfaces are built once (`JetsnackButton`, `JetsnackSurface`) and reused. Screens never call
  `Button` from Material directly. Same rule for the project's components.
- Previews: a shared preview annotation set (project preview annotations) covering light/dark and font scale.

## Cautions
- JetSnack is Material2-era in places. When it and the M3 custom-design-system doc disagree, follow the M3 doc.
- It is a sample: no networking, DI or persistence guidance. Use NIA for those.
