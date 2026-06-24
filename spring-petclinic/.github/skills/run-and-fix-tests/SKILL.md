---
name: run-and-fix-tests
description: >
  Executes the test suite for code already written by execute-prompt-steps
  and generate-unit-tests, then iterates a diagnose-propose-approve-apply
  fix loop until the suite is green or a configurable attempt limit is
  reached. Use this whenever the developer has just finished generating
  tests and asks to run them, says "run the tests", "make the tests
  pass", "fix the failing tests", or is handing off from
  generate-unit-tests. Works across Maven/Gradle for Spring Boot (JUnit
  5), npm/ng test for Angular (Jasmine/Karma), and the equivalent
  commands for Ionic. The skill refuses to disable failing tests,
  refuses to mark tests as flaky without evidence, refuses to apply any
  code change without explicit developer approval of the proposed fix,
  refuses to modify files outside the story's logged scope, refuses to
  add dependencies or do architectural refactors to make a test pass,
  refuses to exceed the configured attempt limit (default 3) without an
  explicit override, and refuses to claim a run passed when any tests
  were skipped or disabled. A test-run log is written under
  .github/story-test-run-logs/.
---

# Run And Fix Tests Skill

Runs the test suite, parses the results, and — if anything fails —
proposes a concrete fix, gets explicit developer approval, applies it,
and re-runs. The developer stays in control: every test run is a
checkpoint, and every fix is proposed and approved before any code is
touched.

This is the fifth and final skill in the Copilot-driven SDLC loop:

| Skill | Input | Output | Purpose |
|---|---|---|---|
| `build-context` | JIRA story | `context.md` | Capture **what** the work is |
| `build-prompt-steps` | `context.md` | Timestamped plan file | Plan **how** to implement it |
| `execute-prompt-steps` | plan file | Code changes + execution log | Run the plan, one step at a time |
| `generate-unit-tests` | code + ACs | Test files + test-generation log | Cover ACs with reviewable tests |
| `run-and-fix-tests` (this skill) | test files | Test-run log + applied fixes | Get the suite to green safely |

Stack assumed: **Angular** on the frontend (`ng test`), **Spring Boot**
on the backend (`mvn test` or `./gradlew test`), **Ionic + Angular** on
mobile.

---

## Why this skill exists

When a developer asks Copilot to "run the tests and fix anything that
breaks", the default behaviour is to loop indefinitely — running tests,
patching code, re-running, patching again — until either the suite goes
green or the chat runs out of context. This breaks the loop in three
ways:

1. **Silent fixes compound.** A wrong fix in attempt 1 changes what
   attempt 2 is fixing. By attempt 5 the code no longer resembles what
   the plan and execution log say was implemented.
2. **The cheapest "fix" wins.** When Copilot is allowed to choose
   freely, it will gravitate toward disabling the failing test,
   loosening the assertion, or marking the test flaky — because that
   makes the immediate failure go away. The suite turns green; the bug
   stays.
3. **No diagnosis step.** A failing test can mean "test is wrong",
   "production code is wrong", "both are wrong", or "environment is
   wrong". Each needs a different fix. Without an explicit diagnosis,
   Copilot tends to patch whichever file is more familiar — often the
   test.

Two failure modes this skill is designed to prevent:

1. **Unbounded loop.** Running fix-and-re-run more times than the
   developer can meaningfully review. **More than three attempts on
   the same failure almost always means the underlying issue is
   structural, not a simple test/code mismatch.** The skill enforces a
   hard cap and forces a human decision when it's hit.
2. **Green-by-erosion.** Disabling tests, weakening assertions, or
   silently marking tests skipped to make the suite pass. A suite that
   gets greener by removing checks is worse than one that stays red
   honestly.

Everything below serves these two goals.

---

## Banned actions — never do any of these

