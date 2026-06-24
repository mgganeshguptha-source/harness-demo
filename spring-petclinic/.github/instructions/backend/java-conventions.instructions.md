---
applyTo: "src/main/java/**/*.java"
---

# Java Source Conventions (Spring Boot)

## Naming Conventions

- Classes: `PascalCase`
- Methods and variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Packages: lowercase, `com.company.project.layer`
- Repositories: `PascalCase` with `Repository` suffix (e.g. `OwnerRepository`)
- Controllers: `PascalCase` with `Controller` suffix (e.g. `OwnerController`)
- Services: `PascalCase` with `Service` suffix
- DTOs: `PascalCase` with `Request` / `Response` / `Dto` suffix as appropriate

## Code Style

- Use constructor injection. Do not use field injection (`@Autowired`
  on fields).
- Mark injected dependencies `private final`.
- Apply `@Transactional` on service-layer methods where a transactional
  boundary is required, not on controllers.
- Use Lombok judiciously: `@Getter`/`@Setter`/`@RequiredArgsConstructor`
  where helpful; `@Data` is acceptable on DTOs but not on JPA entities.
- Use SLF4J for logging with appropriate levels (`INFO`, `DEBUG`,
  `ERROR`). Never log secrets, tokens, or PII.
- Keep controllers thin — no business logic. Business logic belongs in
  services.
- Never build SQL or JPQL via string concatenation of user input.

## Package Structure

```
src/main/java/com/company/project/
  config/       Configuration classes, Spring beans
  controller/   REST controllers, API endpoints
  service/      Business logic layer
  repository/   Data access layer (Spring Data JPA)
  model/        Entities, DTOs, request/response objects
  exception/    Custom exceptions and global handlers
  security/     Security configuration, filters
  util/         Utility classes, helpers
```

Place new classes in the package matching their layer. Do not put
business logic in `controller/` or persistence concerns in `service/`.
