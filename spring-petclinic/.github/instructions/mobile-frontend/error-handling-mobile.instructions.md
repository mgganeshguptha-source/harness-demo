---
applyTo: "src/app/**/*.ts,src/app/**/*.html"
---

# Error Handling — Ionic Mobile

Mobile-specific error-handling additions. The base rules from `error-handling-angular.instructions.md` all apply — this file covers what's different on mobile: offline, network state, native plugin errors, and platform-specific UX.

## Network state awareness

- Use `@capacitor/network` to observe connection state. Subscribe in a root service, expose as an observable.
- Before firing an HTTP request: if the app is offline AND the request is not queueable, show "You're offline" UI rather than letting the HTTP call fail with a generic network error.
- Distinguish three states in UX:
  1. **Online** — normal
  2. **Offline** — read from cache, queue writes, show banner
  3. **Online but flaky** — slow / intermittent timeouts — retry with backoff

## Offline-tolerant operations

- **Reads:** Cache-first with stale-while-revalidate. Show cached data immediately; refresh in background; update UI when fresh data arrives.
- **Writes:** Two patterns —
  - **Reject offline:** simple, safe default. Show "This action needs an internet connection." Use for anything PHI-modifying.
  - **Queue and replay:** for low-risk writes (analytics, non-PHI preferences). Store in secure storage (never `localStorage`), replay when online, handle idempotency on the server.
- Never queue PHI writes locally without explicit security review — offline storage of PHI is a HIPAA risk.

## HTTP error mapping — mobile-specific additions

On top of the Angular HTTP interceptor's RFC 7807 handling, add:

- **`status === 0` or `error instanceof TimeoutError`** → `NetworkAppError` with a `cause` of `offline` / `timeout` / `dns-failed` / `tls-failure` (where detectable).
- **Certificate pinning failure** (when using `@capacitor-community/http` with pinning) → `SecurityAppError` — do NOT retry, do NOT silently downgrade. Surface to user as "Connection not trusted" and log to remote.
- **Capacitor plugin errors** (Camera permission denied, Geolocation unavailable, etc.) — distinct from HTTP errors. Map to typed `PluginAppError` with the plugin name and reason.

## Plugin permission errors

- For permission-gated plugins (Camera, Geolocation, Photos, Push), check permission state before invoking. Don't catch a permission denial after the fact — bad UX.
- If permission is denied permanently (`'denied'` not `'prompt'`), guide the user to system settings via `App.openSettings()` rather than re-asking.
- Never crash on permission denial — every plugin call is wrapped in a try/catch that maps to a user-friendly message.

## Background and lifecycle errors

- App lifecycle (`@capacitor/app`): handle `appStateChange`. When the app returns from background after a long pause, **refresh auth state before resuming any PHI-displaying screen** — token may have expired, session policy may require re-auth.
- Long-running operations interrupted by backgrounding: persist progress to secure storage, resume on foreground, or restart cleanly.

## User-facing error UX on mobile

- Use Ionic `ToastController` for transient errors, `AlertController` for blocking ones.
- Toasts: 3–5 seconds, top or bottom (consistent across the app — pick one).
- Include the correlation ID in support-actionable errors so users can quote it (mobile users rarely can dig into devtools).
- For repeated failures of the same call: don't spam toasts. De-duplicate within a short window.
- Tap-to-retry: include a retry action on transient errors; never silently retry forever.

## Crash reporting

- Integrate Firebase Crashlytics or Sentry React Native equivalent for Ionic.
- Wire the custom `ErrorHandler` (see Angular error-handling) into the crash reporter.
- **PHI scrubbing in `beforeSend`** — same rule as web. Crash reports persist on vendor servers.
- Native crashes (Java / Swift / Obj-C) and JavaScript crashes are reported separately by most tools — verify both channels are configured.

## What never to do (mobile-specific)

- ❌ `alert(...)` inside a Capacitor app — uses browser alert, looks broken on native. Use `AlertController`.
- ❌ Catch a plugin error and continue without telling the user — they'll see a feature silently not work.
- ❌ Retry a TLS / certificate-pinning failure — that's a security signal, not a network blip.
- ❌ Store error logs containing PHI in `Preferences` / `Storage` — secure storage only, and ideally not at all.
- ❌ Assume the network is up. Mobile networks fail constantly. Every HTTP call needs network-aware handling.

## Refusal pattern

> ⚠️ Mobile error-handling guardrail: <one-line rule>. Suggested alternative: <code>.
