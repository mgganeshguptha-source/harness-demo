---
name: build-prompt-steps
description: >
  Generates a numbered execution plan from a context.md file, so the developer
  can implement the story step by step in Copilot Chat — reviewing each step's
  output before moving to the next. Use this whenever a developer asks for
  prompt steps, an execution plan, or a step-by-step plan from a context.md
  they have prepared. Works across Angular frontend, Spring Boot backend, and
  full stack work, and across new development, enhancements, and bug fixes.
  The skill writes the plan to a timestamped file under
  .github/story-prompt-steps/, structured as goal + suggested prompt +
  review checkpoint per step, with a standing instructions block at the
  top. In NON-INTERACTIVE / CI mode it reads the newest context file from
  .github/story-context-files/ on disk (not a chat attachment) and produces
  the full plan in one pass without human checkpoints.
---

# Build Prompt Steps Skill

Helps a developer turn an approved `context.md` into a numbered execution
plan they can run step by step in Copilot Chat. Each step is small enough
to review meaningfully before moving on, so the developer stays in control
of what Copilot does to their code.

This is the second skill in the two-step Copilot workflow:

| Skill | Input | Output | Purpose |
|---|---|---|---|
| `build-context` | JIRA story | `context.md` | Capture **what** the work is |
| `build-prompt-steps` (this skill) | `context.md` | Timestamped plan file | Plan **how** to implement it |

Stack assumed: **Angular** on the frontend, **Java Spring Boot microservices**
on the backend.

---

## Why this skill exists

Pasting an entire context.md into Copilot with "implement this" produces
unpredictable results. Copilot makes design decisions invisibly, picks
implementation approaches that don't match the team's conventions, and
generates large diffs that are hard to review.

The plan-then-execute pattern fixes this by breaking the work into small,
reviewable steps. The developer sees what Copilot intends to do *before*
it touches code, and can course-correct at every step.

This skill produces the plan. The developer drives execution manually.

Two failure modes this skill is designed to prevent:

1. **The unreviewable mega-step.** Steps so large that the developer
   skims the output and approves it without really reading. If a step's
   prompt asks Copilot to "implement the backend," the resulting diff is
   unreviewable. Right granularity: one logical change per step,
   typically one file or one design decision.
2. **The drifted plan.** A plan generated against an outdated context.md,
   or a plan that quietly assumes implementation approaches the developer
   would have chosen differently. The skill must surface design decisions
   as explicit steps, not bake them in.

---

## Workflow

### 0. Mode detection — interactive vs non-interactive (CI)

**Before anything else, determine the run mode.**

- **Interactive mode (default):** a human is present and attaches files in chat.
  Use the attachment-based workflow in steps 1+ below.
- **Non-interactive / CI mode:** invoked by an automated harness with no chat and
  no attachments. **CI mode requires an EXPLICIT positive signal** — at least one of:
  a system/harness instruction stating the run is non-interactive or "CI mode", or
  the invoking prompt explicitly saying "CI mode" / "read the context from disk".
  **The mere absence of an attachment is NOT sufficient to enter CI mode** — a
  developer in an IDE who simply forgot to attach a file must get the normal
  interactive "please attach the context file" response, not a disk read.

**When in non-interactive / CI mode, override the attachment rules as follows:**

1. **Do NOT wait for a chat attachment and do NOT stop to ask for one.**
2. **Read the context file from disk:** take the **newest** file in
   `.github/story-context-files/`. That IS the authoritative context for this run
   (the build-context skill wrote it there in CI mode). The normal rule
   "never substitute a file found on disk" is REVERSED in CI — disk is the source.
3. If `.github/story-context-files/` is empty or missing, do not invent a plan —
   write nothing and report that no context file was found (the harness will halt).
4. Generate the plan exactly as in interactive mode (Impacted Files block + steps),
   but **do not pause for human checkpoints** — produce the full plan in one pass.
