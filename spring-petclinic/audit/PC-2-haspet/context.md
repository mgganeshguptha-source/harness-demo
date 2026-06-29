# Story: Owner.hasPet(name)

## 1) Short description
As a clinic staff member, I want to check whether an owner already has a pet with a given name so that I can prevent duplicate pet names when registering a new pet for that owner.

## 2) Story
**As** a clinic staff member
**I want** to check whether an owner already has a pet with a given name
**So that** I can prevent duplicate pet names when registering a new pet for that owner.

## 3) Background / Current behaviour
Currently the codebase does not expose a single read-only convenience method on the Owner model for checking whether any existing pet for that owner has a given name. Callers must iterate the pet collection and implement the comparison themselves, which leads to duplicated logic in tests and production code.

## 4) Layer and story type
- Layer: Backend (domain/model)
- Story type: Small enhancement / refactor (add read-only helper on domain object)

## 5) Scope
- In scope: Add a public method to the Owner domain/model that checks for a matching pet name (read-only), and add unit tests for that method.
- Out of scope: UI changes, controller or repository changes, database migrations, API contract changes, or other callers being refactored to use the new method (these can be done in follow-ups).

## 6) Expected behaviour
- A public method with the signature `boolean hasPet(String name)` exists on the Owner model and returns true if any Pet belonging to the owner has a name equal to `name`, comparing case-insensitively via `String.equalsIgnoreCase`.
- The method is read-only: it must not modify the Owner or its Pet collection.
- If `name` is null, the method returns false.
- Leading/trailing whitespace is significant (no trimming). An empty string `""` returns false.

## 7) Acceptance Criteria (from the story)
1. Add a public method `boolean hasPet(String name)` to the `Owner` class.
2. Returns `true` if the owner has a pet whose name matches `name` (case-insensitive).
3. Returns `false` if no pet matches, or if `name` is null.
4. Does not modify existing pets or owner state (read-only).
5. Unit tests cover: a matching name, a non-matching name, case-insensitive match, and a null argument.

## 8) Clarifications (resolved)
- Name comparison does NOT trim whitespace. " Fido " does not match "Fido".
- Case-insensitivity uses `String.equalsIgnoreCase` only. No full Unicode/locale-aware case-folding.
- Empty string "" returns false (no match), does not throw.

## 9) Constraints / Implementation constraints (team defaults)
- Backend: follow Spring Boot conventions (constructor injection, Jakarta Bean Validation where relevant). This is a pure domain/model change; keep it small and unit-testable.
- Do not change persistence mappings or DB schema.
- Tests: use existing project test frameworks (JUnit 5). Keep tests fast and focused on the domain method.

## 10) Test cases (explicit)
- TC1: matching name
  - Given an Owner with a Pet named "Fido"
  - When hasPet("Fido") is called
  - Then returns true

- TC2: non-matching name
  - Given an Owner with a Pet named "Fido"
  - When hasPet("Rex") is called
  - Then returns false

- TC3: case-insensitive match
  - Given an Owner with a Pet named "FiDo"
  - When hasPet("fido") is called
  - Then returns true (comparison via equalsIgnoreCase)

- TC4: null argument
  - Given an Owner with any pets
  - When hasPet(null) is called
  - Then returns false

- TC5: empty string
  - Given an Owner with a Pet named ""
  - When hasPet("") is called
  - Then returns false per clarification (empty string should not match)

## 11) Out of scope (explicit exclusions)
- Do not alter controllers, services, repositories, or API contracts.
- Do not change DB schema, persistence annotations, or migration scripts.
- Do not implement callers to use the new method in this change.

## 12) Notes for implementer
- Keep the method side-effect-free; do not mutate collections or objects.
- Use standard Java iteration/streams to check the pet collection; ensure null-safety for pet names.
- Make unit tests deterministic and only exercise the domain object; no integration or DB tests required.


_No [NEEDS CLARIFICATION] items — all clarifications were provided in the story._
