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

## Clarifications (resolved)

- Name comparison does NOT trim whitespace. " Fido " does not match "Fido".
- Case-insensitivity uses `String.equalsIgnoreCase` only. No full Unicode/locale-aware case-folding.
- Empty string `""` returns `false` (no match), does not throw.

## Suggested Unit Tests

- `hasPet_returnsTrue_forExactMatchingName()` — owner with a pet named "Fido"; input "Fido" -> true.
- `hasPet_returnsFalse_forNonMatchingName()` — owner with pets none named "Rex"; input "Rex" -> false.
- `hasPet_isCaseInsensitive()` — owner with pet named "fIdO"; input "FIDO" -> true.
- `hasPet_returnsFalse_forNullName()` — input `null` -> false.

Notes for implementers:
- Implement as a read-only check over the owner's pet collection (no mutation).
- Use `String.equalsIgnoreCase` for comparison.
