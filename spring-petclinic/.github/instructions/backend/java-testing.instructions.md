---
applyTo: "src/test/java/**/*.java"
---

# Java Testing Conventions (Spring Boot)

## Test generation workflow

When the developer asks to generate tests for a class — however briefly phrased ("write tests for X", "JUnit for X", "test this class", or with the file open and any test-related ask) — follow this exact workflow. Do not require the developer to specify scope, style, or coverage targets — infer them.

### Step 1 — Auto-detect test type (no developer question needed)

Infer test type from the class under test:

| Class signal | Test type | Annotation |
|---|---|---|
| `@RestController` / `@Controller` | Controller test | `@WebMvcTest` |
| `@Repository` / extends `JpaRepository` / `CrudRepository` | Repository test | `@DataJpaTest` |
| `@Service`, `@Component`, plain POJO with collaborators | Pure unit test | `@ExtendWith(MockitoExtension.class)` |
| `@SpringBootApplication`, wiring configuration | Integration test | `@SpringBootTest` |
| Utility class, mapper, validator, no Spring annotations | Pure unit test | `@ExtendWith(MockitoExtension.class)` |

If the class could legitimately be tested at multiple levels (e.g., a `@Service` that the team typically tests with `@SpringBootTest`), look at one existing test in the same package to determine the team's pattern. Match it.

Do not ask the developer for the test type unless detection fails on all the above signals AND no nearby test exists to copy from.

### Step 2 — Auto-detect existing patterns (no developer question needed)

Before generating, scan the test package for 1–2 existing test files:
1. Read the imports — note assertion library (JUnit assertions vs AssertJ vs Hamcrest)
2. Read the structure — note BDD style (`given/when/then`) vs Arrange/Act/Assert
3. Read fixture patterns — `@BeforeEach` setup, test data builders, Object Mother patterns
4. Read mock setup — `@Mock` field declaration style, `when().thenReturn()` patterns, argument captor usage

Match what you find. Do not impose patterns the codebase does not already use.

If the package has no existing tests, look one level up. If still none, fall back to the conventions in the rest of this file.

### Step 3 — Auto-determine scope of coverage (no developer question needed)

**In scope by default:**
- Every public method
- Every package-private method with non-trivial logic
- All branches, exception paths, and null-input cases per the Coverage section below

**Out of scope by default (skip silently — do not generate trivial tests):**
- Lombok-generated methods (getters, setters, equals, hashCode, toString)
- toString / equals / hashCode without business logic
- Constructors without validation logic
- Simple getters / setters

### Step 4 — Present the plan (one short confirmation, NOT a question)

Before generating any code, output a brief plan in this exact shape:

> Generating <test type> for `<ClassName>`. Detected pattern from `<reference file>` (or "no nearby tests — using file defaults").
> **Methods in scope:** `<method1>`, `<method2>`, `<method3>` (<N> branches), `<method4>` (<M> exceptions).
> **Methods skipped:** `<methodX>` (trivial getter), `<methodY>` (Lombok-generated).
> Generating now.

Then generate immediately. Do not wait for confirmation unless Step 5 applies.

### Step 5 — Ask ONLY genuine ambiguities

Ask a question only if:
- The class has no test-type signal AND no existing tests nearby to copy
- A method's business intent is unclear from code and Javadoc alone (e.g., a method named `process()` with complex branching and no documentation)
- The class depends on a collaborator with no obvious mock strategy (e.g., a third-party SDK requiring a specific mock pattern)

If none apply, do not ask — generate.

**Never ask:**
- "What test type do you want?" — you can detect it
- "Which methods should I cover?" — default is all public + branches
- "What style do you prefer?" — look at existing tests
- "Should I use AssertJ or JUnit assertions?" — look at existing tests
- "What coverage percentage do you want?" — defaults are below

---

## Framework and Tooling

