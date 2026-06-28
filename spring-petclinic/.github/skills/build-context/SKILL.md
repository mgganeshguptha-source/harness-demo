---
name: build-context
description: >
  Builds a structured context.md file for GitHub Copilot from a JIRA story,
  screenshot, or Figma export. Use this whenever a developer pastes a user
  story, mentions building context.md, says they have a story to prepare for
  Copilot, or shares a design alongside a story. Works across Angular
  frontend, Spring Boot backend, and full stack work, and across new
  development, enhancements, and bug fixes. The skill enforces a hard quality
  bar — it efuses to output context with vague language like "should work
  better", "displayed properly", or "performance should be acceptable", and
  it asks targeted questions until acceptance criteria are testable. The
  final context is written to a timestamped file under
  .github/story-context-files/, not just shown in chat.

  In NON-INTERACTIVE / CI mode (no human to answer questions), the skill does
  NOT ask questions. Instead it records every gap as a `[NEEDS CLARIFICATION]`
  line in Section 8 of context.md and writes the file immediately. A downstream
  harness gate blocks progression while any `[NEEDS CLARIFICATION]` remains.
---

# Build Context Skill

Helps a developer turn a JIRA story (and any attached design) into a clean
`context.md` file Copilot can act on. The output describes **what** the work
is — not **how** to implement it. Implementation discovery happens later in
the analysis prompt step.

Stack assumed: **Angular** on the frontend, **Java Spring Boot microservices**
on the backend.

---

## Why context.md exists

When developers paste a raw JIRA story into Copilot, results are inconsistent
because stories are usually written for humans, not models — vague acceptance
criteria, missing edge cases, implicit assumptions. A good `context.md`
captures the *what* with enough specificity that Copilot can reason about the
*how* without guessing.

Two failure modes this skill is designed to prevent:

1. **The empty form.** A context.md filled with vague criteria like "search
   should work correctly" — useless, because that line could describe any
   search behaviour. **A context.md that contains banned phrases (see below)
   is worse than no context.md at all** — it gives Copilot false confidence
   and produces wrong implementations.
2. **The over-specified spec.** File paths, class names, or implementation
   steps written into context.md — which prematurely narrows Copilot's
   analysis and produces solutions that don't fit the existing codebase.

Everything below serves these two goals.

---

## Banned phrases — never appear in any output

These phrases (and close variants) must not appear in Expected Behaviour or
Acceptance Criteria. If you find yourself writing one, stop and ask the
developer for the specific behaviour instead.

| Banned | Why | Replace with |
|---|---|---|
| "should work better" / "work correctly" / "work properly" | Untestable | The exact input → exact output mapping |
| "displayed properly" / "displayed clearly" | Untestable | The specific fields shown, ordering, layout |
| "performance should be acceptable" / "promptly" / "quickly" | Untestable | A concrete number (P95 < Xms, render < Ys) |
| "handle errors properly" / "gracefully" | Untestable | The specific error response or UI state |
| "relevant results" / "appropriate behaviour" | Untestable | The exact match rule or behaviour |
| "improve" / "enhance" without saying *what* about it changes | Restates the story title | The specific delta from current to expected |

**This is a hard preflight check.** Before outputting context.md, scan for
these phrases. If any are present, do not output — go back and ask one more
targeted question.

**Banned-phrase scan applies inside `[NEEDS CLARIFICATION]` blocks too.**
A clarification line that says *"Search should work better - specify match
rule"* still propagates the banned phrase into the document. The
clarification must describe only the **missing dimension**, not parrot
back the vague phrase it's replacing.

| Bad clarification (banned phrase leaks through) | Good clarification (names the missing dimension) |
|---|---|
| `[NEEDS CLARIFICATION]: Performance is acceptable - specify metric` | `[NEEDS CLARIFICATION]: Performance target — P95 latency, result-set size, concurrency` |
| `[NEEDS CLARIFICATION]: Search should work better - specify match rule` | `[NEEDS CLARIFICATION]: Match rule — case sensitivity, match type, fields searched` |
| `[NEEDS CLARIFICATION]: Results displayed properly - specify layout` | `[NEEDS CLARIFICATION]: Result display — column order, sort, mobile layout` |

