Title: Owner.hasPet(name)

1. Story

As a clinic staff member
I want to check whether an owner already has a pet with a given name
So that I can prevent duplicate pet names when registering a new pet for that owner.

2. Layer / Scope

Backend — domain model change on the Owner domain object (read-only behaviour: add a query method to check if an owner has a pet with the provided name). No controller, repository, API, or DB schema changes are required.

3. Current behaviour

There is currently no dedicated Owner.hasPet(String) convenience method on the Owner domain object. Call-sites perform ad-hoc checks by iterating pets or rely on higher-level code to avoid duplicates.

4. Expected behaviour

- Add a public method boolean hasPet(String name) to the Owner domain model.
- The method returns true if any Pet owned by the Owner has a name that matches the provided name in a case-insensitive comparison.
- The method returns false if no pet matches or if name is null.
- The method is read-only and must not mutate Owner or Pet state.

5. Acceptance Criteria (from story)

1. Add a public method `boolean hasPet(String name)` to the `Owner` class.
2. Returns `true` if the owner has a pet whose name matches `name` (case-insensitive).
3. Returns `false` if no pet matches, or if `name` is null.
4. Does not modify existing pets or owner state (read-only).
5. Unit tests cover: a matching name, a non-matching name, case-insensitive match, and a null argument.

6. Tests / Verification

Unit tests (JUnit 5) must be added to the Owner unit test suite covering these cases:
- matching name: owner with a pet named "Fido" -> hasPet("Fido") == true
- non-matching name: owner with pets but none named "Rex" -> hasPet("Rex") == false
- case-insensitive match: owner with pet "Buddy" -> hasPet("buddy") == true
- null argument: hasPet(null) == false

Tests must assert the method does not alter the Owner or Pet objects (no added/removed pets, names unchanged).

7. Constraints

- Implementation must be simple, efficient, and avoid side effects. Method should not modify collections or entity state.
- Use safe case-insensitive comparison — at minimum String.equalsIgnoreCase or an agreed project utility. If Unicode-aware case folding is required, flag in Clarifications.
- Unit tests should use JUnit 5 and existing test conventions in the repo (no new testing frameworks).
- Keep the change local to the domain model; do not add new dependencies.

8. Out of scope

- Any API/controller changes to enforce unique pet names are out of scope.
- Database schema or repository-level uniqueness constraints are out of scope.
- Client-side (UI) validations and messages are out of scope.

9. Risks and notes

- Locale and Unicode: simple equalsIgnoreCase handles ASCII and some Unicode, but may not be sufficient for all locales. If pet names may contain accented characters or locale-specific casing rules, a more robust Unicode case-folding approach might be required.
- Whitespace differences: callers may pass names with leading/trailing whitespace; decide whether the method should trim input before comparison.
- Mutability: ensure the method does not trigger lazy-loading side-effects that modify entity state; prefer safe iteration over the pet collection.

10. ## Clarifications (resolved)
- Name comparison does NOT trim whitespace. " Fido " does not match "Fido".
- Case-insensitivity uses `String.equalsIgnoreCase` only. No full Unicode/locale-aware case-folding.
- Empty string "" returns false (no match), does not throw.