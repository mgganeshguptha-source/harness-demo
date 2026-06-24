---
applyTo: "src/app/**/*.ts,src/app/**/*.html,capacitor.config.ts,capacitor.config.json"
---

# Performance Standards — Ionic Mobile

Mobile-specific performance rules. The Angular performance rules in `performance-angular.instructions.md` all apply — this file adds what's different on mobile: startup time, native bridge cost, list virtualization, image sizing, and battery.

## Startup time

Cold start budget: **≤ 3s to interactive on mid-tier Android**. Splash → first usable screen.

- Lazy-load every feature module. Only login + shell + first authenticated route in the initial bundle.
- Defer Capacitor plugin initialisation that isn't needed at startup (push registration, analytics, biometric setup) — fire after first paint.
- Avoid heavy work in `APP_INITIALIZER` — it blocks the app from rendering. Use it only for genuinely required setup (config fetch, auth state hydration).
- Splash screen: configure `@capacitor/splash-screen` to auto-hide on first stable render, not on a fixed timeout. Use `SplashScreen.hide()` when the first route's data is loaded.

## Bundle size — tighter than web

- Initial bundle budget: **≤ 350 KB gzipped** (mobile networks + storage are more constrained).
- Same import discipline as Angular (tree-shakeable imports, no `import *`).
- Capacitor plugins: each adds bundle weight + native code. Audit `package.json` quarterly for unused plugins.

## Lists — always virtualize

- Any list that may grow beyond ~30 visible items uses Ionic's `<ion-virtual-scroll>` (deprecated in some versions) or `@angular/cdk/scrolling`'s `cdk-virtual-scroll-viewport`.
- `*ngFor` without virtualization on a 200-item list renders 200 DOM trees — visible jank on scroll, especially on Android.
- `trackBy` is mandatory (see Angular performance rules).
- Infinite scroll: use Ionic's `<ion-infinite-scroll>` with cursor-based pagination from the backend (see `api-design.instructions.md`).

## Images

- **Mandatory: specify `width` and `height`** on every `<img>` — prevents layout shift, helps the rendering engine.
- Use `NgOptimizedImage` directive (Angular 15+) — it handles lazy loading and warns on missing dimensions.
- Serve images sized to the device: don't ship a 2000px-wide hero to a 360px phone. Use responsive `srcset` or a server-side resizer.
- Prefer WebP/AVIF with JPEG fallback.
- For user-captured photos (insurance cards, ID): resize before upload. A 12MP camera photo is ~4MB — slow upload on mobile networks.

## Native bridge cost

- Every Capacitor plugin call crosses the JS↔native bridge — non-trivial cost. Batch where possible.
- ❌ Calling `Preferences.get()` 10 times in a loop. ✅ Call once with a structured key, or use a single in-memory cache hydrated from storage at startup.
- Filesystem reads: same — batch into one read where the API supports it.
- Geolocation: don't poll. Use `watchPosition` with a coarse accuracy if continuous tracking is needed; otherwise one-shot `getCurrentPosition`.

## Memory

- Mobile devices have far less RAM than dev machines. A leak that's invisible on desktop crashes the app on a 3GB Android.
- Detach off-screen heavy components.
- Clear large in-memory caches when the app goes to background (`@capacitor/app` `appStateChange` → `inactive`).
- Test on a low-end device — emulator and desktop browser hide most of these issues.

## Battery

- Avoid `setInterval` polling — keeps the CPU awake.
- Avoid foreground location tracking unless required. Background location dramatically increases drain and triggers App Store / Play Store scrutiny.
- Push for push notifications instead of poll-based "check for updates."

## Network

- Assume slow, intermittent connections. Set explicit HTTP timeouts (connect ~5s, read ~10s for mobile — looser than backend-to-backend).
- Coalesce requests on app foreground — don't fire 10 parallel GETs the moment the user opens the app. Stagger or batch.
- Honour `Cache-Control` headers and use HTTP caching aggressively.

## App size

- Total installed app size affects install conversion. Target: **< 50 MB** download on app stores.
- Audit native dependencies — large native SDKs (full Firebase, large analytics suites) inflate APK/IPA.
- Use Android App Bundles (AAB) for Play Store — smaller per-device downloads.

## Rendering

- Use Ionic components for native-feel transitions — they're hardware-accelerated. Custom CSS animations should use `transform` and `opacity` only (GPU-accelerated); avoid animating `width`, `height`, `top`, `left`.
- Avoid `backdrop-filter` on large surfaces — expensive on older devices.
- Test scroll performance on a 3-year-old mid-tier Android, not a flagship.

## Capacitor config — performance-relevant flags

- `android.useLegacyBridge: false` (use modern bridge unless a plugin requires legacy)
- `android.allowMixedContent: false` (security + performance — HTTP downgrades break HTTP/2)
- `ios.scrollEnabled: true`, `ios.contentInset: 'automatic'` — defaults are usually right; only change with cause

## Measurement

- Lighthouse mobile audits for the served Angular app.
- Native profiling: Android Studio Profiler, Xcode Instruments — use for crashes and ANRs.
- Sentry / Datadog mobile RUM for startup time, slow frames, crash-free rate.
- Set crash-free session target: **≥ 99.5%** for a HIPAA-grade app.

## What never to do

- ❌ Test only on emulator / desktop browser — most mobile perf issues hide there
- ❌ Ship dev builds — they're 3–10x slower than production builds
- ❌ Use `console.log` in hot paths — even in dev, it's measurable on mobile
- ❌ Poll the backend every few seconds for updates — use push or SSE
- ❌ Load all user data on login "just in case" — fetch as the user navigates
- ❌ Keep heavy work on the main thread — use Web Workers for CPU-bound tasks (CSV parsing, PDF rendering, crypto)

## Refusal pattern

> ⚠️ Mobile performance guardrail: <one-line rule>. Suggested alternative: <code>.