5. **In CI, write the plan to the path the harness specifies in its prompt**
   (the harness uses `.harness/prompt-steps.md` as the working/audit copy so it can
   append the execution record after coding). Follow the harness's stated output
   path; do not also write to `.github/story-prompt-steps/` unless asked. Do not ask
   for approval; the harness gates approval separately.
6. If the context file contains unresolved `[NEEDS CLARIFICATION]` markers, do not
   plan around them — the harness should have halted earlier; if you still see them,
   write nothing and report the unresolved markers.

**Why:** in CI the file hand-off happens on disk, not via chat. The harness wrote
the context to `.github/story-context-files/`; this skill reads it from there,
plans in one pass, and the harness handles approval gating.

---


The developer attaches the context file to the chat when invoking this
skill. The skill reads from chat attachments, not from disk. Throughout
this skill, "the context file" means whatever file the developer
attached, with whatever filename they chose.

Before generating the plan, run these checks in order:

- **A context file is attached to the chat.** If nothing is attached,
  ask: *"I don't see a context file attached. Please attach the
  context file you want me to plan from."* and stop. Do not proceed
  with anything else.

- **The attached file is actually a context file.** Presence is not
  enough — the developer may have attached the JIRA story, an old
  context file, copilot-instructions.md, or some other file by mistake.
  Verify the attached file contains the expected context structure: at
  minimum the sections "What Are We Trying to Achieve", "Expected
  Behaviour", and "Acceptance Criteria". If those sections are not
  present, do not proceed — say:

  > The attached file doesn't look like a context file — it's missing
  > the expected sections (What Are We Trying to Achieve, Expected
  > Behaviour, Acceptance Criteria). Did you attach the right file?
  > Please attach the context file produced by the build-context skill.

  Then stop and wait.

- **Never read a context file from disk or pick one yourself.** Do not
  look in `.github/story-context-files/` or anywhere else on disk and
  choose a file. The developer must consciously attach the specific
  context file for this story. If no valid context file is attached,
  stop and ask — do not substitute a file found on disk, and do not
  infer the context from the conversation history.

- **Confirm the file and story before planning.** Once a valid context
  file is attached, state which file and which story you are planning
  from, so a wrong-file mistake is caught before a full plan is
  generated:

  > Planning from: [attached filename] (story: "[the goal from What Are
  > We Trying to Achieve, one line]"). Generating the plan now.

  If the developer indicates this is the wrong story or file, stop and
  ask them to attach the correct one.

- **No unresolved `[NEEDS CLARIFICATION]` items in the context file.**
  If any exist, show this warning and pause:

  ```markdown
  > ## ⚠️ Unresolved clarifications in the context file
  >
  > The context file still has [NEEDS CLARIFICATION] items. The plan
  > will make assumptions for each one, and the resulting code will
  > reflect those assumptions — which may be wrong.
  >
  > **Recommendation:** resolve clarifications with your BA or PO first.
  >
  > Continue with assumptions, or pause to resolve clarifications first?
  ```

  Continue only if the developer says yes. If they continue, the plan's
  pre-flight section must list each unresolved item and the assumption
  the plan makes about it.

- **`.github/copilot-instructions.md` exists.** If missing, warn the
  developer that team coding conventions won't be auto-loaded, and the
  generated code will follow generic Spring Boot / Angular defaults
  instead. Same continue-or-pause prompt.

### 2. Read the inputs

Read the attached context file fully. **Note its exact filename** — you
will reference this filename throughout the generated plan, so the
developer can re-attach the same file in future sessions.

Read `.github/copilot-instructions.md` fully (auto-loaded by Copilot
when present). Note:
- Layer (backend / frontend / full stack) — inferred from context.md
- Story type (bug fix / new development / enhancement) — inferred from
  Current Behaviour presence and verb choice in What Are We Trying to
  Achieve
- Whether the UI interaction model is changing (Expected Behaviour
  describes new trigger/loading/empty/error states) or unchanged

### 3. Lightweight codebase inventory

