# Architecture Analysis Sections

## Section 1: Module Boundaries & Cohesion

**What to check:**
- Does each module/package/directory have a single, clear responsibility?
- Are related functions, classes, and data grouped together?
- Is there code that belongs in a different module?
- Do module names accurately describe their contents?
- Are there "god modules" that do too many things (LOC outliers, disproportionate imports)?

**Signals of good cohesion:**
- Module can be described in one sentence without "and"
- Internal classes/functions reference each other frequently
- External modules import a small, stable public API
- Changes to one feature affect one module

**Signals of bad cohesion:**
- Module has unrelated responsibilities joined by coincidence
- Functions in same module never call each other
- Module name is vague ("utils", "helpers", "common", "misc")
- Changes to one feature require editing 5+ modules

**Severity guide:**
- CRITICAL: God module (>1000 LOC, >15 public functions, >10 external importers)
- WARNING: Module with 2+ unrelated responsibilities
- SUGGESTION: Vague naming, minor grouping improvements

---

## Section 2: Dependency Direction & Acyclicity

**What to check:**
- Do dependencies flow in one direction (high-level → low-level)?
- Are there circular imports or mutual dependencies?
- Does the dependency graph form a DAG (directed acyclic graph)?
- Do lower layers import from upper layers (layer violation)?
- Is there a clear dependency hierarchy?

**Analysis approach:**
1. Trace import statements in 10-15 key files
2. Identify dependency direction: UI → Service → Repository → Model
3. Check for inversions: Model importing from Service, Repository importing from Router
4. Check for circular: A imports B imports C imports A

**Severity guide:**
- CRITICAL: Circular dependency between core modules
- CRITICAL: Lower layer importing from upper layer in core architecture
- WARNING: Circular dependency in utility/helper modules
- WARNING: Dependency direction unclear (no layering visible)
- SUGGESTION: Could benefit from dependency inversion (interface extraction)

---

## Section 3: Coupling Assessment

**What to check:**
- How many other modules does each module depend on? (fan-out)
- How many modules depend on each module? (fan-in)
- Are dependencies on concrete implementations or abstractions?
- Is dependency injection used where appropriate?
- Are there hidden coupling through global state, singletons, or shared mutable data?

**Coupling metrics (heuristics):**
- Fan-out > 7: high coupling, module knows too much
- Fan-in > 10: high centrality, changes here break many things
- Concrete dependency on implementation detail: tight coupling
- Dependency on interface/protocol/ABC: loose coupling

**Hidden coupling sources:**
- Global variables / module-level mutable state
- Singletons without injection point
- Shared database tables accessed by multiple modules directly
- Event buses without clear contracts
- Environment variables read deep inside modules (not at boundaries)

**Severity guide:**
- CRITICAL: Global mutable state shared across modules without synchronization
- WARNING: Fan-out > 10 in a single module
- WARNING: Direct implementation dependency where interface would be cleaner
- SUGGESTION: Could use DI to reduce coupling

---

## Section 4: Layer Separation

**What to check:**
- Are layers clearly defined (presentation, business logic, data access)?
- Does each layer only communicate with adjacent layers?
- Is business logic free of presentation/transport concerns?
- Is data access isolated from business rules?
- Are cross-cutting concerns (logging, auth, metrics) handled without polluting layers?

**Common layer violations:**
- HTTP request/response objects in service layer
- SQL queries in router/controller
- Business rules in database triggers or stored procedures
- UI formatting logic in data models
- Framework-specific types leaking across layer boundaries

**Clean layer patterns:**
- Router: deserialize → call service → serialize (zero logic)
- Service: pure business logic, receives typed inputs, returns typed outputs
- Repository/DAL: data access only, returns domain objects
- Cross-cutting: middleware, decorators, aspect-oriented patterns

**Severity guide:**
- CRITICAL: Business logic in router/controller (> 10 LOC of logic)
- WARNING: Data access in service layer (queries outside repository)
- WARNING: Transport types (Request, Response) in domain layer
- SUGGESTION: Could extract cross-cutting concern into middleware

---

## Section 5: Pattern Consistency

**What to check:**
- Is the same pattern used for the same type of problem across the codebase?
- Error handling: same approach in all modules?
- Logging: same library, same format, same levels?
- Validation: same approach (schema-first, decorator, manual)?
- Configuration: same access pattern (env vars, config object, DI)?
- Naming: consistent conventions across modules?

**Consistency dimensions:**
1. **Error handling:** exception types, catch patterns, error response format
2. **Logging:** logger instantiation, structured vs unstructured, levels usage
3. **Validation:** where it happens (boundary vs deep), how it reports
4. **Configuration:** access method, defaults handling, secrets separation
5. **Testing:** file naming, fixture patterns, assertion styles
6. **Async patterns:** callbacks vs promises vs async/await, mixed styles

