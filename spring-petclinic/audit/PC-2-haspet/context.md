# Story: Owner.hasPet(name)

## 1) Summary
As a clinic staff member
I want to check whether an owner already has a pet with a given name
So that I can prevent duplicate pet names when registering a new pet for that owner.

## 2) Acceptance Criteria
1. Add a public method `boolean hasPet(String name)` to the `Owner` class.
2. Returns `true` if the owner has a pet whose name matches `name` (case-insensitive).
3. Returns `false` if no pet matches, or if `name` is null.
4. Does not modify existing pets or owner state (read-only).
5. Unit tests cover: a matching name, a non-matching name, case-insensitive match, and a null argument.

## 3) Clarifications (resolved)
- Name comparison does NOT trim whitespace. " Fido " does not match "Fido".
- Case-insensitivity uses `String.equalsIgnoreCase` only. No full Unicode/locale-aware case-folding.
- Empty string `""` returns false (no match), does not throw.

## 4) Layer and Story Type
- Layer: Backend (domain/model change).
- Story type: Small, focused new development (add a read-only convenience method to domain model).

## 5) Current Behaviour
- The Owner domain model does not expose a `hasPet(String name)` convenience method for checking whether an owner already has a pet with a given name.
- Code that needs this check must iterate the owner's pet collection where used (scattered callers). _Not found in codebase — confirm with team_ if callers exist that should be refactored to use the new method.

## 6) Expected Behaviour
- A new public method `boolean hasPet(String name)` exists on the Owner model.
- The method iterates the owner's pets collection in a read-only manner and returns `true` if any pet's `getName()` matches `name` using `String.equalsIgnoreCase`, otherwise `false`.
- If `name` is `null`, the method returns `false`.
- The method does not mutate owner or pet state and has no side effects.
- Call sites that currently perform this check may be refactored to call `owner.hasPet(name)` (refactor is out of scope unless requested).

## 7) API / Model Contract Changes
- Public API change: adds `boolean hasPet(String name)` to the Owner model/class. This is backward-compatible for external clients because it is an additive API on a server-side model (no controller/API signature change).
- Behavioural contract:
  - Input: `String name` (may be null)
  - Output: `boolean` (true if a case-insensitive match exists, false otherwise)
  - Side effects: none

## 8) Clarifications Needed
- No unresolved clarifications from the provided story. (All required dimensions were specified in the story and clarifications section.)

## 9) Tests
- Unit tests required (JUnit 5):
  1. testHasPet_matchingName_returnsTrue — owner has a pet with exact name -> true
  2. testHasPet_nonMatchingName_returnsFalse — no pet matches -> false
  3. testHasPet_caseInsensitiveMatch_returnsTrue — differing case -> true
  4. testHasPet_nullArgument_returnsFalse — name == null -> false
- Test fixtures must use synthetic sample data (e.g., Pet objects with names like "Fido") and must not include real PII.
- Tests should assert no mutation of the Owner's pet collection after invocation.

## 10) Constraints
- Implementation must be thread-safe with respect to read-only iteration (do not mutate collections while iterating).
- Follow existing project Java conventions: constructor injection, SLF4J logging, and domain-model patterns used in the repo.
- Do not change controller or repository APIs in this story.
- Performance: the method should be O(N) in the number of owner's pets (acceptable for expected small collection sizes); if owners may have extremely large pet collections, raise as a follow-up.

## 11) Out of scope
- Refactoring all call sites to use the new method (unless requested separately).
- Changing persistence schema or database queries.
- Introducing caching for pet-name lookup.

---
Context written in CI mode from the provided story and ACs. Resolve any further questions with the BA/PO before implementation.