Read enough of the codebase to know which files the plan will need to
touch. This is **not** the full analysis — it's just the files-affected
list. Examples for the assumed stack:

- For a backend search/filter story: the relevant `Controller`,
  `Repository` or `Service`, and existing tests for both.
- For a frontend story: the relevant component (`.ts`, `.html`, `.scss`)
  and its spec file.
- For a full stack story: both sets, plus any DTO / API model class.

Do not read every file in the repo. Read only what the story directly
touches. If the developer's repo is unfamiliar, ask them to point at
the relevant directory before proceeding.

### 4. Determine plan granularity

Aim for **8–12 steps** for a typical story. Adjust based on size:
- Trivial bug fix: 4–6 steps may be enough
- Large enhancement touching multiple components: up to 15 steps,
  but consider whether the story is too large and should be split

**One logical change per step.** Examples of "one logical change":
- One file modified for one purpose (one method, one component)
- One design decision made and explained
- One layer of tests added (e.g. all repository tests, not split per
  test method)

**Tests at significant stages, not after every code step.** Group tests
into checkpoints — typically one test step after the backend work is
complete, one after the frontend work is complete. Make the test step
mandatory and prominent in the plan.

**Always include a validation step at the end.** This is separate from
tests. Tests verify the code does what the developer wrote it to do.
Validation verifies the running system does what context.md asked for.
The validation step walks every AC from context.md against the running
application — manually, by the developer, no Copilot involved.

### 5. Write the plan to a file

When the plan is complete, write it to a file — do not output it only
inline in chat. A file is easier to scroll, easier to reference
mid-implementation, and can be re-attached to a new chat session
without copying from chat history.

**Location:** `.github/story-prompt-steps/`

**Filename:** `STORY-DESCRIPTION-prompt-steps-YYMMDD-HHMMSS.md`
where STORY-DESCRIPTION is a short lowercase hyphenated summary of the
story (2–4 words) — use the same description as the corresponding
context file for this story so the two are easy to pair — and the
timestamp is the date and time of generation in YYMMDD-HHMMSS format.

**Example:** `.github/story-prompt-steps/doctor-removal-prompt-steps-260517-143022.md`

Never overwrite an existing prompt-steps file — the timestamp ensures
every plan is preserved.

