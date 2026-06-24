---
name: build-copilot-instructions-mobile-frontend
description: >
  Generates a single repo-wide GitHub Copilot instructions file
  (.github/copilot-instructions.md) for an Ionic + Angular mobile
  application repository. Use this when a developer asks to set up
  Copilot instructions, onboard a mobile repo to Copilot, or create
  copilot-instructions for an Ionic project. The skill reads the
  repository first (package.json, ionic.config.json,
  capacitor.config.ts, angular.json, src/app structure, existing
  pages/components/services, installed Capacitor plugins) to fill in
  what it can discover, asks the developer only for gaps it cannot find,
  and marks anything still unknown with a loud [TODO — MUST COMPLETE]
  marker rather than guessing. This skill does NOT create path-specific
  rules files — rules are managed separately in the copilot-toolkit
  repository and copied into a repo independently. This skill is for
  Ionic + Angular mobile apps; for plain Angular web apps use
  build-copilot-instructions-angular-frontend; for Spring Boot backends use
  build-copilot-instructions-backend.
---

# Build Copilot Instructions — Ionic + Angular Mobile

Generates one file: `.github/copilot-instructions.md` — the repo-wide
Copilot instructions for an Ionic + Angular mobile application.

This skill produces the repo-wide instructions file only. Path-specific
rules files (naming conventions, testing conventions, page/component
rules, etc.) are NOT created by this skill. Those are maintained
centrally in the `copilot-toolkit` repository and copied into a repo's
`.github/instructions/` folder as a separate activity. Keeping the two
concerns separate means shared rules stay consistent across all mobile
repos instead of being regenerated differently each time.

This skill is for **Ionic + Angular mobile applications**. For plain
Angular web apps use `build-copilot-instructions-frontend`; for Spring
Boot backends use `build-copilot-instructions-backend`.

---

## What goes in copilot-instructions.md

Only **cross-cutting, repo-wide** content, true regardless of which file
Copilot is working on:

- Repository overview (purpose, tech stack, target platforms,
  architecture)
- Application structure (Ionic page/tab/routing organisation, feature
  modules, state management approach)
- Native integration conventions (Capacitor plugin usage, permission
  handling, platform-specific code paths, offline/storage strategy)
- API integration conventions (HTTP client usage, error handling,
  interceptors, environment configuration, network-state handling)
- Security guidelines (secure storage, token handling on device, XSS,
  deep-link validation)
- Design patterns the codebase actually uses (smart/dumb components,
  Ionic lifecycle usage, reactive forms, RxJS patterns)
- Unique project patterns (i18n, accessibility, platform theming,
  offline-first behaviour, date/locale handling)
- What to avoid (Ionic, Angular, and project anti-patterns)
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
   (dependencies, Ionic/Angular/Capacitor versions, installed plugins,
   architecture, observed patterns) is filled from the repo, not asked.
2. **Ask only for genuine gaps.** Things the repo cannot reveal (project
   purpose, target platforms if not in config, business rules, security
   intent, offline strategy intent, unique patterns) are asked — one
   question at a time.
3. **Mark unknowns loudly, never guess.** If the developer does not know
   an answer, write `[TODO — MUST COMPLETE]: <what is needed and why it
   matters>` in that section. A wrong instruction is worse than a
   visibly missing one.

---

## Workflow

### 1. Read the repository

Read these before asking anything:

- **package.json** — Ionic version (`@ionic/angular`), Angular version,
  Capacitor version (`@capacitor/core`), installed Capacitor/Cordova
  plugins (camera, geolocation, filesystem, preferences, push,
  secure-storage), state management library, test framework, RxJS,
  lint/format tooling, build scripts.
- **ionic.config.json** — project type, integrations.
- **capacitor.config.ts / capacitor.config.json** — app id, target
  platforms (ios/android/web), plugin configuration, server config.
- **angular.json** — build targets, style preprocessor, environments,
  budgets.
- **src/app structure** — page organisation (tabs/routing), standalone
  vs NgModule, lazy-loaded routes, shared/core split.
- **Representative code** — sample a page component, a shared component,
  a service, the HTTP layer, an interceptor, a route guard, and any
  service that wraps a Capacitor plugin. Observe: Ionic lifecycle hook
  usage (`ionViewWillEnter` etc.) vs Angular hooks, change detection
  strategy, reactive vs template forms, RxJS subscription management,
  platform detection usage (`Platform` service / `Capacitor.getPlatform`),
  permission request patterns, storage/offline patterns.
- **Existing tests** — `.spec.ts` files for test framework and any
  Capacitor plugin mocking (informs "patterns" and "what to avoid"
  sections only — this skill does not generate the test rules file).
- **Existing instructions** — if `.github/copilot-instructions.md`
  already exists, read it. Ask the developer whether to refine it or
  regenerate. Do not overwrite blindly.

State a brief summary of what was discovered so the developer can
correct a wrong inference before generation.

### 2. Identify gaps and ask — one question at a time

For each section of the template (see
`assets/copilot-instructions-mobile-template.md`):

- **Discoverable and found** — fill from the repo. No question.
- **Discoverable but ambiguous** — code shows mixed patterns (e.g. some
  Ionic lifecycle, some Angular lifecycle; some standalone, some
  NgModule). Ask which is the standard going forward, citing the
  observed split.
- **Not discoverable** — ask. Typically: project purpose and domain,
  target platforms if not in capacitor config, offline-first
  expectations, security/secure-storage strategy, accessibility
  baseline, unique patterns, documentation expectations.

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
`assets/copilot-instructions-mobile-template.md` for structure and
section order. Fill every section from the repo, a developer answer, or
a `[TODO — MUST COMPLETE]` marker.

### 5. Self-check before presenting

- [ ] File contains no naming/code-style/folder-structure/test rules —
      those are separate rules files this skill does not produce
- [ ] Every section has real repo content, a developer answer, or a
      `[TODO — MUST COMPLETE]` marker — nothing silently blank, nothing
      guessed
- [ ] Ionic, Angular, and Capacitor versions match what was actually in
      package.json
- [ ] Target platforms match capacitor config (do not claim iOS if only
      android+web are configured)
- [ ] Only Capacitor/Cordova plugins actually installed are referenced
      (do not invent plugin usage)
- [ ] Design patterns and lifecycle usage reflect what is really in the
      repo
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
- **Invented native capability.** Never reference a Capacitor/Cordova
  plugin, permission, or platform that is not actually present in
  package.json / capacitor config.
- **Naming, code style, folder structure, or test rules.** These are
  path-specific rules maintained in copilot-toolkit, not generated here.
- **Rules already enforced by tooling.** Skip what ESLint, Prettier, or
  the Angular compiler enforces.
- **Long prose.** Each instruction is a short statement. Add a reason
  only when it changes Copilot's behaviour in edge cases (e.g. "wrap all
  Capacitor plugin calls in a platform check — calling native plugins on
  the web build throws and the app supports a web target").

---

## Reference

- `assets/copilot-instructions-mobile-template.md` — the target
  structure for the repo-wide file, with per-section guidance on what is
  discoverable, what to ask, and what a filled vs `[TODO — MUST
  COMPLETE]` section looks like.