| Banned | Why | Do instead |
|---|---|---|
| Apply any code change without explicit developer approval of the proposed fix | The approval gate is the entire point of the human-in-the-loop pattern | Always propose first; wait for an explicit choice; apply only after approval |
| Exceed the configured attempt limit without explicit developer override | Unbounded loops compound errors | Stop at the limit; surface the persistent failure; let the developer decide |
| Disable a failing test (`@Disabled`, `xit`, `xdescribe`, `@Ignore`, `it.skip`, commenting out) | Green-by-erosion | Either the test is right (fix the code) or the test is wrong (delete it with reason logged); never disable |
| Weaken an assertion to make a test pass | Same as above — green-by-erosion | If the assertion is wrong, fix it explicitly with reason logged; do not loosen quietly |
| Mark a test as flaky without evidence (multiple runs showing inconsistent results) | Flaky-labelling hides real bugs | Run the test in isolation at least 3 times; only label as flaky if results genuinely vary |
| Modify the test when the diagnosis points to production code | Patches the symptom, hides the bug | Follow the diagnosis — if production code is wrong, change production code |
| Modify production code when the diagnosis points to the test | Drifts the implementation from the AC | Follow the diagnosis — if the test encodes the wrong expectation, change the test |
| Modify test files outside the scope of the current story's test-generation log | Out-of-scope changes break unrelated tests | Restrict fix scope to files listed in this story's logs; if a fix needs an out-of-scope edit, stop and ask the developer |
| Modify production files outside the scope of the current story's execution log | Same — out-of-scope risk | Restrict fix scope to files listed in this story's logs |
| Add new dependencies to make a fix work | Architectural change disguised as a test fix | Flag as a separate concern; do not auto-add |
| Refactor architecture to make a test pass (splitting classes, extracting services, restructuring modules) | Story-level work disguised as a fix | Flag as a separate concern; do not auto-refactor |
| Modify `.github/instructions/` files or `copilot-instructions.md` to make a fix conform | Standards are not per-fix policy | Either the fix follows the standard or it does not; do not silently lower the bar |
| Modify build configuration (pom.xml, angular.json, package.json) to make a test pass | Architectural change disguised as a fix | Flag separately; do not auto-edit |
| Re-run tests with different flags or skips to get a green result | Misrepresents the actual suite state | Always run with the same command the team uses; report what actually happens |
| Claim a run passed when any tests were skipped or disabled | False signal | Always report skipped/disabled test counts separately from pass/fail |
| Bundle multiple unrelated fixes into one proposal | Unreviewable | One coherent fix per proposal; if several failures need different fixes, propose them one at a time |

**This is a hard preflight check.** Before reporting a test run done,
verify the actual command was run, the exit code was captured, skipped
and disabled counts are reported separately, no banned shortcuts were
taken, and every code change was preceded by an explicit developer
approval logged in the test-run log.

---

## Inputs

Like the other loop skills, this skill reads from **chat attachments,
not from disk**. The developer must attach four files for this run:

- **Context file** —
  `STORY-DESCRIPTION-context-YYMMDD-HHMMSS.md`. Source of truth for the
  ACs the tests must cover.
- **Prompt steps file** —
  `STORY-DESCRIPTION-prompt-steps-YYMMDD-HHMMSS.md`. Tells the skill
  which plan step this run is for.
- **Execution log** —
  `STORY-DESCRIPTION-execution-YYMMDD-HHMMSS.md`. Lists the
  production files in scope — fixes are restricted to these.
- **Test-generation log** —
  `STORY-DESCRIPTION-test-generation-YYMMDD-HHMMSS.md`. Lists the test
  files in scope.

**Never read these files from disk or pick them yourself.** Same rule
as the other loop skills.

The skill also runs commands against the live repo (test runner, build
tool) — that is necessary by its nature.

---

## Configuration

This skill has one tunable: the **maximum number of fix attempts per
test run invocation**.

- **Default:** 3 attempts (initial run + up to 2 fix-and-re-run cycles)
- **Override:** the developer can say *"set max attempts to N"* during
  the first checkpoint of the run; the skill confirms back and uses
  that limit for the rest of the run.
- **Hard ceiling:** even with an override, never exceed 5 attempts in
  a single skill invocation. Beyond 5, the developer should pause and
  re-think the approach.

The default of 3 reflects the observation that beyond two fix cycles,
the underlying issue is usually structural — wrong design choice,
wrong AC interpretation, or a missing piece of the implementation —
and a third or fourth patch tends to compound rather than resolve.

---

## Workflow

### 1. Verify inputs

Before doing anything else, run these checks in order:

- **All four files are attached.** If any are missing, ask:
  > I need all four files attached to the chat before I can run and
  > fix tests: the context file, the prompt-steps file, the execution
  > log, and the test-generation log. I see [what's attached, if
  > anything] — please also attach [the missing file(s)].

  Stop and wait. Do not proceed.

