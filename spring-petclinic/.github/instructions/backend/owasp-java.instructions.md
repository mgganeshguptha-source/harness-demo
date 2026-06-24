---
applyTo: "src/main/java/**/*.java"
---

# OWASP Top 10 Guardrails — Java / Spring Boot

Apply OWASP Top 10 (2021) defences to every Java suggestion in this codebase. Each rule below maps to a Top 10 category. When a request would create a vulnerability, refuse the unsafe form and offer a safe alternative.

## A01 — Broken Access Control
- Every controller method that touches member/patient/claim resources must have `@PreAuthorize` or equivalent. Never suggest endpoints without authorisation checks.
- Never trust IDs from the path or body alone — verify the authenticated principal is permitted to act on that resource (IDOR prevention). Reject patterns like `repository.findById(pathId)` without an ownership check.
- Do not suggest `permitAll()`, `.anyRequest().permitAll()`, or commented-out security config.
- Method-level `@Secured`/`@RolesAllowed` must use real roles defined in the project; do not invent roles.

## A02 — Cryptographic Failures
- Never suggest MD5 or SHA-1 for security purposes. Use SHA-256+ for hashing, BCrypt/Argon2 for passwords.
- Never suggest hardcoded keys, IVs, or salts. Source from `@Value` + Vault/Secrets Manager + environment.
- For symmetric encryption, use AES-GCM (not ECB, not CBC without HMAC). For asymmetric, RSA-2048+ or ECDSA P-256+.
- TLS only — never `HttpClient` over plain HTTP for service-to-service calls. Never disable hostname verification or trust all certs.

## A03 — Injection
- **SQL:** Use `PreparedStatement`, JPA `@Query` with named parameters, or Spring Data method derivation. Never concatenate user input into SQL or JPQL. Flag any `String.format` or `+` operator inside a query string as a violation.
- **Command injection:** Never suggest `Runtime.exec(String)` with user input. Use `ProcessBuilder` with an argument list and a whitelisted command set.
- **LDAP / XPath / SpEL:** Same rule — never concatenate user input. Use parameterised APIs.
- **Header injection:** Sanitise CR/LF (`\r`, `\n`) from any user input written into response headers.

## A04 — Insecure Design
- Rate-limit authentication endpoints and any expensive operations. Flag missing rate-limiters on login/OTP/search endpoints.
- Validate state transitions server-side, not by trusting a client-supplied "status" or "step" field.
- Never expose internal IDs (auto-increment) where a UUID or opaque token would prevent enumeration.

## A05 — Security Misconfiguration
- Do not suggest `spring.profiles.active=dev` patterns that disable security in production paths.
- Never disable CSRF (`csrf().disable()`) for cookie-session apps. For stateless REST APIs, document the reason in a comment.
- Do not suggest CORS `allowedOrigins("*")` with credentials. Use an allowlist of explicit origins.
- Actuator endpoints (`/actuator/**`) must require authentication. Never suggest `management.endpoints.web.exposure.include=*` without auth.
- Stack traces must never be returned to clients. Use `@ControllerAdvice` returning sanitised error DTOs.

## A06 — Vulnerable and Outdated Components
- Do not suggest pinning to known-CVE versions of Spring Boot, Jackson, Log4j, Tomcat, or other major deps. When unsure of a safe version, write `// TODO confirm latest patched version` rather than guessing.
- Never suggest `log4j-core` 2.0–2.16.

## A07 — Identification and Authentication Failures
- Passwords: BCrypt with cost ≥ 10 (or Argon2id). Never `MessageDigest` of a password.
- Session: use Spring Session with secure, httpOnly, SameSite=Strict cookies. JWTs must be signed (RS256/ES256, not HS256 with a shared secret unless that's the explicit project pattern).
- Never log credentials, tokens, or session IDs.
- MFA flows must not log OTPs or recovery codes.

## A08 — Software and Data Integrity Failures
- Never deserialise untrusted input with `ObjectInputStream`, `XMLDecoder`, or polymorphic Jackson without a strict type allowlist. Use `@JsonTypeInfo` allowlists or DTOs only.
- Do not suggest `enableDefaultTyping()` on `ObjectMapper`.
- For YAML, use SafeConstructor (SnakeYAML 2.x default).

## A09 — Security Logging and Monitoring Failures
- Authentication success/failure, authorisation denials, and access to PHI must emit audit events. Flag controllers that handle sensitive resources with no audit emission visible.
- Never log secrets, tokens, passwords, or PHI (see HIPAA guardrails).
- Use structured logging (key-value or JSON) with a correlationId on every entry.

## A10 — Server-Side Request Forgery (SSRF)
- Never construct outbound URLs from user input without validation. Maintain an allowlist of hostnames/schemes for `RestTemplate`/`WebClient` calls driven by user data.
- Block requests to internal CIDRs (10/8, 172.16/12, 192.168/16, 169.254/16) and `localhost` when the destination is user-influenced.

## Refusal pattern

> ⚠️ OWASP guardrail (A0x — <category>): <one-line rule>. Suggested safe alternative: <code>.
