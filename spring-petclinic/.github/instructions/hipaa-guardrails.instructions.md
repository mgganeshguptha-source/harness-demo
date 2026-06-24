---
applyTo: "**"
---

# HIPAA Guardrails

This codebase processes Protected Health Information (PHI) under HIPAA. Every code suggestion must respect the rules below. When a request would cause a violation, refuse the unsafe form, explain the rule briefly, and offer a compliant alternative.

## What counts as PHI

The 18 HIPAA identifiers, including but not limited to: name, address (smaller than state), dates tied to an individual (birth, admission, discharge, death), phone, email, SSN, MRN, health plan beneficiary number, account number, certificate/license number, vehicle ID, device ID, URL, IP address, biometric identifier, full-face photo, any other unique identifier. Treat free-text clinical notes and diagnosis codes as PHI by default.

## Rules

### Logging and telemetry
- Never log PHI. Not in `log.info`, `log.debug`, `console.log`, `System.out`, structured loggers, exception messages, stack traces, or breadcrumbs.
- Never include PHI in error responses returned to clients beyond the minimum necessary.
- If a log statement references an object that may contain PHI (`patient`, `member`, `claim`, `enrollee`, `subscriber`, request/response DTOs), log only a non-PHI correlation ID (memberId hash, requestId, traceId) — never the object itself or `.toString()` of it.
- Never log full request bodies or full response bodies for endpoints that handle PHI. Log method + path + status + correlationId + duration only.

### Storage and transmission
- PHI at rest must be encrypted. Do not suggest writing PHI to local files, temp files, in-memory caches without TTL, browser `localStorage`/`sessionStorage`, IndexedDB, or mobile insecure storage.
- PHI in transit must use TLS 1.2+. Never suggest HTTP endpoints, disabled certificate validation, or `trustAllCerts` patterns for any service that handles PHI.
- Never hardcode PHI in test fixtures, seed data, or sample payloads. Use clearly synthetic values (e.g., `MBR-TEST-0001`, `John Q Test`).

### Minimum necessary
- API responses should return only the fields the caller needs for the stated purpose. Flag any DTO that exposes the full member/patient record when the endpoint contract calls for a subset.
- Avoid `SELECT *` patterns and broad object spreads (`{...member}`) when returning data to clients.

### Audit
- Every read or write of PHI must be auditable. If a new service method touches PHI and there is no audit emission visible in the surrounding code, flag it with: `// TODO HIPAA: emit audit event (actor, action, resource, timestamp)`.

### Access control
- Never suggest endpoints that handle PHI without an authentication/authorization check. If the surrounding pattern uses Spring Security, Angular route guards, or similar, the new code must follow it.
- Do not suggest disabling CSRF protection, CORS wildcards, or `permitAll()` for endpoints that may touch PHI.

### De-identification
- If a developer asks for sample/mock PHI data for tests, generate clearly synthetic data only. Never generate realistic-looking SSNs, MRNs, or DOBs that could be mistaken for real records.

## Refusal pattern

If asked to do any of the above-prohibited things (e.g., "log the patient object", "store member SSN in localStorage", "return the full member record"), respond with:

> ⚠️ HIPAA guardrail: <one-line rule>. Suggested compliant alternative: <code>.
