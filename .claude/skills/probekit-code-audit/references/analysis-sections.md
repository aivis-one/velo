# Analysis Sections

Execute sections 1–9 in order from this file. Sections 10, 11, 12 are invoked separately by SKILL.md steps 3, 3.5, and 3.6.
For each section with no findings, write exactly: "No issues found." and move on.
Never invent findings to fill a section.

---

## Section 1 — General Overview

- What does the code do
- Architecture and approach
- Technology stack / framework detected
- Overall quality score: X/10

Scale:
- 9-10: Production-ready, cosmetic only
- 7-8: Good, improvements exist, nothing critical
- 5-6: Works but notable problems
- 3-4: Serious problems, needs rework
- 1-2: Must be rewritten

---

## Section 2 — Critical Bugs and Logic Errors

Targets:
- Logic errors that produce wrong results
- Race conditions, shared mutable state, missing locks
- Null/undefined/nil dereferences and missing guards
- Off-by-one errors, boundary failures
- Async/await mistakes: missing await, unhandled rejections, wrong error propagation
- Type coercion bugs
- Edge cases: empty input, zero, negative values, max values, concurrent access

Every finding must include a diff example. No finding without a concrete fix.

---

## Section 3 — Error Handling

Targets:
- Silent catches: exceptions caught but not logged or re-thrown
- Bare except / catch-all without re-throw
- Unhandled promise rejections
- Generic error messages with no debugging context ("Something went wrong", "Error occurred")
  Good messages include: what failed, which input caused it, where in the system
- Logging completeness: minimum = exception type + message + call origin
  Flag: logging only message string without stack trace or request context
- Missing retry logic on transient failures (network, I/O)
- Missing graceful degradation on non-critical paths

---

## Section 4 — Security and Vulnerabilities

For each vulnerability found: attack vector → impact → fix with diff example.
Show example of malicious input where relevant.

Targets:
- Hardcoded secrets, API keys, tokens, passwords in code or config
- Sensitive data in logs (tokens, PII, passwords)
- Unvalidated user input reaching dangerous sinks:
  - DB queries without parameterization (SQL/NoSQL injection)
  - Template rendering without escaping (XSS)
  - File system paths without sanitization (path traversal)
  - Server-side HTTP calls with user-controlled URLs (SSRF)
  - Deserialization of untrusted data without validation
- Broken authentication or authorization logic
- Missing authorization checks on protected endpoints
- Mass assignment: model binding without allowlist
- Insecure defaults: debug mode on, open CORS, weak or deprecated crypto
- Privilege escalation paths: code grants more permissions than required
  (AI-generated code shows 322% more escalation paths than human-written — flag any pattern
  where a component acquires permissions beyond its stated role)
- Architectural auth drift: auth/authz logic changed across multiple files
  without consistent update — silent authentication failures
- Rate limiting absent on public endpoints
- APIs returning full objects instead of DTOs (data over-exposure)
- Dependency verification: flag any package import for cross-check in Section 10

Additional detection patterns (SSRF, deserialization, mass assignment, IDOR):

- **SSRF**: `requests.get(user_url)`, `urllib.urlopen(url)`, `http.Get(url)`, `fetch(url)` where URL comes from user input without allowlist. Flag any HTTP call where the URL or host is derived from request parameters.
- **Deserialization**: `pickle.loads()`, `yaml.load()` (without `Loader=SafeLoader`), `eval()`, `exec()`, `unserialize()` (PHP), `ObjectInputStream` (Java) on untrusted data. Always CRITICAL.
- **Mass assignment**: ORM model created from `**request.data` or `Object.assign(model, req.body)` without explicit field allowlist. Look for: `Model(**data)`, `Model.create(**kwargs)`, `_.merge(obj, userInput)`.
- **IDOR**: DB query with user-supplied ID without ownership check: `Model.objects.get(id=request_id)` without `.filter(user=current_user)`. Look for: `.get(id=...)`, `.findById(params.id)`, `WHERE id = ?` without `AND user_id = ?`.
- **Open redirect**: `redirect(request.params['url'])`, `res.redirect(req.query.next)` without validating that URL is relative or on allowlist.

