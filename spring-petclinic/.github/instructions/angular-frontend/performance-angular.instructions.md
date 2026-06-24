---
applyTo: "src/app/**/*.ts,src/app/**/*.html"
---

# Performance Standards — Angular Web

Performance rules for the Angular web app. Focus on change detection, rendering, and bundle size — the three things that actually dominate Angular performance.

## Change detection

### Use `OnPush` by default on new components
- All new components: `changeDetection: ChangeDetectionStrategy.OnPush`.
- The default strategy (`Default`) runs change detection on every component for every event — quadratic cost as the app grows.
- `OnPush` runs change detection only when:
  - An `@Input()` reference changes (not mutation — see immutability below)
  - An event fires from the component or a child
  - An `async` pipe in the template emits
  - Change detection is manually triggered

### Immutability for inputs
- Never mutate input objects/arrays in place. `OnPush` does reference equality — `arr.push(x)` won't trigger an update.
- Use spread / immutable patterns: `this.items = [...this.items, newItem]`.
- Signals (Angular 16+) are an alternative — they handle granular reactivity without manual immutability rules.

### Avoid function calls in templates
- ❌ `{{ getFormattedName() }}` — runs every change detection cycle
- ✅ Compute in `ngOnChanges` / a getter cached via memoization, or use a pure pipe
- Pure pipes (`@Pipe({pure: true})`) cache by input — safe to use in templates

## `*ngFor` rules

- **Always use `trackBy`** for any list that may change. Without it, Angular re-creates DOM nodes on any list change.
  ```ts
  trackById(index: number, item: { id: string }) { return item.id; }
  ```
  ```html
  <div *ngFor="let item of items; trackBy: trackById">{{ item.name }}</div>
  ```
- For long lists (>50 items visible), use `@angular/cdk/scrolling` virtual scroll — only renders visible rows.

## Async patterns

- Prefer `async` pipe over manual `subscribe`. The pipe handles unsubscription, marks for check, and integrates with `OnPush`.
- When you must `subscribe()`, **always unsubscribe** on destroy:
  - `takeUntilDestroyed()` (Angular 16+) — cleanest
  - `takeUntil(this.destroy$)` pattern with a Subject in `ngOnDestroy`
- Never subscribe without a teardown path — memory leaks on every component instance.

## Lazy loading

- Every feature module is lazy-loaded via `loadChildren` (standalone components: `loadComponent`). The initial bundle ships only the shell + login + first route.
- Group routes by feature, not by component type.
- Use `CanMatch` guards (not just `CanActivate`) for protected lazy routes — prevents the lazy chunk from downloading if the user isn't authorised.

## Bundle size

- **Hard budget:** initial bundle ≤ 500 KB gzipped. Configure in `angular.json` `budgets` — build fails if exceeded.
- Import only what's used. ❌ `import * as _ from 'lodash'` — pulls the entire library. ✅ `import { debounce } from 'lodash-es'`.
- Avoid heavy libraries when small alternatives exist (moment.js → date-fns or native `Intl`; full lodash → lodash-es with tree-shaking).
- Run `ng build --stats-json` and inspect with webpack-bundle-analyzer when bundle grows.

## Initial load

- Use route-level preloading for the next-likely route: `PreloadAllModules` is too aggressive for healthcare apps; write a custom preloader that loads after idle.
- Server-side rendering (Angular Universal) only if SEO or first-paint metrics demand it — adds operational complexity.
- Inline critical CSS; defer non-critical.
- `<link rel="preconnect">` to the API origin and CDN.

## RxJS efficiency

- `share()` / `shareReplay()` for observables consumed by multiple subscribers — avoids duplicate HTTP calls.
- Use `switchMap` for cancel-previous semantics (search-as-you-type). `mergeMap` for parallel. `concatMap` for serial.
- Debounce user input that triggers HTTP: `debounceTime(300)`.
- Never nest `subscribe` inside `subscribe` — flatten with `switchMap`.

## HTTP

- Use `HttpClient`'s caching headers — `Cache-Control` from the server is respected by the browser. Don't reinvent.
- For frequently re-fetched data, cache in a service with explicit TTL.
- Batch requests where the API supports it. Avoid 10 parallel GETs that could be 1.

## Forms

- Reactive forms only — they're more performant and testable than template-driven.
- For very large forms, use `updateOn: 'blur'` or `updateOn: 'submit'` to avoid per-keystroke validation cost.

## Memory

- Detach the change detector for off-screen components that hold heavy state (`cdr.detach()` / `cdr.reattach()`).
- Clear references on destroy — large objects held in component fields prevent GC.
- Be careful with closures in `setInterval` / `setTimeout` — they pin the surrounding scope.

## Images and media

- Use `NgOptimizedImage` directive for images — handles lazy loading, srcset, and warns on common mistakes.
- Serve modern formats (WebP/AVIF) with fallback.
- Specify `width` and `height` on `<img>` — prevents layout shift.

## What never to do

- ❌ `setTimeout(() => { ... }, 0)` to "fix" change detection bugs — masks the real issue
- ❌ `ChangeDetectorRef.detectChanges()` peppered through components — same
- ❌ `*ngIf` toggling expensive components on/off when they could be hidden via CSS
- ❌ Synchronous heavy loops in component code — block the UI thread
- ❌ Polling the backend every second when SSE/WebSocket would do

## Refusal pattern

> ⚠️ Angular performance guardrail: <one-line rule>. Suggested alternative: <code>.
