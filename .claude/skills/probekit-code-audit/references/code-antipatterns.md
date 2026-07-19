# Code Anti-Patterns Catalog

Reference catalog for code-audit. Flag when found during analysis.

## AP-01: God Class / God Module
- Class/module with >1000 LOC, >15 public functions, or >10 direct dependents
- Name is vague ("utils", "helpers", "common", "misc")
- **Severity:** 🟡 WARNING (🔴 CRITICAL if in critical path)
- **Fix:** Split by responsibility, extract focused modules

## AP-02: Hallucinated Dependency
- Import in code that doesn't exist in package manifest (requirements.txt, package.json, go.mod)
- Dependency >2 years without update (staleness risk)
- Name similar to popular package but slightly different (slopsquatting)
- **Severity:** 🔴 CRITICAL
- **Fix:** Verify in registry, pin version, remove if phantom

## AP-03: Copy-Paste Inheritance
- Multiple classes/components with near-identical structure
- Same boilerplate repeated with minor variations
- **Severity:** 🟡 WARNING
- **Fix:** Extract base class, use composition, or template pattern

## AP-04: Prompt Residue
- TODOs that are generic AI-generated placeholders ("TODO: implement this")
- Docstrings that describe what the function should do but don't match implementation
- Template code that was never customized
- **Severity:** 🟢 SUGGESTION (🟡 WARNING if in security-sensitive path)
- **Fix:** Remove or replace with real implementation

## AP-05: Phantom Code
- Functions defined but never called from anywhere
- Classes instantiated nowhere in the codebase
- Dead imports, unreachable branches
- **Severity:** 🟢 SUGGESTION (🟡 WARNING if >100 LOC of dead code)
- **Fix:** Delete. If needed later, git has history.

## AP-06: Over-Engineering (Gas Factory)
- Abstract factory for single implementation
- Strategy pattern with one strategy
- Plugin system for non-extensible feature
- Multiple layers of indirection without benefit
- **Severity:** 🟡 WARNING
- **Fix:** YAGNI — inline single implementations, remove premature abstraction

## AP-07: Leaky Abstraction
- Internal implementation details exposed in public API
- Database column names in API responses
- Framework-specific types in domain layer
- ORM models returned directly from endpoints
- **Severity:** 🟡 WARNING (🔴 CRITICAL if security-sensitive internals)
- **Fix:** DTOs at boundaries, map internal to external representation

## AP-08: Mixed Paradigms Without Coherence
- Functional and OOP mixed without clear convention
- Callbacks, promises, and async/await in same module
- Some modules use dataclasses, others use raw dicts
- **Severity:** 🟡 WARNING
- **Fix:** Choose paradigm per module/layer, document convention

## AP-09: Silent Exception Swallowing
- `except Exception: pass` or `catch(e) {}` with no logging
- Error caught, logged, but not re-raised and no fallback
- Generic catch hiding specific failures
- **Severity:** 🟡 WARNING minimum (🔴 CRITICAL in critical path)
- **Fix:** Catch specific, log with context, re-raise or return error

## AP-10: Hardcoded Secrets
- API keys, passwords, tokens in source code
- Credentials in config files committed to git
- Sensitive data in log messages
- **Severity:** 🔴 CRITICAL (always)
- **Fix:** Environment variables, secrets manager, .env with .gitignore

## AP-11: Inconsistent Validation
- Some endpoints validate input, others don't
- Validation at wrong layer (deep inside service instead of at boundary)
- Different validation libraries/approaches across modules
- **Severity:** 🟡 WARNING (🔴 CRITICAL if security-relevant)
- **Fix:** Validate at boundary, consistent approach, schema-first

## AP-12: N+1 Query Pattern
- Loop that makes individual DB/API call per item
- List endpoint that loads related data one-by-one
- **Severity:** 🟡 WARNING (🔴 CRITICAL if in production hot path)
- **Fix:** Batch query, JOIN, eager loading, or preload

## AP-13: Truthy fallback for nullable config
- Pattern: `value = CONFIG || "default"` (JS/TS) or `value = cfg or "default"` (Python) applied to nullable config, secrets, or env-vars.
- Problem: truthy-check fires on empty string `""`, zero `0`, empty array, `False` — NOT just `null`/`undefined`/`None`. Intent is usually "use default only if unset", reality is "use default if unset OR falsy". Most painful when build-time env-var substitution emits `""` (deliberate empty value) and the fallback silently bakes a dev-only URL / sentinel into the artifact.
- Detection signal:

```grep-check
pattern: import\.meta\.env\.\w+\s*\|\|
files: "**/*.{ts,tsx,js,jsx}"
positive-should-match: true
negative-should-match: false
```

- Ancillary signals (not covered by the primary grep-check):
  - Python: `os.environ.get("X") or`, `config.get("x") or` for string values that legitimately can be empty.
  - Vite `.env.production` or similar with intentional empty `VAR=` followed by `VAR \|\| "fallback"` consumption.
