---
name: review-angular-code
description: Review Angular code changes for best practices, modern control flow, null safety, RxJS patterns, NgRx state management, i18n, error handling, security, performance, and code quality. Use this skill whenever the user asks to review Angular code, check a component, audit recent changes, validate a pull request, or verify code quality on .ts, .html, or Angular template files. Trigger even when the user says things like "review my changes", "check this component", "look at my code", "PR review", or mentions reviewing any Angular file.
---

# Angular Code Review

**Original Author: MANITEJA PUSULURI**

Review recent Angular code changes. Go file by file and check for the issues listed below.

For every issue found:
- Report **file name and line number**
- Suggest the **exact fix inline**
- Flag **CRITICAL** issues separately at the top of the review

---

## Angular Best Practices

- Unsubscribed Observables (missing `takeUntil`, `DestroyRef`, or `async` pipe)
- Missing `ngOnDestroy` for cleanup
- Direct DOM manipulation instead of `Renderer2`
- Business logic inside components instead of services
- Missing `OnPush` change detection on presentational components
- Avoid empty lifecycle hooks
- No logic inside constructors — use `ngOnInit` instead

## Modern Angular Control Flow (`@for`, `@if`, `@switch`)

- `@for` must always have a `track` expression (`track item.id` or `track index`)
- `@for` missing `@empty` block for empty array handling
- `@if` used without `@else` for user-facing empty states
- Avoid old `*ngIf` and `*ngFor` — migrate to `@if` and `@for` (suggest: `ng generate @angular/core:control-flow`)
- `@switch` missing `@default` block
- Avoid complex expressions inside `@if` (move to component variable or use `@let`)
- Avoid nested `@for` without `track` on both levels
- `@for` used without typing the item (should match interface)
- Heavy function calls inside `@if` condition (causes re-evaluation on every CD)

## Common `@for` Mistakes

- `track $index` used instead of `track item.id` (causes full re-render)
- No `@empty` block when list could be empty in production
- Nested `@for` without `trackBy` on inner loop

## Common `@if` Mistakes

- Null check missing before accessing nested property in `@if`
- `@if` condition duplicated in template instead of using local variable (use `@let` in Angular 18+)
- Async data not using `(data$ | async) as data` pattern with `@if`

## Null & Undefined Checks

- Missing null checks before accessing object properties
- Missing optional chaining (`?.`) where object could be null
- Missing nullish coalescing (`??`) for default values
- Unhandled null returns from HTTP calls or service methods
- Missing safe navigation operator (`?.`) in templates
- Array not checked for empty before looping

## RxJS

- Nested subscriptions that should use `switchMap` or `mergeMap`
- Subjects not being completed on destroy
- Manual subscriptions where `async` pipe would be cleaner
- Missing `catchError` in HTTP observable chains
- Missing `finalize` for loading state cleanup
- No error handling in `subscribe()` error callback

## Error Handling

- HTTP errors not caught with `catchError`
- No global error handler (`ErrorHandler`) for unexpected errors
- Missing try/catch in async functions
- User not notified on API failure
- `console.log` left in production code (use proper logger)
- No fallback UI for failed data loads

## NgRx State Management

- Actions not following `[Source] Event` naming convention
- Business logic inside components instead of Effects
- Selectors not using `createSelector` for memoization
- Direct store mutation instead of immutable state updates
- Missing error actions for failed Effects
- Dispatching multiple actions where one would do
- Selectors not reused across components
- Missing loading/error state in store for async operations

## i18n / Translations

- Hardcoded English text in templates instead of translation keys
- Missing `i18n` attribute on user-facing elements
- Dynamic strings not using `$localize` or translate pipe
- Date, currency, number not using Angular locale pipes
- Missing translation keys for error messages
- New UI text added without adding translation key

## TypeScript

- Use of `any` type instead of proper interfaces/types
- Missing null checks or optional chaining
- Interfaces not defined for API response models
- Enums used instead of const objects (worse tree shaking)
- Missing return types on public methods

## Security

- Unsafe `innerHTML` usage without `DomSanitizer`
- Hardcoded API URLs (use environment files)
- Sensitive data stored in `localStorage`
- Missing auth guard on new routes
- API tokens or secrets in code

## Performance

- Large lists missing `track` in `@for`
- Heavy logic running inside templates
- Missing lazy loading on new feature modules/routes
- Images missing `width`/`height` causing layout shift
- Unnecessary API calls on every component load
- Heavy function calls inside `@if` or `@for` conditions

## Code Quality

- Magic numbers/strings not extracted as constants
- Functions longer than 20 lines (split them)
- Repeated code that should be a shared service or pipe
- Component doing too many things (split it)
- Dead code or unused imports left in

---

## Output Format

1. **CRITICAL issues** — listed at the top with file:line and fix
2. **Issues by file** — grouped per file, with line numbers and inline fix suggestions
3. **Summary** — count of issues by category
