---
applyTo: "**"
---

# Logging Standards — Shared (Repo-Wide)

This file defines the **cross-stack logging contract** that backend, web, and mobile must all honour. Stack-specific implementation rules live in `backend/logging-java.instructions.md` and `angular-frontend/logging-angular.instructions.md`.

## Correlation ID contract (mandatory across all stacks)

- **Header name:** `X-Correlation-Id`
- **Format:** UUID v4, lowercase, no braces (e.g., `8a3b1c2d-4e5f-6789-abcd-ef0123456789`)
- **Origin:** the first system that receives an external request mints the ID. Every downstream call propagates it.
- **Propagation rule:** every outbound HTTP/gRPC/message call must include the inbound `X-Correlation-Id`. Never drop it, never replace it mid-chain.
- **Logging rule:** every log line must include the correlation ID in a field named `correlationId`.
- **Distributed tracing:** if OpenTelemetry is in use, the correlation ID is in addition to (not in place of) `traceId` and `spanId`. All three fields appear in every log line.

## Log levels (consistent across stacks)

| Level | Use for | Do NOT use for |
|---|---|---|
| ERROR | Unrecoverable failure, alarmable | Expected validation errors |
| WARN | Recoverable / degraded behaviour, retried calls | Routine business outcomes |
| INFO | Lifecycle events, request entry/exit, business milestones | Per-field debug detail |
| DEBUG | Detailed flow for troubleshooting, disabled in prod by default | Always-on diagnostics |
| TRACE | Most-verbose; rarely used; never in production | Anything you'd want to see weekly |

## What must never be logged (anywhere, any stack)

- PHI of any kind (see `hipaa-guardrails.instructions.md` for the 18 identifiers)
- Passwords, tokens, API keys, OAuth codes, OTPs, recovery codes, session IDs
- Full HTTP request or response bodies for endpoints that handle PHI
- Stack traces in user-facing error responses (server-side log is fine)
- Full SQL with parameter values when parameters may be PHI

## What every log line must include

Mandatory fields, regardless of stack:

| Field | Source |
|---|---|
| `timestamp` | ISO-8601 with milliseconds + timezone |
| `level` | ERROR / WARN / INFO / DEBUG / TRACE |
| `service` | logical service/app name |
| `correlationId` | from `X-Correlation-Id` |
| `message` | short human-readable summary |

Recommended additional fields when available: `traceId`, `spanId`, `userId` (hashed, never raw), `requestPath`, `httpMethod`, `httpStatus`, `durationMs`.

## Log format

Production: **structured JSON**, one object per line. Never multi-line. Never free-text-only.

Local development: pretty-printed is acceptable, but the same field set must be present.

## Refusal pattern

> ⚠️ Logging guardrail: <one-line rule>. Suggested alternative: <code>.
