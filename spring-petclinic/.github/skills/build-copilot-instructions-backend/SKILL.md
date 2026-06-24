---
name: build-copilot-instructions-backend
description: >
  Generates a single repo-wide GitHub Copilot instructions file
  (.github/copilot-instructions.md) for a Spring Boot Java backend
  repository. Use this when a developer asks to set up Copilot
  instructions, onboard a backend repo to Copilot, or create
  copilot-instructions for a Spring Boot project. The skill reads the
  repository first (pom.xml or build.gradle, package structure, existing
  controllers/services/repositories/tests) to fill in what it can
  discover, asks the developer only for gaps it cannot find, and marks
  anything still unknown with a loud [TODO — MUST COMPLETE] marker rather
  than guessing. This skill does NOT create path-specific rules files —
  rules are managed separately in the copilot-toolkit repository and
  copied into a repo independently.
---

# Build Copilot Instructions — Spring Boot Backend

Generates one file: `.github/copilot-instructions.md` — the repo-wide
Copilot instructions for a Spring Boot Java backend.

This skill produces the repo-wide instructions file only. Path-specific
rules files (naming conventions, testing conventions, etc.) are NOT
created by this skill. Those are maintained centrally in the
`copilot-toolkit` repository and copied into a repo's
`.github/instructions/` folder as a separate activity. Keeping the two
concerns separate means shared rules stay consistent across all backend
repos instead of being regenerated differently each time.

For Angular web apps use `build-copilot-instructions-frontend`; for
Ionic + Angular mobile apps use `build-copilot-instructions-mobile`.

---

## What goes in copilot-instructions.md

This file holds only **cross-cutting, repo-wide** content that is true
regardless of which file Copilot is working on:

- Repository overview (purpose, tech stack, architecture)
- API conventions (versioning, error response format, validation,
  status codes, pagination)
- Security guidelines (DOs and DON'Ts)
- Design patterns the codebase actually uses
- Unique project patterns (date handling, i18n, idempotency, audit)
- What to avoid (stack and project anti-patterns)
- Documentation requirements

It must NOT contain naming conventions, code style rules, package
structure, or test framework rules. Those are path-specific rules,
maintained in the copilot-toolkit repository, applied via separate
`.github/instructions/*.instructions.md` files that this skill does not
generate.

---

## Core principle — discover, don't guess

The value of this skill is that it reads the actual repository and fills
the instructions from what is really there, not a generic template the
developer must rewrite. Three rules:

1. **Read before asking.** Anything discoverable from the repo
   (dependencies, architecture, observed patterns) is filled from the
   repo, not asked.
2. **Ask only for genuine gaps.** Things the repo cannot reveal (project
   purpose, business rules, security intent, unique patterns) are asked
   — one question at a time.
3. **Mark unknowns loudly, never guess.** If the developer does not know
   an answer, write `[TODO — MUST COMPLETE]: <what is needed and why it
   matters>` in that section. A wrong instruction is worse than a
   visibly missing one.

---

## Workflow

### 1. Read the repository

Read these before asking anything:

- **Build file** — `pom.xml` or `build.gradle`. Extract Spring Boot
  version, Java version, build tool, key dependencies (Spring Web,
  Data JPA, Security, MapStruct, Lombok, springdoc), test dependencies,
  datastores.
- **Package structure** — packages under `src/main/java`. Identify
  layering and the base package.
- **Representative code** — sample a controller, a service, a
  repository, an entity, a DTO, and the global exception handler.
  Observe: REST/versioning style, injection style, `@Transactional`
  usage, Lombok usage, mapper usage, and the actual error response
  shape.
- **Existing tests** — `src/test/java` to understand test framework
  and slice-test usage (informs the "what to avoid" and "patterns"
  sections only — this skill does not generate the test rules file).
- **Existing instructions** — if `.github/copilot-instructions.md`
  already exists, read it. Ask the developer whether to refine it or
  regenerate. Do not overwrite blindly.

State a brief summary of what was discovered so the developer can
correct a wrong inference before generation.

### 2. Identify gaps and ask — one question at a time

For each section of the template (see
`assets/copilot-instructions-backend-template.md`):

- **Discoverable and found** — fill from the repo. No question.
- **Discoverable but ambiguous** — code shows mixed patterns. Ask which
  is the standard going forward, citing the observed split.
- **Not discoverable** — ask. Typically: project purpose and domain,
  security specifics, unique patterns, documentation expectations.

One question per turn, each with a concrete example answer. Do not batch.

### 3. Handle unknowns

If the developer does not know, or says skip: write
`[TODO — MUST COMPLETE]: <specific description and why it matters>` in
that section. Do not substitute a generic default. Continue to the next
gap.

If more than five sections become `[TODO — MUST COMPLETE]`, tell the
developer the file will be substantially incomplete and recommend
gathering the missing detail with the team before relying on it.

### 4. Generate the file

Write `.github/copilot-instructions.md` using
`assets/copilot-instructions-backend-template.md` for structure and
section order. Fill every section from the repo, a developer answer, or
a `[TODO — MUST COMPLETE]` marker.

### 5. Self-check before presenting

- [ ] File contains no naming/code-style/package/test rules — those are
      separate rules files this skill does not produce
- [ ] Every section has real repo content, a developer answer, or a
      `[TODO — MUST COMPLETE]` marker — nothing silently blank, nothing
      guessed
- [ ] Tech stack and versions match what was actually in the build file
- [ ] Design patterns listed are ones the codebase actually uses
- [ ] `grep "MUST COMPLETE"` would surface every unfilled section

### 6. Present and instruct

Show the file. Tell the developer:

> Generated .github/copilot-instructions.md
>
> Search for MUST COMPLETE and fill every marked section before relying
> on it.
>
> Note: path-specific rules (naming, code style, testing) are not part
> of this file. Copy the relevant rules files from the copilot-toolkit
> repository into .github/instructions/ as a separate step.

---

## What never goes in this file

- **Guessed conventions.** Not in the repo and not known by the
  developer means `[TODO — MUST COMPLETE]`, not a default.
- **Naming, code style, package structure, or test rules.** These are
  path-specific rules maintained in copilot-toolkit, not generated here.
- **Rules already enforced by tooling.** Skip what Checkstyle, Spotless,
  or the formatter enforces.
- **Long prose.** Each instruction is a short statement. Add a reason
  only when it changes Copilot's behaviour in edge cases.

---

## Reference

- `assets/copilot-instructions-backend-template.md` — the target
  structure for the repo-wide file, with per-section guidance on what is
  discoverable, what to ask, and what a filled vs `[TODO — MUST
  COMPLETE]` section looks like.
