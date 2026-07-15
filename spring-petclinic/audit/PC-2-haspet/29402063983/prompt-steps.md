# Plan for: Owner.hasPet(name)

**Source:** newest context file in .github/story-context-files (story: "Owner.hasPet(name)")
**Stack:** Backend — Spring Boot (Java) with classic layered packages (model, repository, service, controller)
**Total steps:** 9
**Unresolved clarifications:** None

---

## Before you execute any step

1. This plan is CI-mode, planning-only. Do NOT modify any .java or test files in this phase.
2. Keep the context file (the newest file in .github/story-context-files) available when implementing later.
3. Implementation must follow project conventions: constructor injection, SLF4J, Lombok use per repo policy.

---

## Pre-flight

The plan assumes:

1. Backend uses Spring Boot with plain POJO domain model classes under src/main/java (Owner is a simple model class, not an entity with heavy persistence concerns).
2. The new hasPet method is read-only and must not change Owner or Pet state — no transactional or persistence-side changes required.
3. No non-functional requirements (performance, pagination, security) change; this is a small API/internal model addition verified by unit tests.

If any assumption is wrong, stop and revise the context or split the story.

---

## Impacted Files (seed list — Step 1 will confirm exact files and add IDs)

| ID | Path (seed) | Role |
|----|-------------|------|
| F1 | src/main/java/org/springframework/samples/petclinic/model/Owner.java | Domain model: Owner class — add hasPet(String name) |
| F2 | src/main/java/org/springframework/samples/petclinic/model/Pet.java | Domain model: Pet class — read pet.getName() |
| F3 | src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java | Unit tests for Owner (or equivalent test class) — add tests for hasPet |

> Note: Step 1 (inventory) must confirm the exact paths and test class names used in the repository and add any missing files (e.g., different test package or naming). Do not assume paths — verify.

---

## Step 1 — Inventory: confirm exact file set

**Goal:** Discover and confirm the exact Owner and Pet model file paths and the unit test file(s) to modify.

**Suggested prompt for execution phase (paste into Copilot Chat when implementing):**

> Planning from the context file in .github/story-context-files (story: Owner.hasPet(name)). Start with these candidate files: src/main/java/org/springframework/samples/petclinic/model/Owner.java, src/main/java/org/springframework/samples/petclinic/model/Pet.java, and src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java. Check the repository and confirm the exact file paths and the canonical unit test class that tests Owner behavior. If the test class name differs, add it to the impacted files. Also check if there are any utility classes or test fixtures that must be updated (e.g., PetBuilder, OwnerTestData). Return the confirmed list of files with one-line roles each. Do not modify any files yet.

**Review checkpoint:** Confirm the Impacted Files table above is updated with exact repo paths and assign stable IDs F1..Fn. Ensure no other files (repositories, services, controllers) need changes.

---

## Step 2 — Design: method contract and semantics

**Goal:** Decide precise method signature and behaviour details consistent with ACs and conventions.

**Suggested prompt:**

> Using the confirmed files (F1..), propose the exact method signature to add to F1 (Owner). The Acceptance Criteria require: public boolean hasPet(String name); returns true if any Pet owned by this Owner has a name equal to the argument using case-insensitive comparison via String.equalsIgnoreCase; returns false for null or no match; empty string returns false; must be read-only (no state mutation) and thread-safe for normal POJO access. Show the one-line method signature and a short description of behaviour. Do not write code yet — only confirm the signature and behaviour.

**Review checkpoint:** Confirm method signature exactly: public boolean hasPet(String name) and that the description matches ACs and clarifications.

---

## Step 3 — Implementation plan (method body outline)

**Goal:** Describe exactly how the method will be implemented in F1 (Owner.java) without editing files now.

**Suggested prompt:**

> For F1 (Owner.java), write a precise before/after snippet showing only the new method. The code must iterate the existing pets collection (assumed getter getPets()), return false if name is null or empty, and compare each pet's name using equalsIgnoreCase. Do not modify collections or mutate state. Provide a short, exact code snippet to paste into Owner.java in the implementation phase.

