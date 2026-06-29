Title: Owner.hasPet(name)

1. Story

As a clinic staff member
I want to check whether an owner already has a pet with a given name
So that I can prevent duplicate pet names when registering a new pet for that owner.

2. Background

The application models Owners and their Pets. Owners hold a collection of Pets (in-memory or persisted). Callers need a simple, read-only API to determine whether an Owner already has a Pet with a given name to enforce uniqueness at the UI/service layer before creating a new Pet.

3. Current behaviour

_Not found in codebase — confirm with team_: confirm whether a utility or existing Owner-level method already performs this check, or whether callers currently iterate the pet collection manually.

4. Expected behaviour

- Add a public method boolean hasPet(String name) accessible on the Owner model/object.
- Method returns true if the owner has any pet whose name equals the provided name using case-insensitive comparison via String.equalsIgnoreCase.
- Method returns false when no pet matches, when name is null, or when name is the empty string "".
- Method is read-only and does not modify Owner or Pet state.
- Name comparison does NOT trim whitespace; exact characters are compared except for case as specified.

5. Acceptance criteria (testable)

1. The Owner model exposes a public method: boolean hasPet(String name).
2. hasPet("Fido") returns true when Owner has a pet named "Fido".
3. hasPet("fido") returns true when Owner has a pet named "Fido" (case-insensitive match using equalsIgnoreCase).
4. hasPet("Rex") returns false when Owner has pets but none named "Rex".
5. hasPet(null) returns false and does not throw.
6. hasPet("") returns false and does not throw.
7. Method does not mutate Owner or Pet state (read-only). Unit tests must assert immutability where applicable.
8. Unit tests cover: matching name, non-matching name, case-insensitive match, null argument, and empty-string argument.

6. Constraints

- Language / stack: Java (Spring Boot codebase conventions).
- Tests: JUnit 5 (existing project test conventions). Use small, focused unit tests for Owner behavior.
- Implementation: keep method small and deterministic; do not introduce database writes or side-effects.
- String comparison per clarification: use String.equalsIgnoreCase only (no locale-aware folding). Do not trim input; whitespace is significant.

7. Out of scope

- Changing persistence schema or database constraints to enforce pet-name uniqueness — this story only adds an in-memory/POJO-level check.
- UI changes to pet registration forms or server-side validation beyond adding the read-only check.
- Introducing locale-aware case folding or Unicode normalization for name comparisons.

8. Clarifications / Questions (CI-mode markers)

[NEEDS CLARIFICATION]: Confirm whether the codebase already contains an equivalent utility or Owner-level method that performs this check (if present, update tests/spec to cover the existing API rather than adding a duplicate method).

Notes

- Resolved clarifications (from the story):
  - Do NOT trim whitespace. Example: " Fido " does not match "Fido".
  - Case-insensitivity must use String.equalsIgnoreCase only.
  - Empty string "" returns false (no match) and does not throw.

Context written by CI-mode build-context for the story "Owner.hasPet(name)". Resolve the [NEEDS CLARIFICATION] item with the team before implementing if the presence of an existing helper is unknown.
