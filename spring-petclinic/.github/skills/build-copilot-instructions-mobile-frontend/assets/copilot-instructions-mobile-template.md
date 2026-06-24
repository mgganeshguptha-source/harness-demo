# Mobile (Ionic + Angular) copilot-instructions.md — Template and Section Guide

This is the target structure for the single file the skill generates at
`.github/copilot-instructions.md`. This file is **repo-wide,
cross-cutting content only**. Naming conventions, code style, folder
structure, and test rules are NOT part of this file — they are
path-specific rules maintained separately in the copilot-toolkit
repository.

Each section states: what it is for, whether it is discoverable from the
repo, and what to do if it is not.

---

## Section 1 — Repository Overview

**Discoverable:** Partially. Tech stack, versions, and target platforms
come from package.json and capacitor config. Purpose and domain do not.

- **Purpose** — what this app is and who uses it. NOT discoverable. Ask.
  If unknown: `[TODO — MUST COMPLETE]: One-paragraph description of what
  this mobile app does and its primary users. Needed so Copilot
  understands domain context.`
- **Tech Stack** — discoverable from package.json. List Ionic version,
  Angular version, Capacitor version, state management, UI approach,
  test framework.
- **Target Platforms** — discoverable from capacitor config. List
  ios / android / web as configured. If web is a target, this matters
  for native-call guarding (see Section 3).
- **Architecture** — discoverable from src/app. State page/tab/routing
  organisation, standalone vs NgModule, lazy loading.

---

## Section 2 — Application Structure

**Discoverable:** Yes, mostly, from src/app.

Page organisation (tabs, side menu, routed pages), feature/shared/core
split, routing approach, state management approach (NgRx / signals /
services with BehaviorSubject). Fill from observed structure. Do not
claim a state library the repo does not use.

---

## Section 3 — Native Integration Conventions

**Discoverable:** Partially. Installed plugins are discoverable; usage
intent often is not.

- Installed Capacitor/Cordova plugins — read from package.json. List
  them.
- Platform guarding — whether native calls are wrapped in platform
  checks. Critical if web is a target platform: native plugin calls on
  web throw. If the code shows inconsistent guarding, ask what the
  standard is. If unknown:
  `[TODO — MUST COMPLETE]: Standard for guarding native plugin calls
  (e.g. always check Capacitor.isNativePlatform() before plugin use).
  Critical because the app has a web target and unguarded native calls
  crash on web.`
- Permission request pattern — read from code. If not visible, ask.
- Offline / local storage strategy (Preferences, SQLite, secure
  storage) — read from code. If intent unclear, ask, or
  `[TODO — MUST COMPLETE]`.

---

## Section 4 — API Integration Conventions

**Discoverable:** Partially, from the HTTP layer and interceptors.

- HttpClient usage pattern — read from existing services.
- Error handling approach (interceptor, catchError) — read from
  interceptors.
- Environment configuration — read from environments.
- Network-state handling (behaviour when offline, retry, queueing) —
  often NOT discoverable. Ask. If unknown:
  `[TODO — MUST COMPLETE]: Behaviour when a request is made offline —
  fail, queue, cached fallback. Mobile apps lose connectivity routinely;
  this must be explicit.`

---

## Section 5 — Security Guidelines

**Discoverable:** Rarely. Mostly not visible in code.

Short DOs / DON'Ts. The skill may include a standard universal set
without asking:

- Never store auth tokens or secrets in plain Preferences/localStorage;
  use secure storage on device.
- Never disable Angular sanitization.
- Always validate deep-link / custom-scheme parameters before use.
- Always request the minimum necessary native permissions.

Project-specific items (secure storage plugin choice, token strategy on
device, certificate pinning) — ask. If unknown:
`[TODO — MUST COMPLETE]: <specific security item>`.

---

## Section 6 — Design Patterns

**Discoverable:** Yes, mostly, from existing code.

State only the patterns the codebase actually uses: smart/presentational
split, Ionic lifecycle usage convention (`ionViewWillEnter` vs Angular
`ngOnInit` — when each is used), reactive forms, RxJS subscription
management (async pipe preferred), OnPush usage. Do not list patterns
the codebase does not use.

---

## Section 7 — Unique Patterns For This Project

**Discoverable:** Rarely. Highest-value section.

Examples: offline-first behaviour, i18n strategy, accessibility baseline,
platform-specific theming (iOS vs Android styling), date/locale
handling, push notification handling. Mostly NOT discoverable. Ask
explicitly. If unknown:
`[TODO — MUST COMPLETE]: Project-specific rules an AI would not infer
from code — offline-first behaviour, i18n, accessibility baseline,
platform theming, push handling. These cause the most defects when
missed.`

---

## Section 8 — What To Avoid

**Discoverable:** Partially, by inference from architecture.

Ionic/Angular/project anti-patterns: unguarded native plugin calls when
web is a target, manual subscribe without unsubscribe, logic in
templates, any-typed API responses, blocking the UI thread on large
sync work, mixing Ionic and Angular lifecycle hooks inconsistently. The
skill may propose the standard set and ask for project-specific
additions.

---

## Section 9 — Documentation Requirements

**Discoverable:** Partially. JSDoc/Compodoc usage is visible in code.

Code documentation expectations (JSDoc on services and plugin wrappers),
project documentation expectations (README, native build/run steps,
environment config, required native tooling). Fill what is observable;
ask for team expectations not visible in code.

---

## What a filled section looks like

```markdown
## Repository Overview

- Purpose: Mobile companion app for clinic staff to view appointments
  and capture visit notes on the go.
- Tech Stack: Ionic 7 (@ionic/angular), Angular 17, Capacitor 5,
  signals for local state, Jasmine/Karma, ESLint + Prettier.
- Target Platforms: iOS, Android, web (PWA).
- Architecture: Tab-based navigation, standalone components,
  lazy-loaded feature routes, services-with-signals for state.
```

## What an unfilled section looks like

```markdown
## Native Integration Conventions

[TODO — MUST COMPLETE]: Standard for guarding native plugin calls
(e.g. always check Capacitor.isNativePlatform() before plugin use) and
the offline/local-storage strategy. The developer did not know these at
generation time. Critical because the app has a web target — unguarded
native calls crash on web — and offline behaviour is undefined.
```

---

## Not part of this file

Naming conventions, code style, folder structure, and test rules are
**path-specific rules**. They are maintained centrally in the
copilot-toolkit repository and copied into a repo's
`.github/instructions/` folder as a separate step. This skill does not
generate them. Keeping them separate keeps shared rules consistent
across all mobile repos.
