# Frontend copilot-instructions.md — Template and Section Guide

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

**Discoverable:** Partially. Tech stack and architecture come from
package.json / angular.json. Purpose and domain do not.

- **Purpose** — what this application is and who uses it. NOT
  discoverable. Ask. If unknown:
  `[TODO — MUST COMPLETE]: One-paragraph description of what this app
  does and its primary users. Needed so Copilot understands domain
  context.`
- **Tech Stack** — discoverable from package.json. List Angular
  version, state management library, UI library, styling approach,
  test framework, RxJS.
- **Architecture** — discoverable from src/app. State module
  organisation (standalone vs NgModule), routing strategy, lazy loading.

---

## Section 2 — Application Structure

**Discoverable:** Yes, mostly, from src/app.

Feature module organisation, shared/core module split, routing approach
(eager vs lazy), state management approach (NgRx store / signals /
services with BehaviorSubject). Fill from observed structure. Do not
claim a state library the repo does not use.

---

## Section 3 — API Integration Conventions

**Discoverable:** Partially, from the HTTP layer and interceptors.

- HttpClient usage pattern (service-per-resource, typed responses) —
  read from existing services.
- Error handling approach (interceptor, catchError patterns) — read
  from interceptors.
- Environment configuration (environment.ts files, base URL handling) —
  read from environments.
- Auth token attachment (interceptor) — read from code. If not visible:
  ask, or `[TODO — MUST COMPLETE]`.

---

## Section 4 — Security Guidelines

**Discoverable:** Rarely. Mostly not visible in code.

Short DOs / DON'Ts. The skill may include a standard universal set
without asking:

- Never disable Angular's built-in sanitization
  (bypassSecurityTrust* only with strong justification).
- Never store tokens in localStorage if XSS risk is a concern — confirm
  the project's token storage strategy.
- Never interpolate untrusted HTML without sanitization.
- Always use Angular's HttpClient (built-in XSRF support), not raw
  fetch, for state-changing calls.

Project-specific items (auth provider, token storage decision, CSP) —
ask. If unknown: `[TODO — MUST COMPLETE]: <specific security item>`.

---

## Section 5 — Design Patterns

**Discoverable:** Yes, mostly, from existing code.

State only the patterns the codebase actually uses: smart/presentational
component split, container/facade pattern, reactive forms vs template
forms, RxJS subscription management (async pipe preferred), OnPush
change detection usage. Do not list patterns the codebase does not use.

---

## Section 6 — Unique Patterns For This Project

**Discoverable:** Rarely. Highest-value section.

Examples: i18n strategy (ngx-translate vs Angular i18n), feature flag
mechanism, accessibility baseline (WCAG level targeted, ARIA
expectations), date/locale handling, theming strategy. Mostly NOT
discoverable. Ask explicitly. If unknown:
`[TODO — MUST COMPLETE]: Project-specific rules an AI would not infer
from code — i18n, feature flags, accessibility baseline, locale
handling. These cause the most defects when missed.`

---

## Section 7 — What To Avoid

**Discoverable:** Partially, by inference from architecture.

Angular and project anti-patterns: logic in templates, manual
subscribe without unsubscribe, nested subscriptions, any-typed API
responses, business logic in components instead of services, default
change detection where OnPush is the standard. The skill may propose
the standard Angular set and ask for project-specific additions.

---

## Section 8 — Documentation Requirements

**Discoverable:** Partially. JSDoc/Compodoc usage is visible in code.

Code documentation expectations (JSDoc on public APIs and services,
Compodoc if used) and project documentation expectations (README, env
config, run/build instructions). Fill what is observable; ask for team
expectations not visible in code.

---

## What a filled section looks like

```markdown
## Repository Overview

- Purpose: Web portal for clinic receptionists to manage owners, pets,
  and appointments. Internal staff-facing application.
- Tech Stack: Angular 17 (standalone components), RxJS, signals for
  local state, Angular Material, SCSS, Jasmine/Karma, ESLint + Prettier.
- Architecture: Standalone components, lazy-loaded feature routes,
  core/shared split, services-with-signals for state (no NgRx).
```

## What an unfilled section looks like

```markdown
## Unique Patterns For This Project

[TODO — MUST COMPLETE]: Project-specific rules an AI would not infer
from code — i18n strategy, feature flag mechanism, accessibility
baseline (WCAG level), locale/date handling. The developer did not know
these at generation time. Fill before relying on this file — missing
project rules are the most common cause of AI-generated defects.
```

---

## Not part of this file

Naming conventions, code style, folder structure, and test rules are
**path-specific rules**. They are maintained centrally in the
copilot-toolkit repository and copied into a repo's
`.github/instructions/` folder as a separate step. This skill does not
generate them. Keeping them separate keeps shared rules consistent
across all Angular repos.
