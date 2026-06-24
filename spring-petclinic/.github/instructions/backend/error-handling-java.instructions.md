---
applyTo: "src/main/java/**/*.java"
---

# Error Handling — Java / Spring Boot

Stack-specific error-handling rules. Compounds with `owasp-java.instructions.md` (A05, A09) and `hipaa-guardrails.instructions.md` (no PHI in error responses).

## Exception hierarchy

Use a layered hierarchy. Do not throw raw `RuntimeException` or `Exception` from business code.

```
RuntimeException
└── ApplicationException (base — abstract)
    ├── BusinessException        — expected, recoverable, user-facing (4xx)
    │   ├── ValidationException
    │   ├── NotFoundException
    │   ├── ConflictException
    │   └── UnauthorizedException
    └── TechnicalException        — unexpected, infra-related (5xx)
        ├── DownstreamUnavailableException
        ├── DataAccessException (or wrap Spring's)
        └── IntegrationException
```

- Every custom exception must extend one of the two branches.
- 4xx-class exceptions map to 4xx responses; 5xx-class to 5xx. The `@ControllerAdvice` enforces this — never set status manually in business code.

## What never to do

- ❌ Catch `Exception` or `Throwable` broadly. Catch the narrowest type that makes sense.
- ❌ Catch-and-ignore: `catch (Exception e) { /* silent */ }` — always log or rethrow.
- ❌ Catch-and-rethrow as `RuntimeException(e.getMessage())` — loses the cause. Use `throw new MyException("...", e);` with the cause preserved.
- ❌ Log the same exception at every layer — log once at `@ControllerAdvice`.
- ❌ Return `null` to signal failure when an exception is the right tool.
- ❌ Use exceptions for control flow (e.g., `try { parseInt } catch` in a hot loop) — performance and readability cost.

## Centralised handling — @ControllerAdvice

Every Spring service must have exactly one `@RestControllerAdvice` class as the central error mapper. New controllers do not implement their own try/catch for cross-cutting cases.

Responsibilities:

1. Map exception type → HTTP status
2. Build the response body (see RFC 7807 below)
3. Log the exception (once)
4. Sanitise — never leak stack trace, internal class names, SQL, or PHI to the client

## Response body — RFC 7807 Problem Details

All error responses use `application/problem+json` with this schema:

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed",
  "status": 400,
  "detail": "memberId must not be blank",
  "instance": "/api/v1/claims/abc-123",
  "correlationId": "8a3b1c2d-4e5f-6789-abcd-ef0123456789",
  "errors": [
    { "field": "memberId", "code": "NOT_BLANK", "message": "must not be blank" }
  ]
}
```

Rules:
- `correlationId` is mandatory on every error response.
- `detail` is a short, sanitised message safe for the client. Never include PHI, stack traces, SQL, file paths, or internal class names.
- `errors[]` is optional, for field-level validation results only.
- Never include `exception`, `cause`, `trace`, or `path` fields with internal info.

## Status code mapping

| Exception | HTTP | Notes |
|---|---|---|
| `ValidationException`, Spring `MethodArgumentNotValidException` | 400 | Include `errors[]` |
| `UnauthorizedException`, Spring `AuthenticationException` | 401 | Never reveal whether user exists |
| Spring `AccessDeniedException` | 403 |  |
| `NotFoundException` | 404 |  |
| HTTP method mismatch | 405 |  |
| `ConflictException` (optimistic lock, duplicate) | 409 |  |
| Unprocessable business rule | 422 |  |
| Rate limit | 429 | Include `Retry-After` |
| Any other `BusinessException` | 400 |  |
| `DownstreamUnavailableException` | 503 | Include `Retry-After` if known |
| Any uncaught `Exception` | 500 | Generic message; log full trace server-side |

## Validation

- Use Bean Validation (`@Valid`, `@NotBlank`, `@Size`, etc.) on controller DTOs.
- Custom validators extend `ConstraintValidator`. Never validate by writing imperative checks in the controller method — moves error handling out of the centralised mapper.
- Validation errors are 400 with `errors[]` populated.

## Retry and circuit-breaker

- Use Spring Retry or Resilience4j; never write raw `for (i=0; i<3; i++) try {...}` loops.
- Retry only on `TechnicalException` subclasses, never on `BusinessException` — business errors don't get better by retrying.
- Open circuit breakers on downstream failures; do not let a failing downstream cascade into thread pool exhaustion.

## Async / reactive

- For `@Async` methods returning `CompletableFuture`, exceptions must be handled in `.exceptionally()` or `.handle()`. Never let exceptions escape an async boundary unhandled — they get swallowed.
- For Reactor (`Mono`/`Flux`), use `.onErrorMap()` to convert technical exceptions to the application hierarchy before they reach the controller.

## Refusal pattern

> ⚠️ Error-handling guardrail: <one-line rule>. Suggested alternative: <code>.
