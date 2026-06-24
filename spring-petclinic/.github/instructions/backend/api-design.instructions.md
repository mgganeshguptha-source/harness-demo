---
applyTo: "src/main/java/**/*Controller.java,src/main/java/**/controller/**/*.java"
---

# API Design Conventions — REST (Backend)

Conventions for HTTP REST APIs this service exposes. Compounds with `error-handling-java.instructions.md` (error response shape) and `owasp-java.instructions.md` (authZ, injection).

## URL structure

- **Base path:** `/api/v{major}/` — e.g., `/api/v1/`
- **Resource names:** plural nouns, lowercase, hyphenated. `/members`, `/claims`, `/prior-authorizations`. Never verbs in the path.
- **Nesting:** at most one level deep. `/members/{memberId}/claims` is fine. `/members/{memberId}/claims/{claimId}/lines/{lineId}/notes` is too deep — flatten by exposing `/claim-lines/{lineId}/notes`.
- **Identifiers in path:** UUIDs or opaque tokens. Never auto-increment integers (OWASP A01 enumeration risk).
- **Query params:** camelCase (`?pageSize=20&sortBy=createdDate`). Filters use plain keys, not bracket syntax.

## HTTP methods — semantic use

| Method | Purpose | Idempotent | Request body | Response body |
|---|---|---|---|---|
| GET | Read | Yes | No | Yes |
| POST | Create / non-idempotent action | No | Yes | Yes (201 + Location header) |
| PUT | Full replace | Yes | Yes (complete resource) | Yes or 204 |
| PATCH | Partial update | No (technically) | Yes (changes only) | Yes |
| DELETE | Remove | Yes | No | 204 |

- Never use GET to mutate state. Never use POST for safe reads.
- POST that performs an action (`/claims/{id}/submit`) is acceptable — name the action explicitly.

## HTTP status codes

| Code | When |
|---|---|
| 200 OK | Successful GET, PUT, PATCH, action POST |
| 201 Created | Successful resource-creating POST. Include `Location` header. |
| 202 Accepted | Async work queued — include status URL |
| 204 No Content | Successful DELETE or PUT with no response body |
| 400 Bad Request | Validation failure, malformed body |
| 401 Unauthorized | Missing/invalid credentials |
| 403 Forbidden | Authenticated but not permitted |
| 404 Not Found | Resource doesn't exist OR caller can't see it (avoid 403→404 distinction for sensitive resources) |
| 409 Conflict | Optimistic lock failure, duplicate |
| 422 Unprocessable Entity | Body parses but violates business rule |
| 429 Too Many Requests | Rate limit — include `Retry-After` |
| 500 Internal Server Error | Unexpected — generic message |
| 503 Service Unavailable | Downstream down — include `Retry-After` |

- Never return 200 with `{"success": false}`. Use the real status code.
- Never return 500 for validation errors.

## Request and response bodies

- **Content type:** `application/json` for normal responses; `application/problem+json` for errors (RFC 7807, see error-handling).
- **Field naming:** camelCase. No snake_case, no PascalCase.
- **Dates:** ISO-8601 strings (`2026-05-24T09:15:00Z` for instants, `2026-05-24` for dates). Never epoch ints.
- **Money:** decimal as string (`"123.45"`) with explicit `currency` field. Never float, never cents-as-int without documenting it.
- **IDs:** strings, even when numeric — protects against JS precision loss.
- **Booleans:** named `is*` / `has*` / `can*`. `enabled`, `active`, `paid` also fine. Never `disabled` (avoid negative names).
- **Nulls:** omit absent fields rather than emitting `"field": null` (configure Jackson). Exception: PATCH semantics where `null` means "set to null".

## Pagination

Cursor-based for large/active collections; offset-based acceptable for small static lists.

**Cursor (preferred):**
```
GET /api/v1/claims?pageSize=20&cursor=eyJpZCI6Ii4uIn0
→ {
  "items": [...],
  "nextCursor": "eyJpZCI6Ii4uIn0",
  "hasMore": true
}
```

**Offset (only when total count matters and dataset is small):**
```
GET /api/v1/claims?page=0&pageSize=20
→ {
  "items": [...],
  "page": 0,
  "pageSize": 20,
  "totalElements": 142,
  "totalPages": 8
}
```

- Default `pageSize`: 20. Max: 100. Reject larger.
- Never return unpaginated collections.

## Filtering, sorting, searching

- **Filter:** plain query params — `?status=ACTIVE&memberId=abc-123`.
- **Sort:** `?sortBy=createdDate&sortOrder=desc`. Allow multiple via repeat: `?sortBy=status&sortBy=createdDate`.
- **Search:** `?q=...` for full-text. Document searchable fields.
- Document the allowed filter/sort fields per endpoint — do not silently accept arbitrary fields (SQL injection adjacent + leaks schema).

## Versioning

- URL-path versioning: `/api/v1/...`, `/api/v2/...`. No header versioning, no query versioning.
- Only the major version is in the URL. Minor/patch are backward-compatible additions.
- A breaking change requires `v(N+1)`. Run both versions in parallel for ≥1 deprecation cycle.
- Deprecation: response includes `Deprecation: true` and `Sunset: <date>` headers.

## Required headers

- `X-Correlation-Id` — see `logging-standards.instructions.md`
- `Content-Type` — set explicitly on requests with bodies
- `Accept` — clients should set; default to `application/json`
- `Authorization` — Bearer token (never API key in URL)

## Authentication and authorization

- Bearer tokens only (JWT or opaque). Never API key in query string or path.
- Every endpoint has `@PreAuthorize` or equivalent — see `owasp-java.instructions.md` A01.
- Endpoints that touch PHI must verify the caller is permitted for that specific record, not just the resource type.

## Idempotency

- Mutating POST endpoints that may be retried (payments, submissions) accept an `Idempotency-Key` header. Server stores key+result for ≥24h.
- PUT and DELETE are naturally idempotent.

## Async / long-running

- Operations >2s should return 202 with a status URL: `Location: /api/v1/jobs/{jobId}`.
- The status endpoint returns `{status, progress, resultUrl}`.

## What never to do

- ❌ Tunnel methods via POST + `_method` param
- ❌ Return HTML from a JSON API
- ❌ Use HTTP for anything other than what the method semantically means
- ❌ Put secrets in query strings (logged everywhere)
- ❌ Return different shapes for the same endpoint based on a flag — version it instead

## Refusal pattern

> ⚠️ API design guardrail: <one-line rule>. Suggested alternative: <code>.
