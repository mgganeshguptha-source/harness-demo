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

## Implementation Notes

- Add the following public method to `Owner` (example implementation):

```java
public boolean hasPet(String name) {
    if (name == null) {
        return false;
    }
    for (Pet pet : this.getPets()) {
        String petName = pet.getName();
        if (petName != null && petName.equalsIgnoreCase(name)) {
            return true;
        }
    }
    return false;
}
```

- Key points:
  - The method is read-only: it only inspects the owner's pet collection via `getPets()` and does not modify state.
  - Null-safety: if `name` is `null` the method returns `false`.
  - Case-insensitive comparison is done with `String.equalsIgnoreCase`.
  - Handles pets with null names safely.

## Unit Tests

Add a new test class (suggested path):
`src/test/java/org/springframework/samples/petclinic/model/OwnerHasPetTests.java`

Tests to include (JUnit 4 or 5 acceptable):

1. matchingName_shouldReturnTrue
   - Arrange: Owner with a pet named "Buddy"
   - Act: owner.hasPet("Buddy")
   - Assert: returns `true`

2. nonMatchingName_shouldReturnFalse
   - Arrange: Owner with a pet named "Buddy"
   - Act: owner.hasPet("Max")
   - Assert: returns `false`

3. caseInsensitiveMatch_shouldReturnTrue
   - Arrange: Owner with a pet named "Buddy"
   - Act: owner.hasPet("buddy")
   - Assert: returns `true`

4. nullArgument_shouldReturnFalse
   - Arrange: Owner with any pets
   - Act: owner.hasPet(null)
   - Assert: returns `false`

Example JUnit assertion (JUnit 5):

```java
@Test
void caseInsensitiveMatch_shouldReturnTrue() {
    Owner owner = new Owner();
    Pet pet = new Pet();
    pet.setName("Buddy");
    owner.addPet(pet);

    assertTrue(owner.hasPet("buddy"));
}
```

## Files Touched (suggested)

- src/main/java/.../Owner.java — add `public boolean hasPet(String name)`
- src/test/java/.../OwnerHasPetTests.java — add unit tests covering the four cases

## Notes for reviewers

- Verify the method uses the existing pet accessors (`getPets()` or equivalent) and does not mutate collections.
- Confirm tests run on CI and that they assert the required behaviors (case-insensitive, null handling).
- Edge cases: pets with null names are ignored; duplicate pet names are handled (method returns true if any match).

--
Document created for: Story: Owner.hasPet(name)
Timestamp: 2026-06-28T09:27:41Z
