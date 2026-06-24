---
applyTo: "src/app/**/*.spec.ts"
---

# Ionic + Angular Testing Conventions (Mobile)

## Framework and Tooling

- Use the project's configured runner (Jasmine + Karma, or Jest if
  configured). Do not introduce a different runner.
- Use `TestBed` for page, component, and service tests.
- Mock Capacitor plugins — never call real native APIs in tests. Provide
  a fake/spy implementation of the plugin wrapper service.

## What to Test

- Pages/components: rendering for each meaningful state (loading, empty,
  error, populated), and that interactions call the right services.
- Services: each public method, success and error paths. Mock
  `HttpClient` with `HttpTestingController`.
- Plugin wrapper services: test the platform-guard logic (native path
  vs web fallback) using a mocked platform.
- Cover happy path, error path, offline/no-network behaviour, and
  empty/null inputs.

## Structure and Placement

- Spec file next to the file it tests, same name with `.spec.ts`.
- One `describe` per unit; nested `describe` per method or scenario.
- Each `it` asserts one behaviour.
- Tests must be deterministic — no real timers, network, or native
  calls; use fakeAsync/tick where needed.
