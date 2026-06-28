Title: Owner.hasPet(name)

Short summary

As a clinic staff member, check whether an owner already has a pet with a given name to prevent duplicate pet names when registering a new pet for that owner.

Story (raw)

As a clinic staff member
I want to check whether an owner already has a pet with a given name
So that I can prevent duplicate pet names when registering a new pet for that owner.

Layer and story type

Layer: Backend (domain model + unit tests)
Story type: New small feature / enhancement to domain model

Current behaviour

_No explicit code change exists for this behaviour in the story. The current codebase may already expose Owner and Pet domain objects; this story requires adding a read-only check to the owner-side model._

Expected behaviour

- The owner domain model exposes a public method with signature: boolean hasPet(String name).
- The method returns true if any pet belonging to the owner matches the provided name using a case-insensitive comparison.
- The method returns false if no pet matches or if the provided name argument is null.
- The method does not mutate the Owner or Pet objects or any other state (read-only).
- Behaviour must be deterministic and suitable for direct unit testing.

Acceptance criteria (from story)

1. Add a public method `boolean hasPet(String name)` to the Owner class.
2. Returns `true` if the owner has a pet whose name matches `name` (case-insensitive).
3. Returns `false` if no pet matches, or if `name` is null.
4. Does not modify existing pets or owner state (read-only).
5. Unit tests cover: a matching name, a non-matching name, case-insensitive match, and a null argument.

Constraints (technical)

- Follow project Java conventions (constructor injection, Lombok usage where present, JUnit 5 for tests). _Default team copilot-instructions not found in CI mode._
- Keep method simple, performant (iterate existing pet collection, no DB calls), and side-effect free.
- Unit tests must be pure unit tests (no integration or DB required) and validate all acceptance criteria cases.
- Do not change public API shapes beyond adding this method to the owner model.

Testing / Validation

- Add unit tests exercising:
  - matching name returns true
  - non-matching name returns false
  - case-insensitive match (e.g., "fido" vs "Fido") returns true
  - null argument returns false
- Tests should not rely on external systems. Use existing test frameworks and project conventions.

Out of scope

- Changing persistence layer or repository behaviour
- Adding API endpoints or controller changes
- Internationalization beyond basic Unicode case-insensitive comparison
- Database migrations or schema changes

Section 8 — Clarifications Needed

[NEEDS CLARIFICATION]: Treatment of empty-string input ("") — should hasPet("") return false, or should it be treated as invalid and throw an exception?

[NEEDS CLARIFICATION]: Should the name comparison trim leading/trailing whitespace before comparison (e.g., " Fido ")? If yes, confirm trimming is required.

[NEEDS CLARIFICATION]: Required Unicode case-folding behaviour — is simple String.equalsIgnoreCase acceptable, or must full Unicode case-folding / locale-aware rules be used? If project expects locale-aware matching, specify locale or normalization rules.

Notes

- The story explicitly requests a domain-model method and unit tests. Implementers should follow repository code style and test conventions when adding the method and tests.
