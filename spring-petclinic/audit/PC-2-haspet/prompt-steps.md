# Plan for: Owner.hasPet(name)

**Source:** newest file in .github/story-context-files/ (story: "Owner.hasPet(name)")
**Stack:** backend — Spring Boot (Java) with JUnit tests
**Total steps:** 9
**Unresolved clarifications:** None

---

## Before you execute any step

1. Keep the context file (newest file in .github/story-context-files/) in scope while executing these steps in subsequent implementation phases.
2. Follow repository Java conventions (constructor injection, private final fields, SLF4J). Do not change unrelated files.
3. This plan only describes intended edits. DO NOT edit source or test files in this planning phase — implementation occurs later.

---

## Pre-flight

The plan assumes:

1. Backend uses Spring Boot with standard src/main/java and src/test/java layout and JUnit 5 for tests.
2. Existing Owner and Pet model classes follow the conventional names and packages used in this repo (e.g. org.springframework.samples.petclinic.model.Owner, Pet). The change is additive (read-only) and preserves all existing behavior.
3. No non-functional constraints (performance/accessibility) apply to this tiny, in-memory model method; unit tests are sufficient to verify correctness.

If any assumption is wrong, stop and correct the context or ask for clarification.

---

## Impacted Files

| ID | Path | Role |
|----|------|------|
| F1 | src/main/java/org/springframework/samples/petclinic/model/Owner.java | Domain model: add hasPet(String name) read-only helper |
| F2 | src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java | Unit tests for Owner.hasPet — add new test cases |
| F3 | src/main/java/org/springframework/samples/petclinic/model/Pet.java | Domain model (read-only) — referenced by Owner.hasPet |

> Later steps reference files by ID (F1, F2, F3). Do not modify other files.

---

## Step 1 — Inventory (confirm files)

**Goal:** Confirm the exact file locations and existing method signatures for Owner and Pet classes, and identify the canonical test class to extend.

**Suggested prompt:**

> Inspect the repository and confirm the concrete file paths and package declarations for the Owner and Pet model classes, and the Owner unit test class. Starting seed paths: F1 (src/main/java/org/springframework/samples/petclinic/model/Owner.java), F3 (src/main/java/org/springframework/samples/petclinic/model/Pet.java), F2 (src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java). If any path differs, return the real path. Do not modify files — only list exact paths and the Owner class's current public API (field names, existing methods relevant to pet access).

**Review checkpoint:** Confirm the three file paths and Owner's existing methods for accessing pets (e.g., getPets()). Record exact paths in the Impacted Files table if they differ.

---

## Step 2 — Design the method signature and semantics

**Goal:** Decide exact signature and contract for Owner.hasPet(name) consistent with ACs and repo conventions.

**Suggested prompt:**

> Propose the exact method signature and Javadoc for an Owner.hasPet(String name) helper that: returns true if this Owner has a Pet whose name equals the provided name using case-insensitive comparison (String.equalsIgnoreCase), returns false for null or empty name, does not trim whitespace, and does not modify state. Output the canonical Javadoc and any edge-case notes (null, empty string). Do not change code yet.

**Review checkpoint:** Confirm the signature is `public boolean hasPet(String name)` and that the semantics match ACs 1–4.

---

## Step 3 — Implementation plan for model (F1)

**Goal:** Prepare the exact code to add to Owner.java (F1). This is an additive, read-only helper.

**Suggested prompt:**

> Edit F1 (Owner.java) to add a public helper method `hasPet(String name)`. The method must:
> - Return false if name == null or name.isEmpty()
> - Iterate the owner's pets (use existing getter, e.g., getPets()) and return true if any pet.getName().equalsIgnoreCase(name)
> - Not modify any collections or fields
> - Be concise and unit-testable
>
> Provide a before/after snippet for the Owner class showing only the relevant region. Do not run or apply edits.

**Before (example fragment):**

```java
public class Owner {
    private Set<Pet> pets;

    public Set<Pet> getPets() {
        return this.pets;
    }

    // ... other methods
}
```

**After (add this method):**

```java
/**
 * Returns true if the owner has a pet with the given name (case-insensitive).
 * Returns false if name is null, empty, or no pet matches. This method is read-only.
 */
public boolean hasPet(String name) {
    if (name == null || name.isEmpty()) {
        return false;
    }
    if (this.getPets() == null) {
        return false;
    }
    for (Pet pet : this.getPets()) {
        if (pet != null && pet.getName() != null && pet.getName().equalsIgnoreCase(name)) {
            return true;
        }
    }
    return false;
}
```

**Review checkpoint:** Confirm the snippet matches repository code style and uses getPets() accessor rather than direct field access if that matches existing code.

---

## Step 4 — Tests to add (F2)

**Goal:** Add unit tests covering acceptance criteria: matching name, non-matching name, case-insensitive match, null argument, empty string returns false.

**Suggested prompt:**

