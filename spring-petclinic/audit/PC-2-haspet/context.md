# Story: Owner.hasPet(name)

Date: 2026-06-29T10:30:03Z

## Story
As a clinic staff member
I want to check whether an owner already has a pet with a given name
So that I can prevent duplicate pet names when registering a new pet for that owner.

## Layer
Backend — domain/model change (Owner model)

## Story type
Enhancement (add small read-only helper method to domain model)

## Current Behaviour
There is no dedicated `hasPet(String name)` helper method on the Owner model (confirm in code). Callers that need this check inspect the owner's pet collection manually.

## Expected Behaviour
- Owner exposes a public method `boolean hasPet(String name)` that checks the owner's pet collection for a name match.
- The method is read-only and must not mutate Owner or Pet state.

## Acceptance Criteria
1. Add a public method `boolean hasPet(String name)` to the `Owner` class.
2. Returns `true` if the owner has a pet whose name matches `name` (case-insensitive).
3. Returns `false` if no pet matches, or if `name` is null.
4. Does not modify existing pets or owner state (read-only).
5. Unit tests cover: a matching name, a non-matching name, case-insensitive match, and a null argument.

## Constraints / Technical defaults
- Use existing project conventions (Spring Boot / JUnit 5). `.github/copilot-instructions.md` not found; defaults applied:
  - Constructor injection for services; domain model changes are plain POJOs.
  - Unit tests: JUnit 5 + AssertJ (or project's existing test libs).
  - Keep method simple and deterministic; no locale-aware case-folding beyond `String.equalsIgnoreCase` (as clarified).

## Tests (explicit)
- Unit test: hasPet_returnsTrue_whenNameMatchesExactIgnoreCase
- Unit test: hasPet_returnsFalse_whenNoMatch
- Unit test: hasPet_isCaseInsensitive
- Unit test: hasPet_returnsFalse_whenNameIsNull
- Ensure tests do not rely on database; test pure model behavior in-memory.

## Out of scope
- UI validation or form-level duplicate checks (front-end).
- Database migrations or schema changes.
- Changing pet naming rules (trimming, normalization) — comparison does NOT trim whitespace per clarifications.

## Clarifications (resolved)
- Name comparison does NOT trim whitespace. " Fido " does not match "Fido".
- Case-insensitivity uses `String.equalsIgnoreCase` only. No full Unicode/locale-aware case-folding.
- Empty string `""` returns false (no match), does not throw.

## Implementation notes for developer
- Add a simple public method to the Owner domain/model that iterates the pet collection and returns true on first match using `pet.getName().equalsIgnoreCase(name)`.
- Ensure method is null-safe: if `name` is null, return false immediately.
- Do not alter pet or owner collections; do not sort or mutate the collection.
- Add unit tests in the same package as other Owner model tests.

---

> ## ⚠️ Missing copilot-instructions.md
>
> I don't see **.github/copilot-instructions.md** in this repo.
>
> **What this means:** the context.md will use generic Spring Boot
> and Angular defaults for the Constraints section. The team's actual
> coding standards are not being applied.
>
> **Recommendation:** create copilot-instructions.md before running
> the analysis prompt. Otherwise Copilot may produce code that doesn't
> match your conventions.
>
> **Continue with defaults, or pause to set up copilot-instructions.md first?**


## Section 8 — Clarifications Needed
- None — all required dimensions were specified in the story and clarifications.


(End of context)