# Architecture Patterns Catalog

Reference catalog for architecture review. Check codebase against these patterns.

## GOOD PATTERNS (reward when found)

### GP-01: Composition Over Inheritance
- Mixin-based composition for shared behavior
- Strategy pattern for variant algorithms
- Delegation instead of deep class hierarchies
- **Why it matters:** Flexible, testable, avoids fragile base class problem

### GP-02: Explicit Session/Transaction Management
- Transaction boundary defined at one layer (router/handler)
- Service layer does `flush()` only, never `commit()`
- Single point of transaction control per request
- **Why it matters:** Prevents partial commits, simplifies error recovery

### GP-03: Lazy Singleton with Reset
- Resource created on first access, not at import time
- Factory function with module-level cache
- Reset mechanism for testing
- **Why it matters:** Solves async lifecycle issues, enables test isolation

### GP-04: Double-Entry / Self-Verifying Data
- Every state change creates balancing records
- Sum invariants (always zero, always positive)
- Immutable audit trail alongside mutable state
- **Why it matters:** Data integrity, auditability, catch bugs early

### GP-05: Snapshot at Decision Point
- Copy mutable data into immutable record at action time
- Decision survives future changes to source data
- Clean separation: current state vs historical state
- **Why it matters:** Audit trail, no retroactive data corruption

### GP-06: Three-Stage Pipeline
- Separate stages for: resolve → execute → aggregate
- Each stage independent (can fail without blocking others)
- Exponential backoff on empty work queues
- **Why it matters:** Resilience, horizontal scaling, debuggability

### GP-07: Guarded Field with Warning
- `__setattr__` hook warns on direct writes to computed/managed fields
- Distinguish creation vs mutation (check persistence state)
- Warning, not exception — catches bugs without blocking valid code
- **Why it matters:** Prevents silent corruption of derived data

### GP-08: Dependency Injection via Function Parameters
- Dependencies passed as parameters, not imported directly
- Factory functions or DI framework for wiring
- Configuration injectable, not hardcoded
- **Why it matters:** Testability, flexibility, explicit dependencies

### GP-09: Domain Exception Hierarchy
- Base error with code + message + HTTP status
- Domain-specific subclasses (NotFound, Conflict, Forbidden)
- Catch specific, log with context, translate at boundary
- **Why it matters:** Consistent error handling, good diagnostics

### GP-10: Trace ID Propagation
- Unique ID per request/operation
- Bound to structured logging context
- Propagated across async boundaries
- Returned in response headers
- **Why it matters:** Distributed tracing, debugging, audit correlation

### GP-11: Structured Logging with Context Binding
- JSON/key-value logs with contextual fields (user_id, operation, duration_ms)
- Logger bound to request context via middleware (structlog, winston, zap)
- Log levels used consistently: ERROR=unexpected, WARNING=degraded, INFO=business events, DEBUG=internal
- **Why it matters:** Machine-parseable logs, fast incident investigation, correlation across services

### GP-12: Bounded Connection Pool with Health Checks
- Pool size explicitly configured (not defaults), with min/max bounds
- `pre_ping` or equivalent health check before returning connection
- `pool_recycle` to prevent stale connections
- Metrics on pool utilization (active, idle, waiting)
- **Why it matters:** Prevents connection leaks, handles database restarts gracefully

### GP-13: Context-Based Timeout Propagation
- Timeout/deadline set at entry point and propagated through all layers
- Python: `asyncio.timeout()` or `httpx.Timeout`; Go: `context.WithTimeout`; JS: `AbortController`
- Each layer respects remaining budget, not a fresh timeout
- **Why it matters:** Prevents cascading timeouts, ensures predictable request lifecycle

---

## BAD PATTERNS (flag when found)

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

### GP-14: Repository Pattern
- Data access encapsulated behind interface (ABC / Protocol)
- Business logic depends on interface, not on concrete DB implementation
- Concrete implementation injected at startup
- **Why it matters:** Swappable persistence (SQLite → PostgreSQL), testable without DB

### GP-15: DTO / Value Object at Layer Boundaries
- Dedicated types for data crossing layer boundaries (API → Service, Service → DB)
- No ORM models in API responses, no request dicts in business logic
- Validation at boundary (Pydantic, dataclass, TypedDict)
- **Why it matters:** Prevents leaky abstractions, clear contracts between layers

### GP-16: Middleware Chain / Pipeline Pattern
- Cross-cutting concerns (auth, logging, rate limiting) composed as ordered pipeline
- Each middleware has single responsibility
- Order configurable, not hardcoded
- **Why it matters:** Clean separation of concerns, easy to add/remove/reorder

### GP-17: Configuration Hierarchy with Startup Validation
- Config loaded from multiple sources with priority (env > file > defaults)
- All config validated at startup, fail-fast on invalid values
- Typed config objects (Pydantic BaseSettings, dataclass), not raw dicts/strings
- **Why it matters:** No runtime config surprises, self-documenting settings

### GP-18: Graceful Shutdown
- Signal handler catches SIGTERM/SIGINT
- In-flight requests complete before exit
- Resources cleaned up in reverse order of initialization
- Timeout for forced shutdown if graceful takes too long
- **Why it matters:** No dropped requests, no leaked connections, clean restarts

### GP-19: Retry with Jitter
- Failed operations retried with exponential backoff + random jitter
- Max retries bounded, not infinite
- Idempotent operations only (or idempotency key used)
- **Why it matters:** Prevents thundering herd on service recovery

### GP-20: Dead Letter Queue with Monitoring
- Failed jobs moved to separate queue after max retries
- DLQ monitored with alerts on growth
- Manual replay mechanism available
- **Why it matters:** No silent data loss, operational visibility into failures

---

