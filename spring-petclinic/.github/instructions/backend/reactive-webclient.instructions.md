---
applyTo: "**/webclient/**/*.java"
---

# Common-Layer Client Conventions (Reactive WebClient)

These rules apply to the classes that call the common service layer. BCBSM services do
**not** access a database directly for their main flows — they call a common service layer
(owned by another team) over HTTP using a reactive `WebClient`. All calls are non-blocking
and `Mono`-returning.

## Class-level

- Annotate the class with `@Service`.
- Extend `AbstractCommonService<RequestType, ResponseType>` from the internal
  `mem-security-lib`.
- Implement a local interface for the service (e.g. `ClaimsCompositeCommonServices`), so the
  business layer depends on the interface, not the implementation.
- Naming: implementation classes use the `...CommonServicesImpl` suffix (e.g.
  `ClaimsCompositeCommonServicesImpl`).

## Making the call

- The HTTP call to the common layer goes through `AbstractCommonService.getWsResponse()`.
  Use the inherited mechanism; do not hand-roll a new `WebClient.get()/post()` pipeline
  unless the pattern genuinely requires it.
- Inject the `WebClient` bean by name with `@Qualifier("<beanName>")`. The beans are defined
  in `@Configuration` classes (one per downstream endpoint, e.g. `WebclientConfig`,
  `NonSecuredWebClientConfig`).
- The OAuth2 bearer token is attached automatically by
  `ServerOAuth2AuthorizedClientExchangeFilterFunction` on every `WebClient` call — do **not**
  manually add an `Authorization` header.
- All methods return `Mono<ResponseType>` (or `Flux<T>`). Never block — `.block()` and
  `.collectList()` are strictly prohibited (they caused production performance problems
  under load). Use `.buffer()` or `.reduce()` where you would have collected a list.

## Retries and timeouts

- Do **not** add service-level retry logic. There is no team-standard retry config at the
  WebClient layer — retries, if any, are handled by the infrastructure (load balancer /
  service mesh). Adding `.retry()` / `.retryWhen()` here is a convention violation unless a
  story explicitly asks for it.
- Do not set ad-hoc per-call timeouts unless the story requires it; timeout behaviour is
  configured centrally.

## Caching

- Where caching applies, use the custom `@ReactiveCacheable(value="...", keys={...})`
  annotation on the WebClient impl methods (backed by `ReactiveRedisTemplate`).
- Cache keys are **composite** — build them from the identifying request fields
  (e.g. `personId`, `contractNumber`, `startDate`, `endDate`), not a single id.
- Manual eviction goes through the separate `RedisCacheService` — do not evict inline.

## Error handling

- Let errors propagate. The shared `SharedControllerAdvice` (from the internal library)
  maps them to the standard JSON error envelope. Do not catch-and-wrap into a custom error
  shape here.

## Do not

- Do not block (`.block()`, `.blockFirst()`, `.blockLast()`, `.toFuture().get()`, blocking I/O) — strict ban.
- Do not use `.collectList()` — use `.buffer()` or `.reduce()` instead.
- Do not manually attach the bearer token — the exchange filter does it.
- Do not add retry logic — infrastructure owns retries.
- Do not create a new `WebClient` inline — inject the qualified bean.
- Do not use a single-value cache key where the real key is composite.
- Do not add a local reactive DB repository as the standard pattern. Most services have no
  local DB and only call the common layer. (A local reactive repository exists in one
  reference service for a lookup table, but it is explicitly NOT the standard pattern —
  do not replicate it unless a story calls for it.)
