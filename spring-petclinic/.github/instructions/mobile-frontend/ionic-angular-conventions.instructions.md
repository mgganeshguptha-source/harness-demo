---
applyTo: "src/app/**/*.ts"
---

# Ionic + Angular Source Conventions (Mobile)

## Naming Conventions

- Pages: `PascalCase` class with `Page` suffix, `kebab-case` selector
  with app prefix, files `owner-list.page.ts`
- Components: `PascalCase` class, `kebab-case` selector, files
  `owner-card.component.ts`
- Services: `PascalCase` with `Service` suffix
- Plugin wrappers: `PascalCase` with `Service` suffix (e.g.
  `CameraService` wrapping the Capacitor Camera plugin)
- Methods and variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Observables: suffix with `$`

## Code Style

- Use constructor injection; mark dependencies `private`/
  `private readonly`.
- Prefer the `async` pipe over manual `subscribe`; if subscribing
  manually, unsubscribe (`takeUntilDestroyed`).
- Type all HTTP responses. No `any` for API payloads.
- Keep pages/components thin — logic in services.

## Native / Capacitor Rules

- Always guard native plugin calls with a platform check
  (`Capacitor.isNativePlatform()`) when the app has a web target —
  unguarded native calls crash on web.
- Wrap every Capacitor/Cordova plugin behind an injectable service. Do
  not call plugin APIs directly from a component or page.
- Only use plugins that are actually installed in `package.json`. Never
  reference a plugin, permission, or platform that is not configured.
- Request the minimum native permissions required, at the point of use.
- Never store tokens or secrets in plain Preferences/localStorage — use
  secure storage on device.

## Lifecycle

- Follow the project's standard for Ionic lifecycle
  (`ionViewWillEnter`/`ionViewDidLeave`) vs Angular lifecycle
  (`ngOnInit`/`ngOnDestroy`). Do not mix the two inconsistently within
  the same page.

## Structure

- Group by feature. Lazy-load feature routes where the project does so.
- One page/component/service per file.
