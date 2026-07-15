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
- Empty string "" returns false (no match), does not throw.

## Implementation Notes

- Add `public boolean hasPet(String name)` to `Owner`.
- If `name == null` return `false` immediately.
- Iterate the owner's pets (e.g., `for (Pet p : getPets())`) and compare with:
  - `if (p.getName() != null && p.getName().equalsIgnoreCase(name)) return true;`
- After iteration return `false`.
- Ensure method is read-only and does not mutate any collections or objects.

## Tests

Create or update unit tests (e.g., OwnerTests or OwnerTest) to include four cases:

- testHasPet_matchingName_returnsTrue
- testHasPet_nonMatchingName_returnsFalse
- testHasPet_caseInsensitiveMatch_returnsTrue
- testHasPet_nullArgument_returnsFalse

Each test should construct an Owner, add Pet instances via existing API, and assert the boolean result. Do not rely on trimming; use exact name strings per the clarifications.
