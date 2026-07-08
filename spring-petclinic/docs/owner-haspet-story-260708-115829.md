# Story: Owner.hasPet(name)

As a clinic staff member
I want to check whether an owner already has a pet with a given name
So that I can prevent duplicate pet names when registering a new pet for that owner.

---

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

## Implementation notes

- Signature: `public boolean hasPet(String name)` in `Owner` (same package and visibility as other getters/setters).
- Behavior:
  - If `name == null` -> return `false`.
  - Iterate the owner's pet collection (e.g., `getPets()` / internal `pets` set/list). For each `Pet p`, retrieve `p.getName()` and if non-null, compare with `name` using `name.equalsIgnoreCase(p.getName())` or `p.getName().equalsIgnoreCase(name)` (ensure NPEs are avoided).
  - Do not alter any Pet or Owner fields.
  - If any pet matches -> return `true`; otherwise `false`.

- Performance: linear scan over pets; acceptable given expected small number of pets per owner.

## Unit test guidance

Create JUnit tests (matching repository style) that cover these scenarios:

1. matchingName_returnsTrue
   - Owner with a pet named "Fido"; call `hasPet("Fido")` -> assertTrue.

2. nonMatchingName_returnsFalse
   - Owner with pets "Fido", "Spot"; call `hasPet("Rex")` -> assertFalse.

3. caseInsensitiveMatch_returnsTrue
   - Owner with a pet named "fIdO"; call `hasPet("FIDO")` -> assertTrue.

4. nullArgument_returnsFalse
   - Owner with any pets; call `hasPet(null)` -> assertFalse.

Additional test notes:
- Include a test for empty string: `hasPet("")` -> assertFalse.
- Ensure pet names that are null inside Pet instances do not cause exceptions; `hasPet` should skip pets with null names.

## Example snippet (pseudo-Java)

// in Owner.java
public boolean hasPet(String name) {
    if (name == null) return false;
    for (Pet p : this.getPets()) {
        String petName = p.getName();
        if (petName != null && petName.equalsIgnoreCase(name)) {
            return true;
        }
    }
    return false;
}

---

Document created for story: Owner.hasPet(name)

