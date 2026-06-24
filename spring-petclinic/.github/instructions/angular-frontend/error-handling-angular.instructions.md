---
applyTo: "src/app/**/*.ts"
---

# Error Handling — Angular Web

Stack-specific error-handling rules for Angular. Compounds with `logging-angular.instructions.md` and `hipaa-guardrails.instructions.md`.

## Three layers of error handling

| Layer | Tool | Responsibility |
|---|---|---|
| HTTP errors | `HttpInterceptor` | Map HTTP responses to typed app errors, retry idempotent calls, refresh tokens on 401 |
| Component / async errors | RxJS operators | Local recovery, user-facing display |
| Uncaught errors | Custom `ErrorHandler` | Last-resort capture, log to remote sink, show fallback UI |

All three layers must coexist. Components do not implement HTTP-error mapping locally — that belongs in the interceptor.

## HTTP error interceptor

- One central `HttpInterceptor` maps the RFC 7807 `application/problem+json` body to typed app errors:
  ```ts
  class AppError { code: string; title: string; detail: string; correlationId: string; }
  class ValidationAppError extends AppError { fieldErrors: FieldError[]; }
  class UnauthorizedAppError extends AppError {}
  // etc.
  ```
- Status code mapping:
  - 400 → `ValidationAppError` if `errors[]` present, else `BusinessAppError`
  - 401 → trigger token refresh; if already retried, redirect to login
  - 403 → `ForbiddenAppError` — show "no access" UI, never silently swallow
  - 404 → `NotFoundAppError`
  - 409 → `ConflictAppError` — usually means refresh-and-retry workflow
  - 429 → `RateLimitedAppError` — display retry-after info from header
  - 5xx → `ServerAppError` — generic "something went wrong" UI
  - Network error / timeout → `NetworkAppError`
- The interceptor rethrows the typed error via `throwError()`. Components subscribe and handle.

## Token refresh

- Single-flight: if a 401 fires while a refresh is already in progress, queue requests on the same refresh observable. Never fire N parallel refreshes.
- Refresh failure → log out and route to login. Do not retry indefinitely.

## Retry rules

- Retry only **idempotent** methods (GET, PUT, DELETE) and only on **network errors** or **503/504**.
- Never retry POST automatically — duplicate creates. If POST retry is needed, the server must support `Idempotency-Key` (see backend api-design).
- Max 2 retries with exponential backoff (e.g., 500ms, 1500ms). Beyond that, surface to the user.
- Use RxJS `retryWhen` or `retry({count, delay, resetOnSuccess})`.

## Component-level handling

- Components use `.pipe(catchError(...))` to handle expected errors locally (validation, conflict).
- Unexpected errors propagate to the global `ErrorHandler` — do not silently catch and move on.
- Never `subscribe(() => ..., () => {})` with an empty error handler. That swallows errors without a trace.
- Standard pattern:
  ```ts
  this.service.load().pipe(
    catchError(err => {
      if (err instanceof ValidationAppError) { this.fieldErrors = err.fieldErrors; return EMPTY; }
      throw err; // bubble up to ErrorHandler
    })
  ).subscribe(...);
  ```

## Global `ErrorHandler`

- Provide a custom `ErrorHandler` in `app.config.ts` / `app.module.ts`.
- Responsibilities:
  1. Log to the remote sink via `LoggerService` (with PHI scrubbing — see `logging-angular.instructions.md`)
  2. Show a user-friendly error UI (toast / snackbar / modal)
  3. Never re-throw — that crashes Angular's change detection
- Never log raw `error.message` to the user — may contain technical detail or PHI from a poorly-sanitised backend.

## User-facing messages

- Always show a message tied to the `correlationId` so users can quote it to support:
  > "Something went wrong. Reference: 8a3b1c2d. Please try again or contact support."
- Never show raw exception messages, stack traces, or backend technical detail.
- Map known error codes to friendly translations via i18n keys.
- For validation errors, render field-level messages next to the field, not in a global banner.

## Form errors

- Reactive Forms with `Validators` for client-side checks. The backend's RFC 7807 `errors[]` populates server-side validation:
  ```ts
  err.fieldErrors.forEach(fe => form.get(fe.field)?.setErrors({ server: fe.message }));
  ```
- Show client errors only after the user has interacted with the field (`touched && invalid`).

## What never to do

- ❌ `try { await ... } catch (e) {}` with empty catch — swallows the error
- ❌ `subscribe(success, () => {})` — same problem
- ❌ Log the error to console and continue — the global ErrorHandler should decide
- ❌ Show `alert(error.message)` — breaks UX, may leak detail
- ❌ Different error handling per component for the same error type — centralise via the interceptor
- ❌ Catch `Error` and rethrow `new Error(e.message)` — loses the stack and the typed error

## Refusal pattern

> ⚠️ Angular error-handling guardrail: <one-line rule>. Suggested alternative: <code>.
