# Backend copilot-instructions.md — Template and Section Guide

This is the target structure for the single file the skill generates at
`.github/copilot-instructions.md`. This file is **repo-wide,
cross-cutting content only**. Naming conventions, code style, package
structure, and test rules are NOT part of this file — they are
path-specific rules maintained separately in the copilot-toolkit
repository.

Each section states: what it is for, whether it is discoverable from the
repo, and what to do if it is not.

---

## Section 1 — Repository Overview

**Discoverable:** Partially. Tech stack and architecture come from the
build file and package structure. Purpose and domain do not.

- **Purpose** — what this service is and who consumes it. NOT
  discoverable. Ask. If unknown:
  `[TODO — MUST COMPLETE]: One-paragraph description of what this
  service does and its primary consumers. Needed so Copilot understands
  domain context.`
- **Tech Stack** — discoverable from `pom.xml` / `build.gradle`. List
  Spring Boot version, Java version, build tool, key dependencies, test
  tooling, datastores.
- **Architecture** — discoverable from package structure. State the
  layering and any API-first / OpenAPI usage.

---

## Section 2 — API Conventions

**Discoverable:** Partially, from existing controllers and the exception
handler.

- Versioning scheme (e.g. `/api/v1/resource`) — read from controllers.
  If none exist: ask, or `[TODO — MUST COMPLETE]`.
- Error response format — read from the global exception handler.
  Include the actual JSON shape used. If none: ask or mark.
- Input validation approach — read from existing DTOs.
- HTTP status conventions and pagination format — read from existing
  list endpoints.

---

## Section 3 — Security Guidelines

**Discoverable:** Rarely. Mostly not visible in code.

Short DOs / DON'Ts. The skill may include a standard universal set
without asking:

- Never hardcode secrets, API keys, passwords.
- Never build SQL via string concatenation.
- Never log sensitive data (passwords, tokens, PII).
- Always validate inputs with Jakarta Validation.
- Always hash passwords with a secure algorithm.

Project-specific items (auth provider, token strategy, CORS policy) —
ask. If unknown: `[TODO — MUST COMPLETE]: <specific security item>`.

---

## Section 4 — Design Patterns

**Discoverable:** Yes, mostly, from existing code.

State only the patterns the codebase actually uses: Repository, Service
layer, DTO + mapper, dependency injection style, any Strategy/Factory.
Do not list patterns the codebase does not use.

---

## Section 5 — Unique Patterns For This Project

**Discoverable:** Rarely. Highest-value section — these rules cause the
most defects when an AI does not know them.

Examples: date/timezone handling (UTC stored, converted at edge), i18n
(translation service, never hardcoded strings), idempotency, audit
logging. Mostly NOT discoverable. Ask explicitly. If unknown:
`[TODO — MUST COMPLETE]: Project-specific rules an AI would not infer
from code — date handling, i18n, idempotency, audit. These cause the
most defects when missed.`

---

## Section 6 — What To Avoid

**Discoverable:** Partially, by inference from architecture.

Stack and project anti-patterns: business logic in controllers,
entities as request/response objects, ignoring transaction boundaries,
circular service dependencies. The skill may propose the standard Spring
set and ask for project-specific additions.

---

## Section 7 — Documentation Requirements

**Discoverable:** Partially. JavaDoc/OpenAPI usage is visible in code.

Code documentation expectations (JavaDoc on public APIs, OpenAPI
annotations) and project documentation expectations (README, env vars,
profiles). Fill what is observable; ask for team expectations not
visible in code.

---

## What a filled section looks like

```markdown
## Repository Overview

- Purpose: REST backend for the clinic scheduling platform. Consumed by
  the Angular web portal and the Ionic mobile app. Handles owners, pets,
  visits, and appointment scheduling.
- Tech Stack: Spring Boot 3.2, Java 17, Maven, Spring Data JPA,
  MapStruct, springdoc-openapi, JUnit 5 + Mockito, PostgreSQL.
- Architecture: Layered REST API — controller → service → repository →
  model, with MapStruct DTO mappers. OpenAPI spec at
  src/main/resources/openapi.yml.
```

## What an unfilled section looks like

```markdown
## Unique Patterns For This Project

[TODO — MUST COMPLETE]: Project-specific rules an AI would not infer
from code — date/timezone handling, i18n strategy, idempotency
requirements, audit logging. The developer did not know these at
generation time. Fill before relying on this file — missing project
rules are the most common cause of AI-generated defects.
```

---

## Not part of this file

Naming conventions, code style, package structure, and test rules are
**path-specific rules**. They are maintained centrally in the
copilot-toolkit repository and copied into a repo's
`.github/instructions/` folder as a separate step. This skill does not
generate them. Keeping them separate keeps shared rules consistent
across all backend repos.