- **The attached files are the right types and pair correctly.** All
  four should share the same STORY-DESCRIPTION prefix. If any look
  wrong or the prefixes do not match, warn and stop.

- **Confirm files, step, and scope before running.** Once all four
  are valid and paired, identify which plan step this run is for, and
  from the execution log and test-generation log derive the in-scope
  files. State back:

  > Running tests for:
  > • Story: "[goal from context file, one line]"
  > • Plan test step: Step [N] — "[step title]"
  > • Test files in scope (from test-generation log):
  >   - path/to/Test1.java
  >   - path/to/Test2.java
  > • Production files in scope (from execution log) — fixes will be
  >   restricted to these:
  >   - path/to/File1.java
  >   - path/to/File2.java
  > • Max fix attempts: 3 (default — say "set max attempts to N" to
  >   change before I start)
  >
  > Detecting the test command from the repo...

  Detect the test command from the repo structure: presence of
  `pom.xml` → `mvn test`, `build.gradle` → `./gradlew test`,
  `angular.json` → `ng test --watch=false --browsers=ChromeHeadless`,
  Ionic project structure → the equivalent. If multiple are present
  (full stack story), ask the developer which to run first.

  State the detected command back:

  > Detected test command: `mvn test`. Ready to run the suite?

  Wait for go-ahead. This is the first human checkpoint.

- **`.github/copilot-instructions.md` and the relevant testing
  instructions files exist.** Same warnings as the other loop skills
  if missing.

### 2. Run the test suite (Attempt 1)

Run the detected test command. Capture:

- Exit code
- Total tests run
- Passed count
- Failed count
- Skipped count (any non-zero skipped count is reported separately
  and the run is not considered "green")
- Disabled count (same — never absorbed into pass count)
- For each failure: test name, test file, error message, stack trace
  (first frame in the team's own code, plus any AssertionError or
  exception cause)
- Wall-clock duration

If the test command itself fails to run (compile error, missing
dependency, test framework not configured), treat this as a Type C
environment failure — see section 5.

### 3. Report the run and stop for the decision

After every test run (passing, failing, or broken), stop and report.
Never silently proceed to a fix.

#### If all tests pass and nothing is skipped or disabled

> ### Test run [N] — passed ✓
>
> **Command:** `[exact command]`
> **Duration:** [N]s
> **Results:** [N] passed, 0 failed, 0 skipped, 0 disabled
> **Exit code:** 0
>
> The suite is green. The test step is complete.
>
> **Your decision:**
> 1. **Approve** — I will write the final summary to the test-run log
>    and end the run. You can resume execute-prompt-steps from the
>    next plan step.
> 2. **Re-run to confirm stability** — I will run the suite once more
>    to verify the result is reproducible (recommended if any test in
>    this story has had a fix applied)
>
> Which would you like?

#### If any tests are skipped or disabled

The suite is **not** green even if every non-skipped test passes:

> ### Test run [N] — tests skipped or disabled ⚠
>
> **Command:** `[exact command]`
> **Results:** [N] passed, [N] failed, [N] skipped, [N] disabled
>
> **Skipped or disabled tests:**
> - [test name] (in [file]) — [reason from annotation if any]
>
> Skipped or disabled tests cannot be ignored — they represent
> behaviour that is not being verified. Per the team's testing
> conventions, the suite is not considered green until every test in
> scope is either passing or has been deleted with a logged reason.
>
> **Your decision:**
> 1. **Investigate each skip** — I will surface each one in turn for
>    you to triage (delete with reason, or unskip and treat as a
>    failure to fix)
> 2. **Accept and proceed anyway** — only do this if every skipped
>    test is genuinely out of scope for this story (will be logged
>    explicitly)
>
> Which would you like?

#### If any tests fail (and no environment broken)

