---
name: bad-patterns
description: "Bad architecture patterns (BP-XX) for arch-review pattern catalog"
---

# Bad Patterns (BP) — Flag When Found

### BP-01: God Module
- Module with >1000 LOC, >15 public functions, or >10 direct dependents
- Name is vague ("utils", "helpers", "common")
- **Fix:** Split by responsibility, extract focused modules

### BP-02: Circular Dependencies
- Module A imports B, B imports C, C imports A
- Or more subtle: A uses B's type, B uses A's function
- **Fix:** Extract shared interface, dependency inversion, restructure layers

### BP-03: Layer Violation
- Router/controller contains business logic
- Service layer has SQL/HTTP-specific code
- Model/entity has presentation logic
- **Fix:** Push logic to correct layer, use DTOs at boundaries

### BP-04: Shotgun Surgery
- Single logical change requires edits in 5+ files across 3+ modules
- Feature additions follow "touch everywhere" pattern
- **Fix:** Consolidate related logic, better module boundaries

### BP-05: Hidden State Coupling
- Global mutable variables shared across modules
- Singleton with state that persists between operations
- Module-level caches without invalidation
- **Fix:** Make state explicit, pass as parameter, use proper state management

### BP-06: Inconsistent Error Handling
- Some modules use exceptions, others return error codes
- Some endpoints return 4xx with body, others return empty 5xx
- Bare `except` / `catch(e)` without context or re-raise
- **Fix:** Establish error convention, refactor to consistency

### BP-07: Import-Time Side Effects
- Database connections established at import
- HTTP clients initialized at module load
- Configuration read and validated at import time
- **Fix:** Lazy initialization, factory functions, DI

### BP-08: Leaky Abstraction
- Internal implementation details exposed in public API
- Database column names in API responses
- Framework-specific types in domain layer
- **Fix:** DTOs at boundaries, map internal to external representation

### BP-09: Mixed Paradigms Without Coherence
- Functional and OOP mixed without clear convention
- Callbacks, promises, and async/await in same module
- **Fix:** Choose paradigm per module/layer, document convention

### BP-10: Over-Engineering (Gas Factory)
- Abstract factory for single implementation
- Strategy pattern with one strategy
- Plugin system for non-extensible feature
- Multiple layers of indirection without benefit
- **Fix:** YAGNI — remove abstraction until needed, inline single implementations

### BP-11: Unprotected Shared Mutable State
- Global dicts/lists modified in async or threaded code without locks
- Module-level counters incremented without atomics
- Cache reads and writes not synchronized
- **Fix:** Add `asyncio.Lock`, `threading.Lock`, or use immutable data structures

### BP-12: Sync Blocking in Async Context
- `time.sleep()` in async function (blocks entire event loop)
- Sync HTTP client (`requests`) called inside async handler
- CPU-heavy computation in async without `run_in_executor`
- **Fix:** Use `asyncio.sleep()`, async HTTP client (`httpx`, `aiohttp`), offload CPU work

### BP-13: Missing Observability Foundation
- No structured logging (only `print()` or plain-text logger)
- No correlation IDs across request lifecycle
- No health check endpoints on a service with external dependencies
- Secrets or PII visible in log output
- **Fix:** Add structured logging library, correlation middleware, health endpoints, log sanitization

### BP-14: Anemic Domain Model
- Classes with only data fields (getters/setters), no behavior
- All logic in external "service" classes that manipulate dumb data objects
- Domain rules scattered across services instead of encapsulated
- **Fix:** Move behavior into domain objects where it belongs

### BP-15: Distributed Monolith
- Multiple services that must be deployed together to function
- Shared database between services
- Synchronous RPC chains (Service A → B → C → D)
- **Fix:** Establish clear service boundaries, use async messaging, own-your-data

### BP-16: Shared Database Between Services
- Multiple services reading/writing to same tables
- Schema changes require coordinating multiple teams
- No clear data ownership
- **Fix:** Database-per-service, expose data via APIs, eventual consistency

### BP-17: Configuration Sprawl
- Config loaded from env vars, files, CLI args, and hardcoded defaults in scattered locations
- No single source of truth for configuration
- Config values used without validation (raw `os.getenv()` with no type check)
- **Fix:** Centralize config loading, validate at startup, type all settings

### BP-18: Log-and-Throw Anti-pattern
- `except Exception: logger.error(...); raise` — same error logged multiple times as it bubbles up
- Log noise makes incident investigation harder
- **Fix:** Log at the point of handling (catch + resolve), not at every re-raise

### BP-19: Missing Idempotency
- Non-idempotent operations exposed via retry-prone channels (HTTP, message queue)
- Duplicate processing on retry (double charge, double email)
- No deduplication key or idempotency token
- **Fix:** Add idempotency key, check-before-act, atomic upserts

