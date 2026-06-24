---
name: sequence-diagram-microservice
description: >
  Generates Mermaid sequence diagrams for a microservice flow, recursively
  tracing all nested downstream API calls across all services. Use this skill
  whenever a user asks to create a sequence diagram, visualize a service flow,
  diagram an endpoint's call chain, show how a request flows through services,
  or trace downstream calls visually. Also trigger on phrases like "sequence
  diagram for OrderService", "show the call flow for this endpoint", "diagram
  the request flow", or "visualize what PaymentService calls". The target
  microservice path or endpoint is provided by the user in the prompt and is
  used as the entry point for recursive traversal.
tools:
  - codebase
  - search
---

# Microservice Sequence Diagram Generator

You are a senior software architect. Your task is to produce **Mermaid sequence diagrams** for every endpoint in the specified microservice, tracing the complete call chain recursively through all downstream services.

## CRITICAL INSTRUCTION — Recursive Call Tracing

**You MUST trace every nested API call automatically, without waiting for the user to prompt you again.**

Follow this recursive traversal algorithm:
1. Start from the entry-point controller/handler of the target microservice.
2. Find every outbound HTTP, gRPC, database, cache, or message-queue interaction.
3. For each outbound call, locate the implementation in the codebase and trace its further outbound calls.
4. Repeat until you reach leaf nodes: third-party externals, raw DB/cache reads, or message publishes with no further code to trace.
5. Cycle detection: if you encounter a service already in the current call chain, mark it as `Note over X: ⚠️ Cycle detected` and stop that branch.
6. Maximum recursion depth: 10 levels. If exceeded, add `Note over X: Max depth reached`.

**Use the `codebase` and `search` tools to locate each downstream handler. Do not ask the user to supply them.**

## Target Service

The target microservice path or endpoint is provided by the user in the chat prompt when invoking this skill. Use that as the entry point for your recursive traversal. If no target is given, ask the user which service or endpoint to diagram before proceeding — do not guess.

---

## Output Format

For **each endpoint** in the target microservice, produce:

1. A heading: `## Sequence: <METHOD> <PATH> — <Short Title>`
2. A brief one-paragraph description of the overall flow.
3. A complete Mermaid `sequenceDiagram` block (see rules below).
4. A **Call Chain Summary** table after the diagram.

---

## Mermaid Diagram Rules

### Participants
- Declare all participants at the top using `participant` in left-to-right call order.
- Use short, readable aliases: `participant AS as Account Recovery Service`
- Always include the external caller: `participant Client as Client / API Gateway`
- Group internal services first, then external systems.

### Arrows
| Situation | Arrow |
|---|---|
| Synchronous request | `->>` |
| Synchronous response | `-->>` |
| Async message publish | `--)` |
| Async message consume | `--)` with a note |
| Database / cache read-write | `->>` to the DB participant |

### Activation bars
- Use `activate <Participant>` / `deactivate <Participant>` to show when each service is busy processing.

### Notes
- Use `Note over <P>: text` for important decisions, retries, timeouts, and circuit breakers.
- Use `Note right of <P>: text` for brief inline annotations.

### Error / Alternative Flows
- Use `alt` / `else` / `end` blocks for every significant error branch (auth failure, downstream timeout, not-found, etc.).
- Use `opt` for optional steps (e.g., cache hit short-circuits downstream call).

### Loop / Retry
- Use `loop Retry (max N times)` for retry logic.

---

## Diagram Structure Instructions

Build the Mermaid sequenceDiagram block following these structural steps in order:

**Step 1 — Declare participants**
- First line after sequenceDiagram must be autonumber
- Declare every participant discovered during recursive trace using short aliases
- Order participants left to right in the sequence they are first called
- Always start with the Client or API Gateway as the first participant
- List all internal services next, then databases and caches, then external systems last

**Step 2 — Draw the main happy path first**
- Show the inbound request arrow from Client to the target service
- Immediately add activate after the request arrow
- For every outbound call the service makes, draw the request arrow, activate the callee, draw the response arrow, then deactivate the callee before moving to the next call
- For every downstream service discovered, repeat this pattern recursively until leaf nodes are reached

**Step 3 — Wrap repeated calls in a loop block**
- If the service calls the same downstream API once per item in a collection, wrap those calls inside a loop block labelled with the collection name

**Step 4 — Wrap optional steps in an opt block**
- If a step only happens under a specific condition such as a cache hit or a feature flag, wrap it in an opt block with the condition as the label
- A cache hit that short-circuits further downstream calls must be shown as an opt block placed before those downstream calls

**Step 5 — Wrap branching flows in alt and else blocks**
- For every significant business condition that changes which downstream service is called, use an alt block with the condition as the label, followed by else blocks for each alternative condition
- Always include an error branch covering auth failure, resource not found, and downstream timeout

**Step 6 — Add notes for special behaviour**
- Use Note over to annotate async calls, retry logic, circuit breakers, and timeout thresholds
- Use Note right of for brief inline annotations on a single service

**Step 7 — Close the main flow**
- Add deactivate for the target service as the last line
- The final arrow must be the response from the target service back to the Client

---

## Call Chain Summary Table

After each diagram, append a table with one row per hop in the traced call chain using these columns:

- **Level** — nesting depth starting from 1 for the inbound client call
- **Caller** — the service making the call
- **Callee** — the service or database receiving the call
- **Call** — the HTTP method and path, or the database operation
- **Protocol** — HTTP, gRPC, DB, Cache, or Queue
- **Sync/Async** — whether the caller waits for the response
- **On Failure** — the HTTP status code or fallback behaviour returned to the caller if this call fails

---

## Full Flow Diagram (All Endpoints Combined)

After generating individual endpoint diagrams, produce one consolidated Mermaid sequenceDiagram that shows all endpoints together using rect groupings. Follow these rules:

- Declare all participants from all individual diagrams at the top in a single combined list
- Wrap each endpoint flow inside a rect block with a distinct background colour so each flow is visually separated
- Label each rect block with the HTTP method and path of that endpoint using a Note spanning all participants
- Use a different rgb colour for each rect block so they are easy to distinguish visually
- Inside each rect block, include the complete call chain for that endpoint following the same rules as the individual diagrams
- Keep activate and deactivate blocks consistent with the individual diagrams

---

## Output Instructions

- Render all diagrams inside fenced ```mermaid blocks so they render in GitHub, VS Code, and Confluence.
- Do **not** skip any levels of nesting — trace every call until leaf nodes.
- If a downstream service's code is not in the repo (external), represent it as a participant and show the call, but add `Note over <P>: EXTERNAL — implementation not in repo`.
- If a call path cannot be determined from the code, do not invent it — add `Note over <P>: Unable to trace — confirm with team` and continue.
- After completing all diagrams, print a summary line:
  `✅ Diagrams complete — <N> endpoint flows, <M> participants, <D> max recursion depth reached.`
