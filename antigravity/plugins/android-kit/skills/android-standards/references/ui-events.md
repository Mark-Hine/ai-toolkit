# One-shot ViewModel → UI events: house pattern and reference code

Rule: `guidance/android/ui-events.md`. This file holds the canonical code and the reasoning.

## Position (decided 2026-09-03)
- Official guidance (developer.android.com/topic/architecture/ui-layer/events, updated 2026-05) says ViewModel events
  "should always result in a UI state update" and names Channels as not guaranteeing delivery. Graded Strongly Recommended,
  defined there as "unless it clashes fundamentally with your approach".
- The single source behind it (manuelvivo.dev/viewmodel-events-antipatterns) calls itself opinionated and concedes the
  `Dispatchers.Main.immediate` mitigation; kotlinx.coroutines#2886 (Elizarov's endorsement of that mitigation) is still open.
  Orbit, MVIKotlin, FlowMVI and Ballast ship channel-style side effects as first-class APIs. The `kotlin-flow-state-event-modeling`
  skill marks `Channel(BUFFERED).receiveAsFlow()` as the correct primitive for single-consumer exactly-once events.
- House decision: use the buffered Channel for one-shot events. The defects that matter are (a) collection that is not
  lifecycle-aware and (b) `SharedFlow(replay = 0)` losing events. Residual, accepted: in-memory events die with the process,
  and an event received on a non-immediate dispatcher just before the collector is cancelled can be dropped.

## Base ViewModel

```kotlin
abstract class EventViewModel<Event, UiState>(initialState: UiState) : ViewModel() {

    private val _uiState = MutableStateFlow(initialState)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    private val _events = Channel<Event>(Channel.BUFFERED)
    /** Single consumer, exactly-once, buffered while nothing collects. Collect lifecycle-aware. */
    val events: Flow<Event> = _events.receiveAsFlow()

    /** Synchronous and atomic. Call it from wherever the new state is known; do not wrap it in launch. */
    protected fun updateUiState(update: UiState.() -> UiState) = _uiState.update(update)

    /** viewModelScope is Dispatchers.Main.immediate, which keeps send/receive ordering tight. */
    protected fun sendEvent(event: Event) {
        viewModelScope.launch { _events.send(event) }
    }
}
```
No `delayInMillis` parameters: a caller needing a delay writes `viewModelScope.launch { delay(x); sendEvent(e) }` so the
timing is visible at the call site and controllable in tests with a `TestDispatcher`.

## Sealed UiState and Event

```kotlin
sealed interface HomeUiState {
    data object Loading : HomeUiState
    data class Loaded(val balance: Money, val offers: ImmutableList<Offer>) : HomeUiState
    sealed interface Error : HomeUiState {
        val message: String
        data class Auth(override val message: String) : Error
        data class Generic(override val message: String) : Error
    }
}

/** Screen-scoped. Snackbars are NOT here: they are app-scoped and go through SnackbarPresenter (below). */
sealed interface HomeNavigationEvent {
    data object DetailsScreen : HomeNavigationEvent
    data object ContentScreen : HomeNavigationEvent
    data class OpenUri(val uri: String) : HomeNavigationEvent
    data object FinishActivity : HomeNavigationEvent
}

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val snackbarPresenter: SnackbarPresenter,
) : EventViewModel<HomeNavigationEvent, HomeUiState>(HomeUiState.Loading) {
    fun onDetailsClick() = sendEvent(HomeNavigationEvent.DetailsScreen)
    fun onSaveFailed() = snackbarPresenter.show(SnackbarMessage(R.string.save_failed))
}
```
Annotate UI state classes `@Immutable`/`@Stable` and use `kotlinx.collections.immutable` for lists (Compose stability).
Why two mechanisms and no marker interface: navigation belongs to the screen that raised it and dies with it; a snackbar
must survive the navigation it often accompanies and is shown by the root Scaffold. Scope and consumer differentiate them.

## Collecting events in Compose (lifecycle-aware)

```kotlin
@Composable
fun <T> EventEffect(events: Flow<T>, onEvent: (T) -> Unit) {
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    val currentOnEvent by rememberUpdatedState(onEvent)   // collector survives recomposition, handler stays fresh
    LaunchedEffect(events, lifecycle) {
        lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
            events.collect { currentOnEvent(it) }
        }
    }
}

/** Extracted handler: plain function, exhaustive when, unit-testable with a fake navigator/context. */
internal fun onHomeNavigationEvent(
    navigator: HomeNavigator,          // whatever the host provides: NavController, Nav3 back stack, or a lambda bundle
    activity: Activity?,
    uriHandler: UriHandler,
    event: HomeNavigationEvent,
) {
    when (event) {
        HomeNavigationEvent.DetailsScreen -> navigator.toDetails()
        HomeNavigationEvent.ContentScreen -> activity?.startActivity(ContentActivity.createIntent(activity))
        is HomeNavigationEvent.OpenUri -> uriHandler.openUri(event.uri)
        HomeNavigationEvent.FinishActivity -> activity?.finishAndRemoveTask()
    }
}

@Composable
fun HomeRoute(
    navigator: HomeNavigator,
    viewModel: HomeViewModel = hiltViewModel(),
) {
    val activity = LocalActivity.current          // androidx.activity.compose; no `context as? Activity`
    val uriHandler = LocalUriHandler.current
    EventEffect(viewModel.events) { onHomeNavigationEvent(navigator, activity, uriHandler, it) }

    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    HomeContent(uiState = uiState, onDetailsClick = viewModel::onDetailsClick)
}
```
The ViewModel never sees `navigator`, `Activity` or a navigation library; only the handler does. In a hybrid repo the same
handler mixes Compose destinations, `startActivity` and `finish`, which is what makes the pattern portable across apps.
Why `repeatOnLifecycle`: `LaunchedEffect` is scoped to the composition, which stays alive while the screen is STOPPED, so a
bare `collect` would navigate or `startActivity` in the background (blocked on Android 10+). Events sent while stopped wait
in the Channel buffer and are delivered when the screen restarts. This is the property that makes the buffered Channel
preferable to `SharedFlow` here.

