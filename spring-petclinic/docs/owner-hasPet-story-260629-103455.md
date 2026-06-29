# Story: Owner.hasPet(name)

As a clinic staff member
I want to check whether an owner already has a pet with a given name
So that I can prevent duplicate pet names when registering a new pet for that owner.

## Acceptance Criteria

1. Add a public method `boolean hasPet(String name)` to the `Owner` class.
2. Returns `true` if the owner has a pet whose name matches `name` (case-insensitive).
3. Returns `false` if no pet matches, or if `name` is null.
4. Does not modify existing pets or owner state (read-only).
5. Unit tests cover: a matching name, a non-matching name, case-insensitive match, and a null argument.

## Clarifications

- Name comparison does NOT trim whitespace. " Fido " does not match "Fido".
- Case-insensitivity uses `String.equalsIgnoreCase` only. No full Unicode/locale-aware case-folding.
- Empty string `""` returns false (no match), does not throw.

## Implementation notes

- Method signature (in `org.springframework.samples.petclinic.model.Owner`):

  public boolean hasPet(String name)

- Behavior:
  - If `name` is `null`, return `false` immediately.
  - Iterate the owner's pets collection (read-only). For each pet, retrieve `pet.getName()` and compare to `name` using `equalsIgnoreCase`.
  - If any pet name equals (case-insensitive) the input `name`, return `true`.
  - Otherwise return `false`.
  - Do not modify any state on `Owner` or `Pet`.

- Edge cases:
  - If a pet's `getName()` is `null`, skip that pet (do not throw).
  - Whitespace is significant per clarification.

## Unit tests (suggested)

Place tests under the existing test package for model classes, e.g. `src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java` (or similar).

Test cases to implement:

- testHasPet_matchingName() — owner has a pet named "Fido"; hasPet("Fido") returns true.
- testHasPet_nonMatchingName() — owner has pets but none named "Spot"; hasPet("Spot") returns false.
- testHasPet_caseInsensitive() — owner has "Fido"; hasPet("fIdO") returns true.
- testHasPet_nullArgument() — hasPet(null) returns false.

Each test must not modify Owner or Pet state beyond setup. Use synthetic test data; no PHI concerns.

## Notes for reviewers

- Confirm that the iteration uses the existing collection accessor (e.g., `getPets()` or equivalent) and does not change access modifiers.
- Confirm tests cover the empty-string case (returns false).

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