---

## Section 5 — Performance

Targets:
- O(n²) or worse algorithms where O(n log n) or O(n) is achievable
- N+1 query problems
- Missing indexes on frequently queried fields
- Unnecessary repeated computation inside loops
- Missing caching on expensive or repeated operations
- Excessive memory allocation: large objects created in loops
- Blocking I/O on async paths
- Missing pagination on potentially large result sets

---

## Section 6 — Code Quality and Best Practices

Targets:
- Naming: variables, functions, classes that mislead or obscure intent
- SOLID violations: classes doing multiple things, tight coupling, no interfaces
- DRY violations: duplicated logic that should be extracted
- KISS violations: unnecessary complexity for simple problems
- Dead code: unused functions, unreachable branches, commented-out blocks
- Comments: missing where logic is non-obvious, or present but lying about what code does
- Modern language features unused where they would simplify (optional chaining, destructuring,
  async/await vs callbacks, dataclasses vs raw dicts, etc.)
- Inconsistent conventions: mixed naming styles, mixed patterns within same module

---

## Section 7 — Testability

Targets:
- Hard dependencies on global state or singletons blocking unit tests
- Missing dependency injection preventing mocking
- Functions doing too much to test in isolation
- Absence of test directory or test files for critical paths
- No error path tests (only happy path tested)
- Tests that test implementation details instead of behavior
- Concrete suggestions: what to extract, what to inject, what to mock

---

## Section 8 — Refactoring Recommendations

Only for patterns that meaningfully improve the code.
Each recommendation must include a before/after example.

Targets:
- Extract: functions/classes that should be split
- Abstract: duplicated structures that need a base class or utility
- Simplify: over-engineered solutions
- Alternative architecture: only when current approach has structural problems

---

## Section 9 — Minor Improvements and Polish

- Type annotations missing on public interfaces
- Linter / formatter issues visible in the code
- Stylistic inconsistencies
- Small correctness improvements not covered above

---

## Section 11 — Cross-Module Consistency (multi-file only)

Run only when 2+ files are reviewed together. Skip for single-file reviews.
If a single file is being reviewed, write: "Skipped (single file review)."

Targets:
- Duplicate functionality across files (same CRUD, same validation, same error handling)
- Inconsistent patterns: one file uses pattern A, another uses pattern B for the same concept
- Inconsistent datetime handling (aware vs naive, UTC vs local, different format strings)
- Inconsistent error handling strategies across modules (one logs, another swallows, third re-throws)
- Shared state or dependencies where a change in one file silently breaks another
- API contract mismatches: caller expects X, callee returns Y
- Inconsistent naming for the same concept across files (e.g. `db_path` vs `database_path`)
- Connection/resource management differences (pooling vs per-call, pragma usage vs bare connect)
- Duplicate APIs: multiple files providing CRUD for the same DB table with incompatible interfaces

Every finding must reference BOTH files and explain the inconsistency with a diff example showing the recommended unification.

---

## Section 12 — Test Quality Audit

Run whenever test files are detected. If test_audit_mode = true, give expanded treatment.
If no test files found: write "No test files detected." and close section.

This section evaluates whether existing tests actually protect the codebase —
not just whether they exist or whether coverage numbers look good.

**12.1 — Coverage Gaps**
- Identify critical paths in production code that have zero test coverage
- Flag: public API methods with no corresponding test
- Flag: error handling branches that are never exercised
- Flag: boundary conditions never tested (empty input, zero, max values, None/null)
- Do not require 100% coverage — flag gaps on high-risk paths only
- Note: coverage percentage alone is meaningless; a test that asserts nothing can cover 100%

**12.2 — Test Effectiveness (Are Tests Actually Testing Anything?)**

The most critical subsection. A passing test suite with bad tests provides false confidence.

- Assert-free tests: test function that runs code but has no assertions
  → WARNING: test passes no matter what the code does, provides false confidence