## BAD PATTERNS — continued

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

---

## DIAMOND PATTERNS (exceptional quality — highlight when found)

### DP-01: JSONB/Flexible Schema with Mutation Safety
- Schema-flexible storage (JSONB, document) with explicit mutation tracking
- `set_jsonb()` or equivalent that forces change detection
- Deep-copy before mutation to prevent reference bugs
- **Why it's diamond:** Solves framework limitation elegantly, prevents silent data loss

### DP-02: Two-Session Fusion for Read-Write Operations
- Read session provides user/context, write session provides transaction
- Framework reuses same connection for both
- Eliminates `merge()` / reattach overhead
- **Why it's diamond:** Zero-cost pattern that prevents subtle ORM bugs

### DP-03: Atomic Update with WHERE Guard
- `UPDATE ... SET counter = counter + 1 WHERE counter < max`
- Prevents race conditions without locks
- Returns affected rows count for conflict detection
- **Why it's diamond:** Lock-free concurrency that's both safe and performant

### DP-04: Savepoint Pattern for Duplicate Detection
- `begin_nested()` + `flush()` to catch IntegrityError
- Rolls back only inner savepoint, outer transaction survives
- **Why it's diamond:** Clean duplicate handling without killing the transaction

### DP-05: Progressive Trust Architecture
- Actions classified by risk level (low → auto, high → approval)
- Risk level determines execution path, not just logging level
- Human-in-the-loop at trust boundaries
- **Why it's diamond:** Safety without operational friction

### DP-06: Lock-Free Concurrency via Immutable Data
- Shared state represented as immutable snapshots
- Updates create new versions (copy-on-write, persistent data structures)
- No locks needed — readers always see consistent state
- **Why it's diamond:** Eliminates entire class of race conditions by design, not by discipline

### DP-07: Circuit Breaker with Observability
- External dependency calls wrapped in circuit breaker (closed → open → half-open)
- Breaker state exposed as metric (Prometheus gauge, structured log event)
- Fallback behavior defined per dependency (cached response, default, error)
- **Why it's diamond:** Graceful degradation + automatic recovery + full visibility

### DP-08: Correlation-Aware Structured Logging
- Request ID generated at entry, propagated via context (ContextVar, AsyncLocalStorage, Go context)
- All log statements automatically include request_id, user_id, operation
- Response headers include request ID for client-side correlation
- Logs are JSON with consistent field naming across all services
- **Why it's diamond:** Any production issue traceable end-to-end in seconds

### DP-09: Transactional Outbox Pattern
- State change + outgoing event written in same DB transaction
- Background poller reads outbox table, publishes events, marks as sent
- Guarantees at-least-once delivery without 2PC
- **Why it's diamond:** Solves distributed consistency without distributed transactions

### DP-10: Event Sourcing with Projection Rebuild
- State derived from ordered event log, not mutable rows
- Projections (read models) can be rebuilt from scratch by replaying events
- Event log is append-only, immutable audit trail for free
- **Why it's diamond:** Complete audit history + time-travel debugging + zero data loss

### DP-11: CQRS with Physical Separation
- Write model (normalized, transactional) and read model (denormalized, fast) in separate stores
- Write events trigger async projection updates to read store
- Each side optimized independently (write for consistency, read for throughput)
- **Why it's diamond:** Scales reads and writes independently, eliminates query/write trade-offs

### DP-12: Saga with Compensations & Idempotency
- Multi-step workflow with explicit compensation for each step (undo on failure)
- Each step idempotent (safe to retry)
- Saga state persisted, recoverable after crash
- **Why it's diamond:** Reliable distributed transactions without 2PC, self-healing on partial failure

### DP-13: Hexagonal Architecture (Ports & Adapters)
- Domain core has zero framework dependencies
- All I/O through ports (interfaces) with injectable adapters
- Tests use in-memory adapters, production uses real adapters
- **Why it's diamond:** Framework-independent domain, trivially testable, swappable infrastructure

### DP-14: Strangler Fig with Routing Facade
- New system built alongside legacy, routing facade directs traffic
- Features migrated one-by-one, not big-bang rewrite
- Legacy and new coexist safely during transition
- **Why it's diamond:** Zero-downtime migration, reversible at any point

### DP-15: Bulkhead Isolation
- Critical resources partitioned into isolated pools (separate thread pools, connection pools, rate limits per tenant)
- Failure in one partition cannot exhaust resources for others
- Monitoring per partition for anomaly detection
- **Why it's diamond:** Prevents cascading failures, guarantees fairness under load

### DP-16: Contract Testing Between Services
- Producer and consumer both test against shared contract (Pact, OpenAPI schema)
- Contract changes caught before deployment (CI gate)
- No integration environment needed for contract validation
- **Why it's diamond:** Catches breaking changes at build time, not runtime

### DP-17: Graceful Degradation Cascade
- Structured degradation levels (full → reduced → minimal → offline)
- Each level has defined behavior (not ad-hoc error handling)
- Degradation triggered by metrics (circuit breaker, budget, latency), not just exceptions
- **Why it's diamond:** System stays useful under partial failure, not just "up or down"

### DP-18: Idempotency Key Pattern
- Client sends unique key per operation, server deduplicates
- Key stored with result; duplicate request returns cached result
- TTL on idempotency records prevents unbounded storage
- **Why it's diamond:** Safe retries at every layer, no double-processing

### DP-19: Typed Configuration with Startup Validation
- All config fields typed (Pydantic BaseSettings, Go struct tags, TS zod schema)
- Validation runs at startup, fail-fast on invalid config
- Secrets loaded from vault/env, never from config files
- Default values explicit, documented, and tested
- **Why it's diamond:** Zero runtime config surprises, self-documenting, testable settings
