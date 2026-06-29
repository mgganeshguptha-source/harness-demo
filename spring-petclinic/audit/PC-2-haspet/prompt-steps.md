# Plan for: Owner.hasPet(name)

**Source:** owner-has-pet-context-260629-101011.md + .github/copilot-instructions.md
**Stack:** Backend — Spring Boot (Spring Data/JPA) (inferred)
**Total steps:** 9
**Unresolved clarifications:** None

---

## Before you execute any step

1. Keep owner-has-pet-context-260629-101011.md in your Copilot Chat context throughout the plan.
2. .github/copilot-instructions.md is auto-loaded by Copilot when present in the repo.
3. Execute steps in one Copilot Chat session when possible. If you restart, paste the full plan back into the new chat alongside the context file.
4. When a step asks Copilot to modify a file, confirm Copilot read the file's current contents before applying edits.

---

## Pre-flight

The plan assumes:

1. Backend uses Spring Boot with standard package layout under src/main/java and JUnit 5 for unit tests (matches this repo).
2. Existing behaviours (getPet(...) methods) remain unchanged; hasPet(name) is a read-only helper that must not modify Owner or Pet state.
3. Non-functional constraints: this is a tiny, local-change unit-testable story — no performance or migration work required.

If any assumption is wrong, stop and revise the context file before proceeding.

---

## Impacted Files (seed — Step 1 will confirm and may add files)

| ID | Path | Role |
|----|------|------|
| F1 | src/main/java/org/springframework/samples/petclinic/owner/Owner.java | Domain model: add hasPet(String) method (read-only helper) |
| F2 | src/main/java/org/springframework/samples/petclinic/owner/Pet.java | Domain model: referenced by Owner (read-only) |
| F3 | src/test/java/org/springframework/samples/petclinic/owner/OwnerTest.java | Existing owner unit tests (extend with new tests or add a new test file) |

> Later steps reference files by ID (F1, F2, F3). Step 1 may add additional files (e.g., a new test file); if it does, a new ID will be appended.

---

## Step 1 — Inventory: confirm the exact files to change

**Goal:** Confirm the concrete file set to edit and any non-code artifacts required (none expected).

**Suggested prompt:**

> Planning from owner-has-pet-context-260629-101011.md. Start with these candidate files: F1 (src/main/java/org/springframework/samples/petclinic/owner/Owner.java), F2 (src/main/java/org/springframework/samples/petclinic/owner/Pet.java), F3 (src/test/java/org/springframework/samples/petclinic/owner/OwnerTest.java). Read each file and return the confirmed Impacted Files table (ID | Path | Role). Add any genuinely required files (for example, a new test file) and remove any not impacted. Do not propose edits yet.

**Review checkpoint:** Confirm the Impacted Files block above matches Copilot's reading. If a different test file is preferred (create OwnerHasPetTest.java vs modifying OwnerTest.java), record it as a new ID (F4) and continue.

---

## Step 2 — Design: implementation approach for hasPet

**Goal:** Decide the simplest, safe implementation matching ACs.

**Suggested prompt:**

> Given F1 (Owner.java) and F2 (Pet.java), propose 2 concise implementations for hasPet(String name): (A) iterate over getPets() and use equalsIgnoreCase; (B) reuse existing getPet(name) helper if semantics match. For each option, list pros/cons (read-only safety, null handling, code duplication). Recommend one. Do not modify files yet.

**Review checkpoint:** Pick the option that: (a) uses equalsIgnoreCase, (b) returns false on null, (c) does not modify state. Prefer reusing existing getPet(name) if it returns non-null for matches and its ignoreNew semantics are acceptable; otherwise implement a small loop.

---

## Step 3 — Implement: add hasPet(String name) to F1 (Owner.java)

**Goal:** Add a public boolean hasPet(String name) method to Owner that returns true for case-insensitive matches, false if name is null or no match, and does not modify owner/pets.

