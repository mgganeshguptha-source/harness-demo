## What Are We Trying to Achieve
Add a read-only check so clinic staff can determine whether an owner already has a pet with a given name, preventing duplicate pet names when registering new pets.

## Current Behaviour
No convenience method exists on the owner model to query whether an owner already has a pet by name; callers must iterate the owner's pet collection each time.

## Expected Behaviour
A public method with the signature `boolean hasPet(String name)` is available on the owner model. It returns true if the owner has a pet whose name matches the provided `name` using case-insensitive comparison via `String.equalsIgnoreCase`. It returns false when `name` is null, when no pet matches, or when `name` is the empty string. The method does not modify owner or pet state and does not trim whitespace — e.g., " Fido " does not match "Fido".

## Acceptance Criteria
- AC1: Add a public method `boolean hasPet(String name)` to the owner model.
- AC2: Returns `true` if any pet's name equalsIgnoreCase(name).
- AC3: Returns `false` if no pet matches or if `name` is null.
- AC4: Method is read-only and does not modify owner or pet collections.
- AC5: Unit tests cover: a matching name, a non-matching name, case-insensitive match, and a null argument. Also include a test asserting that empty string returns false.

## Edge Cases
- `name == null` → returns false (no exception).
- `name == ""` (empty string) → returns false.
- Whitespace differences: leading/trailing whitespace is significant; no trimming performed.
- Multiple pets with same name: method returns true if any match exists.
- Names with apostrophes or special chars (O'Brien, García) compare with equalsIgnoreCase — locale-aware folding is _not_ required.
- Concurrent reads: method must not modify collections; callers that mutate concurrently are out-of-scope.

## Constraints
> ## ⚠️ Missing copilot-instructions.md
>
> I don't see **.github/copilot-instructions.md** in this repo.
>
> **What this means:** the context.md will use generic Spring Boot defaults for the Constraints section. The team's actual coding standards are not being applied.
>
> **Recommendation:** create copilot-instructions.md before running the analysis prompt. Otherwise Copilot may produce code that doesn't match your conventions.
>
> **Continue with defaults, or pause to set up copilot-instructions.md first?**

Auto-applied defaults (used because copilot-instructions.md is missing):
- Backend: Constructor injection, standard error response format, Jakarta Validation on inputs, JUnit 5 + Mockito for tests, paginated list responses when applicable.
- Code style: Use private final dependencies, constructor injection, SLF4J for logging, and avoid leaking PHI into logs.

Performance / testing constraints:
- Unit tests only for the new method (no integration required). Ensure tests run under existing JUnit 5 suite.

## Out of Scope
- Any changes to database schema or persistence layer.
- Trimming or normalising pet names (whitespace handling is intentionally unchanged).
- Locale-aware case folding beyond `String.equalsIgnoreCase`.
- API or UI changes — this is an internal model helper only.

## Clarifications Needed
_None — all clarifications provided in the story._