- **Severity:** 🟡 WARNING (🔴 CRITICAL if the "truthy fallback" bakes a dev URL, secret placeholder, or sentinel into a production artifact — silently visible only at runtime).
- **Fix:** Replace with nullish-only check — `??` in JS/TS, `if x is None else default` in Python. Keep `\|\|` / `or` only when all falsy values genuinely should trigger the fallback (rare for config).
- **Canonical case study:** BOGame P79 C350 — `frontend-web/src/api/client.ts` used `import.meta.env.VITE_API_URL \|\| "http://localhost:8001"`. Setting `VITE_API_URL=` in `.env.production` produced empty string, which is falsy, so Vite baked the dev URL into the production bundle. Fix: one-character change to `??`. ~4 hours lost to the wrong smoke-test path.

## AP-15: Lazy-import-inside-method wrapped in try/except — silent ImportError in prod
- Pattern: `def method(self): ... try: from <wrong.path> import X ... except Exception as e: logger.error(...); return False`.
- Problem: the import is **lazy** (inside the method body, not at module top) so it isn't validated at import time. It's also wrapped in a broad `try/except` that logs-and-returns-False. An `ImportError` (typo'd module path, refactor-induced stale reference, packaging change) becomes a silent WARN/ERROR log in prod instead of either a startup failure or a surfaced error response. The service appears "healthy" (container Up, other endpoints serving) while the affected feature is completely non-functional.
- Detection signal:

```regex-check
pattern: try:\s*\n\s+from\s+\S+\s+import\s+\S+\s*\n\s*except\s+(?:Exception|ImportError)
files: "framework/**/*.py"
positive-should-match: true
negative-should-match: false
```

- Ancillary signals (broader triage, not the primary invariant):
  - `grep -rn "^\s\+from\s\+\w\+\." framework/ --include="*.py"` — non-top-level imports that aren't inside `TYPE_CHECKING` or clearly-conditional-feature blocks.
  - Top-level `from X import Y` coexisting with lazy `from X.sub import Z` inside methods — hints at stale legacy paths that module-level linters miss.
- **Severity:** 🔴 CRITICAL when the affected feature is user-facing OR security-relevant. 🟡 WARNING for internal-only features with redundant paths.
- **Fix:**
  - Move the import to module top level wherever possible. Lazy imports are justified only for genuine circular-import mitigation or truly optional dependencies — not as a stylistic default.
  - When a lazy import is unavoidable, the except branch MUST re-raise OR surface via `/health/deep`-style probe — never "log and return False" without observability.
  - Add a class-wide grep regression test (see `probekit-unit-test` test-generation.md § Protective Regression Test Pattern, Variant 2) to catch recurrence of the bare-path form.
- **Canonical case study:** BOGame C384 — `framework/services/telegram/telegram_service.py:53,138` used `from services.telegram.handlers import router` (bare; correct form is `framework.services.telegram.handlers`). Wrapped in `try: ... except Exception as e: logger.error(...): return False`. Bot's `initialize()` returned False silently; container reported `Up (healthy)` via `/health/live`. Bot offline in production for ~7 weeks (entire S14 sprint) before surfacing via audit scout. 13 sites across 5 files in the `framework/services/` tree shared the same pattern; all used lazy imports + broad try/except. See also `probekit-deploy-readiness-bogame` Probe 9 (health probe depth) which pairs the detection at deploy-audit time.

## AP-14: Web form missing `autoComplete` attrs on admin / config surfaces
- Pattern: admin/settings/config form contains a password or secret `<input type="password">` adjacent to plain `<input type="text">` fields, with no explicit `autoComplete` attribute tree.
- Problem: Chrome (and other browsers) pattern-match the form as a login form and inject saved credentials into the first text input. User sees unexpected value ("admin" or a saved username appearing in a text field with no code path populating it) and reports it as data corruption. It is not — it is autofill pollution. No actual backend data is wrong.
- Detection signal:

```regex-check
pattern: <input[^>]*type=["']password["'](?![^>]*autoComplete)
files: "**/*.{tsx,jsx,html}"
positive-should-match: true
negative-should-match: false
```

- Ancillary signals:
  - Form with a single `<input type="password">` followed by text fields intended for config values (chat IDs, API base URLs, operator names).
  - No `<form autoComplete="off">` wrapper and no per-input `autoComplete` on admin/settings pages.
- **Severity:** 🟡 WARNING (information-display bug; user-reported as data corruption; time-to-diagnose is the real cost).
- **Fix:**
  - Password/secret inputs: `autoComplete="new-password"` (hints browser "this is not a login").
  - Plain text config inputs: `autoComplete="off"`.
  - Form wrapper: `<form autoComplete="off">` as belt-and-braces.
  - For truly secret fields that should NEVER be autofilled, combine `autoComplete="new-password"` with `data-lpignore="true"` to cover password-manager extensions.
- **Canonical case study:** BOGame P79 C350 admin walkthrough — `AdminSettings.tsx` showed `admin` in the Nikita chat ID text field. Initial hypothesis was "login saved wrong value into DB". Reality: Chrome autofill treated password+text layout as a login form and injected saved username. Zero data corruption, pure UX artifact. Filed as UX-BACKLOG-S14-40 before root cause understood.
