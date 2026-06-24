---
applyTo: "src/app/**/*.ts,src/app/**/*.html,capacitor.config.ts,capacitor.config.json"
---

# Mobile Security Guardrails — Ionic + Angular + Capacitor

Mobile-specific security rules. Pairs with `owasp-angular.instructions.md`, `angular-security.instructions.md`, and `hipaa-guardrails.instructions.md`.

## Secure storage

- Never use `localStorage`, `sessionStorage`, IndexedDB, or `Storage` (Capacitor `@capacitor/preferences`) for tokens, PHI, credentials, or PII. These are plaintext on disk.
- Use platform-secure storage:
  - iOS: Keychain via `@capacitor-community/secure-storage` or `@ionic-enterprise/identity-vault`
  - Android: EncryptedSharedPreferences / Keystore via the same wrappers
- For maximum-sensitivity data (auth tokens for PHI access), prefer Identity Vault with biometric unlock if available in the project.
- Never write PHI or tokens to app logs, crash reports, or files in `Documents`/`Cache`/`Library`.

## Network security

- TLS 1.2+ only. Configure ATS (iOS `Info.plist`) and Network Security Config (Android `network_security_config.xml`) to forbid cleartext.
- Never set `NSAllowsArbitraryLoads = true` on iOS, never set `cleartextTrafficPermitted="true"` on Android.
- **Certificate pinning** for production: pin to the API server's cert or public key for endpoints handling PHI. Use `@capacitor-community/http` with pinning or native pinning via Identity Vault.
- Never disable TLS verification, even in development builds that touch PHI. Use a dev API endpoint with a real cert.

## Authentication and session

- Biometric auth: use Identity Vault or `@capacitor-community/biometric-auth`. Never roll your own.
- Session tokens must be cleared on logout and on app uninstall (handled by Keychain/Keystore wrappers).
- Implement inactivity timeout for PHI sessions (default: 5–15 minutes per HIPAA risk assessment).
- Never store passwords on device. If "Remember me" is required, store a refresh token in secure storage, never the password.

## WebView and Capacitor config

- `capacitor.config.ts`:
  - `server.androidScheme: 'https'` (not http)
  - `server.hostname` set to the production hostname; do not commit dev hostnames
  - `server.allowNavigation` — strict allowlist of domains; never `["*"]`
  - `android.allowMixedContent: false`
  - `ios.contentInset: 'always'` does not affect security but verify other iOS flags
- Never enable `WebView.setWebContentsDebuggingEnabled(true)` in release builds.
- Disable WebView debugging for production: `if (BuildConfig.DEBUG) { ... }` guard on Android; `WKWebView` debugging only in dev on iOS.

## Deep links and URL schemes

- Validate every deep link parameter on receipt — never pass directly into `Router.navigate` or string-concat into HTML.
- Use Universal Links (iOS) / App Links (Android) with verified domain associations, not custom URL schemes alone — custom schemes can be hijacked by other apps.
- Deep links must not be able to trigger authenticated actions without a fresh auth check.

## Permissions

- Request runtime permissions only when needed and explain why in the prompt UI.
- Never request permissions the app doesn't use (camera, location, contacts) — App Store / Play Store reviewers reject these.
- Camera/photo permissions for capturing PHI (insurance cards, ID photos): ensure images are encrypted at rest before upload and deleted from device cache after upload.

## Code protection

- Never hardcode API keys, signing secrets, or encryption keys in the Angular code or Capacitor config — they are extractable from the app bundle.
- Use a backend-for-frontend (BFF) pattern: the mobile app holds only a user token; sensitive keys live server-side.
- Obfuscate release builds (Android: R8/ProGuard; iOS: built-in symbol stripping). This is defence-in-depth, not a substitute for the above.

## Jailbreak / root detection

- For PHI-handling flows: consider Identity Vault's built-in jailbreak/root detection, or `@capacitor-community/root-detection`. Block PHI access on detected compromise, with a clear user message.
- Document the policy decision in code if jailbreak detection is intentionally NOT used.

## Logging

- Disable verbose logging in release builds. Capacitor: configure `Capacitor.DEBUG = false` for production.
- Never log PHI, tokens, or full request/response bodies on device.
- Native crash reporters (Firebase Crashlytics, Sentry) must scrub PHI in `beforeSend` hooks before transmission.

## Capacitor plugin trust

- Audit third-party Capacitor plugins before adding — they have native code access. Prefer official `@capacitor/*` plugins, then `@capacitor-community/*`, then well-known maintainers.
- Do not suggest plugins with no recent releases, no GitHub activity, or single anonymous maintainers.

## Refusal pattern

> ⚠️ Mobile security guardrail: <one-line rule>. Suggested safe alternative: <code>.