- **JUnit 5 only.** Do not use JUnit 4. No `@RunWith`, no `org.junit.Test` — use `org.junit.jupiter.api.Test`.
- **Mockito** for mocking: `@Mock`, `@InjectMocks`, `@ExtendWith(MockitoExtension.class)` for pure unit tests.
- **AssertJ preferred** for fluent assertions when existing tests use it; otherwise match the prevailing style in the package.
- Verify mock interactions **only when the interaction is the thing under test** — do not blanket-verify every call.
- For mocking final classes or static methods, use `mockito-inline`. Note this in the test class.

---

## Test Types

- **Pure unit tests:** no Spring context, no real database. Deterministic and fast. Use `@ExtendWith(MockitoExtension.class)`.
- **Repository tests:** `@DataJpaTest`. Use an in-memory database (H2) unless the codebase already uses Testcontainers — match the existing pattern.
- **Controller tests:** `@WebMvcTest` with `MockMvc`. Assert status codes, response shape (RFC 7807 fields per `error-handling-java.instructions.md`), and controller-to-service interactions.
- **Full integration tests:** `@SpringBootTest`. Mock external dependencies with `@MockBean`. Naming convention: `*IT.java` if the project separates integration tests via Failsafe; otherwise `*Test.java`.
- **Do not use a real database connection in unit tests.** Repository tests use the in-memory or container DB only.

---

## Test class declaration

- Test classes **MUST be declared `public class <ClassName>Test`**.
- Even though JUnit 5 does not require the `public` modifier, this codebase's convention is explicit `public` on the class.
- Test methods MUST be `void` with **no access modifier** (package-private), per JUnit 5 norm.
- Use `@DisplayName` only when the test name alone is not self-explanatory — do not add it to every method.

---

## Test Structure and Placement

- Test class naming: `<ClassName>Test`, file suffix `*Test.java`. Integration tests may use `*IT.java` if the project uses Failsafe separation.
- Place tests under `src/test/java` mirroring the production package structure exactly. Do not create tests outside this folder.
- Cover, at minimum: happy path, negative cases, edge cases, and null/empty inputs (see Coverage section for specifics).
- Each test asserts one behaviour. Prefer several focused tests over one test with many assertions.
- Test method names should describe behaviour, not implementation. Use the style in existing tests — common patterns: `should_returnX_when_Y`, `givenX_whenY_thenZ`, or plain `methodName_scenario_expectedResult`.

---

## Coverage

This project's coverage thresholds (enforced by JaCoCo in `pom.xml`):
- **Line coverage: ≥ 90% per class**
- **Branch coverage: ≥ 80% per class**

These are defaults. Individual classes may be excluded via JaCoCo `<excludes>` configuration when justified (e.g., generated code, configuration-only classes, classes with `main` methods). **Do not lower the global threshold to fit a single hard-to-test class — exclude the class instead.**

### Required coverage when generating tests

For every class in scope, you MUST cover:
1. Every public method — at least one happy-path test
2. Every public method's documented exceptions — one test per exception type thrown
3. Every `if`/`else` branch in business logic methods — one test per branch
4. Every loop with non-trivial body — empty collection + single element + multiple elements
5. Every null-checkable parameter — one null-input test per parameter
6. Every `catch` block — one test that triggers the caught exception

### Do NOT cover

- Lombok-generated methods
- Trivial getters / setters
- toString / equals / hashCode without business logic
- Constructor injection assignments

### Do NOT claim a coverage percentage in your response

You cannot measure coverage — only JaCoCo can. Never write "this achieves 90% coverage" or any specific percentage.

Instead, after generating tests, output a **coverage checklist**:

```
| Method            | Happy path | Exceptions  | Branches    | Null inputs |
|-------------------|------------|-------------|-------------|-------------|
| processOrder      | ✅         | ✅ (2/2)    | ✅ (3/3)    | ✅          |
| validateInput     | ✅         | ✅ (1/1)    | ⚠️ partial  | N/A         |
| handleApiError    | ✅         | ✅ (2/2)    | ✅ (2/2)    | N/A         |
```

Then list:
- Methods explicitly out of scope (with one-word reason)
- Branches you could not cover and why
- Anything that requires the developer to verify with JaCoCo