> ### Test run [N] — failures ✗
>
> **Command:** `[exact command]`
> **Duration:** [N]s
> **Results:** [N] passed, [N] failed, [N] skipped, [N] disabled
> **Exit code:** [N]
>
> **Failures:**
>
> 1. **[testName]** in `[testFile]`
>    - **Error:** [error message, first line]
>    - **First in-codebase frame:** [file:line]
>    - **Likely diagnosis:** [one of: test is wrong / production code
>      is wrong / both / environment — based on a quick look at the
>      assertion and the stack trace]
>
> 2. **[testName]** in `[testFile]`
>    ...
>
> **Attempt [N] of [max] — your decision:**
> 1. **Auto-fix** — I will propose a concrete fix for the first
>    failure using the diagnosis above; you approve before any code
>    is touched. If multiple failures, we go one at a time.
> 2. **Diagnose differently** — tell me which failure you want to
>    fix first and what you think the cause is; I will use your
>    diagnosis to build the proposal.
> 3. **Manual fix** — you will fix the code yourself; tell me when
>    you are done and I will re-run the suite
> 4. **Stop the run** — pause; we can resume later or revisit the
>    plan
>
> Which would you like?

Wait for an explicit choice. **Do not start proposing a fix on
silence, filler, or ambiguous phrasing.** Same empty-reply handling as
the other loop skills.

### 4. Propose, approve, and apply the fix (if requested)

When the developer chooses Auto-fix or Diagnose differently, the skill
follows a strict propose → approve → apply sequence. **Never apply a
fix without explicit approval of the proposed change.**

#### 4a. Build the diagnosis

If the developer chose Auto-fix, use the diagnosis the skill produced
in section 3 (test wrong / production code wrong / both / environment).

If the developer chose Diagnose differently, use their diagnosis
verbatim — do not "correct" it. If the diagnosis seems clearly wrong
based on the stack trace (e.g., developer says "test is wrong" but
the assertion matches the AC and the production code returns the
wrong value), say so once before proposing:

> Your diagnosis says the test is wrong, but the test assertion
> matches AC2 verbatim and the production code's return value does
> not. Do you want to proceed with your diagnosis (fix the test), or
> use the alternative (fix the production code)?

Wait for an explicit choice. Then proceed with whichever the
developer picks. Do not override.

#### 4b. Read the in-scope files

Before proposing any change, read:

- The failing test file(s) — the actual assertion and setup
- The production file(s) named in the stack trace's first
  in-codebase frame
- Any collaborator files the production code calls into for the
  failing behaviour

Restrict this reading to files in the execution log (production) and
test-generation log (tests). If the failure points at a file outside
this scope, stop and ask:

> The failure points at [path], which is outside the files this
> story was supposed to touch (execution log lists: [files], test-
> generation log lists: [files]). This usually means either:
> 1. The implementation in an earlier plan step affected this file
>    without logging it, or
> 2. The test setup depends on something pre-existing that broke
>    independently, or
> 3. The scope of the story needs to grow to include this file.
>
> How should I treat this — in scope (you'll update the relevant
> log), or stop the run for you to investigate?

#### 4c. Propose the concrete fix

Show the developer a precise, reviewable fix — not a description of a
fix. Use this exact pattern:

> ### Proposed fix [N] for failure: [testName]
>
> **Diagnosis:** [test wrong / production code wrong / both /
> environment]
>
> **Root cause (one line):** [why the test fails — the actual
> mismatch between expected and actual]
>
> **File to change:** path/to/File.java
>
> **Scope check:** ✓ in [execution log / test-generation log]
>
> **Proposed change:**
> ```diff
> [actual diff — what comes out, what goes in. Show enough context
> that the developer can read it without opening the file.]
> ```
>
> **Why this fixes the failure:** [one or two sentences tying the
> change back to the AC and the failing assertion]
>
> **What stays the same:** [the things this fix deliberately does
> not touch — to reassure the reviewer the blast radius is contained]
>
> **Banned-actions self-check:**
> - Disables/weakens no test ✓
> - No new dependencies ✓
> - No architectural refactor ✓
> - No out-of-scope edits ✓
> - No build config or instruction-file changes ✓
>
> **Your decision:**
> 1. **Apply** — I will write the change exactly as shown above
> 2. **Modify** — tell me what to change in the proposal; I will
>    show you a revised proposal and ask again
> 3. **Reject** — I will not apply this fix; tell me what to try
>    instead, or choose Manual fix / Stop the run
>
> Which would you like?

Wait for an explicit choice. **Do not apply on silence, filler, or
ambiguous phrasing.** Same empty-reply handling as the other loop skills.

#### 4d. Apply the approved change

Only when the developer says Apply:

- Make the file edit exactly as proposed. Do not "improve" it on the
  way in.
- Verify the file write succeeded — the file exists on disk with the
  new content.
