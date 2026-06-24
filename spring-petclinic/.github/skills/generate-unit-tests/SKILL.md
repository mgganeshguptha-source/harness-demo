---
name: generate-unit-tests
description: >
  Generates unit tests for production code already written by the
  execute-prompt-steps skill, one test file at a time, with explicit
  human approval between each. Use this whenever the developer reaches
  a test step in the plan, attaches the context and plan files and asks
  for tests, says "generate tests for [class/component]", or is handing
  off from execute-prompt-steps after a Type D test step. Works across
  JUnit 5 + Mockito for Spring Boot, Jasmine/Karma for Angular, and the
  mobile testing setup for Ionic. The skill refuses to write more than
  one test file per invocation, refuses to modify production code (it
  flags bugs but does not fix them), refuses to write integration or
  end-to-end tests, refuses to write happy-path-only tests when ACs
  describe edge cases, and refuses to use @Disabled / xit to defer
  tests. Every test file maps explicitly back to the acceptance
  criteria it covers. A test-generation log is written under
  .github/story-test-generation-logs/.
---

# Generate Unit Tests Skill

Writes unit tests for the production code produced by the previous
skills in the loop, one test file at a time, so the developer can
review each test class before the next is generated.

This is the fourth skill in the Copilot-driven SDLC loop:

| Skill | Input | Output | Purpose |
|---|---|---|---|
| `build-context` | JIRA story | `context.md` | Capture **what** the work is |
| `build-prompt-steps` | `context.md` | Timestamped plan file | Plan **how** to implement it |
| `execute-prompt-steps` | plan file | Code changes + execution log | Run the plan, one step at a time |
| `generate-unit-tests` (this skill) | code + ACs | Test files + test-generation log | Cover ACs with reviewable tests |
| `run-and-fix-tests` | test files | Test run log + fixes | Execute tests and iterate to green |

Stack assumed: **Angular** on the frontend (Jasmine/Karma), **Spring
Boot** on the backend (JUnit 5 + Mockito), **Ionic + Angular** on
mobile.

---

## Why this skill exists

When a developer asks Copilot to "write tests for this", the default
behaviour is to produce a single sprawling test file with one test per
public method, mostly happy-path, ignoring the acceptance criteria
that defined the work. This breaks the loop in three ways:

1. **AC drift.** Tests assert what the code does, not what the story
   required. A passing suite means nothing if the suite never tested
   the actual behaviours the BA/PO signed off on.
2. **Unreviewable mega-output.** A test file with 30 tests generated
   in one turn gets skim-approved. Bugs in the tests themselves slip
   through, and the suite gives false confidence forever.
3. **Convention drift.** Field injection in test setup, real
   filesystem/network calls instead of mocks, `@Disabled` annotations
   left in to "deal with later", missing assertions — patterns the
   team's `*-testing.instructions.md` files exist to prevent.

Two failure modes this skill is designed to prevent:

1. **AC-blind generation.** Writing tests against the implementation
   rather than against the contract in `context.md`. The acceptance
   criteria are the source of truth — tests that don't map back to
   them are testing the wrong thing.
2. **Test-as-implementation-mirror.** Tests so closely coupled to the
   current implementation that any refactor breaks them, without any
   behaviour actually changing. Tests assert the *what*, not the *how*.

Everything below serves these two goals.

---

## Banned actions — never do any of these

| Banned | Why | Do instead |
|---|---|---|
| Generate more than one test file per invocation | Defeats the HITL checkpoint | Do exactly one test file, stop, wait for the developer's decision |
| Modify production code | Out of scope; corrupts the separation between skills | If you spot a real bug, flag it in "What I noticed"; the developer decides |
| Write integration tests, end-to-end tests, or tests that touch a real database / network | Out of scope; brittle in CI; belongs in a separate suite | Write unit tests that mock collaborators; flag if the AC genuinely needs an integration test |
| Write happy-path-only tests when ACs describe edge cases | AC drift — the suite gives false coverage | Map every AC to at least one test case; cover edge cases the AC names |
| Use `@Disabled`, `xit`, `xdescribe`, `@Ignore`, or commented-out tests | Defers risk silently; tests are forgotten | Write the test fully or do not write it; if it cannot be written, surface why |
| Mock the class under test | Defeats the purpose of testing it | Mock only collaborators; instantiate the system under test for real |
| Test trivial getters / setters / generated code | Inflates the suite without catching defects | Test behaviour, not boilerplate |
| Invent class names, method signatures, or import paths | Tests reference nonexistent symbols | Read the production file first; use exactly what is there |
| Assert nothing (no expectations, no verification) | Test always passes; gives false confidence | Every test must have at least one assertion or verification call |
| Skip the team's testing instruction files (java-testing, angular-testing, ionic-angular-testing) | Convention drift | Apply every matching instruction; state which ones applied |
| Use random data, current time, or external IDs without controlling them | Flaky tests | Inject clocks, fix seeds, use test fixtures |

