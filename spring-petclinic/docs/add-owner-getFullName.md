Story: Add getFullName() to Owner

Summary
-------
Add a convenience method Owner#getFullName() that returns the owner's
firstName and lastName joined with a single space (`"<firstName> <lastName>"`).
This documents the intended behavior, acceptance criteria, and test/QA steps.

Motivation
----------
- Simplifies view templates and callers that need the owner's display name.
- Centralises formatting (handles nulls/empty fields consistently).

Design / Behavior
-----------------
- Method signature:
  - public String getFullName()
- Return value rules:
  1. If both firstName and lastName are non-empty: return "First Last" (single space).
  2. If only firstName present: return firstName (no trailing space).
  3. If only lastName present: return lastName.
  4. If both null/empty: return empty string "".
- Trim leading/trailing whitespace from stored names before joining.
- Method must be side-effect free and deterministic.

Files likely impacted (implementation guidance)
-----------------------------------------------
- src/main/java/org/springframework/samples/petclinic/model/Owner.java — add method
- src/test/java/.../OwnerTests.java — add unit tests that exercise all rules above
- Templates / views that display owner name may be updated to use getFullName()

Acceptance Criteria
-------------------
1. Owner#getFullName() exists and is public.
2. Returns "First Last" for both names present.
3. Handles missing or null names per the rules above.
4. Unit tests cover all combinations (both present, only first, only last, both missing) and edge cases (names with extra whitespace).

QA / Validation Steps
---------------------
1. Unit tests: run `mvn -DskipTests=false test` (or project test command) and ensure new tests pass.
2. Manual sanity check in app:
   - Find an Owner with both names → UI should display the full name when using getFullName() (or verify via a quick controller call).
   - Owner with only first or only last → shows the single name correctly.
   - Owner with neither → displays no name (empty string) where used.
3. Code review: ensure no business logic moved into the model beyond formatting, and method uses existing getters/fields with no DB changes.

Notes / Implementation hints
---------------------------
- Prefer trimming stored values in the method rather than assuming callers sanitize inputs.
- Avoid introducing null-pointer risk; use safe guards (e.g., check null or use Optional-like pattern).
- Keep the method lightweight and free of I/O or expensive operations.

Story links / context
---------------------
- STORY: Add getFullName() to Owner returning firstName + space + lastName

Contact
-------
If questions arise about display conventions (middle names, locale-specific ordering), confirm with the product owner before extending the method beyond the simple "first + space + last" rule.
