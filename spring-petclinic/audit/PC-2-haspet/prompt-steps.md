# Plan for: Owner.hasPet(name)

**Source:** newest file in .github/story-context-files/ (story: "Owner.hasPet(name)")
**Stack:** backend — Spring Boot (Java)
**Total steps:** 10
**Unresolved clarifications:** None

---

## Before you execute any step

1. This is CI-mode planning only. Do NOT modify any source or test files in this phase.
2. Keep the context file from .github/story-context-files/ available during implementation steps.
3. Each implementation step later will reference file IDs from the Impacted Files block; do not use full paths outside Step 1.

---

## Pre-flight

The plan assumes:

1. Backend uses Spring Boot with standard packages (model under src/main/java/**/model). The Owner entity is the model to change.
2. Behaviour preservation: existing Owner and Pet behaviour remains unchanged except for the added read-only hasPet(String) method. No state mutation, no change to persistence mapping.
3. Non-functional: this is a tiny read-only method — performance is negligible. Unit tests will validate behaviour; no load testing required.

---

## Impacted Files (seed candidates)

| ID | Path | Role |
|----|------|------|
| F1 | src/main/java/org/springframework/samples/petclinic/model/Owner.java | Domain model: add read-only hasPet(String) method |
| F2 | src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java | Unit tests for Owner.hasPet — add test cases (matching, non-matching, case-insensitive, null) |

> If the file paths differ in the repo, locate the Owner model and its existing unit test file in the corresponding packages. Add any missing test file under src/test matching the package of Owner.

---

## Step 1 — Inventory (confirm file set)

Goal: Confirm the exact Owner model and test file paths, and whether any additional helper classes (e.g., Pet model, test fixtures) must be touched.

Suggested prompt (CI):

> Read the newest context file in .github/story-context-files/ (story: Owner.hasPet(name)). List the concrete paths in this repository that will be touched to implement a read-only domain method on Owner that checks for a pet name match: the Owner model, Pet model (if needed), and the unit test file(s). Include package-qualified class names and any non-code artifacts required (none expected). Return one line per file: path + one-line role. Do not modify files.

Review checkpoint: Confirm F1 points to the actual Owner.java file and F2 to the test file. If F2 doesn't exist, plan to create it in the same package as Owner under src/test.

---

## Step 2 — Design the method (options)

Goal: Decide implementation approach for hasPet(String name).

Suggested prompt:

> Given Owner has a collection of Pet objects (List<Pet> getPets() or Set<Pet>), propose 2 implementation options for hasPet(String name): (A) imperative loop over pets returning true on equalsIgnoreCase, (B) using Java Streams with anyMatch and equalsIgnoreCase. For each option list pros/cons and which aligns best with existing code style in the repo. Do not modify code.

Review checkpoint: Choose the simplest approach consistent with repo style (likely imperative loop or streams). Ensure approach is read-only and does not call persistence or mutate entities.

---

## Step 3 — Implementation spec (method signature and behaviour)

Goal: Specify exact method signature, contract, and edge-case behaviour to implement.

Specification (to be implemented later):

- Add to Owner.java:

```java
// New public read-only convenience method
public boolean hasPet(String name)
```

Contract:
- Returns true if the owner has any Pet p where p.getName().equalsIgnoreCase(name).
- Returns false if name is null, or empty string, or no match found.
- Does not trim whitespace (per clarification). Uses String.equalsIgnoreCase only.
- Does not modify Owner or Pet state.

Before/After snippet (conceptual):

Owner.java — before (excerpt):

```java
public class Owner {
    private Set<Pet> pets;

    public Set<Pet> getPets() { return this.pets; }
    // ... other methods
}
```

Owner.java — after (excerpt):

```java
public class Owner {
    private Set<Pet> pets;

    public Set<Pet> getPets() { return this.pets; }

    public boolean hasPet(String name) {
        if (name == null || name.isEmpty()) {
            return false;
        }
        for (Pet p : getPets()) {
            if (p != null && p.getName() != null && p.getName().equalsIgnoreCase(name)) {
                return true;
            }
        }
        return false;
    }
    // ... other methods
}
```

Note: Implementation must guard against null pet names and null pet collection.

Review checkpoint: Confirm signature and null/empty handling satisfy ACs 1–4.

---

## Step 4 — Test design (which tests to add)

Goal: Define unit tests required by ACs.

Tests to add (descriptions & suggested names):

