---
applyTo: "src/main/java/**/*.java"
---

# Logging — Java / Spring Boot

Stack-specific logging rules for Spring Boot. Follows the shared contract in `logging-standards.instructions.md`. Compounds with `hipaa-guardrails.instructions.md` (no PHI in logs, ever).

## Logger acquisition

- Use SLF4J only: `private static final Logger log = LoggerFactory.getLogger(MyClass.class);`
- Never use `System.out`, `System.err`, `printStackTrace()`, `java.util.logging`, or `Log4j` API directly.
- Prefer Lombok `@Slf4j` if the project already uses Lombok; otherwise the explicit declaration above.

## Parameterised logging

- Always use `{}` placeholders, never string concatenation:
  - ✅ `log.info("order processed orderId={}", orderId);`
  - ❌ `log.info("order processed orderId=" + orderId);` — builds the string even when level is disabled
- For expensive payloads guarded by level: `if (log.isDebugEnabled()) { log.debug(...); }`
- Pass the exception as the **last** argument to capture the stack trace:
  - ✅ `log.error("payment failed orderId={}", orderId, ex);`
  - ❌ `log.error("payment failed orderId=" + orderId + " " + ex.getMessage());` — loses the trace

## Structured logging (JSON in production)

- Use Logback with `logstash-logback-encoder` or `logback-spring.xml` configured for JSON output in the `prod` profile.
- Add fields via `StructuredArguments.kv("key", value)` or MDC — never by interpolating into the message.
- Example:
  ```java
  log.info("order processed", kv("orderId", orderId), kv("durationMs", elapsed));
  ```

## MDC (Mapped Diagnostic Context)

- Populate MDC in a single `OncePerRequestFilter` at the edge of the service. Mandatory keys: `correlationId`, `traceId`, `spanId`, `userId` (hashed).
- **Always clear MDC at the end of the request** (`finally { MDC.clear(); }`) — leaked MDC pollutes the next request on a thread pool.
- For async code (`@Async`, `CompletableFuture`, reactive), propagate MDC explicitly. Plain async drops it.

## Correlation ID handling

- Inbound: read `X-Correlation-Id` header. If absent, mint a UUID v4 and put it in MDC.
- Outbound: a `RestTemplate` / `WebClient` interceptor must copy `MDC.get("correlationId")` onto every outbound request as `X-Correlation-Id`.
- Never let a request reach a downstream service without a correlation ID.

## What to log at request boundaries

- **Inbound, request entry:** INFO with `httpMethod`, `requestPath`, `correlationId`.
- **Inbound, request exit:** INFO with `httpStatus`, `durationMs`. Do not log the full response body.
- **Outbound call:** DEBUG with method + URL + status + duration. Never the full body for PHI-handling targets.

## What never to log (Java-specific reminders)

- DTO `.toString()` for any DTO that may contain PHI — DTOs often auto-generate `toString()` via Lombok `@Data`. Use `@ToString(exclude = {...})` or explicit field selection.
- JPA entities — their `toString()` may trigger lazy-load and dump the entire object graph.
- `Authentication` / `Principal` objects — they may contain credentials.
- `HttpServletRequest` / `HttpServletResponse` directly — they may contain headers like `Authorization`.

## Exception logging

- Log the exception once at the boundary where it's handled. Do not log-and-rethrow at every layer — produces duplicate stack traces.
- `@ControllerAdvice` is the typical single point. Inner layers re-throw without logging.
- For expected business exceptions (validation, not-found), log at WARN. For unexpected, ERROR.

## Refusal pattern

> ⚠️ Java logging guardrail: <one-line rule>. Suggested alternative: <code>.
