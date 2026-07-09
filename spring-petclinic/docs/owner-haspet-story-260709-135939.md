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

### Clarifications (resolved)
- Name comparison does NOT trim whitespace. " Fido " does not match "Fido".
- Case-insensitivity uses `String.equalsIgnoreCase` only. No full Unicode/locale-aware case-folding.
- Empty string `""` returns `false` (no match), does not throw.

## Implementation notes

- Add the method to `src/main/java/org/springframework/samples/petclinic/model/Owner.java` (or the existing Owner model class location).
- The method must be read-only: iterate over the owner's pet collection without modifying it.
- Pet names on `Pet` instances may be `null`; guard against NPE.

### Suggested implementation

```java
public boolean hasPet(String name) {
    if (name == null) {
        return false;
    }
    for (Pet pet : getPets()) {
        if (pet.getName() != null && pet.getName().equalsIgnoreCase(name)) {
            return true;
        }
    }
    return false;
}
```

- This implementation uses `equalsIgnoreCase` and respects the clarified rules (no trimming, null-safe).

## Unit tests

- Add tests under `src/test/java/...` alongside other Owner tests. Example JUnit 5 test cases:
  - `hasPet_matchingName_returnsTrue()` — owner has a pet named `"Fido"`, call `hasPet("Fido")` → `true`.
  - `hasPet_nonMatchingName_returnsFalse()` — owner has `"Fido"`, call `hasPet("Rex")` → `false`.
  - `hasPet_caseInsensitiveMatch_returnsTrue()` — owner has `"Fido"`, call `hasPet("fIdO")` → `true`.
  - `hasPet_nullArgument_returnsFalse()` — call `hasPet(null)` → `false`.

- Tests should assert no mutation of the owner's pet collection.

## Notes for reviewers

- Verify the method is public and placed on the `Owner` model.
- Ensure tests cover the four acceptance cases and the implementation handles `pet.getName()==null` safely.

<!-- End of owner-haspet story document -->