**Planned before/after snippet (to include in later commit):**

Before (conceptual excerpt — no edits now):

```java
// inside class Owner
// existing fields and methods
```

After (exact method to add):

```java
public boolean hasPet(String name) {
    if (name == null || name.isEmpty()) {
        return false;
    }
    if (this.getPets() == null) {
        return false;
    }
    for (Pet pet : this.getPets()) {
        String petName = pet.getName();
        if (petName != null && petName.equalsIgnoreCase(name)) {
            return true;
        }
    }
    return false;
}
```

**Review checkpoint:** Confirm the snippet meets ACs: null -> false, empty string -> false, case-insensitive via equalsIgnoreCase, does not trim, does not mutate state, handles null pet names safely.

---

## Step 4 — Unit test design

**Goal:** Specify the unit tests to add to F3 (or the actual test file confirmed in Step 1). Tests must cover: matching name, non-matching name, case-insensitive match, and null argument. Also include empty string case per clarifications.

**Suggested prompt:**

> For the confirmed Owner test class (F3), add the following unit tests (use JUnit 4 or JUnit 5 consistent with the project):
> 1) testHasPet_matchingName_returnsTrue
> 2) testHasPet_nonMatchingName_returnsFalse
> 3) testHasPet_caseInsensitiveMatch_returnsTrue
> 4) testHasPet_nullArgument_returnsFalse
> 5) testHasPet_emptyString_returnsFalse
>
> For each test, construct an Owner, add a Pet with name "Fido" (or use existing test fixture builder), and assert the expected boolean. Provide exact test method bodies as a code snippet to paste into the test class during implementation.