After writing the file, tell the developer (do not wrap the filename in
backticks — Copilot Chat auto-links backticked filenames into broken
vscode-file:// URLs):

> Plan written to .github/story-prompt-steps/STORY-DESCRIPTION-prompt-steps-YYMMDD-HHMMSS.md
>
> To execute: open the file, read the standing instructions at the top,
> then paste each step's suggested prompt into Copilot Chat one at a
> time — keeping the context file attached throughout.
>
> Re-attach the plan file alongside the context file if you restart the
> session.

Use the structure below. Every plan starts with a standing instructions
block, then a pre-flight section, then the numbered steps, then a done
criteria section.

#### Plan structure

```markdown
# Plan for: [Story title from the context file]

**Source:** [attached context filename] + .github/copilot-instructions.md
**Stack:** [backend / frontend / full stack — from inference]
**Total steps:** N
**Unresolved clarifications:** [None / list each item if any]

---

## Before you execute any step

1. Keep [attached context filename] in your Copilot Chat context
   throughout the plan. Re-attach it after any session restart.
2. .github/copilot-instructions.md is auto-loaded by Copilot when present
   in the repo. You don't need to attach it manually. If team coding
   conventions are not being applied to the generated code, verify that
   the file exists at .github/copilot-instructions.md and that the VS
   Code setting github.copilot.chat.codeGeneration.useInstructionFiles
   is enabled.
3. Execute steps in one Copilot Chat session when possible. If you
   restart, paste the full plan back into the new chat alongside
   [attached context filename].
4. If a step asks Copilot to modify a file, confirm Copilot is reading
   the file's current contents rather than guessing. If the response
   doesn't reference real function names or imports from the file,
   ask Copilot to read the file first.
5. After Step 1, record the confirmed file set in the Impacted Files
   block (IDs F1, F2, …). Later steps refer to files by ID; if you don't
   fill the block, those references won't resolve.

---

## Pre-flight

[List assumptions the plan makes. Always include the three from the
"Pre-flight assumptions" section below. Add any story-specific ones.]

If any of these assumptions are wrong, stop and revise the context file
or the plan before proceeding.

---

## Impacted Files

[Populated by Step 1 after Copilot confirms the file set. Until Step 1
runs, this lists the seed candidates. Each file gets a stable ID that
every later step references instead of repeating the path.]

| ID | Path | Role |
|----|------|------|
| F1 | [path] | [one-line role] |
| F2 | [path] | [one-line role] |
| …  | …      | …             |

> Later steps refer to files by ID (e.g. "edit F3 and F5"), never by
> re-listing paths. If Step 1 discovers a file the seed missed, add a new
> ID here — do not renumber existing IDs.

---

## Step 1 — [One-line goal]

**Goal:** [One sentence describing what this step accomplishes.]

**Suggested prompt:**

> [The prompt the developer can paste into Copilot Chat. Seeds the file
> list with concrete paths framed as candidates, asks Copilot to add any
> genuinely required files — including non-code files like DB
> schema/migration scripts, seed data, or config — and to remove any not
> impacted. Returns path + one-line role per file. Does not propose edits.]

**Review checkpoint:** [Developer confirms the file set, then records it
in the Impacted Files block above with IDs. Concrete and specific.]

---

## Step 2 — [...]

**Suggested prompt:**

> [Later-step prompts reference files by ID from the Impacted Files block
> — e.g. "edit F3 (PetController)" — not by re-listing the full path.
> Paths live in the table; steps cite IDs.]

[Same format otherwise.]

---

[... all steps ...]

---

## Done criteria

Before opening a PR, confirm:
- [Specific items derived from context.md ACs and constraints]

---
```

#### Pre-flight assumptions to always include

Three assumptions appear in every plan, regardless of story:

1. **Stack assumption** — restate the stack inferred from context.md.
   Example: *"Backend uses Spring Boot with Spring Data JPA. Frontend
   is server-rendered Thymeleaf, not a separate Angular SPA."* This
   catches the case where the skill misread the story.
2. **Behaviour preservation** — list every behaviour from Current
   Behaviour that Expected Behaviour preserves. Example: *"The
   single-match redirect to owner detail page is preserved (AC6)."*
   This makes preserved behaviours visible so they aren't accidentally
   removed.
3. **Non-functional handling** — restate how performance, accessibility,
   or load targets will be handled. Example: *"Performance target P95
   < 500ms is treated as a non-functional constraint, verified by load
   test, not by unit test."* This prevents performance targets from
   being mis-implemented as ACs in code.

#### Step prompt construction rules

Each step's suggested prompt must:

- Reference the attached context file by its **actual attached
  filename** (the one captured in step 2 of the workflow), not by a
  generic placeholder. Same applies to `.github/copilot-instructions.md`
  — reference by literal path.
- The plan carries a single **Impacted Files** block (a table of
  `ID | Path | Role`) between Pre-flight and Step 1. This is the only
  place full file paths appear, apart from Step 1's seed list.
- For Step 1 (inventory) only: seed the affected-files list with concrete
  paths, framed as a starting point — *"start with these, add any
  genuinely required files (including non-code files: DB schema/migration
  scripts, seed data, config), remove any not impacted."* Step 1's output
  populates the Impacted Files block with one ID per confirmed file.
- For all later steps: reference files by their **ID** from the Impacted
  Files block (e.g. *"edit F3 (PetController) and F5"*). Do **not**
  re-list full paths in later-step prompts. Paths live in the table; steps
  cite IDs. This keeps prompts self-contained — the developer re-attaches
  the plan file, so an ID resolves by scrolling up, with no dependency on
  chat history.
- If Step 1 discovers a file the seed missed, add a new ID to the block
  (do not renumber existing IDs); every later step that touches it cites
  the new ID.
- If a step's work could belong in a layer not yet in the block (e.g. the
  repository/query layer for a filtering change), say so explicitly and
  let the design step decide — do not silently route all work through the
  controller just because the seed list named it.