> Edit F2 (Owner unit tests) to add new test methods for Owner.hasPet(String). Use JUnit 5 and the repository's test utilities. Include four test cases:
> 1. matchingName_returnsTrue — owner with a pet named "Fido" -> hasPet("Fido") == true
> 2. nonMatchingName_returnsFalse — owner with pet "Fido" -> hasPet("Spot") == false
> 3. caseInsensitiveMatch_returnsTrue — owner with pet "FIDO" -> hasPet("fido") == true
> 4. nullName_returnsFalse — hasPet(null) == false
> 5. emptyName_returnsFalse — hasPet("") == false
>
> Provide example test method snippets (do not run)

**Example test snippet:**

```java
@Test
void matchingName_returnsTrue() {
    Owner owner = new Owner();
    Pet p = new Pet();
    p.setName("Fido");
    owner.getPets().add(p);

    assertTrue(owner.hasPet("Fido"));
}

@Test
void caseInsensitiveMatch_returnsTrue() {
    Owner owner = new Owner();
    Pet p = new Pet();
    p.setName("FIDO");
    owner.getPets().add(p);

    assertTrue(owner.hasPet("fido"));
}

@Test
void nullName_returnsFalse() {
    Owner owner = new Owner();
    assertFalse(owner.hasPet(null));
}

@Test
void emptyName_returnsFalse() {
    Owner owner = new Owner();
    assertFalse(owner.hasPet(""));
}
```

**Review checkpoint:** Confirm tests compile against current model (constructor availability, getPets() returns a mutable collection). If getPets() returns null by default, tests must initialize the collection first (use existing patterns in other tests).

---

## Step 5 — Edge-case and defensive notes

**Goal:** Ensure implementation handles null pet names and null pet collection safely.

**Suggested prompt:**

> Review F1 and F3 and confirm defensive checks: skip null pets, skip pets with null names, and treat null owner pet collection as empty. If repository uses an immutable emptySet by default, ensure tests initialize a mutable collection before adding.

**Review checkpoint:** Confirm no NullPointerException risk in typical model state and tests account for initialization semantics.

---

## Step 6 — Run tests locally (implementation phase)

**Goal:** Execute unit tests and verify the new tests pass. (IMPLEMENTATION NOTE: run after implementing changes.)

**Suggested action (for implementation phase):**

- Run `mvn -q -DskipTests=false test -Dtest=**/*Owner*` or use repository's test command.
- If tests fail, inspect stack traces, fix null-init issues or adjust tests to follow existing patterns.

**Review checkpoint:** All new Owner.hasPet tests pass; no unrelated tests broken.

---

## Step 7 — Convention drift check

**Goal:** Verify changed files follow project conventions (.github/copilot-instructions.md).

**Suggested prompt (implementation phase):**

> Review modified files (F1, F2) for coding convention drift against .github/copilot-instructions.md and repository style (logging, injection, imports). List any drift and small fixes to apply.

**Review checkpoint:** No drift that requires design changes. Minor style fixes ok.

---

## Step 8 — Validation against Acceptance Criteria (manual)

**Goal:** Manually verify each AC using the running unit-test results and code review.

**Checklist:**
- AC1: Owner has public method boolean hasPet(String name) — confirmed by signature
- AC2: Returns true when a pet name matches case-insensitively — covered by case-insensitive test
- AC3: Returns false if no pet matches or name is null — covered by non-matching and null tests
- AC4: Method is read-only — review code to ensure no modifications to collections
- AC5: Unit tests cover matching, non-matching, case-insensitive, null, and empty string — confirm presence and passing

**Review checkpoint:** Mark each AC pass/fail. If any fail, loop back to the appropriate step.

---

## Done criteria

Before opening a PR, confirm:

- F1 contains the new `public boolean hasPet(String name)` method with the agreed semantics and Javadoc.
- F2 contains unit tests for matching name, non-matching, case-insensitive match, null, and empty string, all passing.
- No behavior outside Owner.hasPet was modified.
- Code compiles and tests pass locally: `mvn -q test` (or repo standard command).
- A short PR description explains the change, references this story, and includes example usage and test coverage notes.


---

# Implementation notes for the developer (to paste into implementation-phase prompt)

- Add the method exactly as shown in the "After" snippet in Step 3 to F1.
- Add the test methods shown in Step 4 to F2, adapting collection initialization to match repository patterns (e.g., `owner.setPets(new HashSet<>())` if required).
- Keep code defensive: check for nulls, do not mutate collections, use `equalsIgnoreCase` for comparison per clarification.


Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

## --- EXECUTION RECORD (appended by harness) ---
- timestamp: 2026-07-01T15:34:54
- phase: coding
- approved impacted files: ['src/main/java/org/springframework/samples/petclinic/model/Owner.java', 'src/main/java/org/springframework/samples/petclinic/model/Pet.java', 'src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java']
- actually touched: ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java']
- ⚠ SCOPE ADDITION (touched, not in approved plan): ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java']
  -> review this scope change before approving the coding phase.
- review status: APPROVED by human at 2026-07-01T15:34:54
