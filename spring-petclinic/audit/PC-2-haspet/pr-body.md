Story: Owner.hasPet(name)

Summary

Add a public method Owner.hasPet(String name) that checks whether an Owner already has a pet with the given name. The method is read-only and returns true when any pet owned by the Owner has a name that equals the provided name using case-insensitive comparison (String.equalsIgnoreCase). Returns false when no match is found or when the supplied name is null. Empty string "" does not match any pet names.

What changed

- Added Owner.hasPet(String name) (public, read-only).
- Implementation uses equalsIgnoreCase for comparisons; does not trim input.
- Added unit tests covering: matching name, non-matching name, case-insensitive match, and null argument.

Notes

- Behavior follows acceptance criteria exactly. No owner or pet state is modified.
