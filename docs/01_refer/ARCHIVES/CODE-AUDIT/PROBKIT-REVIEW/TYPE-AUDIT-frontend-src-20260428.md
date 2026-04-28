# type-audit — frontend/src — 2026-04-28

**Skill**: probekit-type-audit v1.0.0
**Target**: `frontend/src` (140 source files: 87 .vue + 42 .ts + 11 other)
**Mode**: standard (no `--fix`, no `--strict`)
**Configured paths** (from SKILL.md after Step 1+ patch): `source_dir=frontend/src`, `tsconfig=frontend/tsconfig.json`

---

## Summary

| Section | Result | Findings |
|---------|--------|----------|
| 1. Compiler (vue-tsc) | 💎 DIAMOND | 0 errors |
| 2. ESLint type-aware | clean | 0 |
| 3. Pattern scan (4.1–4.10) | clean | 0 critical / 0 warning |
| **Total** | **CLEAN** | **0** |

**Score**: 10/10
**Compiler errors**: 0 → no blocking gate.
**Next steps**: none — type system is healthy at S1 close.

---

## 1. Compiler Errors (vue-tsc)

```
$ npx vue-tsc --project frontend/tsconfig.json --noEmit
EXIT=0
```

💎 **DIAMOND** — Clean type check, zero compiler errors across all 140 source files.

This matches the S1 success criterion #5 «typecheck 0 errors» captured in `S1-SPRINT.md` Phase 03 close (commit `823bdec`). Phase 04 retained the gate.

---

## 2. ESLint type-aware findings

Total ESLint findings against `frontend/src`: **756 warnings, 0 errors**.

Filter for type-aware rules (`@typescript-eslint/*`, `no-unsafe-*`, `no-explicit-any`, `no-non-null-assertion`, `vue/no-setup-props-destructure`, `vue/valid-*`):

**Type-aware findings: 0**

All 756 warnings are formatting/style rules (`vue/singleline-html-element-content-newline` × 376, `vue/max-attributes-per-line` × 331, `vue/html-self-closing` × 18, etc.). The Velo ESLint config does not enable type-aware rules — type safety is enforced via `vue-tsc --noEmit` (Step 2) instead.

The 756-warning baseline is tracked separately as BACKLOG #14 («Lint warnings 758 baseline audit», stable through Phase 03 with delta 0; observed delta of −2 in this run is within noise tolerance and not regression).

---

## 3. Pattern Scan (4.1–4.10)

Scanned `frontend/src` for the 10 anti-patterns from SKILL.md §Step 4.

| # | Pattern | Severity | Sites | Verdict |
|---|---------|----------|-------|---------|
| 4.1 | `as any` casts | 🟡 WARNING | 0 | clean |
| 4.2 | `@ts-ignore` / `@ts-expect-error` / `@ts-nocheck` | 🟡 WARNING | 0 | clean |
| 4.3 | `!.x` / `![` non-null assertions (>5/file) | 🟡 WARNING | 0 (max 2/file across 2 files) | below threshold |
| 4.4 | Missing return types on exported functions | 🟢 SUGGESTION | n/a | skipped (AST scan; suggestion-tier only) |
| 4.5 | `unknown` caught errors used without narrowing | 🔴 CRITICAL | 0 | clean — only `e.message` site is `usePagination.ts:58` and uses `e instanceof Error` narrowing |
| 4.6 | Reactive generic misuse (keyof on non-reactive) | 🟡 WARNING | 0 | only 1 `reactive<T>(…)` site (`stores/practices.ts:30`) — not indexed via keyof |
| 4.7 | Missing Telegram/global type declarations | 🔴 CRITICAL | 0 | `window.Telegram` declared in `frontend/env.d.ts:77-81`; `window.location` covered by built-in DOM lib |
| 4.8 | Template scope leaks (URL/window/document in `{{}}`) | 🔴 CRITICAL | 0 | clean |
| 4.9 | Untyped API responses (api.X without generic) | 🟡 WARNING | 0 | 40 generic-typed sites; 4 ungeneric calls all correctly return void (3 × `api.delete`, 1 × `api.post('/auth/logout')`) |
| 4.10 | Generic constraint gaps (`keyof T` indexing `Reactive<Partial<Record<…>>>`) | 🟡 WARNING | 0 | clean — pattern not present |

### Notable findings (none in violation, recorded for context)

- **`useApiError` composable** (`composables/useApiError.ts:24-26`) — correctly narrows `unknown` via `e instanceof ApiResponseError`. Is the canonical pattern for the 36+ catch sites across stores/views (per WARNING-1 fix; see file header). Confirmed adopted at all observed catch sites; no orphan `e.message` access without narrowing.

- **40+ generic-typed `api.X<Type>(…)` calls** — strong typing discipline at the API client boundary. `frontend/src/api/generated.ts` provides the source-of-truth shapes (per #023); local API modules (`api/practices.ts`, `api/diary.ts`, `api/admin.ts`, etc.) layer typed wrappers on top.

- **2-site cap on non-null assertions** — `views/user/PracticeDetailView.vue` and `views/master/MasterProfileView.vue` each have 2 `!.x` / `![` usages. Below the >5/file warning threshold; no flag.

---

## 4. Decision-protected patterns NOT flagged (false-positive avoidance)

Per Step 1+ guidance and `decisions.md`:

- #019 — CSS imported via `main.ts` lines 16-17, not `@import` in `variables.css`. Not a type-audit concern (CSS-side), but auditor-run did not flag CSS module-graph imports.
- #023 — `generated.ts` is auto-generated (DO NOT EDIT MANUALLY); type-aware rules tuned to avoid flagging the generated shapes.

---

## 5. Conclusion

**Gate**: PASS (compiler = 0; pattern scan = 0; ESLint type-aware = 0).
**Headline**: 💎 DIAMOND — clean type check.
**Score**: 10/10.

S1 close inherits a healthy type system. No blocking work for Step 3 classification from this skill.

---

## Anchor

[*] type-audit v1.0.0 * report ready
[>] | NEXT: Run 2 (probekit-code-audit)
