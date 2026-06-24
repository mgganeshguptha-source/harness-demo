---
applyTo: "src/main/java/**/*.java"
---

# Performance Standards — Java / Spring Boot

Backend performance rules. Focus on the cheapest mistakes that cause production incidents.

## Database access

### N+1 queries — the #1 backend performance bug
- For any `@OneToMany` / `@ManyToMany` relationship, default to lazy fetch. Then use `JOIN FETCH` in JPQL or `@EntityGraph` when the relationship is needed for the current call.
- Never iterate a collection from a parent entity and call a repository inside the loop — that's the N+1 pattern. Fetch in one query.
- Enable `hibernate.generate_statistics=true` in dev to detect N+1.
- Flag any `for (Parent p : parents) { p.getChildren()... }` pattern in a transactional method as a likely N+1.

### Query patterns
- Use projections (DTO interfaces or `@Query` constructor expressions) when the caller doesn't need the full entity. Avoid `findAll()` returning entities for read-only endpoints.
- Never `SELECT *` via `findAll()` without pagination on tables that grow. Paginate or constrain by index.
- Add explicit indexes for every column used in `WHERE`, `JOIN`, or `ORDER BY` on hot paths. Schema migrations include the index.
- Avoid `count(*)` on large tables in hot paths — cursor pagination removes the need.

### Transactions
- `@Transactional` at the service layer, not the repository layer.
- Keep transactions short. Never wrap remote HTTP calls inside `@Transactional` — blocks a DB connection for the duration of the call.
- Read-only operations: `@Transactional(readOnly = true)` — lets Hibernate skip dirty-checking.

### Connection pool
- HikariCP defaults are fine for most services. Tune only with evidence.
- Pool size: starting point is `(2 * cores) + effective_spindle_count` (~10–20 for typical service). Do not arbitrarily set to 100.
- Monitor `HikariPool` metrics — pool exhaustion is a common cause of cascading failure.

## HTTP client behaviour

- Always set connect, read, and write timeouts on `RestTemplate` / `WebClient`. No-timeout calls block threads indefinitely under downstream failure.
  - Default starting point: connect 2s, read 5s. Tune per endpoint SLA.
- Use a single shared `RestTemplate` / `WebClient` per downstream — connection pooling matters. Do not `new RestTemplate()` per call.
- Wrap downstream calls in a circuit breaker (Resilience4j). Open on >50% failure rate; cascading-failure prevention.
- For bulk parallel calls, use `WebClient` reactive or `CompletableFuture.allOf` — never serial loops over remote services.

## Caching

- Cache reads that are expensive AND tolerant of staleness. Do not cache PHI in a process-level cache without TTL and access control.
- Use Spring `@Cacheable` with Caffeine (in-process) or Redis (distributed). Set explicit TTL — never unbounded.
- Cache invalidation: on the write path, evict via `@CacheEvict`. Document the invalidation strategy in a comment.
- Never cache responses that depend on the authenticated user without keying the cache by user.

## Async and concurrency

- Use `@Async` with an explicit `Executor` bean — never the default. The default `SimpleAsyncTaskExecutor` creates a new thread per call.
- Bounded thread pools only. `Executors.newCachedThreadPool()` is unbounded and a known OOM cause.
- Reactive (`Mono`/`Flux`) requires reactive all the way down. Mixing blocking JDBC into a reactive chain blocks the event loop — worst of both worlds.
- Never `Thread.sleep()` in request-handling code. Use scheduled tasks or async wait.

## Collections and algorithms

- Use the right collection: `ArrayList` for ordered + indexed; `HashMap` for O(1) lookup; `LinkedHashMap` when insertion order matters. Don't reach for `LinkedList` for general use.
- Initialise collections with capacity if size is known: `new ArrayList<>(expectedSize)`.
- Avoid `String` concatenation in loops — use `StringBuilder`.
- Streams are fine but not always faster than for-loops. Don't use parallel streams without measuring — they default to the common ForkJoinPool which can be contended.

## Memory

- Avoid loading large result sets into memory. Stream from JDBC or use cursor pagination.
- Be careful with `@Cacheable` on methods returning large objects — heap fills quickly.
- Don't hold large objects in static fields ("just in case") — pinned in old gen forever.
- Watch for memory leaks: thread-locals not cleared, listeners not removed, MDC not cleared (see `logging-java.instructions.md`).

## Serialisation

- Jackson `ObjectMapper` is thread-safe — reuse a single instance. Do not `new ObjectMapper()` per call.
- For high-throughput paths, consider streaming Jackson (`JsonParser`/`JsonGenerator`) rather than full DOM binding.

## Logging cost

- Log at the right level — DEBUG/TRACE off in production. Don't compute expensive payloads for log lines that won't fire.
- Avoid synchronous file appenders on hot paths — use async Logback appenders.

## Startup time

- Spring Boot startup matters for autoscaling. Avoid `@ComponentScan` over huge packages — scope tightly.
- Lazy initialisation (`spring.main.lazy-initialization=true`) is acceptable for non-critical-path services; not for hot-path APIs.

## Measurement before optimisation

- Do not optimise without a baseline. Use Micrometer + Prometheus/Datadog for production metrics; JMH for micro-benchmarks; JFR/async-profiler for CPU profiling.
- Flag premature optimisation: complex code "for performance" without a measurement is a code smell.

## Refusal pattern

> ⚠️ Performance guardrail: <one-line rule>. Suggested alternative: <code>.
