Title: Owner.hasPet(name)

1. Story

As a clinic staff member
I want to check whether an owner already has a pet with a given name
So that I can prevent duplicate pet names when registering a new pet for that owner.

2. Background / Current Behaviour

- The Owner domain class currently does not expose a hasPet(String name) convenience method (codebase scan not performed in CI mode). Calling code performs manual iteration over the owner's pet collection to check names. No UI or persistence changes are requested.

3. Expected Behaviour (precise, testable)

- Add a public method on Owner: boolean hasPet(String name).
- Return true if the owner has a pet whose name equals the provided name using case-insensitive comparison via String.equalsIgnoreCase.
- Return false if no pet matches, if the owner has no pets, if name is null, or if name is an empty string.
- The method must be read-only: it must not modify the Owner or Pet state, nor persist changes.
- The method must not trim input or stored names. Exact character sequence (except case) must match.

4. Acceptance Criteria (from story)

1. A public method boolean hasPet(String name) exists on Owner.
2. Returns true if an owned pet's name matches name (case-insensitive via equalsIgnoreCase).
3. Returns false if no pet matches, or if name is null.
4. Does not modify existing pets or owner state (read-only).
5. Unit tests cover: a matching name, a non-matching name, case-insensitive match, and a null argument. Additionally ensure empty string returns false per clarifications.

5. Implementation notes (developer-facing, non-prescriptive)

- Place the method on the Owner domain class alongside other convenience accessors.
- Implementation: iterate the owner's pet collection (null-safe) and compare each pet.getName() with the supplied name using name.equalsIgnoreCase(petName) or the null-safe variant. Do not call trim() on either side.
- Do not change persistence mappings, entity relationships, or equals/hashCode semantics.
- Mark the method as simple, side-effect free. No transactions are required.
- Add Javadoc describing behaviour (null/empty handling, case rules).

6. Unit tests (concrete cases)

- Test: hasPet_matchingName_returnsTrue
  - Owner with pet named "Fido" -> hasPet("Fido") == true
- Test: hasPet_caseInsensitiveMatch_returnsTrue
  - Owner with pet named "Fido" -> hasPet("fido") == true
- Test: hasPet_nonMatchingName_returnsFalse
  - Owner with pet named "Fido" -> hasPet("Rex") == false
- Test: hasPet_nullName_returnsFalse
  - Owner with pet(s) -> hasPet(null) == false
- Test: hasPet_emptyString_returnsFalse
  - Owner with pet named "" or with no pet -> hasPet("") == false

Test fixtures should use synthetic pet names (e.g., "Fido", "Rex"). Use JUnit 5 + existing test conventions in repo. Tests should assert no modification to the Owner or Pet collections after call.

7. Constraints

- Use String.equalsIgnoreCase for case-insensitive comparison only. Do NOT implement locale-aware case-folding.
- Do NOT trim input or stored names; whitespace is significant.
- Method must be side-effect free and not perform persistence operations.
- Keep method implementation simple and readable; favour null-safety and avoid Optional-heavy APIs unless repo conventions require it.
- Follow project Java conventions (place method in model/entity package, include Javadoc).

8. Clarifications Needed (CI-mode rules)

- None — the story and resolved clarifications specify null handling, trimming behaviour, and case-insensitivity implementation.

Out of scope

- Normalizing or trimming names before comparison.
- Locale-aware case folding beyond equalsIgnoreCase.
- UI changes, API surface changes, database migrations, or auditing changes.
- Preventing duplicates at persistence level — this story only adds an in-memory convenience method and unit tests.

Notes for reviewer

- Confirm placement of the new method follows project package layout for domain/model classes.
- Ensure unit tests run under the repository's existing test framework and assert no state mutation.

Context written in CI mode from the supplied story and clarifications.
