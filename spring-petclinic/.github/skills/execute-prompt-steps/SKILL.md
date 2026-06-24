---
name: execute-prompt-steps
description: >
  Executes an approved prompt-steps plan one step at a time against the
  codebase, with explicit human approval between every step. Use this
  whenever a developer attaches a prompt-steps file and asks to start
  implementing the plan, run the next step, resume execution, or execute
  the story. Works across Angular frontend, Spring Boot backend, and
  full stack work, and across new development, enhancements, and bug
  fixes. The skill processes exactly one step per invocation, refuses to
  plow ahead, refuses to generate test code (test steps hand off to the
  generate-unit-tests skill), refuses to auto-fix convention drift, and
  refuses to execute manual validation steps on the developer's behalf.
  Every step ends with the developer choosing approve, reject with
  comment, or skip. An execution log is appended to a timestamped file
  under .github/story-execution-logs/.
---

# Execute Prompt Steps Skill

Walks a developer through an approved `prompt-steps` file one step at a
time, doing the code changes for each step and then stopping for a
human decision before the next step.

This is the third skill in the Copilot-driven SDLC loop:

| Skill | Input | Output | Purpose |
|---|---|---|---|
| `build-context` | JIRA story | `context.md` | Capture **what** the work is |
| `build-prompt-steps` | `context.md` | Timestamped plan file | Plan **how** to implement it |
| `execute-prompt-steps` (this skill) | plan file | Code changes + execution log | Run the plan, one step at a time |
| `generate-unit-tests` | code changes | Test files | Write tests for what was implemented |

Stack assumed: **Angular** on the frontend, **Java Spring Boot
microservices** on the backend.

---

## Why this skill exists

When a developer asks Copilot to "implement the plan", the default
behaviour is to blast through every step in one turn, mixing production
code and test code, inventing file paths it never verified, and silently
auto-fixing convention drift that the developer never saw. This breaks
the HITL-equivalent loop in three ways:

1. **No checkpoints.** Drift in step 2 isn't caught until step 6 has
   compounded on top of it.
2. **No separation of concerns.** Production code, tests, and drift
   fixes get intertwined, making clean review impossible.
3. **Phantom edits.** Copilot describes changes in chat without actually
   writing them to disk, and the developer doesn't notice until something
   downstream fails.

Two failure modes this skill is designed to prevent:

1. **Plow-through mode.** Executing steps 1 through N in one turn
   without stopping. **A skill that processes more than one step per
   invocation is worse than no skill at all** — it defeats the human
   checkpoint that is the entire point of the HITL approach.
2. **Step-type blindness.** Treating every step as an implementation
   step. The plan distinguishes inventory, design-decision,
   implementation, test, frontend-wiring, validation, convention-drift,
   and non-functional steps — each needs different handling. Executing
   a validation step (which is meant for the developer to do manually)
   or auto-fixing convention drift defeats the plan's intent.

Everything below serves these two goals.

---

## Banned actions — never do any of these

| Banned | Why | Do instead |
|---|---|---|
| Execute more than one step per invocation | Defeats the HITL checkpoint | Do exactly one step, stop, wait for the developer's decision |
| Generate unit, integration, or end-to-end test code | That is the generate-unit-tests skill's job | When the current step is a test step, stop and hand off |
| Auto-fix convention drift surfaced by a convention-drift step | The plan deliberately surfaces drift for the developer to decide on | List the drift; let the developer choose whether to fix |
| Execute a validation step on the developer's behalf | Validation is a manual walkthrough — no Copilot involvement | List the ACs to walk, stop, wait for the developer to complete the walkthrough |
| Invent file paths, class names, or method signatures not visible in the repo or named in the plan | Premature codification — produces code that doesn't fit | Read the relevant file first; if the plan is silent, ask one targeted question |
| Describe edits in chat without writing them to disk | Phantom edits — developer thinks code was written when it wasn't | Use file-write tools; confirm the file was saved before reporting done |
| Skip applying a relevant instruction file whose applyTo glob matches the edited file | Convention drift — the whole point of instructions is enforcement | Apply every matching instruction; state which ones applied |
| Continue past a failed write, compile, or contradiction in the plan | Compounds errors silently | Stop, log as Failed, ask the developer how to proceed |

**This is a hard preflight check.** Before reporting a step done,
verify exactly one step was processed, no test code was written, every
file claimed-as-edited exists on disk with the new content, and the
step's intent matched its type.

---

## Inputs

Like `build-prompt-steps`, this skill reads from **chat attachments,
not from disk**. The developer must consciously attach the two files
for this run:

