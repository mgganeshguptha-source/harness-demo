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
- Empty string `""` returns false (no match), does not throw.

## Implementation notes

- Location: add method to model class `Owner` (package `org.springframework.samples.petclinic.model` or existing package for Owner in this codebase).
- Method signature: `public boolean hasPet(String name)`.
- Implementation must iterate the owner's pets (read-only) and compare each pet's `getName()` with `name` using `equalsIgnoreCase`. If `name` is `null` return `false` immediately.
- Do not mutate any collections or pet instances. Keep method side-effect free.

Example implementation sketch:

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

## Tests

- Create unit tests (e.g., `OwnerTests` or `OwnerTest`) under `src/test/java/.../model/`.
- Required test cases:
  - matching name -> true
  - non-matching name -> false
  - case-insensitive match (e.g., "fIdO" vs "Fido") -> true
  - null argument -> false
- Additional: empty string `""` should return false (covered by non-matching case).

Example test command:

```
mvn -Dtest=OwnerTests test
```

## Notes

- This document records the behavior and test expectations; implementation should respect existing project coding and testing conventions.
- Ensure new tests are deterministic and clean (no reliance on external state).
