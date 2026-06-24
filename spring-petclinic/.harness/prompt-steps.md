# Plan for: Add getFullName() to Owner

**Source:** .harness/context.md
**Stack:** Java / Spring Boot
**Total steps:** 6
**Unresolved clarifications:** None

---

## Before you execute any step
1. Keep .harness/context.md in the chat context while running steps.
2. This plan assumes standard Maven build: `mvn test` is the verification command.
3. Apply project Java conventions and run the build before opening a PR.

---

## Pre-flight assumptions
1. Owner.java exists at src/main/java/org/springframework/samples/petclinic/owner/Owner.java and exposes getFirstName() / getLastName().
2. The change is a read-only convenience accessor; no DB or mapping changes are required.
3. Tests run locally with `mvn test`; CI uses the same command.

---

## Impacted Files
| ID | Path | Role |
|----|------|------|
| F1 | src/main/java/org/springframework/samples/petclinic/owner/Owner.java | Domain model — add accessor |

---

## Step 1 — Inventory (confirm file)
**Goal:** Confirm the primary file to edit and verify there are no related compilation constraints.

**Suggested prompt:**
> Read F1 and report: class package, superclass, presence of getFirstName()/getLastName(), and any TODOs or generated code markers. Also list any tests referencing Owner that may need update.

**Review checkpoint:** Confirm F1 is the correct file and getFirstName()/getLastName() are available.

---

## Step 2 — Implement getFullName() in Owner.java
**Goal:** Add the accessor that returns "firstName lastName".

**Suggested prompt:**
> Edit F1: add the following method below toString():
>
> ```java
> /**
>  * Return the owner's full name as "firstName lastName".
>  */
> public String getFullName() {
>     return String.format("%s %s", getFirstName(), getLastName());
> }
> ```
>
> Make the edit with constructor injection and code style consistent with repo rules.

**Review checkpoint:** Confirm the method was added exactly as shown, compiles, and no other lines were changed.

---

## Step 3 — Build and run tests
**Goal:** Verify the change does not break compilation or existing tests.

**Suggested prompt:**
> Run `mvn -DskipTests=false test` (or `mvn test`) in the repo root and paste the build summary (pass/fail counts). If compilation or tests fail, show failures and stop.

**Review checkpoint:** All tests pass locally. If failures occur, stop and fix before proceeding.

---

## Step 4 — (Optional) Add a unit test
**Goal:** Add a small unit test asserting getFullName() returns expected string.

**Suggested prompt:**
> Create test `src/test/java/org/springframework/samples/petclinic/owner/OwnerTest.java` with a test `getFullName_returnsFirstAndLastName()` that constructs an Owner (setFirstName/setLastName) and asserts `getFullName()` equals "First Last". Match existing test style (JUnit 5 + AssertJ or JUnit assertions as in repo).

**Review checkpoint:** Test exists and passes with `mvn test`.

---

## Step 5 — Manual validation
**Goal:** Quick sanity check in IDE or runtime to ensure method behaves as expected.

**Suggested prompt:**
> Open F1 and visually verify getFullName() uses getFirstName() and getLastName(). In an interactive shell or small main, instantiate Owner, set names, and print getFullName(). Confirm output.

**Review checkpoint:** Manual verification done and output matches AC: "<firstName> <lastName>".

---

## Step 6 — Commit, push, and open PR
**Goal:** Commit the change, push to a feature branch, and open a PR.

**Suggested prompt:**
> Git steps: create branch `feature/add-owner-getFullName`, commit changes with message:
>
> `Add Owner.getFullName() — return "firstName lastName"`
>
> Include commit trailer:
> `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`
>
> Push branch and open PR against main.

**Review checkpoint:** PR created; diff includes only the Owner.java change (and optional test file if added).

---

## Done criteria
- Owner.java contains public String getFullName() returning firstName + space + lastName.
- `mvn test` completes with all tests passing.
- PR opened with a clear commit message and Co-authored-by trailer.


---

Notes:
- This change is minimal and read-only in the data model. If other code expects a different name format (e.g., reversed or trimmed), address it in a follow-up story.
- If CI uses a different JDK or build script, run the same command CI uses before finalizing the PR.
