# JetSnack as a design-system blueprint

Repo: https://github.com/android/compose-samples/tree/main/Jetsnack
Companion doc: https://developer.android.com/develop/ui/compose/designsystems/custom

## Shape to mirror in `views/shared/compose/theme`
- `JetsnackTheme` = `CompositionLocalProvider(LocalJetsnackColors provides colors) { MaterialTheme(...) }`; colours
  are an `@Immutable` class with `mutableStateOf` fields updated via `update()`, exposed through
  `JetsnackTheme.colors`. The project theme should follow this; keep new tokens there, not in composables.
- Components live in one package, take `modifier: Modifier = Modifier`, expose slot content (`content: @Composable () -> Unit`)
  rather than many boolean flags (`compose-slot-api-pattern` skill).
- Gradient buttons and surfaces are built once (`JetsnackButton`, `JetsnackSurface`) and reused; screens never call
  `Button` from Material directly. Same rule for the project's components.
- Previews: a shared preview annotation set (project preview annotations) covering light/dark and font scale.

## Cautions
- JetSnack is Material2-era in places; when it and the M3 custom-design-system doc disagree, follow the M3 doc.
- It is a sample: no networking, DI or persistence guidance. Use NIA for those.