- **Context file** — the same `STORY-DESCRIPTION-context-YYMMDD-HHMMSS.md`
  the plan was built from. Used as the source of truth for ACs the
  step refers back to.
- **Prompt steps file** — the `STORY-DESCRIPTION-prompt-steps-YYMMDD-HHMMSS.md`
  the developer wants to execute.

**Never read either file from disk or pick one yourself.** Do not look
in `.github/story-context-files/` or `.github/story-prompt-steps/`. The
developer must attach the specific files for this story. If both are
not attached, stop and ask.

The skill writes one new file (the execution log) per run — see
section 6 below.

---

## Workflow

### 1. Verify inputs

Before doing anything else, run these checks in order:

- **Both files are attached.** If either is missing, ask:
  > I need both the context file and the prompt-steps file attached to
  > the chat before I can start. I see [what's attached, if anything] —
  > please also attach [the missing file].

  Stop and wait. Do not proceed.

- **The attached files are the right types.** Presence is not enough.
  Verify the prompt-steps file has the expected structure (standing
  instructions block at the top, pre-flight section, numbered steps).
  Verify the context file has the expected sections (What Are We
  Trying to Achieve, Expected Behaviour, Acceptance Criteria). If
  either looks wrong, say:

  > The attached [context/prompt-steps] file doesn't look like a
  > [context/plan] file — it's missing the expected sections. Did you
  > attach the right file?

  Stop and wait.

- **The two files pair correctly.** Both should share the same
  STORY-DESCRIPTION prefix per the project's naming convention. If they
  don't match, warn:

  > The context file (STORY-A) and prompt-steps file (STORY-B) don't
  > appear to be for the same story. Are you sure these go together?

  Continue only if the developer confirms.

- **Confirm files and story before executing.** Once both files are
  valid and paired, state back what you found:

  > Executing from:
  > • Plan: [attached prompt-steps filename] ([N] steps)
  > • Context: [attached context filename]
  > • Story: "[goal from What Are We Trying to Achieve, one line]"
  >
  > I will execute one step at a time, stopping after each for your
  > decision. Ready to start with Step 1?

  Wait for go-ahead. This is the first human checkpoint.

- **`.github/copilot-instructions.md` exists.** If missing, warn the
  developer that team conventions will not auto-apply (do not put
  backticks around the filename — Copilot Chat auto-links backticked
  filenames into broken vscode-file:// URLs):

  ```markdown
  > ## ⚠️ Missing copilot-instructions.md
  >
  > I don't see .github/copilot-instructions.md in this repo.
  >
  > **What this means:** the generated code will not be checked against
  > the team's repo-wide conventions. Path-scoped instructions under
  > .github/instructions/ will still apply, but cross-cutting standards
  > may be missed.
  >
  > **Recommendation:** run the relevant build-copilot-instructions
  > skill before executing the plan. Otherwise convention drift is likely.
  >
  > **Continue without it, or pause to set up copilot-instructions.md first?**
  ```

  Continue only if the developer says yes.

### 2. Identify the next step

On the first invocation, the next step is Step 1.

On subsequent invocations, look for an existing execution log for this
story (see "Resuming an interrupted run" below). If one exists, the
next step is the one after the last completed-or-skipped step. Never
auto-resume — confirm with the developer first.

Read the step from the plan. Note its **type** (see section 3) — the
type determines how you handle it.

### 3. Handle the step according to its type

The plan's steps fall into eight types. Each is handled differently.

#### Type A — Inventory step (always Step 1)

The step asks Copilot to list affected files with a one-line role for
each. **No code changes.**

- Read the files named in the step.
- Produce the list as the step's suggested prompt asks for.
- Stop and use the step's existing review checkpoint as the criteria.

#### Type B — Design decision step

The step asks Copilot to propose 2–3 options with pros and cons for a
technical choice. **No code changes — the developer picks the option.**

- Produce the options as the step's suggested prompt asks for.
- Do not pick an option silently.
- Stop and use the step's existing review checkpoint as the criteria.
- The developer's choice becomes input for the next implementation step
  — capture it in the execution log so the next step has context.

#### Type C — Implementation step

The step asks for a concrete code change to one logical unit (one file,
one method, one component).

- Read the target files before editing.
- For every file you are about to edit, identify which
  `.github/instructions/` files have an applyTo glob that matches it.
  State briefly which ones apply:

  > Editing OwnerController.java — applying java-conventions, owasp-java,
  > logging-java, error-handling-java, api-design, performance-java.

  This is not optional. Every matching instruction must shape the code.

- Make the change. Production code only — no test code, even if the
  step description mentions testing in passing.
- Verify each file write succeeded.
- Stop and use the step's existing review checkpoint as the criteria.

#### Type D — Test step (groups tests at significant stages)

The step asks for unit tests to be added.

- **Do not write the tests in this skill.** Stop and hand off:

  > ### Step [N] is a test step
  >
  > **What needs testing:** [list from the step's goal — e.g. "the
  > searchOwners service method and the new repository derived query"]
  >
  > **Source files involved:** [files added/changed in earlier
  > implementation steps]
  >
  > **Recommended next action:** Run the `generate-unit-tests` skill,
  > attaching this plan file and the context file. It will write the
  > tests, then `run-and-fix-tests` will execute them.
  >
  > Once the test step is done, come back to me to continue from
  > Step [N+1].

  Log this step in the execution log as **Handed off — pending
  generate-unit-tests** so the resume logic knows where to pick up.

- Do not mark the step as approved or skipped. It is a handoff, not a
  completion.

#### Type E — Frontend wiring step (full stack only)

A connection step — usually wiring a frontend component to a backend
change (form field names, route paths, response shape handling).

- Handle as an Implementation step (Type C), with extra care to verify
  both ends of the wire match (request shape, response shape, field
  names, status codes).
- State explicitly what contract is being matched:

  > Wiring search-form.component to /api/v1/owners/search — request
  > shape: { lastName: string }; response shape: { content: Owner[],
  > totalElements: number }; matches OwnerController.search signature.

#### Type F — Validation step (always second-to-last)

The plan says the developer walks through every AC manually against
the running app. **No Copilot involvement.**

- Do not attempt to verify ACs yourself.
- Do not run the app or simulate the walkthrough.
- Stop and present the AC list with a checklist:

  > ### Step [N] — Manual validation
  >
  > This step is for you to do, not me. Walk through each AC below in
  > the running app and mark pass / fail / unclear.
  >
  > **Acceptance criteria from [context filename]:**
  > 1. [AC text]
  > 2. [AC text]
  > ...
  >
  > **Your decision when done:**
  > 1. **All ACs pass** — approve, I will move to Step [N+1]
  > 2. **One or more ACs fail** — tell me which, with which earlier
  >    step's output caused the failure; I will help loop back
  > 3. **Skip** — only if you've decided to validate later
  >
  > Which would you like?

#### Type G — Convention drift step (always last code-related step)

The plan says Copilot reviews all changed files against
`copilot-instructions.md` and flags drift. **Lists drift; never
auto-fixes.**

- Read every file changed in earlier implementation/wiring steps from
  the execution log.
- Check each against `copilot-instructions.md` and any
  `.github/instructions/` files matched by applyTo.
- Produce a drift list (file → rule → what was drifted → suggested
  fix). If no drift, say so explicitly.
- Stop and use the step's existing review checkpoint as the criteria —
  the developer decides what to fix and what to leave.

#### Type H — Non-functional step (when present)

The plan documents how a non-functional target (performance,
accessibility, load) will be verified. **Not unit-testable; not run
inline.**

- Produce the verification documentation as the step's suggested
  prompt asks for.
- Do not attempt to run the verification.
- Stop and use the step's existing review checkpoint as the criteria.

#### If the step type is ambiguous

If you cannot tell which type a step is, do not guess. Stop and ask:

> Step [N] could be either an implementation step or a [other type]. I
> want to make sure I handle it right before touching code. Which is it?

### 4. Step preflight before reporting done

Before telling the developer the step is complete, every item must
pass. If any fail, do not report done — fix what failed or surface it.

- [ ] Exactly one step from the plan was processed in this turn
- [ ] The step's type was identified correctly and handled per section 3
- [ ] No test files (`*Test.java`, `*.spec.ts`) were created or modified
      by this skill (test steps hand off; they do not write code here)
- [ ] No convention drift was auto-fixed — drift is listed, not patched
- [ ] No validation work was simulated — validation steps stop and ask
      the developer to walk through ACs manually
- [ ] Every file the skill claimed to edit exists on disk with the new
      content
- [ ] Every applicable instruction file (matched by applyTo glob) was
      applied
- [ ] No file paths, class names, or method signatures were invented —
      every name used either existed in the repo or was named in the
      plan or context
- [ ] If the step touched HIPAA-relevant data (PHI identifiers), the
      hipaa-guardrails rules were applied to the new code
- [ ] For implementation/wiring steps, the code compiles / passes
      type-check (`mvn compile`, `ng build --configuration=development`)
      if a build tool is reachable

### 5. Stop and ask for the decision

After preflight passes, summarise what was done and stop. Use this
exact pattern (the step's own review checkpoint becomes the criteria
the developer evaluates against — do not invent generic criteria):

> ### Step [N] — [step title] complete
>
> **Type:** [Inventory / Design decision / Implementation / Test (handed
> off) / Frontend wiring / Validation (pending you) / Convention drift /
> Non-functional]
>
> **What I did:** [one-paragraph summary]
>
> **Files changed:** *(omit for Inventory, Design decision, Validation,
> Convention drift, Non-functional steps that don't write code)*
> - path/to/File1.java — [one-line description of the change]
> - path/to/File2.java — [one-line description of the change]
>
> **Instructions applied:** [comma-separated list]
>
> **What I noticed:** [optional — patterns matched, conventions chosen
> between, smells seen but left out of scope]
>
> **Plan's review checkpoint for this step:** [verbatim quote from the
> step's review checkpoint in the plan]
>
> **Your decision:**
> 1. **Approve** — I will move to Step [N+1]
> 2. **Reject with comment** — tell me what to change and I will redo
>    Step [N]
> 3. **Skip** — only if Step [N] turned out to be unnecessary; I will
>    log it as skipped and move to Step [N+1]
>
> Which would you like?

Wait for an explicit choice. **Do not move to the next step on silence,
filler words (`ok`, `next`, `sure`), or ambiguous phrasing.** This
mirrors the build-context skill's empty-reply handling: missing
choices must be acknowledged, not silently swallowed.

### 6. Update the execution log

Write or append to the execution log file after every step (approved,
rejected-and-redone, skipped, handed-off, or failed). This file is the
persistent state of the run — it lets the skill resume cleanly if the
chat session ends mid-execution.

**Location:** `.github/story-execution-logs/`

**Filename:** `STORY-DESCRIPTION-execution-YYMMDD-HHMMSS.md` — same
STORY-DESCRIPTION as the context and plan files, with the timestamp of
when execution started (not when each step ran).

**Note for the toolkit owners:** the path
`.github/story-execution-logs/` and the filename format above need to
be added to `.github/instructions/copilot-output-naming.instructions.md`
when this skill is shipped, so the convention is documented alongside
context files and prompt-steps files.

**Entry format per step:**

```markdown
## Step [N] — [step title]

- **Type:** Inventory | Design decision | Implementation | Test | Frontend wiring | Validation | Convention drift | Non-functional
- **Status:** Approved | Rejected (redone) | Skipped | Handed off (pending generate-unit-tests) | Failed | Pending (validation walkthrough)
- **Started:** YYMMDD-HH:MM:SS
- **Completed:** YYMMDD-HH:MM:SS
- **Files changed:** path/to/File1.java, path/to/File2.java
- **Instructions applied:** java-conventions, owasp-java, logging-java
- **Design decision chosen (if applicable):** [verbatim choice]
- **Developer comment (if any):** [verbatim text]
- **Notes:** [anything the skill flagged in "What I noticed"]
```

### 7. Handling failures mid-step

If a file write fails, a compile fails, the plan contradicts the
context, or any other blocker hits, stop. Log the step as Failed and
surface it:

> ### Step [N] failed
>
> **What failed:** [error message, what was being attempted]
>
> **What I tried:** [what was done before the failure]
>
> **Your decision:**
> 1. **Provide guidance** — tell me how to resolve it and I will retry
> 2. **Skip this step** — log as skipped and move to Step [N+1]
> 3. **Stop the run** — pause execution; we can resume later from this step
>
> Which would you like?

Never silently work around a failure. A skipped step is recoverable; a
silently broken one is not.

### 8. End-of-plan handling

When the developer approves the last step in the plan, write a final
summary entry to the execution log:

```markdown
## Execution complete

- **Started:** YYMMDD-HH:MM:SS
- **Completed:** YYMMDD-HH:MM:SS
- **Steps approved:** [N]
- **Steps skipped:** [N]
- **Steps rejected and redone:** [N]
- **Steps handed off to generate-unit-tests:** [N]
- **Steps failed:** [N]
- **Total files changed:** [list]
```

Then tell the developer:

> All plan steps executed. Execution log at
> .github/story-execution-logs/STORY-DESCRIPTION-execution-YYMMDD-HHMMSS.md
>
> Any test steps in the plan were handed off — make sure those have
> been completed via generate-unit-tests and run-and-fix-tests before
> opening the PR.

(Do not wrap the filename in backticks in the message to the developer
— Copilot Chat auto-links backticked filenames into broken
vscode-file:// URLs.)

---

## Resuming an interrupted run

If the developer invokes the skill and an execution log already exists
for this story (search by STORY-DESCRIPTION) with status not yet
complete, do not start over. Read the log, find the last completed-or-
skipped step, and ask:

> I see an execution log for this story —
> .github/story-execution-logs/STORY-DESCRIPTION-execution-YYMMDD-HHMMSS.md
>
> The last completed step was Step [N] ([status]). Should I resume
> from Step [N+1], or start over with a fresh log?

Wait for an explicit choice. Never auto-resume — the developer may
have made changes outside the skill that change what should happen next.

**Special case — last step was a test handoff.** If the last entry's
status is "Handed off (pending generate-unit-tests)", ask:

> Step [N] was handed off to generate-unit-tests. Has that completed?
> 1. **Yes** — I will mark Step [N] as approved and move to Step [N+1]
> 2. **No** — please run generate-unit-tests first, then come back
> 3. **Skip the test step** — I will mark it skipped and move to Step
>    [N+1] (not recommended — your story will ship without those tests)

---

## What never goes in the production code

These belong elsewhere in the loop, not in `execute-prompt-steps` output:

- **Unit tests** — generate-unit-tests skill writes these
- **Integration tests / end-to-end tests** — out of scope; flag if the
  plan asks for them
- **Build configuration changes** (pom.xml dependencies, angular.json
  settings) **unless the plan step explicitly calls for it** — never
  add dependencies opportunistically
- **Commented-out code** — write the change or don't; do not leave
  alternatives commented out for review
- **TODO comments without an owner and date** — either resolve the
  issue or surface it in "What I noticed", not buried in the code
- **Auto-fixes to convention drift** — the convention-drift step
  exists precisely to surface this for developer review, not for
  silent correction

---

## Developer override paths

Override types — never conflate them:

- **Step-level skip** — applies only to the current step. Triggers:
  *"skip this step"*, *"this step isn't needed"*, *"move past this one"*.
  Log as Skipped, continue to next step in the next invocation.
- **Run-level pause** — applies to the whole run. Triggers: *"stop"*,
  *"pause"*, *"let me check something first"*. Log the run as paused at
  the current step, exit cleanly. The developer can resume later.
- **Ambiguous phrasing** — for example *"let's skip this for now"*,
  *"hold on"*, *"hmm"*. **Do not act on these.** Ask:

  > To make sure I get this right — do you mean:
  > 1. Skip only this step and continue with the next, or
  > 2. Pause the whole run and resume later?

  Wait for an explicit choice. Same pattern as build-context.

---

## Examples

### Calibrating "What I did" summaries

| Too vague | Specific |
|---|---|
| "Added the search endpoint" | "Added GET /api/v1/owners/search to OwnerController, delegating to a new searchOwners method on OwnerService; both follow existing patterns in OwnerController.findById and OwnerService.findById" |
| "Updated the service" | "Added searchOwners(String lastName, Pageable pageable) to OwnerService, calling the new findByLastNameContainingIgnoreCase repository method; constructor-injected, no field injection" |
| "Wrote the repository method" | "Added findByLastNameContainingIgnoreCase(String lastName, Pageable pageable) to OwnerRepository — Spring Data derived query, no custom @Query needed" |

### Calibrating "What I noticed"

| Too vague (or absent) | Useful |
|---|---|
| "Looks good" | "OwnerController already had a private validateLastName helper — I reused it rather than duplicating the validation logic" |
| (silence) | "The existing GET /owners endpoint uses page size 20 by default — I matched it for consistency, though the plan step didn't specify" |
| "Done" | "Saw that OwnerService.findById throws OwnerNotFoundException — for search I return an empty page instead, since no-results is not an error condition" |

### Step-type handling cheat sheet

| Step says... | Type | Skill does |
|---|---|---|
| "List affected files with one-line role" | Inventory | Produce list; no code; stop at checkpoint |
| "Propose three options with pros/cons" | Design decision | Produce options; do not pick; stop at checkpoint |
| "Add method X to service Y" | Implementation | Edit file; apply instructions; verify write; stop at checkpoint |
| "Wire component to new endpoint" | Frontend wiring | Edit; verify request/response shapes match; stop at checkpoint |
| "Add unit tests for service Y" | Test | Hand off to generate-unit-tests; log as handed off |
| "Walk through ACs manually" | Validation | Present AC checklist; do not run app; stop at checkpoint |
| "Review changed files for drift" | Convention drift | List drift; do not auto-fix; stop at checkpoint |
| "Document how P95 target will be verified" | Non-functional | Produce doc; do not run verification; stop at checkpoint |

---

## Reference files

- `assets/execution-log-template.md` — Template for the execution log
  file with section headers and the per-step entry format. Read this
  when you need to remember the exact log structure.
