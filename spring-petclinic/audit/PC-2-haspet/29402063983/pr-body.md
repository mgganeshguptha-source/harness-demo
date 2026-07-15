Story: Owner.hasPet(name)

Summary
-------
Add a new public method boolean hasPet(String name) to the Owner class that lets clinic staff check whether an owner already has a pet with the given name.

What changed
------------
- Owner: new public method boolean hasPet(String name).
  - Returns true if the owner has any pet whose name equalsIgnoreCase(name).
  - Returns false if name is null, empty, or no pet matches.
  - Comparison does NOT trim whitespace and uses String.equalsIgnoreCase per requirements.
  - Method is read-only and does not modify owner or pet state.

Tests
-----
- Added unit tests covering:
  1. matching name -> true
  2. non-matching name -> false
  3. case-insensitive match -> true
  4. null argument -> false

Acceptance criteria mapping
---------------------------
1. Public method hasPet(String name) implemented on Owner.
2. Case-insensitive comparison implemented using equalsIgnoreCase.
3. Returns false when name is null or when no match exists.
4. Method is read-only; no state changes.
5. Unit tests cover the four scenarios listed above.

Notes
-----
- Per clarification, whitespace is not trimmed: " Fido " does not match "Fido".
- Empty string "" returns false (no match) and does not throw.

Reviewer guidance
-----------------
Review Owner.hasPet implementation for adherence to equalsIgnoreCase and absence of side effects; verify unit tests exercise the four scenarios and pass.