The developer runs `mvn verify` (or `mvn jacoco:report`) to get the real numbers from JaCoCo.

---

## Generated tests must be self-contained and deterministic

- No reliance on system time, random values, environment variables, or external services.
- All mocks must be configured with `when(...).thenReturn(...)`, `doNothing()`, `doThrow()`, etc. **before** the method under test is invoked.
- Use `Mockito.lenient()` only when strictly needed (unused stubbing on shared `@BeforeEach`).
- Verify test setup is complete: every collaborator the SUT touches must have a stubbed response — otherwise the test produces a misleading `NullPointerException` masking the real issue.
- For time-sensitive code: inject a `Clock` and use `Clock.fixed(...)` in tests, never `Instant.now()`.
- For random-sensitive code: inject a seeded source or mock the random provider.

---

## Completeness of test generation

When asked to generate tests for a class:

- Generate tests for **all in-scope methods in a single response**, not partial. Do not stop mid-class.
- If the response would be very long, ask the developer first whether to split by method, rather than silently truncating.
- After generation, list each test method by name with a one-line summary of what it asserts, so the developer can verify completeness without reading every test.
- If a method genuinely cannot be tested in isolation (e.g., requires Spring context the dev didn't ask for), call it out explicitly with a `// TODO testing: requires <context>` comment and skip it — do not fake a test that passes vacuously.

---

## Self-check before presenting generated test code

Before showing the generated code, mentally compile-check the result:

- [ ] Every imported type is actually used; every used type is imported
- [ ] Every mock field's type matches the constructor parameter or `@Autowired` field it stands in for
- [ ] No references to methods that don't exist on the target class — verify method names, parameter types, and return types against the source
- [ ] Generic types are consistent (no raw types where the target uses parameterised types)
- [ ] Static imports are explicit (`assertEquals`, `assertNotNull`, `when`, `mock`, `any`, `verify`, AssertJ's `assertThat`)
- [ ] Method signatures match the source — return type, parameter types, exception declarations
- [ ] Final classes / methods are not being mocked with plain Mockito (requires `mockito-inline`)
- [ ] `@WebMvcTest` includes the controller class in `controllers = ...` or scans correctly
- [ ] `@DataJpaTest` does not pull in non-repository beans

**If any check fails, fix before presenting. Do not present code you cannot mentally compile.**

If the developer reports compilation errors after generation, fix them in a single follow-up — do not wait for the developer to iterate per-error.

---

## JDK and environment references in generated content

- This project requires **IBM Semeru JDK** at the version specified in `pom.xml` / `build.gradle`.
- When generating run scripts, Maven commands, or VS Code launch configurations, **never hardcode a JDK path**. Reference `JAVA_HOME` or use the IDE's configured runtime.
- If a generated script needs a JDK path, use `${JAVA_HOME}` (Unix/macOS) or `%JAVA_HOME%` (Windows), not a literal path.
- Do not reference developer-specific paths like `C:\Users\<name>\jdks\semeru-17.0.9` in any generated content.

---

## What never to do

- ❌ Generate tests that pass vacuously (no real assertion, or asserting only that the mock was called)
- ❌ Catch `Exception` in a test and assert nothing inside the catch — use `assertThrows(...)` or AssertJ's `assertThatThrownBy(...)`
- ❌ Use `@MockBean` in pure unit tests — that pulls in Spring context unnecessarily
- ❌ Use `Thread.sleep()` to wait for async behaviour — use Awaitility or a synchronous test design
- ❌ Hardcode timestamps, UUIDs, or current dates in expected values
- ❌ Share mutable state between tests via static fields
- ❌ Make tests depend on execution order
- ❌ Suppress test output or exceptions with empty catch blocks
- ❌ Skip generating tests for branches with a comment like "// trivial, no test needed" when the branch contains business logic

---

## Refusal pattern

> ⚠️ Java testing guardrail: <one-line rule>. Suggested alternative: <code>.

---

|
