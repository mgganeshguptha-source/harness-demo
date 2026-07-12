## What Are We Trying to Achieve
Add a read-only convenience method on the Owner domain object to determine whether an owner already has a pet with a given name, so clinic staff can prevent registering duplicate pet names for the same owner.

## Current Behaviour
_Skip — New development_: the Owner class does not currently expose a public hasPet(String name) method.

## Expected Behaviour
- A public method boolean hasPet(String name) is added to the Owner class.
- The method returns true if the owner has at least one Pet whose name matches the supplied name using case-insensitive comparison via String.equalsIgnoreCase.
- The method returns false if no pet matches, if the owner's pet collection is empty, or if the supplied name is null.
- The method does not modify the Owner or Pet state (read-only). It performs no trimming of whitespace; exact string equality ignoring case is used (so " Fido " does not match "Fido").
- Empty string "" is considered a valid input and returns false when no pet has that exact name; it must not throw.

## Acceptance Criteria
- AC1: A public method boolean hasPet(String name) exists on Owner.
- AC2: hasPet("Fido") returns true when the owner has a pet named "Fido".
- AC3: hasPet("fIdO") returns true when the owner has a pet named "Fido" (case-insensitive match using equalsIgnoreCase).
- AC4: hasPet("Rex") returns false when the owner has no pet named "Rex".
- AC5: hasPet(null) returns false and does not throw an exception.
- AC6: The implementation does not modify any Owner or Pet state (read-only).
- AC7: Unit tests cover: a matching name, a non-matching name, a case-insensitive match, and a null argument.

## Edge Cases
- Whitespace sensitivity: names are NOT trimmed. " Fido " does not match "Fido".
- Empty string: hasPet("") returns false unless a pet's name is exactly "".
- Multiple pets with the same name: returns true if any pet matches.
- Null pet collection: if the Owner has no pets (null or empty collection), method returns false.
- Unicode/locale: comparison uses String.equalsIgnoreCase only (no locale-aware case-folding). This is intentional per clarification.

## Constraints
- Using project defaults (copilot-instructions.md not found in repository):
  - Constructor injection on new classes (if any).
  - Follow existing domain model conventions in the project.
  - Unit tests: JUnit 5 + Mockito.
  - Keep method behaviour simple and side-effect free.

> ## ⚠️ Missing copilot-instructions.md
>
> I don't see .github/copilot-instructions.md in this repo.
>
> What this means: the Constraints above use generic Spring Boot defaults. The team's actual coding standards are not being applied.
>
> Recommendation: add .github/copilot-instructions.md if you want repository-specific constraints applied to generated code.

## Out of Scope
- Changing persistence mappings, repository interfaces, or database schema.
- Trimming or normalising pet names (whitespace or Unicode normalisation).
- Introducing locale-aware or full Unicode case-folding beyond String.equalsIgnoreCase.
- Updating callers of Owner or other refactors beyond adding the single method.

## Clarifications Needed
_None — the story includes explicit clarifications: whitespace is not trimmed; equality uses String.equalsIgnoreCase; empty string returns false._
