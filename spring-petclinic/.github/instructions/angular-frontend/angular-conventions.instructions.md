---
applyTo: "src/app/**/*.ts"
---

# Angular Source Conventions (Web)

## Naming Conventions

- Components: `PascalCase` class, `kebab-case` selector with app prefix
  (e.g. `app-owner-search`), files `owner-search.component.ts`
- Services: `PascalCase` with `Service` suffix, file
  `owner.service.ts`
- Interfaces/models: `PascalCase`, no `I` prefix
- Methods and variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Observables: suffix with `$` (e.g. `owners$`)

## Code Style

- Use constructor injection for dependencies; mark them `private` (or
  `private readonly`).
- Prefer the `async` pipe over manual `subscribe`. If you must
  subscribe manually, unsubscribe (takeUntil, or `DestroyRef`/
  `takeUntilDestroyed`).
- Never nest subscriptions — use RxJS operators (`switchMap`,
  `mergeMap`, etc.).
- Type all HTTP responses. Do not use `any` for API payloads.
- Keep components thin — data shaping and business logic belong in
  services, not components.
- Do not put logic in templates beyond simple expressions.
- Follow the project's existing component model consistently (standalone
  vs NgModule) — do not mix without reason.
- Do not disable Angular sanitization (`bypassSecurityTrust*`) without
  an explicit, justified reason.

## Structure

- Group by feature. Shared, reusable pieces go in a shared module/folder;
  app-wide singletons in core.
- Lazy-load feature routes where the project does so.
- Keep one component/service per file.