**Planned test snippets (example, to adapt to project's test framework):**

```java
@Test
public void testHasPet_matchingName_returnsTrue() {
    Owner owner = new Owner();
    Pet pet = new Pet();
    pet.setName("Fido");
    owner.addPet(pet);
    assertTrue(owner.hasPet("Fido"));
}

@Test
public void testHasPet_nonMatchingName_returnsFalse() {
    Owner owner = new Owner();
    Pet pet = new Pet();
    pet.setName("Fido");
    owner.addPet(pet);
    assertFalse(owner.hasPet("Rex"));
}

@Test
public void testHasPet_caseInsensitiveMatch_returnsTrue() {
    Owner owner = new Owner();
    Pet pet = new Pet();
    pet.setName("Fido");
    owner.addPet(pet);
    assertTrue(owner.hasPet("fIdO"));
}

@Test
public void testHasPet_nullArgument_returnsFalse() {
    Owner owner = new Owner();
    Pet pet = new Pet();
    pet.setName("Fido");
    owner.addPet(pet);
    assertFalse(owner.hasPet(null));
}

@Test
public void testHasPet_emptyString_returnsFalse() {
    Owner owner = new Owner();
    Pet pet = new Pet();
    pet.setName("Fido");
    owner.addPet(pet);
    assertFalse(owner.hasPet(""));
}
```

**Review checkpoint:** Confirm tests map to ACs and project uses same testing framework/imports (adjust imports / helper methods accordingly in implementation phase).

---

## Step 5 — Tests for null pet name and empty pet list

**Goal:** Add edge-case tests to ensure method handles null pet names and owner with no pets.

**Suggested prompt:**

> Add tests to verify: if a Pet in the collection has null name, hasPet("Fido") still returns false (unless another pet matches); and if owner.getPets() is empty or null, hasPet returns false. Provide code snippets.

**Planned snippets:**

```java
@Test
public void testHasPet_nullPetName_doesNotThrowAndReturnsFalse() {
    Owner owner = new Owner();
    Pet pet = new Pet();
    pet.setName(null);
    owner.addPet(pet);
    assertFalse(owner.hasPet("Fido"));
}

@Test
public void testHasPet_noPets_returnsFalse() {
    Owner owner = new Owner();
    // owner.getPets() is null or empty depending on model
    assertFalse(owner.hasPet("Fido"));
}
```

**Review checkpoint:** Confirm edge-case coverage.

---

## Step 6 — Implementation notes and style checks

**Goal:** Ensure implementation follows repo conventions.

**Suggested prompt:**

> When adding the method to F1, ensure:
> - Use existing getter getPets() rather than direct field access.
> - Do not introduce Lombok annotations changes.
> - Keep method public in the model class.
> - Add a Javadoc comment describing behaviour and refer to ACs.
> - Do not change equals/hashCode or serialization behavior.
>
> Also, update no other files.

**Review checkpoint:** Verify added Javadoc and code style match repo conventions (indentation, braces, imports). No other files modified.

---

## Step 7 — Convention drift check

**Goal:** After implementation, review changed files against .github/copilot-instructions.md (coding conventions).

**Suggested prompt:**

> Review the diffs for F1 and F3 against the project's copilot-instructions.md. List any convention drifts (e.g., field access vs getter, Lombok usage, logging patterns). Do not auto-fix — list required follow-ups.

**Review checkpoint:** Confirm zero or acceptable minor drifts; address any flagged items before PR.

---

## Step 8 — Manual validation (second-to-last; run by developer)

**Goal:** Manually verify acceptance criteria against the running code or via unit test run.

**Suggested prompt (for guidance only):**

> List manual validation steps derived from the acceptance criteria. Include exact commands to run unit tests (e.g., mvn -Dtest=OwnerTests test or ./mvnw test) and which test methods to inspect. Describe what to assert in each test outcome.

**Review checkpoint:** All specified tests pass locally/CI. Confirm ACs 1–5 satisfied.

---

## Step 9 — Done criteria

Before opening a PR, confirm:

- [ ] F1 (Owner.java) contains the public boolean hasPet(String name) method with the exact behaviour in Step 3.
- [ ] Unit tests added in F3 cover: matching name, non-matching name, case-insensitive match, null argument, empty string, null pet name, and no-pets case.
- [ ] No other source files modified.
- [ ] Tests pass locally and in CI (run project's test command).
- [ ] Code follows .github/copilot-instructions.md — address any convention drift from Step 7.
- [ ] Javadoc/comment added describing behaviour and AC mapping.

---

## Implementation-phase checklist (for later)

- Implement Step 1–6 in order, committing small atomic changes: one commit for Owner.java change, one commit for tests.
- Run unit tests after adding tests.
- Include Co-authored-by trailer in commits per repo policy (Copilot trailer is added automatically by tooling in previous runs; ensure commit message includes it if required).

---

## Notes and rationale

- The implementation is intentionally simple and defensive: checks for null/empty input, null pet names, and null pet collections. Uses equalsIgnoreCase per clarification and does not perform trimming or locale-sensitive folding.
- No persistence or service-layer change is required because behaviour is confined to the domain model.

---

Plan written for CI: do not implement now. When ready to implement, follow steps 1 through 9 in order and paste the code snippets above into the confirmed files.

## --- EXECUTION RECORD (appended by harness) ---
- timestamp: 2026-07-15T08:50:44
- phase: coding
- approved impacted files: ['src/main/java/org/springframework/samples/petclinic/model/Owner.java', 'src/main/java/org/springframework/samples/petclinic/model/Pet.java', 'src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java']
- actually touched: ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java']
- ⚠ SCOPE ADDITION (touched, not in approved plan): ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java']
  -> review this scope change before approving the coding phase.
- review status: APPROVED by human at 2026-07-15T08:50:44

## --- EXECUTION RECORD (appended by harness) ---
- timestamp: 2026-07-15T08:51:47
- phase: coding
- approved impacted files: ['src/main/java/org/springframework/samples/petclinic/model/Owner.java', 'src/main/java/org/springframework/samples/petclinic/model/Pet.java', 'src/test/java/org/springframework/samples/petclinic/model/OwnerTests.java']
- actually touched: ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java']
- ⚠ SCOPE ADDITION (touched, not in approved plan): ['src/main/java/org/springframework/samples/petclinic/owner/Owner.java']
  -> review this scope change before approving the coding phase.
- review status: APPROVED by human at 2026-07-15T08:51:47