**This is a hard preflight check.** Before reporting a test file done,
verify exactly one file was written, every AC in scope has at least
one mapped test, no banned patterns are present, and the file actually
exists on disk.

---

## Inputs

Like the other loop skills, this skill reads from **chat attachments,
not from disk**. The developer must attach three files for this run:

- **Context file** — `STORY-DESCRIPTION-context-YYMMDD-HHMMSS.md`. The
  source of truth for which behaviours need tests.
- **Prompt steps file** — `STORY-DESCRIPTION-prompt-steps-YYMMDD-HHMMSS.md`.
  Tells the skill which test step is being executed and what scope it
  covers.
- **Execution log** —
  `STORY-DESCRIPTION-execution-YYMMDD-HHMMSS.md`. Tells the skill which
  production files were actually changed in implementation/wiring
  steps, so it knows what to test.

**Never read these files from disk or pick them yourself.** Same rule
as the other loop skills.

The skill also reads the production source files it is going to test
— these are read from disk because they are the artefact under test,
not story state.

---

## Workflow

### 1. Verify inputs

Before doing anything else, run these checks in order:

- **All three files are attached.** If any are missing, ask:
  > I need all three files attached to the chat before I can generate
  > tests: the context file, the prompt-steps file, and the execution
  > log. I see [what's attached, if anything] — please also attach
  > [the missing file(s)].

  Stop and wait. Do not proceed.

- **The attached files are the right types.** Presence is not enough.
  Verify each one has the expected structure:
  - Context file: sections What Are We Trying to Achieve, Expected
    Behaviour, Acceptance Criteria.
  - Plan file: standing instructions block, pre-flight section,
    numbered steps.
  - Execution log: per-step entries with Type, Status, Files changed.

  If any look wrong:
  > The attached [name] file doesn't look like the right type — it's
  > missing the expected sections. Did you attach the right file?

  Stop and wait.

- **All three files pair correctly.** They should share the same
  STORY-DESCRIPTION prefix per the project's naming convention. If
  they don't match, warn:
  > These three files don't share a story description prefix —
  > [context: A], [plan: B], [execution log: C]. Are you sure they go
  > together?

  Continue only if the developer confirms.

- **Confirm files, step, and source scope before generating.** Once
  all three are valid and paired, identify which test step from the
  plan is being executed, and from the execution log derive which
  production files were changed. State back:

  > Generating tests for:
  > • Story: "[goal from What Are We Trying to Achieve, one line]"
  > • Plan test step: Step [N] — "[step title]"
  > • Production files implemented before this step:
  >   - path/to/File1.java (Step 2)
  >   - path/to/File2.java (Step 3)
  >   - path/to/File3.java (Step 4)
  > • Acceptance criteria this step's tests must cover:
  >   - AC1: [text]
  >   - AC2: [text]
  >   - AC3: [text]
  >
  > I will generate tests one file at a time, stopping after each for
  > your decision. Which production file should I start with?

  Wait for an explicit choice. This is the first human checkpoint —
  it confirms the scope and lets the developer steer the order.

- **`.github/copilot-instructions.md` and the relevant
  `*-testing.instructions.md` files exist.** If
  copilot-instructions.md is missing, warn as in the other skills. If
  the relevant testing instructions file is missing (java-testing.
  instructions.md for backend files, angular-testing.instructions.md
  for frontend files, ionic-angular-testing.instructions.md for
  mobile), warn separately:

  ```markdown
  > ## ⚠️ Missing testing instructions
  >
  > I don't see .github/instructions/[java/angular/ionic-angular]-testing.instructions.md.
  >
  > **What this means:** the tests will be generated against generic
  > defaults (JUnit 5 + Mockito or Jasmine/Karma standard patterns)
  > rather than the team's test conventions.
  >
  > **Recommendation:** ensure the testing instructions file is
  > present before generating tests. Otherwise convention drift in
  > the test suite is likely.
  >
  > **Continue with defaults, or pause to set up the file first?**
  ```

### 2. Read the production file and map ACs

Once the developer has picked a production file, read it fully. Note:

- Public API of the class / component: what methods, what inputs, what
  outputs, what side effects.
- Collaborators (dependencies that need mocking).
- Existing tests, if any, for this file. The skill must not duplicate
  existing tests and must follow their style if they look conventional.

Then build an **AC-to-method coverage map** before writing any test
code. For each AC in scope, identify which method(s) on the file under
test are responsible for the behaviour. Show this to the developer:

> **AC-to-test coverage map for [filename]:**
>
> - AC1 ("[text]") → covered by `methodX()` — will test: normal case,
>   empty input
> - AC2 ("[text]") → covered by `methodY()` — will test: case
>   sensitivity, multi-field match
> - AC3 ("[text]") → covered by `methodX()` — will test: pagination
>   defaults, out-of-range page
> - AC4 ("[text]") → not covered by this file (belongs to controller
>   tests in a later step)
>
> Plus edge cases the file handles that ACs don't name explicitly:
> - Null input handling on `methodX()`
> - Empty string input on `methodX()`
>
> Total: [N] test cases planned. Proceed?

Wait for the developer's go-ahead. If the map shows an AC with no
covering method on this file, ask whether it belongs in a different
file's tests, or whether the implementation step missed something.

### 3. Generate the test file

Once the coverage map is approved:

- **Identify which testing instructions apply.** For the file under
  test, list which `*-testing.instructions.md` and which other
  `.github/instructions/` files have an applyTo glob that matches the
  *test file's* path. State briefly which ones applied:

  > Writing OwnerServiceTest.java — applying java-testing,
  > java-conventions, logging-java (for log assertions if any).

  This is not optional.

- **Write the test file following the standard naming and location
  for the stack:**
  - Java: `src/test/java/...` mirroring the production package; class
    named `[ProductionClass]Test.java`.
  - Angular: `*.spec.ts` co-located with the component / service.
  - Ionic: per `ionic-angular-testing.instructions.md`.

  If the conventional location is unclear from the repo, read other
  existing tests in the repo to match their pattern. Do not invent a
  new convention.

- **One test method per behaviour, named for the behaviour.** Examples:
  - Good (JUnit): `searchOwners_returnsMatchingOwnersIgnoringCase`,
    `searchOwners_returnsEmptyPageWhenNoMatch`,
    `searchOwners_throwsValidationExceptionForNullInput`.
  - Bad (JUnit): `testSearchOwners`, `testSearchOwners2`,
    `searchOwnersTest`.
  - Good (Jasmine): `should filter results when 3+ characters are typed`,
    `should restore full list when input is cleared`.

- **Use the Arrange–Act–Assert structure** with a blank line between
  sections. Tests should read top-to-bottom like a small story.

- **Mock only collaborators.** The class under test is instantiated
  for real. For Spring Boot, prefer `@Mock` + `@InjectMocks` with
  constructor injection over `@SpringBootTest` for unit tests. For
  Angular, mock services via `TestBed.configureTestingModule` with
  provider overrides.

- **Every test must have at least one assertion or verification call.**
  No tests that "just run" the method without checking anything.

- **For tests that need controlled time, randomness, or external
  IDs**, inject the dependency rather than calling system clocks /
  generators directly. If the production code is hard to test because
  it calls these directly, surface as a flag in "What I noticed" —
  but do not modify the production code.

- **Write the file.** Verify it exists on disk with the new content.

### 4. Test-file preflight before reporting done

Every item must pass — if any fail, do not report done.

- [ ] Exactly one test file was written in this turn
- [ ] No production files were modified
- [ ] No integration tests, end-to-end tests, real DB / real network
      calls were included
- [ ] Every AC in scope for this file has at least one mapped test
- [ ] Every test has at least one assertion or verification call
- [ ] No `@Disabled` / `xit` / `xdescribe` / `@Ignore` /
      commented-out tests
- [ ] The class under test is instantiated (not mocked); only
      collaborators are mocked
- [ ] Every test method name describes the behaviour, not the method
- [ ] The Arrange–Act–Assert structure is visible
- [ ] All class names, methods, and imports referenced actually exist
      in the production code
- [ ] The relevant testing instructions file's rules were applied
- [ ] The test file compiles / passes type-check
      (`mvn test-compile`, `ng build --configuration=development`) if
      the build tool is reachable
- [ ] AC4-style "covered elsewhere" items are explicitly listed for
      the developer, not silently dropped

### 5. Stop and ask for the decision

After preflight passes, summarise and stop:

> ### Test file [N of M] — [filename] complete
>
> **Production file tested:** path/to/ProductionFile.java
> **Test file written:** path/to/ProductionFileTest.java
> **Test framework:** [JUnit 5 + Mockito / Jasmine + Karma / etc.]
> **Testing instructions applied:** [comma-separated list]
>
> **Tests written ([N] total):**
> 1. `testNameOne` — covers AC1 (normal case)
> 2. `testNameTwo` — covers AC1 (empty input edge case)
> 3. `testNameThree` — covers AC2 (case-insensitive match)
> ...
>
> **AC coverage from this file:**
> - AC1 → tests 1, 2
> - AC2 → test 3
> - AC3 → not yet covered (will be in [next file's] tests)
>
> **What I noticed:** [optional — production smells flagged but not
> fixed, patterns reused from existing tests, conventions chosen
> between]
>
> **Your decision:**
> 1. **Approve** — I will move to the next production file: [name]
> 2. **Reject with comment** — tell me what to change and I will redo
>    this test file
> 3. **Skip remaining files for this test step** — I will log what's
>    been done and hand off to run-and-fix-tests (not recommended if
>    ACs are uncovered)
>
> Which would you like?

Wait for an explicit choice. **Do not move to the next file on
silence, filler words, or ambiguous phrasing.** Same empty-reply
handling as the other loop skills.

### 6. Update the test-generation log

Append to the log file after every test file (approved, rejected-and-
redone, or skipped). This file is the persistent state of the
test-generation run.

**Location:** `.github/story-test-generation-logs/`

**Filename:** `STORY-DESCRIPTION-test-generation-YYMMDD-HHMMSS.md` —
same STORY-DESCRIPTION as the context, plan, and execution log files,
with the timestamp of when test generation started.

**Note for the toolkit owners:** the path
`.github/story-test-generation-logs/` and the filename format above
need to be added to `copilot-output-naming.instructions.md` when this
skill is shipped, alongside the entry that `execute-prompt-steps`
also needs (`.github/story-execution-logs/`).

**Entry format per test file:**

```markdown
## Test file [N] — [test filename]

- **Status:** Approved | Rejected (redone) | Skipped | Failed
- **Started:** YYMMDD-HH:MM:SS
- **Completed:** YYMMDD-HH:MM:SS
- **Production file tested:** path/to/ProductionFile.java
- **Test file written:** path/to/ProductionFileTest.java
- **Test framework:** JUnit 5 + Mockito | Jasmine + Karma | etc.
- **Testing instructions applied:** java-testing, java-conventions
- **Tests written:**
  - testNameOne (covers AC1)
  - testNameTwo (covers AC1 edge case)
- **AC coverage delta:**
  - Newly covered: AC1, AC2
  - Still uncovered after this file: AC3 (planned for next file)
- **Developer comment (if any):** [verbatim text]
- **Production smells flagged (if any):** [verbatim from What I noticed]
```

### 7. Handling failures mid-generation

If a write fails, a compile fails, the production file does not
match what the execution log claims, or any other blocker hits, stop.
Log the test file as Failed and surface it:

> ### Test file generation failed
>
> **What failed:** [error message, what was being attempted]
> **What I tried:** [what was done before the failure]
>
> **Your decision:**
> 1. **Provide guidance** — tell me how to resolve it and I will retry
> 2. **Skip this file** — log as skipped and move to the next
> 3. **Stop the run** — pause; we can resume later
>
> Which would you like?

Never silently work around a failure.

### 8. End-of-step handling

When the developer approves the last test file in scope for this test
step (or chooses to skip remaining files), write a final summary
entry to the test-generation log:

```markdown
## Test step generation complete

- **Started:** YYMMDD-HH:MM:SS
- **Completed:** YYMMDD-HH:MM:SS
- **Test files written:** [N]
- **Test files skipped:** [N]
- **ACs covered:** AC1, AC2, AC3
- **ACs uncovered (flagged for follow-up):** [list, if any]
- **Production smells flagged:** [list, if any]
```

Then tell the developer:

> All test files for plan Step [N] generated. Test-generation log at
> .github/story-test-generation-logs/STORY-DESCRIPTION-test-generation-YYMMDD-HHMMSS.md
>
> Next step in the loop: run-and-fix-tests skill. It will execute the
> test suite, and if any tests fail, iterate with fix-test-failures
> until the suite is green or the attempt limit is reached.
>
> Once test running is complete, come back to execute-prompt-steps
> to resume from Step [N+1].

(Do not wrap the filename in backticks in the message to the
developer — Copilot Chat auto-links backticked filenames into broken
vscode-file:// URLs.)

---

## Resuming an interrupted run

If the developer invokes the skill and a test-generation log already
exists for this story with status not yet complete, do not start over.
Read the log, find the last completed-or-skipped test file, and ask:

> I see a test-generation log for this story —
> .github/story-test-generation-logs/STORY-DESCRIPTION-test-generation-YYMMDD-HHMMSS.md
>
> The last completed test file was for [production file] ([status]).
> The remaining production files in scope for this test step are:
> [list]. Which one should I generate tests for next, or should we
> start over with a fresh log?

Wait for an explicit choice. Never auto-resume.

---

## What never goes in a unit test

These belong elsewhere, not in `generate-unit-tests` output:

- **Real database calls** — use mocks / in-memory test doubles /
  `@DataJpaTest` slices only if absolutely necessary and the team
  conventions allow it; otherwise mock the repository.
- **Real HTTP calls** — use `MockMvc` for Spring controllers,
  `HttpTestingController` for Angular `HttpClient`. Never reach a
  live endpoint.
- **Real filesystem reads/writes** — mock the IO layer.
- **`Thread.sleep`** to wait for async behaviour — use the framework's
  async assertions (`Awaitility`, `fakeAsync` + `tick`, RxJS marbles).
- **System time** — inject a `Clock` or equivalent; never assert on
  `LocalDateTime.now()` in a test.
- **Production code changes** — even tiny ones, even obvious bug
  fixes. Flag and let the developer decide.
- **TODO comments without an owner and date** — write the test or
  surface what's blocking; do not bury "fix later" in the test code.

---

## Developer override paths

Same override taxonomy as the other loop skills — never conflate:

- **File-level skip** — applies only to the current production file's
  tests. Triggers: *"skip this file"*, *"tests for this aren't needed
  yet"*. Log as Skipped, continue to the next file in the scope.
- **Step-level skip** — applies to the whole test step. Triggers:
  *"skip remaining files"*, *"hand off now"*. Log what's done, write
  the end-of-step summary, hand off to run-and-fix-tests.
- **Run-level pause** — applies to everything. Triggers: *"stop"*,
  *"pause"*, *"let me check the production code first"*. Log as
  paused at the current file, exit cleanly. The developer can resume
  later.
- **Ambiguous phrasing** — for example *"let's skip"*, *"hold on"*,
  *"hmm"*. **Do not act on these.** Ask:

  > To make sure I get this right — do you mean:
  > 1. Skip only the current file's tests and continue with the next file,
  > 2. Skip all remaining files in this test step and hand off, or
  > 3. Pause the whole run and resume later?

  Wait for an explicit choice.

---

## Examples

### Calibrating test method names

| Vague (banned) | Specific |
|---|---|
| `testSearchOwners` | `searchOwners_returnsMatchingOwnersIgnoringCase` |
| `testSearchOwners2` | `searchOwners_returnsEmptyPageWhenNoMatch` |
| `testNullInput` | `searchOwners_throwsValidationExceptionForNullLastName` |
| `should work` | `should filter results when 3+ characters are typed` |
| `should work with empty` | `should restore full list when input is cleared` |

### Calibrating AC coverage maps

| Vague (banned) | Specific |
|---|---|
| "Tests cover the search behaviour" | "AC1 (case-insensitive match) → test 1, 2; AC2 (multi-field) → test 3; AC3 (pagination defaults) → test 4, 5" |
| "Edge cases handled" | "Null lastName → test 6; empty string lastName → test 7; whitespace-only lastName → test 8" |
| "Errors tested" | "Repository throws DataAccessException → test 9 (verifies service translates to ServiceException with original cause)" |

### Calibrating "What I noticed" for production smells

| Too vague (or absent) | Useful (flag-without-fix) |
|---|---|
| (silence) | "OwnerService.searchOwners calls `Instant.now()` directly to log the request timestamp — makes the log assertion test brittle. Would be cleaner with an injected Clock. Did not modify; flagging for the developer." |
| "Some issues" | "OwnerController returns 200 with `{ error: '...' }` body for some invalid inputs instead of 400 — looks like a bug, but it's outside the scope of this story. Did not change; flagging." |
| "Looks fine" | "Reused the existing `givenOwnerExists()` test fixture builder from OwnerRepositoryTest — kept the pattern consistent across the test suite." |

---

## Reference files

- `assets/test-generation-log-template.md` — Template for the
  test-generation log file with section headers and the per-test-file
  entry format. Read this when you need to remember the exact log
  structure.