- Reference earlier steps by number when needed (e.g. *"using the option
  chosen in step 2"*) so the developer knows when to paste the plan back
  into context.
- State what NOT to change. Most failures come from Copilot helpfully
  modifying files the developer didn't ask about. Example: *"Do not
  modify the controller yet. Do not modify tests yet — that's the
  next step."*
- For steps involving design decisions, ask Copilot to propose options
  with pros and cons before implementing. Don't let Copilot pick
  invisibly.

#### Step review checkpoint construction rules

Each step's review checkpoint must:

- Be concrete and verifiable. *"Confirm the diff makes sense"* is too
  vague. *"Confirm: only the search method changed, no existing methods
  were touched, the new query handles null/empty input"* is good.
- Reference specific ACs or behaviours from context.md when relevant.
- Tell the developer what to do if the checkpoint fails. Usually:
  loop back rather than weakening the test or accepting the drift.

### 6. Standard step types

Most plans include some combination of these step types. The skill
should pick the right ones for the story, not include all of them.

- **Inventory step** (always step 1) — Copilot lists affected files
  with one line each describing their current role, and explicitly checks
  for **non-code files the change requires** — DB schema/migration
  scripts, seed data, config — not just the obvious source files.
  Doesn't propose changes yet. The confirmed list populates the
  **Impacted Files block**, assigning one stable ID per file. This block
  is the canonical file set: all later steps reference files by ID, never
  by re-listing paths. Step 1 may add files the seed list missed (e.g. a
  Repository, Validator, or schema script) — each gets a new ID and later
  steps must honour it.
- **Design decision step** — for consequential choices (which JPA
  approach, which Angular pattern). Copilot proposes 2–3 options with
  pros/cons; developer picks. Implementation is a separate later step.
- **Implementation step** — applies a chosen approach to one logical
  unit (one file, one method, one component). Tightly scoped.
- **Test step** — at significant stages, not after every code change.
  Covers behaviours, including edge cases from context.md.
- **Frontend wiring step** — for full stack stories, the step that
  connects the frontend to backend changes (e.g. updating form field
  names, route paths, response handling).
- **Validation step** (always second-to-last) — manual walkthrough of
  every AC from context.md against the running application. No Copilot
  involvement. This is the human-in-the-loop confirmation that
  implementation honoured the spec.
- **Convention drift step** (always last code-related step) — Copilot
  reviews all changed files against copilot-instructions.md and flags
  any drift. Doesn't fix automatically — lists drift for the developer
  to decide.
- **Non-functional step** — for stories with performance, accessibility,
  or load requirements that aren't unit-testable. Documents how the
  target will be verified, doesn't try to verify it inline.

### 7. Self-check before showing the plan

Before showing the plan to the developer, verify:

- [ ] Standing instructions block is present at the top
- [ ] Standing instructions and every step's prompt use the **actual
      attached context filename**, not a placeholder or generic path
- [ ] Pre-flight section includes the three standard assumptions
      (stack, behaviour preservation, non-functional handling)
- [ ] If context.md has unresolved [NEEDS CLARIFICATION], pre-flight
      lists each one with the assumption the plan makes
- [ ] Step 1 is an inventory step
- [ ] Validation step is present and second-to-last
- [ ] Convention drift step is present near the end
- [ ] No step has more than one logical change
- [ ] An Impacted Files block exists, populated with `ID | Path | Role`
- [ ] No full file path appears anywhere outside the Impacted Files block
      and Step 1's seed list — every later-step file reference uses an ID
- [ ] Step 1's prompt asks Copilot to check for required non-code files
      (schema/migration/seed/config), not just source files
- [ ] No design-relevant layer (e.g. repository/query) is excluded
      merely because Step 1's seed list didn't name it
- [ ] Every step's prompt is self-contained (works after a session
      restart)
