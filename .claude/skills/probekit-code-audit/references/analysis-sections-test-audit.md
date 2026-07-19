---
name: analysis-sections-test-audit
description: "Section 12 — Test Quality Audit: coverage gaps, test effectiveness, isolation, flakiness, design quality, maintenance debt, and test architecture."
---

# Section 12 — Test Quality Audit

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
- Runtime-mutated hash/serialization source: production code hashes or serializes a
  dict/object that is ALSO mutated at runtime (e.g. a per-execution `_ctx` /
  `_execution_results` key injected into a config or node-data dict). Two audit checks:
  (a) does any write path add keys to the same object that a hash/dedup/checkpoint key
  is later derived from? (b) is there a test proving the hash/serialization uses the
  CLEAN authored value (underscore/runtime keys stripped) on BOTH the forward path and
  any reconstructed/resume path? Missing (b) → WARNING: loop-detection / dedup keys drift
  per-run and never match; serialization can carry non-serializable runtime objects.
  // discovered S20 P108 (governance.py:150 — `_ctx` poisoned resume-leg loop detection)
- Tautological tests: `assert x == x`, comparing a value to itself
- Mocking the system under test: mocking the very function being tested
  means the test never exercises real code
- Happy path only: no error path, no edge case, no boundary tested
  → tests document that code works when everything is fine; silent on failure modes
- Secret catchers: test with no assertions relying on implicit exception catch —
  passes even when the function does the wrong thing silently
- **AI Test Tautology:** AI writes function → AI writes test → test verifies
  implementation matches implementation, not business intent. Signals:
  - Test mirrors the function logic step-by-step (same conditions, same branches)
  - Test was generated in the same session as the implementation (check git timestamps)
  - Test has no edge cases from production experience (idempotency, race conditions,
    vendor API quirks, timezone issues, currency rounding)
  - Test asserts internal data shapes rather than business outcomes
  - Bulk test updates: AI changed behavior → AI updated 10+ tests to match new behavior
    (question: were all those test changes intentional or did AI just make tests pass?)
  - Test uses exact same mock data patterns as the implementation's defaults
    → test is a mirror, not a contract

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

**12.8 — Multi-Failure Triage (`--maxfail=20+` rule)**

When auditing a test suite with many failures, NEVER survey with `--maxfail=1`. A single-failure view hides co-occurring root-cause patterns and produces incorrect repair plans.

- **Rule:** surveying runs use `--maxfail=20` minimum. Classify failures by root-cause signature groups, not by file or by test name.
- **Why:** one pending-fix story typically flushes many tests simultaneously (NodeRegistry gap → every MB whose entry node isn't registered; approval-pause default flip → every flow relying on the old default; schema rename → every structural test referencing the old field). Each has a recognisable failure signature (error class + message shape + site pattern). Grouping by signature reveals 3 patterns from 14 failures; `--maxfail=1` sees "one test broke."
- **Procedure:**
  1. `pytest --maxfail=20 -x- --tb=short` (or higher cap if >20 expected).
  2. Group failures by signature: Pattern A = first recurring error class + first traceback line shape; Pattern B, C, ... similarly.
  3. Report in AUDIT: `N failures, M patterns` — where M is the number of independent fix stories.
- **Anti-pattern:** "14 failures → 14 fix tasks" in the report is a triage failure, not a complexity finding. Collapse to root-cause groups before producing the fix backlog.
- **Severity:** if audit run was performed with `--maxfail=1` and skipped the triage grouping, flag as SUGGESTION (the audit itself was shallow). Canonical case: BOGame P80 C359 S14-34 — 14 failures collapsed into 3 patterns (A: 6 tests, B: 5 tests, C: 3 tests). Full writeup: `probekit-test-suite/references/scoring-formula.md § Multi-Failure Triage`.

**12.9 — False-Green Guard (un-skip ≠ mechanism proven)**

A test that passes without exercising the mechanism it names is worse than a failing test —
it converts a live gap into a green checkmark. The audit question for every test guarding a
mechanism (budget, limit, breaker, timeout, dedup, guard): *would this test still pass if the
mechanism were deleted?* If yes, it proves nothing.

- **Trigger sites:** un-xfailed / un-skipped batches (removing the marker is not evidence the
  behavior works); tests asserting only "no exception" around a bounded operation; tests whose
  fixture never crosses the threshold the mechanism enforces (budget=0 defaults, empty configs).
- **Rule:** the assertion must FAIL when the mechanism is absent — assert the enforcement
  outcome (the raised bound-exceeded error, the breaker state flip, the capped count), not the
  happy path around it. When feasible, verify by mentally (or actually) reverting the mechanism
  and confirming the test would go red.
- **Severity:** 🟡 WARNING per false-green test; 🔴 CRITICAL when the false-green guards a
  safety/spend bound (budget, rate limit, kill switch).
- **Canonical case:** BOGame S19 C451 — un-xfailing 8 delegated-path governance tests looked
  like coverage, but none exercised `stalemate_detection.llm_call_budget`; the adapter dropped
  the field so the budget silently defaulted to unlimited. The real guard asserts
  `FlowExecutionError("LLM call budget exceeded")` fires on the adapter-produced flow
  (`tests/executor/test_delegated_stalemate_budget.py`).

**12.9 — Linter baseline tolerance for generated tests**

When generating new tests (or when auditing tests that were just generated), newly-added test files MUST NOT introduce additional linter violations (ruff, mypy, flake8) beyond the project's existing baseline. Existing unchanged files may retain pre-existing violations — those belong to their own cleanup cycle.

- **Rule:** run `ruff check {new_test_files}` isolated to just the new/modified test files. Zero new violations. Pre-existing violations in untouched files are out of scope.
- **Why:** a generated test file that adds 5 new ruff warnings to a project that already has 100 pre-existing warnings is an invisible regression — CI-wide ruff count goes from 100 to 105 and nobody notices. Scoping to `git diff --name-only {base}..HEAD | grep ^tests/` isolates the regression surface to this cycle's additions.
- **Severity:** any new ruff/mypy/flake8 violation in a newly-generated test file → WARNING (bundled with the test generation for this cycle).
- **Anti-pattern:** "ruff baseline is already high, a few more won't hurt" — this is the slow-rot path. Each cycle must leave the baseline ≤ where it started.
- **Canonical case study:** BOGame `tests/services/test_tier5_services.py` entered the suite with 3 pre-existing ruff violations; those are baseline. Any cycle touching that file inherits the responsibility to not add to the count. Cycles generating entirely new test files start from 0 and must stay at 0.

Severity escalation for Section 12:
- Assert-free test → WARNING (silently passes always)
- Test with only trivial assertions on critical path → WARNING
- Flaky test (sleep-based, time-dependent) → WARNING
- Skipped test with no reason → SUGGESTION
- Copy-paste tests that should be parameterized → SUGGESTION
- God test → SUGGESTION
- Missing regression test for known bug → WARNING
- AI test tautology (test mirrors implementation, no production edge cases) → WARNING
- Bulk AI test update (10+ tests changed to match new behavior in one commit) → CRITICAL
