---
name: build-copilot-instructions-angular-frontend
description: >
  Generates a single repo-wide GitHub Copilot instructions file
  (.github/copilot-instructions.md) for an Angular web application
  repository. Use this when a developer asks to set up Copilot
  instructions, onboard a frontend repo to Copilot, or create
  copilot-instructions for an Angular project. The skill reads the
  repository first (package.json, angular.json, tsconfig, src/app
  structure, existing components/services) to fill in what it can
  discover, asks the developer only for gaps it cannot find, and marks
  anything still unknown with a loud [TODO — MUST COMPLETE] marker rather
  than guessing. This skill does NOT create path-specific rules files —
  rules are managed separately in the copilot-toolkit repository and
  copied into a repo independently. This skill is for plain Angular web
  apps; for Ionic + Angular mobile apps use
  build-copilot-instructions-mobile-frontend; for Spring Boot backends use
  build-copilot-instructions-backend.
---

# Build Copilot Instructions — Angular Web

Generates one file: `.github/copilot-instructions.md` — the repo-wide
Copilot instructions for an Angular web application.

This skill produces the repo-wide instructions file only. Path-specific
rules files (naming conventions, testing conventions, component rules,
etc.) are NOT created by this skill. Those are maintained centrally in
the `copilot-toolkit` repository and copied into a repo's
`.github/instructions/` folder as a separate activity. Keeping the two
concerns separate means shared rules stay consistent across all Angular
repos instead of being regenerated differently each time.

This skill is for **plain Angular web applications**. For Ionic + Angular
mobile apps use `build-copilot-instructions-mobile`; for Spring Boot
backends use `build-copilot-instructions-backend`.

---

## What goes in copilot-instructions.md

Only **cross-cutting, repo-wide** content, true regardless of which file
Copilot is working on:

- Repository overview (purpose, tech stack, architecture)
- Application structure (feature modules, routing strategy, state
  management approach)
- API integration conventions (HTTP client usage, error handling,
  interceptors, environment configuration)
- Security guidelines (XSS prevention, auth token handling, sanitization)
- Design patterns the codebase actually uses (smart/dumb components,
  facade, reactive forms vs template forms, RxJS patterns)
- Unique project patterns (i18n, feature flags, accessibility baseline,
  date/locale handling)
- What to avoid (Angular and project anti-patterns)
- Documentation requirements

It must NOT contain naming conventions, code style rules, folder
structure rules, or test framework rules. Those are path-specific rules,
maintained in the copilot-toolkit repository, applied via separate
`.github/instructions/*.instructions.md` files that this skill does not
generate.

---

## Core principle — discover, don't guess

The value of this skill is that it reads the actual repository and fills
the instructions from what is really there, not a generic template the
developer must rewrite. Three rules:

1. **Read before asking.** Anything discoverable from the repo
   (dependencies, Angular version, architecture, observed patterns) is
   filled from the repo, not asked.
2. **Ask only for genuine gaps.** Things the repo cannot reveal (project
   purpose, business rules, security intent, unique patterns) are asked
   — one question at a time.
3. **Mark unknowns loudly, never guess.** If the developer does not know
   an answer, write `[TODO — MUST COMPLETE]: <what is needed and why it
   matters>` in that section. A wrong instruction is worse than a
   visibly missing one.

---

## Workflow

### 1. Read the repository

Read these before asking anything:

- **package.json** — Angular version, key dependencies (RxJS, NgRx /
  Akita / signals for state, Angular Material / PrimeNG / Tailwind for
  UI, Jasmine/Karma or Jest for tests, ESLint, Prettier), build scripts.
- **angular.json** — project structure, build targets, style
  preprocessor (SCSS/CSS/Less), budgets, environments.
- **tsconfig** — strict mode settings, path aliases.
- **src/app structure** — module organisation (feature modules vs
  standalone components), routing setup, lazy-loaded routes.
- **Representative code** — sample a feature component, a shared
  component, a service, the HTTP layer, an interceptor, a route guard.
  Observe: standalone vs NgModule, change detection strategy
  (OnPush usage), reactive vs template forms, RxJS subscription
  management (async pipe vs manual subscribe/unsubscribe), state
  management approach.
- **Existing tests** — `.spec.ts` files to understand test framework and
  TestBed usage (informs the "patterns" and "what to avoid" sections
  only — this skill does not generate the test rules file).
- **Existing instructions** — if `.github/copilot-instructions.md`
  already exists, read it. Ask the developer whether to refine it or
  regenerate. Do not overwrite blindly.

State a brief summary of what was discovered so the developer can
correct a wrong inference before generation.

### 2. Identify gaps and ask — one question at a time

For each section of the template (see
`assets/copilot-instructions-frontend-template.md`):

- **Discoverable and found** — fill from the repo. No question.
- **Discoverable but ambiguous** — code shows mixed patterns (e.g. some
  standalone components, some NgModule; some OnPush, some default). Ask
  which is the standard going forward, citing the observed split.
- **Not discoverable** — ask. Typically: project purpose and domain,
  security specifics, unique patterns, accessibility baseline,
  documentation expectations.

One question per turn, each with a concrete example answer. Do not batch.

### 3. Handle unknowns

If the developer does not know, or says skip: write
`[TODO — MUST COMPLETE]: <specific description and why it matters>` in
that section. Do not substitute a generic default. Continue to the next
gap.

If more than five sections become `[TODO — MUST COMPLETE]`, tell the
developer the file will be substantially incomplete and recommend
gathering the missing detail with the team before relying on it.

### 4. Generate the file

Write `.github/copilot-instructions.md` using
`assets/copilot-instructions-frontend-template.md` for structure and
section order. Fill every section from the repo, a developer answer, or
a `[TODO — MUST COMPLETE]` marker.

### 5. Self-check before presenting

- [ ] File contains no naming/code-style/folder-structure/test rules —
      those are separate rules files this skill does not produce
- [ ] Every section has real repo content, a developer answer, or a
      `[TODO — MUST COMPLETE]` marker — nothing silently blank, nothing
      guessed
- [ ] Angular version and key libraries match what was actually in
      package.json
- [ ] Design patterns listed are ones the codebase actually uses
      (do not claim NgRx if there is no NgRx)
- [ ] State management approach reflects what is really in the repo
- [ ] `grep "MUST COMPLETE"` would surface every unfilled section

### 6. Present and instruct

Show the file. Tell the developer:

> Generated .github/copilot-instructions.md
>
> Search for MUST COMPLETE and fill every marked section before relying
> on it.
>
> Note: path-specific rules (naming, code style, testing) are not part
> of this file. Copy the relevant rules files from the copilot-toolkit
> repository into .github/instructions/ as a separate step.

---

## What never goes in this file

- **Guessed conventions.** Not in the repo and not known by the
  developer means `[TODO — MUST COMPLETE]`, not a default.
- **Naming, code style, folder structure, or test rules.** These are
  path-specific rules maintained in copilot-toolkit, not generated here.
- **Rules already enforced by tooling.** Skip what ESLint, Prettier, or
  the Angular compiler enforces.
- **Long prose.** Each instruction is a short statement. Add a reason
  only when it changes Copilot's behaviour in edge cases (e.g. "use
  OnPush — the app relies on immutable state updates and default change
  detection causes performance regressions in the data grid").

---

## Reference

- `assets/copilot-instructions-frontend-template.md` — the target
  structure for the repo-wide file, with per-section guidance on what is
  discoverable, what to ask, and what a filled vs `[TODO — MUST
  COMPLETE]` section looks like.