- [ ] Every step's review checkpoint is concrete and verifiable
- [ ] Done criteria section maps back to context.md ACs

If any check fails, fix it before showing.

---

## What never goes in a plan

Things the plan should not do, and what to do instead:

- **Don't include the full text of context.md or copilot-instructions.md
  in the plan.** Reference them by path. Repeating their contents
  bloats the plan and goes stale if those files change.
- **Don't make design decisions invisibly.** If the story needs a
  technical choice (which JPA approach, which Angular pattern, which
  test framework if multiple are in use), surface it as a design
  decision step. Don't pick silently.
- **Don't include load testing, security testing, or accessibility
  audits as code-generation steps.** These belong in non-functional
  steps that document how the target is verified, or in separate
  follow-up stories.
- **Don't include "open the PR" as a step.** That's a developer
  workflow action, not a Copilot prompt step. It belongs in done
  criteria.

---

## Examples

### Pre-flight section example

```markdown
## Pre-flight

The plan assumes:

1. Backend uses Spring Boot with Spring Data JPA. Frontend is
   server-rendered Thymeleaf, not a separate Angular SPA — context.md
   Constraints state "Do not break the existing server-rendered owner
   search flow."
2. The single-match redirect to owner detail page is preserved (AC6).
   The existing pagination at 5 per page is preserved (out of scope to
   change).
3. Performance target P95 < 500ms at 1000 owners under 10 concurrent
   users is treated as a non-functional constraint, verified by load
   test, not by unit test. Step 10 documents how this is handled.

If any of these assumptions are wrong, stop and revise the context file
or the plan before proceeding.
```

### Step example — design decision

```markdown
## Step 2 — Design the repository query change

**Goal:** Decide how the contains-match across lastName, firstName,
address, and telephone will be expressed in the repository — Spring
Data JPA derived query, JPQL, or Specification.

**Suggested prompt:**

> The current repository searches owners by lastName starting with a
> value. We need to change it to: case-insensitive contains-match
> across lastName, firstName, address, and telephone, OR-combined.
>
> Propose three implementation options for the repository layer:
> 1. A derived query method (if expressible)
> 2. A JPQL @Query annotation
> 3. A JPA Specification
>
> For each option, state pros, cons, and how it affects existing
> repository tests. Recommend one that aligns with patterns in
> .github/copilot-instructions.md. Do not write code yet.

(Note: this example shows `.github/copilot-instructions.md` because
that path is fixed. If the example referenced the context file, it
would use the developer's attached filename — for instance,
`OwnerSearch-context.md` — not a placeholder.)

**Review checkpoint:** Pick the option that fits your codebase's
existing patterns. If other repository methods use Specifications,
follow suit. If they use @Query, follow that. The wrong approach here
is hard to undo later — take the time to choose.
```

### Step example — validation

```markdown
## Step 9 — Manual validation against acceptance criteria

**Goal:** Walk through every acceptance criterion in context.md with
the running application and confirm each passes.

**Suggested prompt:**

> List the acceptance criteria from [attached context filename — e.g.
> OwnerSearch-context.md]. For each AC, describe a manual test that
> verifies it on the running application. Do not run the tests for me
> — give me the checklist so I can verify in the browser.

**Review checkpoint:** Walk through each AC manually in your browser
or REST client. Mark each AC as pass, fail, or unclear. If any AC
fails, identify which earlier step's output caused the failure and
loop back to that step rather than patching at the end.
```

---

## Reference

- The plan format is inspired by the runbook pattern: small steps,
  explicit checkpoints, designed for handoff between people (or
  between sessions). The goal is that any developer on the team can
  pick up a plan and execute it, even if they didn't generate it.