Views (Fragment/Activity): `viewLifecycleOwner.lifecycleScope.launch { repeatOnLifecycle(STARTED) { viewModel.events.collect { … } } }`.

## Snackbars (Material3)

```kotlin
class SnackbarPresenter @Inject constructor() {
    private val _messages = Channel<SnackbarMessage>(Channel.BUFFERED)
    val messages: Flow<SnackbarMessage> = _messages.receiveAsFlow()   // expose the Flow, never the Channel
    fun show(message: SnackbarMessage) { _messages.trySend(message) }
}

@Composable
fun SnackbarEffect(presenter: SnackbarPresenter, hostState: SnackbarHostState) {
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    val context = LocalContext.current
    LaunchedEffect(presenter, hostState, lifecycle) {
        lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
            presenter.messages.collect { msg ->
                val result = hostState.showSnackbar(
                    message = context.getString(msg.messageRes),
                    actionLabel = msg.actionRes?.let(context::getString),
                    duration = msg.duration,
                )
                when (result) {
                    SnackbarResult.Dismissed -> msg.onDismiss()
                    SnackbarResult.ActionPerformed -> msg.onAction()
                }
            }
        }
    }
}
```
Install once at the root `Scaffold` (`snackbarHost = { SnackbarHost(hostState) }`). Screens call `presenter.show(...)` or emit
`ShowSnackbar` events; they never own a `SnackbarHostState`.

## Actions holder (callback grouping)

Official position: developer.android.com/develop/ui/compose/state-hoisting prefers individual lambdas because they
"maximize the visibility of what the composable function responsibilities are". The Compose API guidelines
(androidx compose-api-guidelines.md) add that a stateless-parameters-plus-callbacks list "will eventually reach a point of
scale where it becomes unwieldy" and recommend factoring callbacks into a stable holder at that point. house rule: plain
lambdas by default; an `XActions` holder once a screen/section composable would exceed five callbacks.

```kotlin
/** Function types only; a data class of function types is inferred stable. {} defaults keep previews one-liners. */
@Immutable
data class HomeActions(
    val onRetry: () -> Unit = {},
    val onDetailsClick: () -> Unit = {},
    val onOfferClick: (Offer) -> Unit = {},
    val payments: PaymentActions = PaymentActions(),      // per-section slice when the screen grows
)

@Immutable
data class PaymentActions(
    val onPayClick: (PaymentData) -> Unit = {},
    val onChangeDateClick: () -> Unit = {},
)

class HomeViewModel : EventViewModel<HomeNavigationEvent, HomeUiState>(HomeUiState.Loading) {
    val actions = HomeActions(                             // built once; method references have stable identity
        onRetry = ::onRetry,
        onDetailsClick = ::onDetailsClick,
        onOfferClick = ::onOfferClick,
        payments = PaymentActions(onPayClick = ::onPayClick, onChangeDateClick = ::onChangeDateClick),
    )
}

@Composable
fun HomeContent(uiState: HomeUiState, actions: HomeActions, modifier: Modifier = Modifier) {
    // screen level: takes the holder
    when (uiState) {
        is HomeUiState.Loaded -> {
            OfferList(offers = uiState.offers, onOfferClick = actions.onOfferClick)   // leaf: single lambda
            PaymentsSection(payments = uiState.payments, actions = actions.payments)  // section: its slice
        }
        is HomeUiState.Error -> ErrorState(message = uiState.message, onRetry = actions.onRetry)
        HomeUiState.Loading -> Loading()
    }
}
```
Rules: never `HomeActions(...)` inside a composable (allocates per recomposition); never state, `State<T>` or predicates
in the holder; reusable components (`AppButton`, cards, list items) never take a holder. The alternative single sink
`onEvent: (ScreenEvent) -> Unit` (Circuit-style MVI) is not the house pattern: it hides what a screen can do behind a
sealed class and allocates an event per interaction.

## What not to do
- `MutableSharedFlow<Event>()` for events (lossy when nothing collects).
- `MutableLiveData<Boolean>` / `MutableStateFlow("")` as triggers (sticky; re-fire on every re-collection).
- `LaunchedEffect(Unit)` capturing a navigator or context (stale capture).
- Importing a navigation library into a ViewModel (couples every screen to it; hosts differ across repos).
- `ShowSnackbar` as a navigation event, or a screen owning a `SnackbarHostState` (the message dies with the screen).
- A marker interface to separate navigation from other one-shot events; separate by scope and consumer instead.
- Twelve callback parameters plus `State<T>` parameters on one composable: move derived state into `UiState`, group callbacks into an actions holder.
