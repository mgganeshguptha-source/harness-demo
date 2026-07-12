Add Owner.hasPet(String) method and unit tests

Summary
- Adds a public boolean hasPet(String name) to the Owner domain class.
- The method returns true if any pet of the owner has a name equal to name (case-insensitive using String.equalsIgnoreCase).
- Returns false for null or when no match is found. The method is read-only and does not modify Owner or Pet state.

Tests
- Unit tests cover: matching name, non-matching name, case-insensitive match, and null argument.

Behavior notes
- Comparison does NOT trim whitespace; empty string returns false.