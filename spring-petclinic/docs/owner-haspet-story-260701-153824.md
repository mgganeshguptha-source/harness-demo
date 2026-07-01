# Story: Owner.hasPet(name)

As a clinic staff member
I want to check whether an owner already has a pet with a given name
So that I can prevent duplicate pet names when registering a new pet for that owner.

## Acceptance Criteria

1. Add a public method `boolean hasPet(String name)` to the `Owner` class.
2. Returns `true` if the owner has a pet whose name matches `name` (case-insensitive).
3. Returns `false` if no pet matches, or if `name` is null.
4. Does not modify existing pets or owner state (read-only).
5. Unit tests cover: a matching name, a non-matching name, case-insensitive match, a null argument, and empty string.

## Clarifications (resolved)

- Name comparison does NOT trim whitespace. " Fido " does not match "Fido".
- Case-insensitivity uses `String.equalsIgnoreCase` only. No full Unicode/locale-aware case-folding.
- Empty string `""` returns false (no match), does not throw.

## Implementation notes

- Signature to add in Owner (example):

```java
public boolean hasPet(String name) {
    if (name == null) {
        return false;
    }
    for (Pet pet : getPetsInternal()) { // or getPets()
        String petName = pet.getName();
        if (petName != null && petName.equalsIgnoreCase(name)) {
            return true;
        }
    }
    return false;
}
```

- Do not mutate any fields or collections. The method must be read-only.
- If pet names in the model may be null, skip those pets (no NPE).
- Do not trim `name` or pet names; exact characters except case.

## Suggested unit tests

Add tests to src/test/java/.../model/ (following existing Owner test class naming).

Example JUnit 5 test methods (pseudocode):

- testHasPet_matchingName():
  - owner with pet named "Fido" -> assertTrue(owner.hasPet("Fido"));

- testHasPet_nonMatchingName():
  - owner with pet "Fido" -> assertFalse(owner.hasPet("Rover"));

- testHasPet_caseInsensitive():
  - owner with pet "Fido" -> assertTrue(owner.hasPet("fIdO"));

- testHasPet_nullArgument():
  - owner with pet "Fido" -> assertFalse(owner.hasPet(null));

- testHasPet_emptyString():
  - owner with pet "" (if present) or owner with "Fido" -> assertFalse(owner.hasPet(""));

Notes for tests:
- Construct Owner instances using existing test utilities or plain POJOs used elsewhere in the project.
- Ensure tests do not rely on trimming or other normalization.

## Verification checklist

- [ ] Owner.java contains `public boolean hasPet(String name)` with the specified behavior
- [ ] Unit tests added and passing for all listed cases
- [ ] No existing behavior or state mutated by the new method

---

Document generated for: STORY: # Story: Owner.hasPet(name)
Timestamp: 2026-07-01T15:38:24Z