- If the write fails, stop and report the write failure; do not
  retry silently.

If the developer says Modify, revise the proposal per their feedback
and go back to 4c. Do not apply the original, do not apply a
half-modified version.

If the developer says Reject, do not apply anything. Log the rejection
in the test-run log (see section 6) with the developer's reason if
given, then return to section 3 and re-present the decision menu.

#### 4e. Handle multiple failures

If the test run produced multiple failures, do not bundle the fixes.
Propose **one fix at a time**, get approval, apply, then move to the
next failure. After the last failure's fix is applied (or rejected),
return to section 2 — re-run the suite — as Attempt [N+1].

This is the most common place where Copilot drifts: trying to "fix
everything in one sweep" to save turns. Resist. One fix per proposal,
one proposal per approval.

#### 4f. Manual fix or Stop

If the developer chose Manual fix at section 3, pause the skill:

> I will wait for you to make the fix. When you are done, say "fix
> applied" or "re-run tests" and I will run the suite again as
> Attempt [N+1].

If the developer chose Stop, write the run as paused in the log and
exit cleanly.

### 5. Handle environment failures separately

If the test command failed to run at all — compile error, missing
dependency, runner not configured — this is not a test failure to
fix; it is an environment issue. Report separately:

> ### Test run [N] — environment broken ⚠
>
> **Command:** `[exact command]`
> **Exit code:** [N]
> **What broke:** [first error from the output — e.g. "Maven could
> not resolve dependency X", "ng test failed because Karma config is
> missing", "Java version mismatch"]
>
> This is not a test failure — the test runner could not start. A
> code fix is unlikely to help.
>
> **Your decision:**
> 1. **Investigate environment** — I will surface what I can see
>    about the issue; you resolve it (typically: dependency version,
>    JDK version, Karma config, internal artifact repo auth)
> 2. **Treat as a code fix anyway** — only if you believe the issue
>    is in the test or production code that was just changed, not in
>    the environment; I will propose a code fix per section 4 (will
>    be logged as a stretch interpretation)
> 3. **Stop the run** — pause; resolve out-of-band and resume later
>
> Which would you like?

Environment issues do not count against the attempt limit — they are
a separate failure mode.

### 6. Update the test-run log

Append to the log file after every test run and every fix attempt.

**Location:** `.github/story-test-run-logs/`

**Filename:** `STORY-DESCRIPTION-test-run-YYMMDD-HHMMSS.md` — same
STORY-DESCRIPTION as the other story files, with the timestamp of when
this run-and-fix-tests invocation started.

**Note for the toolkit owners:** the path
`.github/story-test-run-logs/` needs to be added to
`copilot-output-naming.instructions.md` when this skill is shipped,
along with the paths for the execution log and test-generation log
from the previous skills.

**Entry format per test run:**

```markdown
## Test run [N]

- **Started:** YYMMDD-HH:MM:SS
- **Completed:** YYMMDD-HH:MM:SS
- **Command:** [exact command run]
- **Result:** Passed | Failed | Skipped-tests-present | Environment-broken
- **Counts:** [N] passed, [N] failed, [N] skipped, [N] disabled
- **Exit code:** [N]
- **Failures (if any):**
  - [testName] in [testFile] — [error first line] — diagnosis: [test wrong / code wrong / both / env]
- **Developer decision:** [Auto-fix | Diagnose differently | Manual fix | Stop | Accept skips]
```

**Entry format per fix attempt:**

```markdown
## Fix attempt [N]

- **Started:** YYMMDD-HH:MM:SS
- **Completed:** YYMMDD-HH:MM:SS
- **Triggered for:** [failure from test run [N-1] — single failure per attempt]
- **Diagnosis:** [test wrong / production code wrong / both / environment]
- **Diagnosis source:** [auto from skill | developer-provided]
- **Root cause (one line):** [text]
- **File changed:** path/to/File.java
- **Scope check:** in [execution log | test-generation log]
- **Proposal:** [the diff that was proposed]
- **Developer decision:** Apply | Modify (then Apply) | Reject
- **Modification rounds (if any):** [N] — proposal revised [N] times before approval
- **Developer comment (if any):** [verbatim text]
- **Banned-actions self-check:** all clear | [item that failed and was fixed in revision]
```

### 7. Hit the attempt limit

When the configured max attempts is reached and the suite is still
not green, **stop**. Do not try one more time. Report:

> ### Attempt limit reached — still failing ✗
>
> **Attempts made:** [N] (limit: [N])
> **Persistent failures:**
> - [testName] — [error] — [diagnosis attempts so far]
>
> Beyond [limit] attempts on the same failure, the issue is usually
> structural rather than a simple test/code mismatch. Examples of
> structural issues that look like test failures:
> - The AC was interpreted differently in the implementation vs the
>   test (one needs to change to match the other)
> - The plan step skipped a piece of work that the test now expects
> - The production code has a design issue that only surfaces under
>   the test's specific input
>
> **Your decision:**
> 1. **Override the limit and try [N] more attempts** — only if you
>    have a fresh diagnosis the prior attempts did not have (will be
>    logged as an override)
> 2. **Pause and re-think** — exit cleanly; come back when you have
>    a clearer view of what is wrong (recommended)
> 3. **Loop back to execute-prompt-steps** — if you suspect the
>    underlying production code from an earlier plan step was wrong,
>    redo that step and come back
> 4. **Loop back to generate-unit-tests** — if you suspect the test
>    itself encodes the wrong expectation
>
> Which would you like?

Hard ceiling: even with overrides, never exceed 5 total attempts in
a single skill invocation.

### 8. End-of-run handling

When the suite is green and the developer approves (or chooses
re-run-to-confirm and that re-run also passes), write a final summary
to the log:

```markdown
## Test run complete

- **Started:** YYMMDD-HH:MM:SS
- **Completed:** YYMMDD-HH:MM:SS
- **Attempts made:** [N]
- **Fix attempts made:** [N]
- **Final result:** Passed
- **Files modified during fixes:** [list]
```

Then tell the developer:

> Test suite green after [N] attempt(s). Test-run log at
> .github/story-test-run-logs/STORY-DESCRIPTION-test-run-YYMMDD-HHMMSS.md
>
> Plan Step [N] is now complete. Go back to execute-prompt-steps to
> resume from Step [N+1].

(Do not wrap the filename in backticks — Copilot Chat auto-links
backticked filenames into broken vscode-file:// URLs.)

When the suite is not green and the developer pauses or hits the
limit, write the run as not-complete:

```markdown
## Test run paused (not complete)

- **Started:** YYMMDD-HH:MM:SS
- **Paused at:** YYMMDD-HH:MM:SS
- **Attempts made:** [N]
- **Final result:** [Failed | Environment-broken | Skips-not-resolved]
- **Persistent failures (if any):** [list]
- **Reason for pause:** [Attempt limit | Developer chose Stop | Environment]
```

---

## Resuming an interrupted run

If the developer invokes the skill and a test-run log already exists
for this story with status not yet complete, do not start over. Read
the log, find the last attempt and its result, and ask:

> I see a test-run log for this story —
> .github/story-test-run-logs/STORY-DESCRIPTION-test-run-YYMMDD-HHMMSS.md
>
> The last attempt was Run [N] ([result]). The persistent failures
> at the time of pause were: [list].
>
> Resume from where we left off, or start over with a fresh log?

Wait for an explicit choice. Never auto-resume.

---

## What a fix proposal must always show

These are the non-negotiables of section 4c — every proposal includes
them, every time:

- **The actual diff** — what comes out, what goes in. Not a description.
- **Root cause in one line** — the actual mismatch between expected
  and actual behaviour, not a restatement of the failure.
- **Why this fixes it** — one or two sentences tying the change to
  the AC and to the failing assertion.
- **What stays the same** — the deliberate non-changes that bound the
  blast radius.
- **Scope check** — confirmation that the file is in the execution
  log or test-generation log.
- **Banned-actions self-check** — explicit pass on the items in the
  banned-actions table.

If any of these are missing from a proposal, do not present it to the
developer — go back and produce a complete proposal.

The banned-actions table at the top of this skill is the authoritative
list of what cannot appear in a fix. The proposal pattern in section 4c
exists to make every banned-action check visible to the reviewer.

---

## Developer override paths

- **Defer-this-failure** — within a multi-failure run at section 3.
  Triggers: *"skip this failure for now"*, *"do the others first"*,
  *"come back to this one"*. Mark the failure as developer-deferred
  in the log, propose a fix for the next failure instead. Deferred
  failures must still be addressed before the run can end green.
- **Modify-the-proposal** — at section 4c. Triggers: *"change X to
  Y"*, *"keep this but also do Z"*, *"actually the diff should..."*.
  The skill revises the proposal per the feedback and re-presents
  it. Multiple revision rounds are allowed; each round is logged.
- **Override attempt limit** — only at section 7. Triggers: *"set
  max attempts to N"*, *"try one more time"*. Allowed up to the hard
  ceiling of 5.
- **Stop the run** — at any decision point. Triggers: *"stop"*,
  *"pause"*, *"let me think"*. Log the run as paused, exit cleanly.
- **Ambiguous phrasing** — *"hmm"*, *"hold on"*, *"let me see"*,
  *"not sure"*. **Do not act on these.** Ask:
  > To make sure I get this right — do you mean:
  > 1. Stop the run entirely (we can resume later),
  > 2. Stay paused while you think, then continue from here, or
  > 3. Something else (please be explicit)?
  Wait for an explicit choice.

---

## Examples

### Calibrating failure diagnoses

| Vague (banned) | Specific |
|---|---|
| "Test is broken" | "Test expects empty page on no-match but production code throws OwnerNotFoundException — production-code-wrong (test correctly encodes AC2)" |
| "Production code is wrong" | "Test asserts case-insensitive match but production code uses equalsIgnoreCase only on lastName, not on firstName — production-code-wrong (scope drift from AC1)" |
| "Just flaky" | "Test asserts `Instant.now()` is within 1 second of the captured value — test-wrong (depends on real clock; needs injected Clock per java-testing.instructions.md)" |
| "Probably env" | "Test failed because Karma can't find ChromeHeadless — environment (CI vs local browser config); not a code issue" |

### Calibrating skip / disabled investigation

| Vague (banned) | Specific |
|---|---|
| "It was already flaky" | "OwnerControllerTest.searchHandlesUnicode was @Disabled in a previous commit with no reason. Investigated: passes when run in isolation; failed in main suite due to test pollution from another test mutating a shared static. Real bug; un-skip and fix the polluting test" |
| "Out of scope" | "Test for the old GET /owners/findByLastName endpoint was @Disabled because that endpoint is being deprecated in this story. Confirmed deprecation note in context.md AC5; delete the test (do not leave @Disabled)" |

### Calibrating end-of-run summaries

| Too vague | Useful |
|---|---|
| "Tests pass" | "Suite green on attempt 2. One fix applied: OwnerService.searchOwners changed to use `containsIgnoreCase` across all four fields (was only on lastName) per AC1. No test code changed." |
| "Done" | "Suite green on attempt 1. No fixes needed. All 12 tests covering AC1–AC3 passed; AC4 covered by OwnerControllerTest in a later plan step." |

### Calibrating fix proposals

A proposal is good when a reviewer can read it once and know exactly
what is happening. A proposal is bad when the reviewer has to open
the file to understand the change.

**Bad proposal** (the reviewer must open the file to verify):

> Fix the searchOwners method to handle the case insensitivity
> correctly across all the search fields.

**Good proposal:**

> **Diagnosis:** production code wrong
>
> **Root cause:** AC1 requires case-insensitive contains across
> lastName, firstName, address, and telephone, but
> `OwnerService.searchOwners` only applies `containsIgnoreCase` to
> lastName.
>
> **File to change:** `src/main/java/.../OwnerService.java`
>
> **Scope check:** ✓ in execution log
>
> **Proposed change:**
> ```diff
> - return ownerRepository.findByLastNameContainingIgnoreCase(query, pageable);
> + return ownerRepository
> +   .findByLastNameContainingIgnoreCaseOrFirstNameContainingIgnoreCaseOrAddressContainingIgnoreCaseOrTelephoneContainingIgnoreCase(
> +     query, query, query, query, pageable);
> ```
>
> **Why this fixes the failure:** Test
> `searchOwners_matchesAcrossAllFieldsIgnoringCase` asserts that the
> result includes an owner whose firstName contains the query string;
> the current code only checks lastName.
>
> **What stays the same:** Pagination behaviour, sort order, empty-
> result handling — none of those are touched.

---

## Reference files

- `assets/test-run-log-template.md` — Template for the test-run log
  file with section headers and the per-run and per-fix entry formats.
  Read this when you need to remember the exact log structure.
