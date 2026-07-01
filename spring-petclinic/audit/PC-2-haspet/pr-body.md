Story: Owner.hasPet(name)

Summary

Add a read-only convenience method to Owner to determine whether an owner already has a pet with a given name.

What changed

- Added public method boolean hasPet(String name) to Owner.
- The method returns true when any pet of the owner has a name that equals the provided name using String.equalsIgnoreCase (case-insensitive). It returns false when name is null, when name is the empty string, or when no matching pet exists.
- Method does not modify Owner or Pet state.
- Unit tests added to cover: matching name, non-matching name, case-insensitive match, and null argument.

Behavior details / Acceptance Criteria mapping

1) Public method boolean hasPet(String name) added to Owner.  
2) Case-insensitive match implemented using equalsIgnoreCase.  
3) Returns false when name is null or when no match exists; empty string returns false.  
4) Read-only: no state changes.  
5) Unit tests added to validate the above cases.

Compatibility

Non-breaking change; only adds a public helper. No behavior of existing code paths changed.

Testing

Includes unit tests for the four acceptance cases; run existing test suite to verify.