**Severity guide:**
- CRITICAL: Security-relevant inconsistency (some endpoints validate, others don't)
- WARNING: 2+ different patterns for the same problem in same codebase
- WARNING: Newer code uses different pattern than older code (pattern drift)
- SUGGESTION: Minor naming inconsistencies

---

## Section 6: Error Architecture

**What to check:**
- Is there a coherent error hierarchy (base error → domain errors)?
- Are errors classified by severity/type?
- Is error information preserved through the stack (no swallowing)?
- Are errors translated at boundaries (internal → user-facing)?
- Are retry strategies consistent?
- Is there dead-letter / fallback handling for async operations?

**Good error architecture:**
- Base error class with code, message, HTTP status
- Domain-specific subclasses (NotFoundError, ValidationError, ConflictError)
- Catch specific exceptions, not bare except/catch
- Log with context (IDs, operation, input summary) before re-raise
- Translate at API boundary: internal error → user-safe response
- Retry with exponential backoff for transient failures

**Bad error architecture:**
- Bare `except Exception` without context or re-raise
- Error strings instead of typed errors
- Silent catch (catch and ignore)
- Leaking internal details to user (stack traces, SQL, paths)
- No retry strategy for network/IO operations
- Inconsistent HTTP status codes for same error type

**Severity guide:**
- CRITICAL: Silent error swallowing in critical path
- CRITICAL: Internal details leaked in error responses
- WARNING: Bare except without documented reason
- WARNING: No retry on transient failure for external calls
- SUGGESTION: Could add error codes for machine-readable errors

---

## Section 7: Data Flow & State Management

**What to check:**
- Is data transformation pipeline clear and traceable?
- Are there hidden state mutations?
- Is mutable shared state minimized?
- Are data boundaries clear (external → internal → storage)?
- Is there unnecessary data copying or transformation?

**Data flow checklist:**
- Input → Validate → Transform → Process → Persist → Respond
- Each step should be identifiable in the code
- Data shapes should be explicit (schemas, types, interfaces)
- Transformations should be pure where possible
- Side effects should be isolated and explicit

**State management red flags:**
- Global mutable state without locks
- Implicit state in module-level variables
- State split across multiple sources of truth
- Cache without invalidation strategy
- Session state without cleanup

**Severity guide:**
- CRITICAL: Mutable shared state causing race conditions
- CRITICAL: Multiple sources of truth for same data
- WARNING: Implicit state mutations (side effects in getters)
- SUGGESTION: Could make transformation more explicit

---

## Section 8: Scalability Design

**What to check:**
- Are there architectural bottlenecks (single point of failure)?
- Can the system scale horizontally (add more instances)?
- Are resources properly pooled (connections, threads)?
- Is work distributable (queue-based, event-driven)?
- Are there N+1 query patterns?

**Scalability patterns:**
- Connection pooling with health checks
- Queue-based async processing
- Batch operations instead of per-item
- Pagination for large datasets
- Caching with clear invalidation
- Stateless request handling (session in external store)

**Scalability anti-patterns:**
- In-process state that prevents horizontal scaling
- Unbounded queries (SELECT * without LIMIT)
- Sequential processing of independent items
- Synchronous calls to slow external services in request path
- No connection pool or pool exhaustion
- N+1 queries (loop of individual SELECTs)

**Severity guide:**
- CRITICAL: Unbounded query in production path
- CRITICAL: N+1 query pattern affecting response time
- WARNING: No connection pooling for database/external services
- WARNING: Synchronous blocking call in async context
- SUGGESTION: Could benefit from caching strategy

---

## Section 9: Testability Assessment

**What to check:**
- Can modules be tested in isolation (unit tests possible)?
- Is dependency injection used to enable test doubles?
- Are there interfaces/protocols/ABCs at module boundaries?
- Are side effects isolated and mockable?
- Is configuration injectable (not hardcoded)?

**Testability enablers:**
- Constructor/parameter injection for dependencies
- Interface-based boundaries (can substitute fakes)
- Pure functions where possible (deterministic, no side effects)
- Configuration as parameters, not global reads
- Lazy initialization (not import-time side effects)
- Clear separation of I/O from logic

**Testability blockers:**
- Hardcoded dependencies (import and use directly)
- Import-time side effects (database connections at module load)
- Global state that persists between tests
- Tight coupling to framework internals
- Hidden dependencies (function reads env vars internally)

**Severity guide:**
- CRITICAL: Import-time side effects preventing test isolation
- WARNING: Hardcoded dependency that blocks unit testing
- WARNING: No injection point for external service dependency
- SUGGESTION: Could extract interface for better testability

---

## Section 10: Evolution Readiness

**What to check:**
- Can new features be added without modifying core?
- Is the codebase open for extension, closed for modification?
- Are there intentional extension points (plugins, hooks, strategies)?
- Is there feature flag infrastructure?
- Can modules be replaced independently?
- Are boundaries aligned with likely change vectors?

**Evolution patterns:**
- Strategy pattern for swappable algorithms
- Plugin architecture for extensions
- Event-driven decoupling for cross-cutting features
- Feature flags for gradual rollout
- Interface-based boundaries at likely split points
- Versioned APIs for backward compatibility

**Evolution blockers:**
- Deep inheritance hierarchies (change at root cascades)
- Switch/if-else chains for type dispatch (add type = modify everywhere)
- Hardcoded integrations without abstraction layer
- No clear boundaries for future extraction
- Mixed concerns that prevent independent deployment

**Severity guide:**
- CRITICAL: Change in one module requires changes in 5+ others (shotgun surgery)
- WARNING: No extension mechanism for likely change area
- WARNING: Deep inheritance blocking modification
- SUGGESTION: Could add strategy pattern for anticipated variation point

---

## Section 11: Concurrency Architecture

**What to check:**
- Is shared mutable state protected (locks, atomics, immutable patterns)?
- Are async/await patterns correct (no missing awaits, no sync calls in async context)?
- Are connection pools configured and bounded (not leaking)?
- Is there a consistent lock ordering to prevent deadlocks?
- Are goroutines/tasks/threads properly lifecycle-managed (no fire-and-forget leaks)?
- Are timeouts propagated through all external calls?

**Race condition signals:**
- Global/module-level mutable dicts, lists, counters modified in async/threaded code without locks
- TOCTOU: `if exists(x): use(x)` — check and use separated by time
- GIL reliance: assuming Python's GIL protects multi-step operations (LOAD+INCR+STORE)
- SQLite without WAL mode in concurrent write scenarios
- Node.js: shared state modified across tick boundaries without guards

**Async correctness signals:**
- `time.sleep()` in async function (blocks event loop)
- Sync HTTP client (requests) called inside async handler
- Missing `await` on coroutine call (coroutine never executes)
- Fire-and-forget tasks with no error handling (`asyncio.create_task` without exception capture)
- `Promise` created but never awaited/caught in JS

**Connection pool signals:**
- No connection pool for database (new connection per request)
- Pool with no max size (unbounded growth)
- Pool with no `pre_ping` / health check (stale connections)
- Pool with no `recycle` setting (long-lived connections go stale)
- Connection obtained but not released in error paths

**Severity guide:**
- CRITICAL: Shared mutable state without synchronization in concurrent code
- CRITICAL: Sync blocking call in async request handler (blocks entire event loop)
- CRITICAL: Connection pool leak (connections not released on error path)
- WARNING: Missing `await` on coroutine (silent no-op)
- WARNING: Fire-and-forget task without error capture
- WARNING: No connection pool configuration (using defaults)
- WARNING: No timeouts on external service calls
- SUGGESTION: Could use immutable data structures to eliminate lock need
- SUGGESTION: Could add `go test -race` / thread sanitizer to CI

---

## Section 12: Observability Design

**What to check:**
- Is logging structured (JSON/key-value) or plain text?
- Are correlation/request IDs generated and propagated through request lifecycle?
- Is log level usage consistent (DEBUG/INFO/WARNING/ERROR used correctly)?
- Are business-critical operations instrumented with metrics?
- Are health check endpoints present and correct (liveness vs readiness)?
- Is sensitive data (PII, secrets) excluded from logs?

**Structured logging signals:**
- `print()`, `console.log()`, `fmt.Println()` in production code → unstructured
- No imports of structured logging libraries (structlog, winston, zap, zerolog)
- Log messages are plain strings with no key-value context
- No correlation ID in any log statement in HTTP handlers
- No middleware generating/propagating request ID

**Metrics signals (RED/USE methods):**
- RED (request-driven): Rate, Errors, Duration per endpoint — missing any of the three
- USE (resource-driven): Utilization, Saturation, Errors for DB pool, memory, CPU — no instrumentation
- No custom business metrics (orders processed, payments completed, queue depth)
- Metric labels have unbounded cardinality (user_id as label → metric explosion)

**Health check signals:**
- No `/health`, `/healthz`, or `/readyz` endpoints
- Single health endpoint that checks everything (should separate liveness from readiness)
- Health check that makes expensive calls (full DB query instead of simple ping)
- Health check returning 200 even when dependencies are down

**Log level consistency signals:**
- ERROR used for non-error conditions (expected 404, validation failure)
- WARNING never used (jump from INFO to ERROR)
- DEBUG left enabled in production (log volume explosion)
- Different modules use different log levels for same event type

**Severity guide:**
- CRITICAL: Secrets or PII in log output (passwords, tokens, credit cards)
- CRITICAL: No structured logging in production service with multiple instances
- WARNING: No correlation ID propagation across request lifecycle
- WARNING: No health check endpoints on service with external dependencies
- WARNING: Metrics with unbounded label cardinality
- WARNING: Inconsistent log level usage across modules
- SUGGESTION: Could add distributed tracing (OpenTelemetry)
- SUGGESTION: Could add readiness probe separate from liveness