### BP-20: Feature Flag Rot
- Feature flags created but never cleaned up after rollout
- Code paths behind permanently-on flags that nobody dares remove
- Flag combinations creating untested states
- **Fix:** Flag lifecycle policy (create date, review date, cleanup deadline)

### BP-21: Chatty Microservices
- Single logical operation requires 10+ inter-service calls
- No batching or aggregation layer
- Network latency dominates response time
- **Fix:** BFF / aggregation layer, batch APIs, async messaging for non-critical paths

### BP-22: Catch-Rethrow Without Context
- `except Exception as e: raise SomeError(str(e))` — loses original traceback and exception chain
- `except Exception: raise CustomError("something went wrong")` — no context
- **Fix:** Use `raise ... from e` (Python) or wrap with cause chain, preserve original traceback

### BP-23: ADR Predicate Not Empirically Testable Now

**Pattern:** an architectural decision is accepted on predicates that are
defensible only in a projected future state — "once we roll out X", "after the
migration", "in the canonical deployment" — rather than on ground-truth that
can be verified against the current codebase + live environment at ADR
review time.

**Why this is a bad pattern:**
- Predicates framed as "roadmap-credible" silently convert the ADR from a
  record of decision into a promise of future work. The ADR is then non-falsifiable
  at the moment it lands — which is the only moment it's actually reviewed.
- The loophole compounds: next ADR cycle cites this one as precedent, inheriting
  the unverified assumption. Two or three hops later the architecture document
  reflects a system that does not exist.
- When ground-truth is finally collected (scout, probe, production incident),
  the delta between ADR-claimed state and actual state is routinely 50%+ —
  not because the team was dishonest, but because the predicates were shaped
  by what the authors believed SHOULD be true.

**Detection signals at ADR review:**
- Predicate phrased in future/conditional tense: "will be", "once migrated",
  "after rollout", "in production mode", "when the feature is enabled".
- Predicate references a state that requires a sweep to verify (e.g. "all
  writers go through DALFactory", "every MB declares service X in config")
  but no scout / probe / grep output is cited in the ADR body or appendix.
- Predicate references an environment the ADR author cannot access at review
  time (prod DB row counts, prod container process list, prod log volumes).
- Predicate is a counting claim ("5 PG tables", "19 writers", "3 migration
  runners invoked") without a linked command whose output produced the count.

**Required evidence (ADR defensibility gate):**
1. Every structural claim about the current system must cite either:
   - A grep / ripgrep / `ast-grep` command + its output, OR
   - A scout report path + the specific section that substantiates it, OR
   - A probe result (e.g. `sqlite3 ... .schema`, `docker exec ... ps`, log
     excerpt) with timestamp.
2. Claims that cannot be substantiated NOW must be tagged explicitly:
   `[predicate pending: <scout-ticket-id> — {what would confirm it}]` and
   the ADR's acceptance gate must list the scout as blocking.
3. The ADR author runs the scout themselves OR commissions one before the
   debate closes. "Roadmap-credible" is not an acceptable substitute.

**Gate at review time:**
- Any predicate failing (1)+(2) is a **CRITICAL** finding: the ADR is not yet
  decidable. Reviewer returns with "gather ground truth first" instead of
  debating on unverified assumptions.
- Exception: predicates about a NEW system being designed (no existing
  implementation to ground-truth against). These are explicitly scoped as
  design intent, not current-state claims, and must be re-ground-truthed at
  the first implementation cycle.

**Canonical case study:** BG-S14-P08-E10 Round 1 debate (ADR-031 platform-
project boundary). 4 structural assumptions underpinned the Round 1 position:
(a) "writers all go through DALFactory", (b) "5 PG tables initialised at boot",
(c) "migration runner invoked from `app_lifespan`", (d) "per-project role
isolation in place". Round 2 scout (read-only, 12 sections, ~4 hours) refuted
all 4: (a) found 19-21 writers opening `aiosqlite.connect()` directly, (b)
found 2 of 5 tables exist on prod (3 have DDL constants but no `initialize()`
call), (c) found migration runner present in code with zero imports from
`app_lifespan.py`, (d) found shared role still in use. The Round 1 "roadmap-
credible" framing had shielded all four from empirical test at review time —
they all failed on first contact with ground truth. Defensibility gate would
have required the scout before Round 1 closed, saving one full debate cycle.

**Fix direction:**
- Adopt scout-before-debate protocol for any ADR making ≥3 structural claims
  about current state.
- At ADR template level, add explicit "Evidence" block per predicate with
  citation format above.
- Re-run ground-truthing at every quarterly arch review: predicates shift as
  code changes, and an ADR accepted 3 quarters ago may now be stale even if
  it was defensible then.

**Cross-reference:** `probekit-deploy-readiness-bogame` Probe 7 (Persistence
reachability probe) — the runtime-level mirror of this review-time rule.
When ADR says "X persists to Y", Probe 7 checks State A/B/C at handoff.
