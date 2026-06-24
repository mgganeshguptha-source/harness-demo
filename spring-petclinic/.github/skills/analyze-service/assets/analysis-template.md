# Microservice Analysis Document — Template

This is the structure the `analyze-microservice` skill fills. Every
section below must appear in the output in this order. Fill each section
from actual code and configuration. Where information cannot be found,
write `_Not found in codebase — confirm with team_` — do not infer,
guess, or substitute a typical default.

---

## 1. Overview

- **Service Name:**
- **Purpose:** _(one paragraph — what business capability does this service own?)_
- **Technology Stack:** _(language, framework, runtime version if detectable)_
- **Repository Path:**
- **Owner / Team:**
- **Last Analysed:** _(date of generation, YYMMDD)_

---

## 2. Endpoints

For **every** exposed endpoint (REST, gRPC, GraphQL, event consumer,
scheduled job), produce a sub-section in this exact shape:

### 2.x `<HTTP_METHOD> <PATH>` — `<Short Title>`

| Field | Detail |
|---|---|
| **Method** | GET / POST / PUT / PATCH / DELETE / EVENT |
| **Path / Topic** | Full path or queue/topic name |
| **Description** | What this endpoint does |
| **Auth / Access Control** | JWT, API key, role required, public, etc. |
| **Rate Limiting** | If present |

**Request Payload**
```json
{
  "field": "type — description — required/optional"
}
```

**Response Payloads**

| Status | Condition | Body |
|---|---|---|
| 200/201 | Success | `{ ... }` |
| 400 | Validation failure | `{ "error": "...", "details": [...] }` |
| 401 | Unauthenticated | `{ "error": "Unauthorized" }` |
| 403 | Forbidden | `{ "error": "Forbidden" }` |
| 404 | Not found | `{ "error": "Not found" }` |
| 409 | Conflict | `{ "error": "..." }` |
| 422 | Business rule violation | `{ "error": "..." }` |
| 500 | Server error | `{ "error": "Internal server error" }` |
| 503 | Downstream unavailable | `{ "error": "..." }` |

**Dependencies Called by This Endpoint**

| # | Dependency | Type | Endpoint / Method Called | Purpose | Sync / Async |
|---|---|---|---|---|---|
| 1 | `<ServiceName>` | HTTP / gRPC / DB / Cache / Queue | `POST /path` | Why it's called | Sync |

**Special Notes**
- Idempotency guarantees (if any)
- Retry / circuit-breaker behaviour
- Caching (TTL, cache key strategy)
- Feature flags gating this endpoint
- Known limitations or TODOs

---

## 3. Data Models

### 3.x `<ModelName>`

| Field | Type | Required | Validation Rules | Description |
|---|---|---|---|---|
| `id` | UUID | Yes | — | Primary identifier |

---

## 4. Dependency Map (Full Recursive Tree)

```
<SERVICE_NAME>
├── [sync]  UserService  →  GET /users/{id}
│   └── [sync]  MongoDB  →  users collection
├── [sync]  TokenService  →  POST /token/validate
├── [async] NotificationQueue  →  publish: user.created
└── [sync]  ExternalService  →  POST /verify  (EXTERNAL)
```

---

## 5. Communication Layer

| Dependency | Protocol | Auth Mechanism | Base URL / Config Key | Timeout | Retry Policy |
|---|---|---|---|---|---|

---

## 6. Configuration & Environment Variables

| Variable | Purpose | Default | Required |
|---|---|---|---|

---

## 7. Error Handling & Resilience Patterns

- Global error handler / middleware
- Circuit breakers, bulkheads, or fallbacks
- Dead-letter queue handling (if async)
- Logging and tracing conventions (correlation IDs, trace headers)

---

## 8. Security Considerations

- Authentication and authorisation model
- PII / sensitive fields — are they masked in logs?
- Input sanitisation approach
- Any known security TODOs in the code

---

## 9. Open Issues / TODOs

Scan for `TODO`, `FIXME`, `HACK`, `NOTE` comments and list them:

| Ref | File:Line | Comment | Severity |
|---|---|---|---|