1. testHasPet_matchingName_returnsTrue — owner with a pet named "Fido"; hasPet("Fido") -> true
2. testHasPet_nonMatchingName_returnsFalse — owner with pets none match; hasPet("Rex") -> false
3. testHasPet_caseInsensitiveMatch_returnsTrue — pet name "fIdO" vs hasPet("FIDO") -> true
4. testHasPet_nullArgument_returnsFalse — hasPet(null) -> false
5. testHasPet_emptyString_returnsFalse — hasPet("") -> false (clarification stated empty string returns false)

Suggested test snippet (conceptual, JUnit 4/5 depending on project):

```java
@Test
public void testHasPet_matchingName_returnsTrue() {
    Owner owner = new Owner();
    Pet p = new Pet(); p.setName("Fido");
    owner.getPets().add(p);
    assertTrue(owner.hasPet("Fido"));
}
```

Review checkpoint: Confirm tests cover the ACs and edge cases. Match test framework/version used in repository (JUnit 4 vs JUnit 5) and use existing test utilities/fixture builders if present.

---

## Step 5 — Implementation step (developer action)

Goal: Implement the hasPet(String) method in F1 (Owner.java) following the chosen option from Step 2 and the spec in Step 3.

Suggested prompt (for implementation phase — run later):

> Edit F1 (Owner.java). Add the public boolean hasPet(String name) method as specified in the plan. Guard against null pets collection, null pet names, and return false for null/empty argument. Use the repository's preferred style (imperative or streams per Step 2). Do not change any other methods or persistence annotations.

Review checkpoint: Diff should only add the new method; no other changes.

---

## Step 6 — Add unit tests (developer action)

Goal: Add/modify F2 (OwnerTests.java) to include the five tests from Step 4.

Suggested prompt (for implementation phase):

> Edit F2 (OwnerTests.java). Add the five unit tests described in Step 4. Use the project's test framework and fixture helpers. Keep tests small and independent; do not hit the DB — instantiate Owner/Pet objects in-memory.

Review checkpoint: Tests compile and target only Owner.hasPet behaviour. No changes to production code other than the new method.

---

## Step 7 — Run tests and fix

Goal: Run unit tests, fix any compile/test failures, and ensure all new tests pass.

Suggested actions:
- mvn -q -DskipTests=false test (or appropriate Gradle/Maven command used by repo)
- If tests fail, inspect stack traces, fix implementation or tests accordingly.

Review checkpoint: All tests (including existing) pass locally.

---

## Step 8 — Convention drift check

Goal: Verify new code follows project conventions (.github/copilot-instructions.md) and other guardrails (null handling, logging, no PHI exposure).

Suggested prompt (for implementation phase):

> Review the diff for F1 and F2 against .github/copilot-instructions.md and the project's Java conventions. List any convention drifts (constructor injection, logging style, visibility, formatting). Do not auto-fix — list items for developer to address.

Review checkpoint: No convention drift, or drift items are small and documented.

---

## Step 9 — Validation (manual)

Goal: Manually verify acceptance criteria against the running code (unit tests + quick sanity checks).

Validation checklist (must all pass):
- AC1: public boolean hasPet(String name) exists on Owner.
- AC2: Matching pet name (case-insensitive) returns true.
- AC3: Non-matching name or null argument returns false.
- AC4: Method is read-only (no persistence changes or side effects) — verify by code review.
- AC5: Unit tests cover matching, non-matching, case-insensitive, null argument, and empty string.

If any item fails, revert to the relevant step and fix.

---

## Step 10 — Done criteria / PR checklist

Before opening a PR, confirm:
- New method added only to Owner.java (F1) with the agreed signature and behaviour.
- Unit tests added/updated in F2 and all tests pass locally.
- No other files modified.
- The change is small, documented in the PR description, and references the context story.
- Include a short note in PR: "Adds Owner.hasPet(String) — read-only convenience method; unit tests added." 

---

## Notes for implementer

- Implementation must handle null collections and null pet names defensively.
- Keep the method simple and readable; prefer clarity over clever stream one-liners if the repo tends toward imperative style.
- Do not add logging or throw exceptions for null/empty input — per AC return false.
- Add TODO audit comment only if the method will be used to gate PHI-handling flows (unlikely here).




## --- EXECUTION RECORD (appended by harness) ---
- timestamp: 2026-06-29T10:32:42
- phase: coding
- approved impacted files: ['src/main/java/org/springframework/samples/petclinic/model/Owner.java', 'src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java']
- actually touched: ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java']
- ⚠ SCOPE ADDITION (touched, not in approved plan): ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java']
  -> review this scope change before approving the coding phase.
- review status: APPROVED by human at 2026-06-29T10:32:42
