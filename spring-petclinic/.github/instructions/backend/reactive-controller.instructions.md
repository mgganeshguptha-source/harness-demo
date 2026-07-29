---
applyTo: "**/controller/**/*.java"
---

# Reactive Controller Conventions (Spring WebFlux / Reactor)

These rules apply to REST controllers in BCBSM backend microservices. The stack is
Java 17, Spring WebFlux, Project Reactor. Controllers are non-blocking and return
reactive types. Do not use Spring MVC / blocking servlet patterns.

## Class-level

- Annotate the class with `@RestController`, `@RequiredArgsConstructor`, and `@Log4j2`.
- Implement the OpenAPI-generated `*Api` interface (e.g. `ClaimsApi`). Do **not** add
  `@RequestMapping` or per-method mapping annotations — the paths are defined in the
  generated interface.
- Inject the service through the constructor (via `@RequiredArgsConstructor`); do not
  use field injection.

## Method signatures

- Every endpoint method returns `Mono<ResponseType>` (or `Flux<T>` for streams).
- The signature follows the generated interface and includes the standard parameters:
  `String messageId` (trace header), `Mono<RequestType> body`, `String appName`, and
  `ServerWebExchange exchange`.
- **Never block — strictly prohibited.** Do not call `.block()`, `.blockFirst()`,
  `.blockLast()`, `.toFuture().get()`, or any blocking API inside a controller. Blocking
  in a reactive chain starves the event-loop threads; the damage is invisible locally and
  only surfaces under concurrent load in the deployed service. This is a hard team rule.
- **Do not use `.collectList()`** (or a `.collect(...)` that buffers an unbounded stream) —
  it caused the same class of production performance problems. Use `.buffer()` (preferred)
  or `.reduce()` depending on the scenario.

## The reactive chain

Build the whole handler as a single reactive chain. A typical order is:

1. **Log without breaking the chain** — the first operator logs the incoming request
   using a non-consuming peek, e.g.
   `.mapNotNull(peek(req -> log.info("Request received ...")))`.
   Never log by subscribing separately or by blocking.
2. **Validate as a `.filter()` step** — input validation is a `.filter(...)` (or
   `Validator::validate`) that returns an **empty `Mono`** on invalid input. Do not throw
   an exception at the controller level for validation failures.
3. **Delegate to the service** with `.flatMap(service::method)`.
4. **Post-process** (e.g. add a response trace header) with `.doOnNext(...)`.

## Security

- Enforce OAuth scope with `@RequestReadScoped` (read endpoints) or
  `@RequestWriteScoped` (write endpoints) from the internal `mem-security-lib`.
- Do not implement token validation in the controller — it happens at the gateway/filter
  level before the controller method runs.

## Logging

- Use `@Log4j2` (Lombok). Log the entry of every endpoint with the `messageId`
  (request trace ID), `appName`, and the request payload, e.g.
  `log.info("Request received messageId:{} appName:{} request:{}", messageId, appName, request)`.
- `messageId` is a header passed in from upstream and threaded through the whole chain —
  propagate it, do not generate a new one.

## Error handling

- Do **not** define a local `@ControllerAdvice`. Errors are handled by the shared
  `SharedControllerAdvice` from the internal library (component-scanned via `com.bcbsm.*`),
  which returns the standard JSON error envelope. Let exceptions propagate to it.

## Do not

- Do not block anywhere in the chain (`.block()`, `.blockFirst()`, `.blockLast()`) — strict ban.
- Do not use `.collectList()` — use `.buffer()` or `.reduce()` instead.
- Do not add `@RequestMapping` (it is in the generated `*Api` interface).
- Do not throw exceptions for input validation — return an empty `Mono` from a filter.
- Do not add a per-service `@ControllerAdvice`.
- Do not add retry logic here — retries are handled by infrastructure (see the WebClient
  conventions).