---

## Workflow

### 0. Mode detection — interactive vs non-interactive (CI)

**Before anything else, determine the run mode.**

- **Interactive mode (default):** a human is present to answer questions (local
  Copilot Chat, IDE, terminal). Use the full questioning workflow in steps 1–8 below.
- **Non-interactive / CI mode:** the skill is invoked by an automated harness with
  no human to answer (e.g. GitHub Actions). **CI mode requires an EXPLICIT positive
  signal** — at least one of: a system/harness instruction stating the run is
  non-interactive or "CI mode", or the invoking prompt explicitly saying "CI mode" /
  "do not ask questions". **The mere absence of a chat channel is NOT sufficient** —
  if you are unsure, default to interactive mode and ask.

**When in non-interactive / CI mode, follow these rules instead of asking questions:**

1. **Never ask a question. Never wait for input. Never block on a human.**
2. Draft `context.md` from the story as far as it is specific enough to support.
3. For **every gap** that you would normally ask about (steps 4–5 below), do NOT
   guess and do NOT fill with vague language. Instead write one precise
   `[NEEDS CLARIFICATION]` line in **Section 8 — Clarifications Needed**, naming the
   exact missing dimension (same quality bar as the table in "Banned phrases":
   name the missing dimension, never parrot a vague phrase).
4. The banned-phrase rules still apply in full — a `[NEEDS CLARIFICATION]` line must
   describe the missing dimension, not restate a vague phrase.
5. Sections you CAN complete from the story, complete normally. Only genuinely
   ambiguous items become `[NEEDS CLARIFICATION]`.
6. Write the file immediately to `.github/story-context-files/` and stop. Do not
   ask for approval.

**Why:** a downstream harness gate scans the written context for
`[NEEDS CLARIFICATION]`. If any remain, the harness halts the run and surfaces them
to a human, who resolves them (by editing the story) and re-runs. So in CI the
clarification loop happens *between* runs, not *during* one — but ambiguity is never
silently guessed. The marker is the contract between this skill and the harness.

---


Before reading the story, check whether `.github/copilot-instructions.md`
exists in the repo. This file holds the standard backend and frontend
constraints the team has agreed on.

