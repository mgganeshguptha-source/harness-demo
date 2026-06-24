---
applyTo: "src/app/**/*.ts,src/app/**/*.html"
---

# OWASP Top 10 Guardrails — Angular Web Frontend

Apply OWASP Top 10 (2021) defences to every Angular suggestion. Angular-specific browser-security rules live in `angular-security.instructions.md`; this file covers OWASP categories.

## A01 — Broken Access Control
- Every protected route must have a `CanActivate`/`CanMatch` guard. Never suggest adding routes to the protected area without a guard.
- Do not rely on hiding UI elements (`*ngIf="isAdmin"`) as the only access control — the backend must enforce it. Hidden UI is UX, not security.
- Never trust user identity, roles, or permissions read from `localStorage` or a decoded JWT payload in the browser as the authoritative source. The server is the source of truth.

## A02 — Cryptographic Failures
- Never implement crypto in the browser for confidentiality (no client-side AES of PHI). Use HTTPS + server-side encryption.
- Never store tokens, secrets, or PHI in `localStorage` or `sessionStorage`. Use httpOnly cookies set by the server, or in-memory state cleared on logout.
- Do not suggest building JWTs in the browser, or "encrypting" payloads with a hardcoded key.

## A03 — Injection (XSS)
- Use Angular interpolation `{{ value }}` and property binding `[prop]="value"` — these escape by default.
- Never use `innerHTML` with untrusted data. Never use `DomSanitizer.bypassSecurityTrustHtml()`, `bypassSecurityTrustScript()`, `bypassSecurityTrustUrl()` on values derived from API responses, URL params, or user input.
- For dynamic HTML that must allow some markup, sanitise with `DOMPurify` first.
- Never use `eval()`, `new Function()`, or `setTimeout(stringArg)`.
- SQL/NoSQL parameters built in the browser must still be parameterised on the server — never trust client-built queries.

## A04 — Insecure Design
- Do not implement business logic that determines pricing, eligibility, claims status, or PHI access purely in the browser. The backend must re-validate every action.
- Forms handling sensitive data must have CSRF tokens (Angular's `HttpClientXsrfModule`) or use SameSite cookies + custom header pattern.

## A05 — Security Misconfiguration
- Do not commit `.env`, API keys, or secrets to the repo. Environment files (`environment.ts`) must contain only non-secret config.
- Do not suggest `--disable-host-check` or `--disable-web-security` for production builds.
- Production builds: `ng build --configuration=production` (AOT + Ivy). Never ship dev builds.

## A06 — Vulnerable and Outdated Components
- Do not suggest deprecated packages or known-CVE versions. When unsure, write `// TODO confirm latest patched version` rather than guess.
- Avoid suggesting npm packages with known maintenance issues (single-maintainer, unmaintained `event-stream`-style risks). Prefer Angular-maintained or well-known libraries.

## A07 — Identification and Authentication Failures
- Never store passwords in any form on the client beyond the immediate submit.
- Token storage: httpOnly cookies preferred. If using bearer tokens in memory, clear on logout and route change to login.
- Implement automatic logout on inactivity for sessions that touch PHI.
- Never log tokens, passwords, OTPs to `console.log` — they appear in browser devtools and may be captured.

## A08 — Software and Data Integrity Failures
- Use Subresource Integrity (`integrity` attribute) for any externally-hosted scripts.
- Do not load Angular, polyfills, or critical libraries from public CDNs in a production HIPAA app — host them.
- Do not `eval` JSON; use `JSON.parse`.

## A09 — Security Logging and Monitoring Failures
- Frontend errors should be sent to a server-side log aggregator (Sentry, Datadog RUM) — but error payloads must be scrubbed of PHI before send. Configure `beforeSend` hooks.
- Do not log full request/response bodies in HTTP interceptors when the endpoint handles PHI.

## A10 — SSRF (frontend's role)
- The frontend cannot directly cause SSRF, but never build a feature where a user-supplied URL is sent to the backend to be fetched without server-side allowlisting. Flag any such call with `// TODO confirm server-side SSRF protection`.

## Refusal pattern

> ⚠️ OWASP guardrail (A0x — <category>): <one-line rule>. Suggested safe alternative: <code>.