**Suggested prompt:**

> Edit F1 (Owner.java). Add the following public method (Javadoc + implementation):
>
> public boolean hasPet(String name) {
>   if (name == null) return false;
>   for (Pet pet : getPets()) {
>     String compName = pet.getName();
>     if (compName != null && compName.equalsIgnoreCase(name)) {
>       return true;
>     }
>   }
>   return false;
> }
>
> Place the method close to the existing getPet(...) helpers. Do not change other code or persistence annotations. Keep the method read-only.

**Review checkpoint:** The diff should show only the new method added to F1. No other methods or imports changed. Method uses equalsIgnoreCase and explicitly short-circuits on name==null.

---

## Step 4 — Tests: add unit tests for hasPet

**Goal:** Add unit tests covering: matching name, non-matching name, case-insensitive match, null argument (and optional empty-string behaviour per clarification).

**Suggested prompt:**

> Create or update tests touching F3 (OwnerTest.java) or add a new test file (e.g., src/test/java/org/springframework/samples/petclinic/owner/OwnerHasPetTest.java). Add JUnit 5 tests:
> - hasPet_returnsTrueForMatchingName
> - hasPet_returnsFalseForNonMatchingName
> - hasPet_isCaseInsensitive
> - hasPet_returnsFalseWhenNameIsNull
> - (optional) hasPet_emptyStringReturnsFalse
>
> Each test should construct an Owner, create Pet(s) with setName(...), add via owner.addPet(pet) and assertTrue/assertFalse on owner.hasPet(...). Do not rely on DB—these are plain unit tests.

**Review checkpoint:** Tests compile and are focused only on hasPet behaviour. No external resources, no DB, no network.

---

## Step 5 — Run unit tests locally

**Goal:** Verify tests pass.

**Suggested prompt (manual execution):**

> Run the unit tests that cover Owner: `./mvnw -Dtest=org.springframework.samples.petclinic.owner.OwnerHasPetTest test` (or run the whole test class that was modified). If using an IDE, run the test class. Fix any compilation issues.

**Review checkpoint:** All new tests pass. If tests fail, inspect stack traces, fix implementation or tests, and re-run.

---

## Step 6 — Convenvention drift check

**Goal:** Ensure the new code follows project conventions (.github/copilot-instructions.md).

**Suggested prompt:**

> Review the modified files (F1 and the test file). List any drift vs .github/copilot-instructions.md (naming, injection of imports, style). Do not auto-fix; report drift with file + line references.

**Review checkpoint:** No convention drift, or acceptable items are listed for manual correction.

---

## Step 7 — Commit guidance

**Goal:** Prepare a small commit that only contains the implementation and tests.

**Suggested commit message:**

Add Owner#hasPet(String) helper and unit tests

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

**Review checkpoint:** Commit touches only the new method in F1 and the test file. Tests included.

---

## Step 8 — Validation against Acceptance Criteria (manual)

**Goal:** Manually verify each AC against the running tests and code review.

**Suggested prompt (manual checklist):**

> 1. Confirm Owner.java declares public boolean hasPet(String name).
> 2. Confirm hasPet uses equalsIgnoreCase and returns true for matching name.
> 3. Confirm hasPet returns false when name is null.
> 4. Confirm no existing pets or owner state are modified by the method.
> 5. Confirm unit tests exist for matching, non-matching, case-insensitive, and null argument.

**Review checkpoint:** All AC items marked PASS. If any fail, return to the corresponding step.

---

## Step 9 — Done criteria

Before opening a PR, confirm:

- F1 contains the new public boolean hasPet(String name) method.
- Unit tests covering the required scenarios are present and pass locally.
- No unrelated files were modified.
- Code follows repository conventions (address any drift reported in Step 6).
- Commit message includes the required Co-authored-by trailer.

---


Good luck executing the steps. After implementation, attach the modified files and test results if you want Copilot to review the diffs or help with a PR description.