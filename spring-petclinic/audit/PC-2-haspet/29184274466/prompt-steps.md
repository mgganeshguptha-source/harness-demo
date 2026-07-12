# Plan for: Owner.hasPet(name)

**Source:** owner-has-pet-context-260712-072822.md
**Stack:** Backend — Spring Boot (Java, JUnit 5)
**Total steps:** 8
**Unresolved clarifications:** None

---

## Before you execute any step

1. Keep owner-has-pet-context-260712-072822.md in your Copilot Chat context throughout the plan. Re-attach it after any session restart.
2. There is no .github/copilot-instructions.md in this repo; the plan follows generic Spring Boot defaults (constructor injection, JUnit 5, Mockito) as noted in the context file.
3. Execute steps in order. This plan is CI-mode: it's planning-only. Do NOT modify source or test files now — implementation happens later. This file is the single allowed write for this phase.

---

## Pre-flight

Assumptions the plan makes:

1. Stack assumption — Backend uses Spring Boot with standard domain model in src/main/java; tests use JUnit 5. Owner is a domain object (not a DTO) and lives under org.springframework.samples.petclinic.owner.
2. Behaviour preservation — All existing Owner behaviour (getPet(...) semantics, addPet, getFullName, persistence mappings) must remain unchanged. The new method is a read-only convenience delegating to existing logic.
3. Non-functional handling — No performance or load concerns; method is O(n) over the owner's pet list (small). No additional caching or DB changes required.

If any assumption is wrong, stop and revise the context file before proceeding.

---

## Impacted Files

| ID | Path | Role |
|----|------|------|
| F1 | src/main/java/org/springframework/samples/petclinic/owner/Owner.java | Domain model: add public boolean hasPet(String name) convenience method (read-only), delegates to existing getPet(name) logic.
| F2 | src/test/java/org/springframework/samples/petclinic/owner/OwnerTest.java | Unit tests: add tests covering matching name, non-matching name, case-insensitive match, and null argument. Use JUnit 5.

> Later steps reference files by ID (F1, F2). Do NOT re-list full paths in later-step prompts; refer to the Impacted Files table.

---

## Step 1 — Inventory (confirm the affected files and test conventions)

**Goal:** Confirm the exact files to change and the project's test conventions (JUnit 5 style, package imports, existing Owner.getPet behaviour).

**Suggested prompt:**

> Planning from: owner-has-pet-context-260712-072822.md. Inspect these seed files as candidates: src/main/java/org/springframework/samples/petclinic/owner/Owner.java, src/test/java/org/springframework/samples/petclinic/owner/OwnerTest.java. Confirm they are the correct Owner domain class and unit test file to update for adding hasPet(String). Also confirm the test framework (JUnit 5) and assert style in tests. Do not apply edits — only list the final impacted files and any additional non-code artifacts required (none expected). Return a short table: path + one-line role.

**Review checkpoint:** Confirm F1 and F2 in the Impacted Files block match the files returned by the inventory step. If additional files are required (e.g., a new test helper), add them to the Impacted Files block before proceeding.

---

## Step 2 — Design the method

**Goal:** Decide the precise implementation approach for hasPet(String name).

**Suggested prompt:**

> Using the Owner class in F1, propose a minimal, side-effect-free implementation for a public method `boolean hasPet(String name)` that satisfies the acceptance criteria in owner-has-pet-context-260712-072822.md. The method should: (a) return false if name is null, (b) perform a case-insensitive equality check using `String.equalsIgnoreCase`, (c) not modify Owner or Pet state, (d) prefer delegating to existing `getPet(String)`/`getPet(String, boolean)` if that yields correct semantics. Present the exact method signature and a before/after snippet for F1. Do not modify files.

**Review checkpoint:** Confirm the proposed method signature matches AC1 and that the approach uses existing getPet logic or minimal iteration without side-effects.

---

## Step 3 — Implementation plan for F1 (Owner.java)

**Goal:** Describe exact edits to add the method to Owner.java.

**Suggested prompt:**

> Edit F1 (Owner.java). Add a public method `boolean hasPet(String name)` that is read-only and satisfies the ACs. Provide a precise before/after code snippet. Do not change other methods or annotations.

**Before / After snippet (example):**

Before (excerpt from F1):

```java
// existing API in Owner.java
public Pet getPet(String name) {
    return getPet(name, false);
}
```

After (add this method to F1, adjacent to getPet methods):

```java
/**
 * Return true if this Owner has a Pet whose name equals the supplied name (case-insensitive).
 * Returns false if name is null or no matching Pet exists. Read-only; does not modify Owner state.
 */
public boolean hasPet(String name) {
    if (name == null) {
        return false;
    }
    return getPet(name) != null;
}
```

