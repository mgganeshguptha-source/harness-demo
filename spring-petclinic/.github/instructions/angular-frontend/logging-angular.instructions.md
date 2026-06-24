---
applyTo: "src/app/**/*.ts"
---

# Logging — Angular Web

Stack-specific logging rules for Angular. Follows the shared contract in `logging-standards.instructions.md`. Compounds with `hipaa-guardrails.instructions.md`.

## Browser `console` discipline

- `console.log` in production code is forbidden. CI lint rule should enforce this.
- Acceptable in production:
  - `console.warn` and `console.error` for genuinely abnormal client-side conditions, **after PHI scrubbing**
  - Nothing else
- Acceptable in development only (must be removed before merge):
  - `console.log`, `console.debug`, `console.info`, `console.trace`, `console.table`
- Never log objects directly that may contain PHI — `console.log(member)` dumps the whole object to devtools. Log a non-PHI correlationId instead.
- Strip all `console.*` from production builds via Angular build optimizer or a Terser `drop_console: true` config.

## Logger abstraction

- Use an injectable `LoggerService` rather than raw `console.*` calls scattered through components. Centralisation lets you swap implementations and apply scrubbing in one place.
- Service shape:
  ```ts
  log(level: 'info'|'warn'|'error', message: string, context?: Record<string, unknown>): void
  ```
- The service routes to `console.*` in dev and to the remote sink (Sentry / Datadog RUM) in prod.

## Remote logging (Sentry / Datadog RUM / similar)

- Initialise the SDK in `main.ts` with `environment` config — never hardcode DSN.
- **`beforeSend` / `beforeSendTransaction` hook is mandatory** and must:
  1. Scrub PHI from `event.request`, `event.user`, `event.extra`, and `event.breadcrumbs`.
  2. Strip query strings from URLs that may carry PHI (`memberId=...`).
  3. Drop the event if it contains an Authorization header or token.
- `tracesSampleRate` and `replaysSessionSampleRate` for session replay: only enable with explicit privacy review. Session replay can capture PHI on forms.
- Configure `denyUrls` to drop noise from browser extensions, ad blockers, etc.

## HTTP interceptor logging

- Log request entry and exit at the interceptor level — never log per-call in services.
- Log: method, sanitised path (no PHI in query string), status, durationMs, correlationId.
- **Do NOT log request or response bodies** in production. They may contain PHI.
- Strip `Authorization` and `Cookie` from any header object logged.

## Correlation ID

- HTTP interceptor mints a UUID v4 if no inbound correlation ID exists (e.g., user-initiated action) and attaches it to every outgoing request as `X-Correlation-Id`.
- Reuse the same ID across all requests within a single user action (e.g., a multi-call form submit).
- Include the correlation ID in any remote-logged error.

## Error tracking

- Implement a custom `ErrorHandler` (see `error-handling-angular.instructions.md`) that routes uncaught errors to the LoggerService.
- Tag every error with `correlationId`, `route`, `userId` (hashed).
- Never tag with raw PHI. Sentry tags are searchable and persistent — once PHI lands there, it's hard to purge.

## What never to log (Angular-specific reminders)

- `localStorage` / `sessionStorage` contents — may contain tokens
- Full route params — may contain memberId or claimId in path
- Form state — may contain PHI mid-typing
- Response objects from member/claim endpoints — log only status + correlationId
- `JWT` payloads decoded in the browser — may contain identifiers
- Service worker `fetch` events — same rules apply

## Test code

- Tests can use `console.log` freely. They run only in CI/local. Production guards do not apply.

## Refusal pattern

> ⚠️ Angular logging guardrail: <one-line rule>. Suggested alternative: <code>.
