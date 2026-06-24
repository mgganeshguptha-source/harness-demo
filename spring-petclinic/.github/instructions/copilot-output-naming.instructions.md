---
applyTo: "**"
---

# Copilot Output File Naming Conventions

When generating any of the following artefacts, always use the exact
file name, location, and format specified below. Do not invent
alternative names or locations.

---

## Context File (build-context skill output)

- **Location:** `.github/story-context-files/`
- **Format:** `STORY-DESCRIPTION-context-YYMMDD-HHMMSS.md`
  where STORY-DESCRIPTION is a short lowercase hyphenated summary of the
  story (2–4 words maximum), and the timestamp is the date and time of
  generation in `YYMMDD-HHMMSS` format.
- **Never overwrite** an existing context file — the timestamp ensures
  each story's context is preserved even on the same branch.
- **Example:** `.github/story-context-files/doctor-removal-context-260517-143022.md`

---

## Prompt Steps File (build-prompt-steps skill output)

- **Location:** `.github/story-prompt-steps/`
- **Format:** `STORY-DESCRIPTION-prompt-steps-YYMMDD-HHMMSS.md`
  where STORY-DESCRIPTION matches the description used in the
  corresponding context file for that story, so the two files pair
  visibly, and the timestamp is in `YYMMDD-HHMMSS` format.
- **Never overwrite** an existing prompt steps file — the timestamp
  ensures each plan is preserved.
- **Example:** `.github/story-prompt-steps/doctor-removal-prompt-steps-260517-144530.md`

---

## Execution Log File (execute-prompt-steps skill output)

- **Location:** `.github/story-execution-logs/`
- **Format:** `STORY-DESCRIPTION-execution-YYMMDD-HHMMSS.md`
  where STORY-DESCRIPTION matches the description used in the
  corresponding context and prompt steps files for that story, and the
  timestamp is the date and time the execution run started (not the
  per-step timestamps, which are captured inside the file).
- **Never overwrite** an existing execution log — each run of the
  execute-prompt-steps skill produces its own log, even on the same
  branch and same story.
- **Example:** `.github/story-execution-logs/doctor-removal-execution-260517-150830.md`

---

## Test Generation Log File (generate-unit-tests skill output)

- **Location:** `.github/story-test-generation-logs/`
- **Format:** `STORY-DESCRIPTION-test-generation-YYMMDD-HHMMSS.md`
  where STORY-DESCRIPTION matches the description used in the
  corresponding context, prompt steps, and execution log files for that
  story, and the timestamp is the date and time the test-generation run
  started.
- **Never overwrite** an existing test generation log — each run of
  the generate-unit-tests skill produces its own log.
- **Example:** `.github/story-test-generation-logs/doctor-removal-test-generation-260517-152100.md`

---

## Test Run Log File (run-and-fix-tests skill output)

- **Location:** `.github/story-test-run-logs/`
- **Format:** `STORY-DESCRIPTION-test-run-YYMMDD-HHMMSS.md`
  where STORY-DESCRIPTION matches the description used in the other
  files for that story, and the timestamp is the date and time the
  test-run-and-fix invocation started.
- **Never overwrite** an existing test run log — each run of the
  run-and-fix-tests skill produces its own log, even when running
  again to verify stability.
- **Example:** `.github/story-test-run-logs/doctor-removal-test-run-260517-153500.md`

---

## Copilot Instructions File (repo-wide)

- **Location:** `.github/`
- **Format:** `copilot-instructions.md`
- **Fixed name** — do not rename or add suffixes.
- **Example:** `.github/copilot-instructions.md`

---

## Path-Specific Instruction Files (rules)

- **Location:** `.github/instructions/`
- **Format:** `NAME.instructions.md`
  where NAME describes the scope of the rules (language, layer, or tool).
- **Must include** an `applyTo` frontmatter block with a glob pattern.
- **Examples:**
  - `.github/instructions/java-conventions.instructions.md`
  - `.github/instructions/java-testing.instructions.md`
  - `.github/instructions/angular-conventions.instructions.md`

---

## Skill Files

- **Location:** `.github/skills/SKILL-NAME/`
- **Format:** `SKILL.md` (always lowercase, always this exact name)
- **Assets** (templates, examples) go in `.github/skills/SKILL-NAME/assets/`
- **Examples:**
  - `.github/skills/build-context/SKILL.md`
  - `.github/skills/build-context/assets/context-template.md`
  - `.github/skills/build-prompt-steps/SKILL.md`

---

## Pairing Convention

Every artefact produced for the same story must use the **same
STORY-DESCRIPTION**, so all five files are immediately recognisable as
a set:

```
.github/
  story-context-files/
    doctor-removal-context-260517-143022.md
  story-prompt-steps/
    doctor-removal-prompt-steps-260517-144530.md
  story-execution-logs/
    doctor-removal-execution-260517-150830.md
  story-test-generation-logs/
    doctor-removal-test-generation-260517-152100.md
  story-test-run-logs/
    doctor-removal-test-run-260517-153500.md
```

The timestamps will differ — each file is generated at a different
point in the workflow, and a single story may run through the loop
more than once (producing additional execution logs, test-generation
logs, and test-run logs each time). The STORY-DESCRIPTION is the
shared key, not the timestamp.

When multiple runs accumulate for the same story, the latest log is
identified by the most recent timestamp in its folder. Skills that
need to resume an interrupted run will read the most recent
not-yet-complete log for the matching STORY-DESCRIPTION.

---

## Summary Table

| Artefact | Location | Filename format |
|---|---|---|
| Context file | `.github/story-context-files/` | `STORY-DESCRIPTION-context-YYMMDD-HHMMSS.md` |
| Prompt steps | `.github/story-prompt-steps/` | `STORY-DESCRIPTION-prompt-steps-YYMMDD-HHMMSS.md` |
| Execution log | `.github/story-execution-logs/` | `STORY-DESCRIPTION-execution-YYMMDD-HHMMSS.md` |
| Test generation log | `.github/story-test-generation-logs/` | `STORY-DESCRIPTION-test-generation-YYMMDD-HHMMSS.md` |
| Test run log | `.github/story-test-run-logs/` | `STORY-DESCRIPTION-test-run-YYMMDD-HHMMSS.md` |
| Repo-wide instructions | `.github/` | `copilot-instructions.md` |
| Path-specific rules | `.github/instructions/` | `NAME.instructions.md` |
| Skill entry point | `.github/skills/SKILL-NAME/` | `SKILL.md` |
| Skill assets | `.github/skills/SKILL-NAME/assets/` | any descriptive name |
