# One-shot model → UI events on iOS: house pattern and reference code

Rule: `~/.codex/guidance/ios/ui-events.md`. This file holds the canonical code and the reasoning. Android twin:
`android-standards` → `references/ui-events.md`; the two differ on purpose, see "Why this differs from Android".

## Position (decided 2026-09-04, sources verified the same day)
- SwiftUI presentation is binding-driven and the framework clears the binding itself. `alert(_:isPresented:actions:)`:
  "When the user presses or taps one of the alert's actions, the system sets this value to `false` and dismisses."
  `sheet(item:)` / `navigationDestination(item:)` take "a binding to an optional source of truth"; `NavigationStack(path:)`
  holds "a type-erased list of data representing the content of a navigation stack" (developer.apple.com/documentation/swiftui).
  So navigation, sheets and alerts are **optional state on the model**, not events: the sticky-state problem that made
  Android choose a Channel does not exist here.
- iOS has no system toast; HIG: "Use alerts sparingly. Alerts give people important information, but they interrupt the
  current task." Toasts are therefore an app-scoped presenter rendered once by the root, never per screen.
- Effects with no presentation binding (haptics, scroll-to, focus, dismissing the current screen) are the only true
  one-shot events. They go through a buffered, main-actor `EventStream` consumed in `.task`, which SwiftUI cancels when the
  view disappears ("If the task doesn't finish before SwiftUI removes the view or the view changes identity, SwiftUI cancels
  the task"). `AsyncStream` alone is not enough: SE-0314 says "concurrent iteration is considered a programmer error" and a
  cancelled iteration resumes `nil`, so a re-appearing view needs a fresh stream and anything sent meanwhile must be buffered.
- Residual, accepted: buffered effects die with the process; an effect sent after the view is removed for good is dropped with the model.

## Model: state, routes, presentation, effects

```swift
enum HomeState { case loading; case loaded(balance: Money, offers: [Offer]); case error(HomeError) }
enum HomeRoute: Hashable { case details(Offer.ID); case content; case web(URL) }
enum HomeAlert: Identifiable { case saveFailed; case sessionExpired; var id: Self { self } }
enum HomeEffect { case haptic(UINotificationFeedbackGenerator.FeedbackType); case scrollToTop; case popScreen }

@MainActor @Observable
final class HomeModel {
    private(set) var state: HomeState = .loading
    var path: [HomeRoute] = []          // NavigationStack(path:)
    var alert: HomeAlert?               // .alert(item:)
    let effects = EventStream<HomeEffect>()

    private let repository: any OffersRepository   // protocol seam; main-safety lives in the repository
    private let toasts: ToastPresenter            // app-scoped, injected from the composition root

    init(repository: any OffersRepository, toasts: ToastPresenter) {
        self.repository = repository
        self.toasts = toasts
    }

    func load() async {
        state = .loading
        do { state = .loaded(balance: try await repository.balance(), offers: try await repository.offers()) }
        catch { state = .error(HomeError(error)) }
    }
    func onOfferTap(_ offer: Offer) { path.append(.details(offer.id)) }
    func onTermsTap(_ url: URL) { path.append(.web(url)) }
    func onSaveFailed() { alert = .saveFailed }
    func onCopied() { toasts.show(Toast(text: "Copied", style: .info)) }
    func onPaid() { effects.send(.haptic(.success)); effects.send(.popScreen) }
}
```
No loading in `init`: the screen's `.task` calls `load()` so the work is cancelled with the view. `state` is `private(set)`;
presentation properties are settable because the presentation modifiers write them back.

## EventStream (buffered, re-subscribable, main actor)

```swift
@MainActor
final class EventStream<Event> {
    private var buffer: [Event] = []
    private var current: (id: UUID, continuation: AsyncStream<Event>.Continuation)?

    func send(_ event: Event) {
        if let current { current.continuation.yield(event) } else { buffer.append(event) }
    }

    /// A fresh stream per subscriber (one at a time); drains what was sent while nothing was listening.
    var events: AsyncStream<Event> {
        let id = UUID()
        return AsyncStream { continuation in
            continuation.onTermination = { [weak self] _ in
                Task { @MainActor [weak self] in self?.detach(id) }
            }
            current?.continuation.finish()
            current = (id, continuation)
            buffer.forEach { continuation.yield($0) }
            buffer.removeAll()
        }
    }

    private func detach(_ id: UUID) { if current?.id == id { current = nil } }
}
```
Lives in the shared package next to `ToastPresenter`. Unit-test it directly: send before subscribing, subscribe, expect the
buffered event; cancel, send, re-subscribe, expect delivery.

## Screen: owns the model, wires presentation, consumes effects

```swift
struct HomeScreen: View {
    @State private var model: HomeModel
    @Environment(\.dismiss) private var dismiss

    init(model: HomeModel) { _model = State(initialValue: model) }   // built once by the composition root

    var body: some View {
        NavigationStack(path: $model.path) {
            HomeContent(state: model.state, actions: model.actions)
                .navigationDestination(for: HomeRoute.self) { route in HomeRouteView(route: route) }
                .alert(item: $model.alert) { alert in
                    switch alert {
                    case .saveFailed: Button("Retry") { Task { await model.load() } }; Button("Cancel", role: .cancel) {}
                    case .sessionExpired: Button("Sign in") { model.onSignInTap() }
                    }
                }
        }
        .task { await model.load() }
        .task { for await effect in model.effects.events { handle(effect) } }
    }

    private func handle(_ effect: HomeEffect) {       // exhaustive; the model never sees UIKit, dismiss or a scroll proxy
        switch effect {
        case .haptic(let type): UINotificationFeedbackGenerator().notificationOccurred(type)
        case .scrollToTop: scrollToTop()               // ScrollViewReader proxy or scrollPosition binding held by the screen
        case .popScreen: dismiss()
        }
    }
}
```
`HomeRouteView` is the one place that maps `HomeRoute` to views (including `web` → an in-app `SFSafariViewController`
wrapper or `openURL`). Deep links append the same `HomeRoute` values to `path`. A `Task { … }` inside a button action is
fine: it is user-initiated and short; loading and observation stay in `.task`.

## Toasts (app-scoped)

```swift
struct Toast: Identifiable, Equatable {
    enum Style { case info, success, error }
    let id = UUID()
    let text: LocalizedStringResource
    let style: Style
    var duration: Duration = .seconds(3)
}

@MainActor @Observable
final class ToastPresenter {
    private(set) var queue: [Toast] = []
    func show(_ toast: Toast) { queue.append(toast) }
    func dismiss(_ id: Toast.ID) { queue.removeAll { $0.id == id } }
}

struct RootView: View {                                  // installed once, at the App/scene root
    @Environment(ToastPresenter.self) private var toasts
    var body: some View {
        AppTabs()
            .overlay(alignment: .top) {
                if let toast = toasts.queue.first {
                    ToastView(toast: toast)                     // design-system component, accessibility label = text
                        .task(id: toast.id) { try? await Task.sleep(for: toast.duration); toasts.dismiss(toast.id) }
                }
            }
    }
}
// App entry: RootView().environment(toastPresenter)  — the same instance the composition root hands to models.
```
A toast survives the navigation it accompanies because the root owns it; a screen never holds toast state.

## Actions struct (closure grouping)

Leaves and design-system components take individual closures. When a screen or section view would exceed five closures,
group them in an `XActions` struct of closures with no-op defaults, exposed by the model, and pass single closures down.

```swift
struct HomeActions {
    var onRetry: () -> Void = {}
    var onOfferTap: (Offer) -> Void = { _ in }
    var onTermsTap: (URL) -> Void = { _ in }
    var payments = PaymentActions()                    // per-section slice when the screen grows
}
struct PaymentActions { var onPay: (PaymentData) -> Void = { _ in }; var onChangeDate: () -> Void = {} }

extension HomeModel {
    var actions: HomeActions {                         // method references only; no state in here
        HomeActions(onRetry: { Task { await self.load() } }, onOfferTap: onOfferTap, onTermsTap: onTermsTap,
                    payments: PaymentActions(onPay: onPay, onChangeDate: onChangeDate))
    }
}

struct HomeContent: View {                             // stateless; #Preview passes fixture state and HomeActions()
    let state: HomeState
    let actions: HomeActions
    var body: some View {
        switch state {
        case .loading: ProgressView()
        case .loaded(let balance, let offers):
            BalanceCard(balance: balance)
            OfferList(offers: offers, onOfferTap: actions.onOfferTap)          // leaf: single closure
            PaymentsSection(actions: actions.payments)                        // section: its slice
        case .error(let error): ErrorState(error: error, onRetry: actions.onRetry)
        }
    }
}
```
Never build the struct inside `body`; never put state, bindings or predicates in it; reusable components never take it.
The alternative single sink `send: (Action) -> Void` (MVI/TCA style) is not the house pattern for new house code: it hides
what a view can do behind an enum. Where a repo already uses a reducer-style store consistently, follow that repo.

## UIKit hosts (hybrid repos)

Same model. The view controller reads `state`/`path`/`alert` with `withObservationTracking` (or `@Published` on the
`ObservableObject` variant below iOS 17) and consumes effects with a task started in `viewIsAppearing(_:)` and cancelled
in `viewDidDisappear(_:)`; `alert != nil` presents a `UIAlertController` whose actions set it back to `nil`.
The model still never imports UIKit navigation types; the controller maps routes to pushes.

## What not to do
- A `Bool`/optional that the model must reset by hand after a delay, or that re-fires on rotation or restoration.
- `PassthroughSubject`/`AsyncStream` created once and iterated by several views, or iterated after the first cancellation.
- `Task {}` in `onAppear` or a model's `init` for loading; `DispatchQueue.main.async` to publish state.
- A screen that owns toast state, or a toast modelled as an alert.
- `NavigationLink(destination:)` with inline views for anything deep-linkable; string routes; `UINavigationController` reach-ins from a model.
- Ten closures plus bindings on one content view: derive booleans into `state`, group closures into an actions struct.