**Review checkpoint:** Confirm the added method's semantics: null => false, uses equalsIgnoreCase via existing getPet, no side-effects, meets AC2–AC6.

---

## Step 4 — Test design (which tests to add and where)

**Goal:** Define the unit tests required to satisfy AC7.

**Suggested prompt:**

> Update F2 (OwnerTest.java). Add four unit tests covering: (1) matching name returns true, (2) non-matching name returns false, (3) case-insensitive match returns true, (4) null argument returns false and does not throw. Use JUnit 5 assertions (assertTrue/assertFalse). Show the exact test method signatures and example bodies as code snippets. Do not run tests yet.

**Test snippets (to add to F2):**

```java
@Test
void hasPet_returnsTrue_whenPetNameMatchesExactly() {
    Owner owner = new Owner();
    Pet p = new Pet();
    p.setName("Fido");
    owner.getPets().add(p);

    assertTrue(owner.hasPet("Fido"));
}

@Test
void hasPet_returnsFalse_whenNoPetMatches() {
    Owner owner = new Owner();
    Pet p = new Pet();
    p.setName("Fido");
    owner.getPets().add(p);

    assertFalse(owner.hasPet("Rex"));
}

@Test
void hasPet_isCaseInsensitive() {
    Owner owner = new Owner();
    Pet p = new Pet();
    p.setName("Fido");
    owner.getPets().add(p);

    assertTrue(owner.hasPet("fIdO"));
}

@Test
void hasPet_returnsFalse_whenNameIsNull() {
    Owner owner = new Owner();
    // no pets added

    assertFalse(owner.hasPet(null));
}
```

**Review checkpoint:** Confirm tests use project imports and patterns (JUnit 5) and do not rely on persistence. Prefer in-memory domain objects only.

---

## Step 5 — Run unit tests locally (implementation phase will run these)

**Goal:** After implementation, run the unit test suite and ensure added tests pass.

**Suggested prompt (for the implementation phase):**

> After editing F1 and F2, run `./mvnw -q -DskipTests=false test` (or the repository's standard test command). If failures occur, inspect diffs and adjust. Do not merge until all tests pass locally.

**Review checkpoint:** All tests pass; newly added hasPet tests included.

---

## Step 6 — Convention drift check

**Goal:** Verify that the changes follow repository conventions (no field injection, use existing domain patterns, small & safe change).

**Suggested prompt:**

> Review the diffs for F1 and F2 against the project's conventions. Flag any deviations such as new dependencies, use of static helpers, or added public state. Do not auto-fix; list drift items for manual review.

**Review checkpoint:** No convention drift; change is a single short method and a few unit tests.

---

## Step 7 — Manual validation against acceptance criteria (second-to-last)

**Goal:** Provide a manual checklist to verify each Acceptance Criterion against the running application or via unit tests.

**Suggested prompt (for the developer to perform after implementation):**

> List each AC from owner-has-pet-context-260712-072822.md and, for each, provide an exact manual verification step (unit test name or small scenario) that demonstrates it passes. E.g., AC2: run hasPet_returnsTrue_whenPetNameMatchesExactly; AC5: run hasPet_returnsFalse_whenNameIsNull.

**Review checkpoint:** Each AC maps cleanly to a unit test or behaviour; mark them Pass/Fail during validation.

---

## Step 8 — Done criteria

Before opening a PR, confirm:

- [ ] F1: Owner.java contains `public boolean hasPet(String name)` with semantics: null → false, delegates to existing logic, no state mutation.
- [ ] F2: Unit tests covering matching name, non-matching name, case-insensitive match, and null argument are present and pass.
- [ ] All unit tests pass locally (`mvn test`).
- [ ] No other files were changed.
- [ ] The change is small, well-documented in the PR description, and references owner-has-pet-context-260712-072822.md.

---

## Notes & rationale

- The Owner class already exposes `getPet(String)` which performs a case-insensitive match using `equalsIgnoreCase`. A tiny convenience `hasPet(String)` keeps callers simple and reduces duplication.
- The implementation is intentionally minimal and read-only to satisfy AC4 and repository conventions.

---

Plan written to .harness/prompt-steps.md. Execute implementation by applying the edits described in Steps 3 and 4, then follow Steps 5–8 to verify and open a PR.

## --- EXECUTION RECORD (appended by harness) ---
- timestamp: 2026-07-12T07:30:45
- phase: coding
- approved impacted files: ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java', 'src/test/java/org/springframework/samples/petclinic/owner/OwnerTest.java']
- actually touched: ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java']
- scope: matches approved plan (no additions)
- review status: APPROVED by human at 2026-07-12T07:30:45
