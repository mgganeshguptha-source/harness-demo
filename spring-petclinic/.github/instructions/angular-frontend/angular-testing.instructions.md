---
applyTo: "src/app/**/*.spec.ts"
---

# Angular Testing Conventions (Web)

## Framework and Tooling

- Use the project's configured test runner (Jasmine + Karma, or Jest if
  configured). Do not introduce a different runner.
- Use `TestBed` for component and service tests.
- Mock dependencies with jasmine spies (`jasmine.createSpyObj`) or the
  project's existing mocking approach.

## What to Test

- Components: rendering for each meaningful state (loading, empty,
  error, populated), and that user interactions call the right service
  methods.
- Services: each public method — success and error paths. Mock
  `HttpClient` with `HttpTestingController`; do not make real HTTP
  calls.
- Pipes and pure functions: input/output including edge cases.
- Cover happy path, error path, and empty/null inputs at minimum.

## Structure and Placement

- Spec file sits next to the file it tests, same name with `.spec.ts`.
- One `describe` per unit under test; nested `describe` per method or
  scenario.
- Each `it` asserts one behaviour.
- Tests must be deterministic — no reliance on real timers or network;
  use fakeAsync/tick or marble testing where needed.