- Trivial assertions: `assert result is not None`, `assert len(result) > 0`
  with no check of actual values — verifies existence, not correctness
- Testing implementation details instead of behavior:
  tests that break on every refactor even if behavior is unchanged
  (e.g., asserting internal method was called instead of asserting output)
- Tautological tests: `assert x == x`, comparing a value to itself
- Mocking the system under test: mocking the very function being tested
  means the test never exercises real code
- Happy path only: no error path, no edge case, no boundary tested
  → tests document that code works when everything is fine; silent on failure modes
- Secret catchers: test with no assertions relying on implicit exception catch —
  passes even when the function does the wrong thing silently

**12.3 — Test Isolation and Reliability**

- Test interdependence: test B fails when test A hasn't run first
  (shared mutable state, database rows, files left on disk)
- Generous leftovers: one test creates data, another test depends on it implicitly
- Global state pollution: tests modify module-level variables or singletons without cleanup
- Missing fixture teardown: files, DB rows, network connections opened but not closed
- Hard-coded environment assumptions: absolute paths, specific ports, env vars only on dev machine
- Time-dependent tests: assertions against `datetime.now()` or similar without pinning
- Non-deterministic data: random inputs or UUIDs used in assertions without seeding

**12.4 — Flakiness Indicators**

Flaky tests erode trust in the entire test suite.

- `time.sleep()` or explicit waits used to synchronize async operations
  → brittle: works on developer machine, fails under load or slow CI
- Assertions on floating point equality without tolerance (`pytest.approx()`)
- Race conditions in tests that share state across concurrent operations
- Tests sensitive to execution order (no `pytest-randomly` guard)
- Tests that retry on failure instead of fixing root cause (masked flakiness)
- Hardcoded dates that will fail after a certain date

**12.5 — Test Design Quality**

- God tests: one test function testing multiple unrelated behaviors
  (name contains "and", or has 20+ assertions across unrelated outcomes)
- Excessive setup (Mother Hen): hundreds of lines of setup for one assertion
  → usually signals the code under test is untestable and needs decomposition
- Copy-paste tests: identical test bodies differing only in one value
  → should be parameterized (`@pytest.mark.parametrize`, `test.each`, table-driven)
- Enumerator naming: tests named test1, test2, test3 or test_thing_1, test_thing_2
  → test names are documentation; anonymous tests are useless after a failure
- Free-ride assertions: unrelated assertions piggybacking in one test
  → when test fails, unclear which behavior broke
- Testing framework code: tests that assert language behavior rather than application behavior
  (`assert [] == []`, `assert True`)

**12.6 — Test Maintenance Debt**

- Skipped/xfail tests with no explanation or tracking issue
  → silent dead weight; skips accumulate and are never revisited
- Commented-out tests: indicate known failures that were silenced instead of fixed
- Tests for deleted code: test file imports a module that no longer exists
- Duplicate test scenarios: same behavior tested multiple times with different names
- Missing regression tests: if a bug was fixed, was a test added to prevent recurrence?

**12.7 — Test Architecture (for larger suites)**

Only flag if the test suite has 20+ test files or 200+ test functions.

- Inverted pyramid: 90%+ unit tests with no integration or acceptance tests
  → mocked behaviors never verified against real dependencies
- Testing only via UI or E2E with no unit/integration layer
  → slow, fragile, impossible to diagnose on failure
- No test categorization: fast unit tests mixed with slow integration tests
  → slow feedback loop, developers skip running tests locally
- Missing contract tests: services calling each other with no verification that
  the caller's assumptions match what the callee actually returns

Severity escalation for Section 12:
- Assert-free test → WARNING (silently passes always)
- Test with only trivial assertions on critical path → WARNING
- Flaky test (sleep-based, time-dependent) → WARNING
- Skipped test with no reason → SUGGESTION
- Copy-paste tests that should be parameterized → SUGGESTION
- God test → SUGGESTION
- Missing regression test for known bug → WARNING
