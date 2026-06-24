---
applyTo: "src/app/**/*.ts,src/app/**/*.html"
---

# Angular Security Guardrails

Angular-specific browser-security rules. Pairs with `owasp-angular.instructions.md` (OWASP categories) and `hipaa-guardrails.instructions.md` (PHI rules).

## XSS prevention

### Always-safe patterns
- `{{ expression }}` — interpolation escapes by default
- `[textContent]="value"` — text binding escapes
- `[attr.title]="value"` — attribute binding escapes
- `[href]="url"` — Angular sanitises URLs (blocks `javascript:`)

### Never-safe patterns (require explicit justification + sanitisation)
- `[innerHTML]="value"` — bypasses default escape; use only with `DOMPurify.sanitize()` or trusted constant strings
- `DomSanitizer.bypassSecurityTrustHtml()` — only for constant strings the developer fully controls; never on API/URL/user data
- `bypassSecurityTrustScript()` — almost never justified; flag every occurrence
- `bypassSecurityTrustUrl()` / `bypassSecurityTrustResourceUrl()` — only for known-safe constant URLs
- `bypassSecurityTrustStyle()` — only for known-safe constant styles

If a developer requests bypass, respond with the DOMPurify alternative first; only use bypass if the developer confirms the input is fully controlled.

## Content Security Policy (CSP)

- Production must serve a CSP header. Recommended baseline:
  - `default-src 'self'`
  - `script-src 'self'` (no `unsafe-inline`, no `unsafe-eval`)
  - `style-src 'self'` (Angular component styles work with this; inline styles via property binding are fine)
  - `connect-src 'self' <api-host>` — list explicit API hosts
  - `img-src 'self' data:`
  - `frame-ancestors 'none'`
  - `object-src 'none'`
- Never suggest `unsafe-eval` or `unsafe-inline` to "make it work" — fix the underlying code that needs them.
- Use `nonce-` based CSP for any unavoidable inline script (rare in Angular).

## Route guards

- Every authenticated route must have `CanActivate` or `CanMatch` (Angular 15+ prefers `CanMatch` — it prevents lazy-loaded module download for unauthorised users, which is also a perf win).
- Guards must call the auth service synchronously or return an `Observable<boolean>` — never return a hardcoded `true`.
- Role-based guards must check roles from a trusted source (auth service that validates server-side), not from `localStorage` directly.
- Add a default deny: any new route added to a protected feature module inherits the parent guard. Never suggest a route without verifying its guard.

## Form input

- Use Reactive Forms with explicit `Validators`. Never trust client-side validation as the only check — the backend re-validates.
- For inputs that accept HTML (rich text editors), sanitise on both client (DOMPurify before display) and server (Java OWASP sanitizer / jsoup).
- File uploads: validate MIME type, file extension, and size on the client for UX, then re-validate on the server. Never let the browser-supplied `File.type` be the only check.

## URL handling

- Use Angular `Router` and `RouterLink` — they handle encoding.
- Never build URLs by string concatenation with user input. Use `Router.navigate(['/path', userInput])` so Angular encodes path segments.
- For external links: `<a [href]="externalUrl" rel="noopener noreferrer" target="_blank">` — `noopener` prevents `window.opener` attacks.

## HTTP

- Use a single `HttpInterceptor` for auth tokens, CSRF tokens, and correlation IDs — never attach them per-call.
- Never disable Angular's built-in XSRF protection unless you have a documented reason. If disabling, comment why.
- Set `withCredentials: true` only on endpoints that explicitly require cookies. Never as a default.

## Dependency rules

- Avoid `eval`-based templating libraries.
- Markdown renderers must be configured to disable HTML pass-through, or piped through DOMPurify.
- Chart and visualisation libraries that accept SVG: pipe SVG content through DOMPurify before render.

## Refusal pattern

> ⚠️ Angular security guardrail: <one-line rule>. Suggested safe alternative: <code>.
