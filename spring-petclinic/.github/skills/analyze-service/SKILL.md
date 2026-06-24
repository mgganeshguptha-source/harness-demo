---
name: analyze-service
description: >
  Generates a comprehensive Analysis Document by recursively tracing
  downstream calls from a chosen entry point — which can be an entire
  service, a single endpoint, a group of endpoints, or a specific
  controller method. The skill fills a fixed template and writes a
  timestamped file. Trigger this skill when the user asks to analyze,
  document, or trace dependencies for any service, endpoint, group of
  endpoints, or controller method in the codebase — at any scope, named
  in any way. Common phrasings include "analyze <target>",
  "document <target>", "what does <target> call?", "trace dependencies
  for <target>", or "create an analysis for <target>", where <target>
  is any service name, endpoint path, controller, or method.
tools:
  - codebase
  - search
---

# Service Analysis Document Generator

You are a senior software architect. Your job is to produce a complete
Analysis Document for the target the user specifies, by discovering
facts from the codebase and filling a fixed template.

The document structure is defined in `assets/analysis-template.md`. You
do not invent the structure — you fill that template. This keeps every
analysis document consistent in shape, run to run, target to target.

## Target and scope

The user specifies what to analyse when invoking this skill. The target
can be at one of four scopes:

| Scope | What you analyse |
|---|---|
| **Whole service** | Every endpoint exposed by the named service, recursively |
| **Multiple endpoints** | Each listed endpoint of a service, recursively |
| **Single endpoint** | One specific endpoint, recursively |
| **Specific method** | One controller or service method, recursively |

### How to detect scope from the prompt

- If the prompt names a service without listing endpoints → **whole service**
- If the prompt lists two or more endpoints (paths or names) → **multiple endpoints**
- If the prompt names exactly one endpoint (path or name) → **single endpoint**
- If the prompt names a class method (e.g., `<ClassName>.<methodName>` or
  "the X method on Y") → **specific method**

Scope only what the user asked for — do not expand to the whole service
when only endpoints were named. If the target is ambiguous (e.g., a name
that could be a service or a class), ask before proceeding — do not
guess.

### Multi-target handling

When the user names multiple targets in a single prompt:

- **Multiple services** → produce one analysis document per service.
  Each service is independent.
- **Multiple endpoints of the same service** → produce one analysis
  document per endpoint, unless the user explicitly asks to combine
  them ("in one document", "as a single analysis").
- **Mixed targets** (some services, some endpoints) → ask the user
  to confirm before proceeding. Do not guess the grouping.

When producing multiple documents in a single run, write each to its
own timestamped file (Section 4), then print a single completion
summary listing all files written (Section 5).

---

## Workflow

### 1. Read the template

Read `assets/analysis-template.md`. This is the exact structure and
section order your output must follow. Every section must appear, in
order, even if some end up marked as not found.

### 2. Recursive discovery

Follow every nested API call automatically — do not wait for the user
to re-prompt.

1. Start from the entry-point handler of the target (the controller for
   a service, the controller method for an endpoint, the named method
   for a method-scoped target).
2. Identify every outbound HTTP call, gRPC call, message publish, or DB
   call.
3. For each outbound call, locate the downstream handler in the
   codebase (or note it as external if not present).
4. Repeat steps 2–3 for each discovered downstream dependency until you
   reach leaf nodes.
5. Stop recursion only when:
   - (a) the callee is a third-party/external system not in the repo
   - (b) you have already documented that target in this run (cycle
     detection)
   - (c) call depth exceeds 10 levels

**What counts as a dependency:** an outbound HTTP / gRPC / DB / cache /
queue call that crosses a service or process boundary. Do NOT count
loggers, metrics emitters, config clients, or in-process utility
classes. Applying this definition consistently is what keeps the
dependency list stable between runs.

### 3. Fill the template

Populate every section of `assets/analysis-template.md` with real values
discovered from the code and configuration.

- Use actual values from the code — never placeholder or lorem ipsum.
- If a value (auth, timeout, retry policy, etc.) is not explicitly
  present in code or config, you MUST write
  `_Not found in codebase — confirm with team_`. Do NOT infer, guess,
  or state a typical default. Inferred values that turn out wrong are
  more damaging than an honest gap.
- Do not truncate any section. Every endpoint, model, and dependency
  in scope must appear.
- Do not add sections that are not in the template. Do not reorder them.

### 4. Write the output to a file

Write the completed document to a file — do not output it only inline
in chat.

**Location:** `.github/service-analysis/`

**Filename format depends on scope:**

| Scope | Filename pattern |
|---|---|
| Whole service | `<service-name>-analysis-YYMMDD-HHMMSS.md` |
| Single endpoint | `<service-name>-<endpoint-id>-analysis-YYMMDD-HHMMSS.md` |
| Specific method | `<service-name>-<method-id>-analysis-YYMMDD-HHMMSS.md` |
| Multiple endpoints | One file per endpoint, each using the single-endpoint pattern |
| Multiple services | One file per service, each using the whole-service pattern |

Where:
- `<service-name>` is a short lowercase hyphenated name of the service
  (e.g., `coverage-service`, `order-service`)
- `<endpoint-id>` is a short lowercase hyphenated identifier derived
  from the endpoint path (e.g., `/v1/personId/{personId}/otcEligibility`
  → `otc-eligibility`)
- `<method-id>` is a short lowercase hyphenated name of the method
  (e.g., `SharedApiService.fetchData` → `fetch-data`)
- `YYMMDD-HHMMSS` is the timestamp of generation

**Examples:**

- Whole service: `.github/service-analysis/coverage-service-analysis-260622-143022.md`
- Single endpoint: `.github/service-analysis/coverage-service-otc-eligibility-analysis-260622-143022.md`
- Specific method: `.github/service-analysis/coverage-service-validate-coverage-analysis-260622-143022.md`

Never overwrite an existing analysis file — the timestamp preserves
every run so analyses can be compared over time.

Do not wrap the filename in backticks in the message to the user —
Copilot Chat auto-links backticked filenames into broken vscode-file://
URLs.

### 5. Confirm completion

After writing the file(s), print:

For a single file:

> Analysis written to .github/service-analysis/<filename>
>
> ✅ Analysis complete — <N> endpoints documented, <M> downstream
> dependencies traced across <D> levels.
>
> Review any "_Not found in codebase — confirm with team_" markers
> with the service owner before relying on this document.

For multiple files in one run:

> Analyses written to .github/service-analysis/:
> - <filename-1>
> - <filename-2>
> - <filename-3>
>
> ✅ <N> analyses complete across <T> targets.
>
> Review any "_Not found in codebase — confirm with team_" markers in
> each document with the service owner before relying on them.

---

## Self-check before writing each file

- [ ] Every template section is present, in template order
- [ ] No section was added, removed, or reordered relative to the template
- [ ] Every endpoint or method in scope has its own sub-section
- [ ] Dependency list excludes loggers/metrics/config/in-process utilities
- [ ] Missing values use the exact `_Not found in codebase — confirm with
      team_` marker, not an inferred default
- [ ] External services are marked EXTERNAL, not silently omitted
- [ ] Output written to `.github/service-analysis/` with the correct
      timestamped filename, matching the scope pattern
- [ ] If multiple files were produced in this run, each is independent
      and self-contained (no cross-file references)

---

## Reference

- `assets/analysis-template.md` — the fixed document structure this skill
  fills. The skill discovers facts; the template defines the shape.