- **Exists** — read it and use those constraints in section 6.
- **Missing** — show this warning verbatim to the developer (do not put
  backticks around context.md or copilot-instructions.md anywhere in this
  message — Copilot Chat tries to auto-link backticked filenames and
  produces broken vscode-file:// URLs):

  ```markdown
  > ## ⚠️ Missing copilot-instructions.md
  >
  > I don't see **.github/copilot-instructions.md** in this repo.
  >
  > **What this means:** the context.md will use generic Spring Boot
  > and Angular defaults for the Constraints section. The team's actual
  > coding standards are not being applied.
  >
  > **Recommendation:** create copilot-instructions.md before running
  > the analysis prompt. Otherwise Copilot may produce code that doesn't
  > match your conventions.
  >
  > **Continue with defaults, or pause to set up copilot-instructions.md first?**
  ```

  Continue only if the developer says yes.

### 2. Read the story and assess specificity

Read the story carefully. If a screenshot or Figma export is attached, list
the visible UI elements (fields, buttons, states, validation indicators) so
the developer can see what was extracted.

Then make a quick judgement call about how specific the story is:

- **Specific story** — concrete fields named, behaviours defined, edge
  cases hinted at, current behaviour described in detail.
- **Vague story** — uses words like "improve", "better", "faster" without
  saying *what* specifically changes. Common in stories written by POs who
  delegate the detail to the team.

If the story is **vague throughout** (more than half the sections would
need to be filled by guessing), enter **strict mode**: do not attempt to
draft context.md. Tell the developer:

> Your story is high-level — that's normal for a refinement story, but it
> doesn't have enough detail yet for a useful context.md. I'll ask 4–6
> targeted questions to fill the specifics. Each one matters, so please
> take a moment with each.

Strict mode means: ask the questions in section 4 even if the story
"covers" them at a vague level. A vague answer is functionally a missing
answer.

### 3. Identify layer and story type silently

From the story content, infer:

- **Layer** — backend (endpoint, repository, query), frontend (form, screen,
  component), or full stack (both). Ask only if genuinely ambiguous.
- **Story type** — bug fix ("fix/broken"), new development ("create/add"),
  or enhancement ("improve/extend").

State your inference back briefly so the developer can correct it:

> Read your story — looks like a full stack enhancement to owner search.
> Let me check a few specifics before I write the context.md.

### 4. Ask targeted questions for the gaps

For each section of the template, ask one question if the story doesn't
already nail it. **In strict mode, treat vague coverage as a gap.**

The questions below are the ones that matter most. Ask them one at a time,
each with a concrete example answer in the right stack — the example does
the teaching.

#### Backend questions

Each question has a completeness rubric — accept the answer only when
every dimension is filled in. Examples in italics.

- **Exact match rule** (search/filter stories).
  - Required dimensions: case sensitivity, match type (starts-with /
    contains / exact), fields searched.
  - Thin: "case-insensitive contains match" → ask "across which fields —
    lastName only, or firstName + lastName + middleName?"
  - Complete: *"case-insensitive contains match across firstName, lastName,
    and middleName"*
- **Empty / no-results behaviour**.
  - Required dimensions: HTTP status, response body shape, UI consequence.
  - Thin: "200 with empty array" → ask "and what does the UI show — empty
    state message, or stay as-is?"
  - Complete: *"200 with empty `content` array and `totalElements: 0`;
    UI shows neutral empty state"*
- **Pagination defaults**.
  - Required dimensions: page size, default sort, out-of-range behaviour.
  - Thin: "page size 20" → ask "default sort? What if the requested page
    number is past the last page — return empty content or 400?"
  - Complete: *"page size 20, sort by lastName ascending, out-of-range
    page returns 200 with empty content"*
- **Performance target** (whenever the story or developer mentions speed).
  - **Required dimensions: metric, target value, AND load context.** A
    P95 number with no load context is meaningless — P95 < 500ms at 100
    rows is trivial; at 100,000 rows is non-trivial.
  - Thin: "P95 < 500ms" → ask "at what result-set size and concurrency?
    For example: 1000-owner result set under typical clinic load
    (~10 concurrent users)?"
  - Complete: *"P95 < 500ms at 1000-owner result set under ~10 concurrent
    users (typical clinic load)"*

#### Frontend questions (any story with a UI)

These four are almost always missing from JIRA stories — but some of them
may genuinely be unchanged from current behaviour. Start with this gate:

> **Is the search/form interaction model changing in this story?**
> If yes — I need to confirm trigger, loading, empty, and error states.
> If no, keep the current behaviour — I'll mirror what Current Behaviour
> describes and skip ahead.

If the answer is "yes" or "unsure", or if the story is **new development**
(no current behaviour to mirror), ask all four below. Each has a
completeness rubric — accept the answer only when every dimension listed
is filled in.

- **Trigger model** — keystroke / Enter / button click.
  - Required dimensions: trigger event, min character count (if keystroke),
    debounce delay (if keystroke).
  - Thin: "on keystroke" → ask "after how many characters and what debounce?"
  - Complete: "on keystroke after 3 characters with 300ms debounce, plus
    a Search button for keyboard/screen-reader users"
- **Loading state** — what's shown during the in-flight request.
  - Required dimensions: visual (spinner / skeleton / disabled), placement,
    when it appears.
  - Thin: "spinner" → ask "where — over the results area, in the input?
    Shown only if the request takes > Xms?"
  - Complete: "spinner overlay on the results area, shown if the request
    exceeds 200ms"
- **Empty state** — zero results.
  - Required dimensions: message text (literal), styling category
    (error vs neutral empty state), any call to action.
  - Thin: "not found" → ask "is 'not found' the literal text? Styled as
    an error (red, alert), or as a neutral empty state? Any CTA like
    'Add new owner'?"
  - Complete: "neutral empty state with text 'No owners match your
    search.' and a secondary 'Clear search' link"
- **Error state** — API call fails (network, 5xx).
  - Required dimensions: notification type, retry mechanism, what
    happens to the user's input.
  - Thin: "show error" → ask "toast or inline? Can the user retry?
    Is their search input preserved?"
  - Complete: "toast 'Could not reach server, please retry' with a
    Retry button; search input preserved"

#### Full stack drift check

For bug fixes and enhancements, every behaviour mentioned in **Current
Behaviour** must be explicitly addressed in **Expected Behaviour** — kept,
changed, or removed. Silent drops cause Copilot to either preserve the
old behaviour by accident or remove it without anyone confirming the
change was wanted.

Walk through Current and ask about anything not addressed in Expected:

> Your current behaviour mentions [single-match results redirect to the
> detail page]. Your expected behaviour describes a list view but doesn't
> say what happens on a single match. Does the redirect stay, or do
> single matches now display in the list?

### 5. Validate every answer — vague, thin, or complete

**First, check whether the developer actually answered the question.** If
the response doesn't address the question — silence, single characters
(`*`, `* * *`, `.`), filler words (`next`, `skip`, `ok`, `sure`), emoji
only, or off-topic content — do not treat it as an answer and do not
move to the next question. Stop and ask:

> I don't see an answer to the previous question. Three options — which
> would you like?
> 1. **Take another pass** — I'll re-ask, with a different example
> 2. **Mark as NEEDS CLARIFICATION** — I'll flag it for your BA/PO and
>    move on
> 3. **Skip this section entirely** — only if the section isn't relevant
>    to your story

Wait for an explicit choice before proceeding. Empty replies are not
answers — they're missing answers, and missing answers must be
acknowledged, not silently swallowed.

Once an actual answer is received, classify it:

- **Vague** — uses language from the banned phrases table or its variants
  ("works better", "displayed properly", "performance acceptable"). Push
  back with a concrete example of what specific looks like in their stack.
- **Thin** — specific in form but missing one or more required dimensions
  from the question's rubric. Ask one follow-up for the missing dimension.
  Don't treat this as a "push back" — it's a normal continuation. Example:
  *"Got the latency target. What result-set size — 1000 owners? Concurrency?"*
- **Complete** — all dimensions filled. Accept and move on.

**Aggressive validation is the default for these teams.** Thin answers
must be sharpened, not accepted with a [NEEDS CLARIFICATION] flag. The
skill earns its keep by recognising what specific looks like — if it
accepts thin answers, developers may as well fill the template by hand.

**Two-round cap.** Ask for the same dimension at most twice. If after the
second ask the developer still can't supply it ("I genuinely don't know"),
*then* capture as `[NEEDS CLARIFICATION]` and move on. Better one
flagged item than blocking the developer.

**Developer override — scope matters.** Two override types exist; never
conflate them:

- **Per-question skip** — applies only to the current question. Triggers:
  *"skip this one"*, *"NEEDS CLARIFICATION for this"*, *"I don't know"*,
  *"mark this one"*. The skill flags this question as `[NEEDS CLARIFICATION]`
  and continues with the next question normally.
- **Global override** — applies to all remaining questions. Triggers
  (must be unambiguous): *"skip the rest"*, *"good enough, generate it"*,
  *"draft what you have"*, *"stop asking, just write the file"*. The skill
  generates the file with every remaining unanswered dimension wrapped as
  `[NEEDS CLARIFICATION]`.
- **Ambiguous phrasing** — for example *"where you don't have answer, mark
  NEEDS CLARIFICATION and move ahead"*, *"NEEDS CLARIFICATION for missing
  ones"*, *"flag what you don't know"*. **Do not act on these.** Ask:

  > To make sure I get this right — do you mean:
  > 1. Skip *only the current question* and continue asking the rest, or
  > 2. Skip *all remaining questions* and generate the file with whatever
  >    you've answered so far?

  Wait for an explicit choice. Honesty over compliance: the gaps must be
  visible, but only after the developer confirms the scope.

For all override paths, the file must still pass the Step 7 preflight —
a context.md full of clarifications is acceptable; a context.md with
banned phrases is not.

**Cap on clarifications:** if more than five `[NEEDS CLARIFICATION]` items
accumulate, stop and tell the developer:

> Five+ items in Clarifications means the story isn't ready for Copilot
> yet. Recommend going back to the BA/PO to refine before we continue —
> otherwise the context.md is mostly questions, not specifications.

### 5a. Inputs-completeness gate — before drafting

Before writing the context.md draft, run this check on the *answers
collected*, not the output:

For each question asked in step 4, walk its completeness rubric:
- Are all required dimensions present in the answer?
- If no — go back and ask for the missing dimension (within the
  two-round cap).
- If yes — proceed.

This is different from the preflight in step 7. The preflight checks the
*output* for banned phrases. This gate checks the *inputs* for completeness
*before* the output is even drafted. Both matter — one catches vagueness,
the other catches thinness.

### 6. Apply technical constraints

If `copilot-instructions.md` was found in step 1, use those constraints.
Otherwise use these defaults and remind the developer they're defaults:

**Backend (Spring Boot):** Constructor injection, standard error response
format, Jakarta Validation on inputs, JUnit 5 + Mockito for tests, paginated
list responses.

**Frontend (Angular):** Existing component library (no new design tokens),
keyboard navigation, ARIA labels on interactive elements, responsive 375px
to 1440px, Jasmine/Karma component tests.

**Full stack:** Both sets, plus *API contract changes must remain backward
compatible* unless the story explicitly says otherwise.

**Performance targets go in Constraints, not Acceptance Criteria.** A line
like "P95 response time < 500ms at 1000-owner result set under typical
clinic load" is a non-functional requirement verified by load testing,
not by a unit or integration test. Putting it in AC misleads the
developer (and Copilot) into thinking it's something to assert in test
code. Add a dedicated *Performance target* line under Constraints instead.
Same applies to: bundle size limits, memory ceilings, time-to-interactive
targets, and any other NFR.

**Always include load context with any latency target.** "P95 < 500ms"
alone is not a target — it's a half-target. The skill must capture metric,
value, AND the load conditions (result-set size and concurrency) before
the target is written into Constraints. If the developer can't supply the
load context, flag as `[NEEDS CLARIFICATION]` rather than write an
unfalsifiable performance line.

### 7. Preflight before output

Before showing context.md, scan it against this checklist. Every item
must pass — if any fail, go back to section 4 and ask one more question.

- [ ] No banned phrases anywhere (see top of skill) — including text
      inside `[NEEDS CLARIFICATION]` blocks
- [ ] No file paths, class names, component names, or table names
- [ ] Every AC has a concrete input → output mapping someone could write
      a test for
- [ ] Every behaviour mentioned in Current Behaviour is addressed in
      Expected Behaviour (kept / changed / removed) — for bug fixes and
      enhancements
- [ ] For frontend or full stack stories where the interaction model is
      changing or new: all four UX states covered with all required
      dimensions (trigger / loading / empty / error)
- [ ] Edge cases name specific scenarios ("empty input string", "lastName
      with apostrophe") not categories ("invalid input")
- [ ] Performance / bundle / memory targets are in Constraints, not in
      Acceptance Criteria, AND include load context (result-set size,
      concurrency) — not just a P95 number
- [ ] Out of Scope has at least 3 explicit exclusions

### 8. Write the context file

When all checks pass, write the context to a file — do not output it
only inline in chat.

**Location:** `.github/story-context-files/`

**Filename:** `STORY-DESCRIPTION-context-YYMMDD-HHMMSS.md`
where STORY-DESCRIPTION is a short lowercase hyphenated summary of the
story (2–4 words), and the timestamp is the date and time of generation
in YYMMDD-HHMMSS format.

**Example:** `.github/story-context-files/doctor-removal-context-260517-143022.md`

Never overwrite an existing context file — the timestamp ensures every
story's context is preserved even on the same branch.

After writing the file, tell the developer:

> Context written to .github/story-context-files/STORY-DESCRIPTION-context-YYMMDD-HHMMSS.md
>
> Resolve any [NEEDS CLARIFICATION] items with your BA or PO before
> running the build-prompt-steps skill.
>
> When you run build-prompt-steps, attach this context file to the chat.

(Do not wrap the filename in backticks in the message to the developer
— Copilot Chat auto-links backticked filenames into broken
vscode-file:// URLs.)

---

## What never goes in context.md

These four belong in the analysis prompt step that runs *after* context.md,
because Copilot needs to discover them by reading the codebase — not be told
upfront:

- File names or paths (`OwnerSearchController.java`, `appointment.component.ts`)
- Class, component, or service names
- Database table or column names
- Implementation approach ("use a new service", "add a guard", "extract a method")

If a developer offers any of these, redirect briefly:

> File and class discovery happens in the analysis step. Keeping context.md
> stack-agnostic lets Copilot see the whole picture before narrowing in.

---

## Visual designs (frontend / full stack)

When a screenshot or Figma export is attached:

1. Describe what you see — fields, buttons, states, copy.
2. Use it to fill Expected Behaviour and Acceptance Criteria where possible.
3. Then run through the four frontend questions (trigger, loading, empty,
   error) — designs almost never cover all four.

---

## Examples

### Calibrating acceptance criteria

| Vague (banned) | Specific — Angular | Specific — Spring Boot |
|---|---|---|
| "Search should work" | "Typing 3+ characters filters the results list within 300ms debounce; clearing the input restores the full list" | "GET /api/v1/owners?lastName=Smith returns only owners whose lastName contains 'Smith' (case-insensitive)" |
| "Form should validate" | "Submit button stays disabled until all required fields are valid; first invalid field receives focus on attempted submit" | "POST /api/v1/appointments returns 400 with field-level errors for any invalid input, no partial save" |
| "Errors handled properly" | "Network failure shows toast 'Could not reach server, please retry' and re-enables the submit button" | "Downstream timeout returns 503 with `error: 'UPSTREAM_UNAVAILABLE'`, never a 500" |
| "Performance acceptable" | "Initial render under 1s on throttled 3G; list re-renders < 100ms per filter change" | "P95 response time under 500ms at 1000-owner result set" |

### Calibrating expected behaviour

| Vague (banned) | Specific |
|---|---|
| "Search returns relevant results" | "Returns owners whose lastName contains the term, case-insensitively, paginated to 20 per page, sorted by lastName ascending" |
| "Form behaves correctly" | "On submit: validates all fields, calls POST /appointments, shows spinner during call, navigates to confirmation on 201, shows inline error toast on 4xx/5xx" |
| "Search is faster" | "Results update within 300ms of last keystroke; spinner shown if API call exceeds 200ms" |

---

## Reference files

- `assets/context-template.md` — Full template with section descriptions and
  worked examples for backend, frontend, and full stack across all three
  story types. Read this when you need to remind yourself what a finished
  context.md looks like or pull a section header.
