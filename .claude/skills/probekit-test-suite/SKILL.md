---
name: probekit-test-suite
description: "Orchestrate the full testing pipeline: probekit-arch-review → probekit-arch-review-bogame → probekit-code-audit → probekit-security-audit → probekit-dependency-audit → probekit-unit-test → probekit-integration-test → probekit-e2e-bdd-test → probekit-perf-test. Runs skills in sequence, passes findings forward, produces a unified SUITE-REPORT. Use when: 'run full test suite', 'test everything', 'quality check', '/probekit-test-suite', 'проведи тесты', 'запусти тесты', 'тестируй всё', 'комплексное тестирование', 'полная проверка', or when comprehensive testing is needed, 'пробкит всё', 'пробкит полный', 'пробкит запусти'. Modes: full (all 9 stages), quick (code-audit + unit), quality (code-audit + unit + integration), arch (arch-review + arch-review-bogame only), deep (arch + code-audit + security + unit + integration), secure (code-audit + security-audit + dependency-audit)."
---

# test-suite v2.3.0

Testing pipeline orchestrator for Claude Code.
Runs testing skills in logical sequence, gates on quality, aggregates results into a single report.

## Configuration

report_dir: docs/02_milestones/ADR/review

## Pipeline

```
arch-review → arch-review-bogame → code-audit → security-audit → dependency-audit → unit-test → integration-test → e2e-bdd-test → perf-test
    ↓              ↓                  ↓              ↓                ↓               ↓             ↓                ↓              ↓
 Score/10       Score/10          Score/10        OWASP/CWE      Pinning/10       Tests + %      Tests + %       Scenarios      Metrics
    ↓              ↓                  ↓              ↓                ↓               ↓             ↓                ↓              ↓
    └──────────────┴──────────────────┴──────────────┴────────────────┴───────────────┴─────────────┴────────────────┴──────────────┘
                                                                      ↓
                                                         SUITE-REPORT-<target>-<date>.md
```

## Modes

| Mode | Stages | When to use |
|------|--------|-------------|
| `full` | All 9 | Pre-release, milestone close, comprehensive check |
| `quick` | code-audit + unit-test | Fast feedback during development |
| `quality` | code-audit + unit-test + integration-test | Thorough without E2E/perf overhead |
| `arch` | arch-review + arch-review-bogame | Architecture-only analysis |
| `deep` | arch + code-audit + security + unit + integration | Architecture + code + security + tests |
| `secure` | code-audit + security-audit + dependency-audit | Security-focused review |

Default: `quality` (if user doesn't specify mode)

## Language Routing

| Target files | Unit test skill | Other skills |
|-------------|----------------|--------------|
| `.py` files | probekit-unit-test (pytest) | All standard |
| `.gd` files | probekit-godot-unit-test (GUT) | Skip probekit-integration-test, probekit-e2e-bdd-test, probekit-perf-test |
| `.js/.ts` files | probekit-unit-test (Jest/Vitest) | All standard |
| Mixed | probekit-unit-test for .py/.js, probekit-godot-unit-test for .gd | Run applicable stages |

## Unified Quality Gate Contract

Every stage produces a gate result:
```
Gate: PASS / WARN / FAIL
Score: X.X/10
Blocking: true/false
```

| Stage | PASS | WARN | FAIL | Blocking? |
|-------|------|------|------|-----------|
| arch-review | ≥ 5.0/10, 0 🔴 | 3.0–4.9 | < 3.0 or systemic 🔴 | No |
| arch-review-bogame | ≥ 5.0/10, 0 🔴 in L0/L1/L2 | 3.0–4.9 | < 3.0 or layer/security 🔴 | No |
| code-audit | ≥ 7/10, 0 🔴 | 4–6 | < 4 | **Yes** |
| unit-test | all pass, cov ≥ 60% | all pass, cov < 60% | any failure | No |
| integration-test | all pass | all pass, error path gaps | any 🔴 failure | No |
| e2e-bdd-test | all pass | all pass, minor issues | any 🔴 failure | No |
| perf-test | thresholds met | p99 warn range | p95/p99 exceeded or err > 1% | No |
| security-audit | 0 🔴, score ≥ 7 | 1-2 🔴, score 4-6 | 3+ 🔴 or secrets found | No |
| dependency-audit | pinning ≥ 8/10, 0 suspicious | pinning 5-7, warnings | unpinned deps or typosquat | No |
| godot-unit-test | all pass, cov ≥ 60% | all pass, cov < 60% | any failure | No |

**Pipeline stops** only when a **Blocking** stage FAILs (code-audit < 4/10).
Non-blocking FAIL: continue, flag in SUITE-REPORT.

## Execution Steps

**Step 1 — Parse input, load config, select mode**

Input formats:
- `/test-suite src/api/` — quality mode on directory
- `/test-suite --full framework/services/` — full mode on directory
- `/test-suite --quick framework/llm/adapter.py` — quick mode on file
- `/test-suite --arch framework/` — architecture review only
- `/test-suite --deep framework/services/` — arch + code + tests
- `/test-suite` (no path) — ask user what to test

**Config loading** (check in order, merge top-down):
1. CLI flags (highest priority)
2. `.probekit.yml` in current directory
3. `.probekit.yml` in git root
4. Defaults in this SKILL.md (lowest priority)

If `.probekit.yml` found, read these sections:
- `paths.review_dir` → override `report_dir`
- `thresholds` → override quality gate thresholds per skill
- `exclude.paths` → skip these paths from analysis
- `features.skills` → enable/disable specific pipeline stages
- `scoring.weights` → override scoring formula weights

If `.probekit.yml` not found → use defaults. Do NOT require it.

Detect target language from file extensions. Select unit test skill accordingly.

**Step 2 — Stage 1: Architecture Review (general)**

_Skip if mode is `quick` or `quality`._

Invoke `probekit-arch-review` on the target path.
Record: {Gate, Score, Blocking, findings_summary}.
Build structured context for next stage (see Inter-Skill Context below).

**Step 3 — Stage 2: Architecture Review (BOGame-specific)**

_Skip if mode is `quick` or `quality`._

Invoke `probekit-arch-review-bogame` on the target path.
Pass structured context from Step 2:
- Hotspot files (files with 🔴/🟡 findings)
- Specific findings with file:line for cross-reference
- Recommendations: "Check these specific patterns in project context"
Record: {Gate, Score, Blocking, findings_summary}.

If mode is `arch` → skip to Step 9 (report).

**Step 4 — Stage 3: Code Audit**

Invoke `probekit-code-audit` on the target path.
Pass structured context from arch stages (if ran):
- Hotspot files to prioritize review
- Architecture violations to check at code level (e.g., "AR-DEP-03 found circular dep in src/api/ — check for coupling antipatterns")
- Recommendations for code-level verification
Record: {Gate, Score, Blocking, findings_summary}.

**Blocking gate check:**
- If code-audit Gate = FAIL → **STOP pipeline**. Report: "Code quality too low (score X/10). Fix 🔴 CRITICAL findings first." Do NOT proceed to test generation.

**Step 4.5 — Stage 3.5: Security Audit**

_Skip if mode is `quick`, `quality`, or `arch`._

Invoke `probekit-security-audit` on the target path.
Pass structured context from code-audit:
- Security findings (Section 4) to validate deeper
- Files with auth-related code for auth/authz matrix
Record: {Gate, Score, Blocking, findings_summary}.

If mode is `secure` → also run Step 4.7, then skip to Step 9.

**Step 4.7 — Stage 3.7: Dependency Audit**

_Skip if mode is `quick`, `quality`, or `arch`._

Invoke `probekit-dependency-audit` on the target path.
No context needed from previous stages — reads manifest files independently.
Record: {Gate, Score, Blocking, findings_summary}.

**Step 5 — Stage 4: Unit Tests**

Invoke `probekit-unit-test` (or `probekit-godot-unit-test` for .gd files) on the target.
Pass structured context from code-audit:
- Findings with file:line:function — generate tests for these functions first
- Specific test scenarios: e.g., "CA-SEC-04 at users.py:42 → test with SQL injection input"
- Complexity hotspots to prioritize for coverage
Record: {Gate, Score, Blocking, findings_summary}.

If mode is `quick` → skip to Step 9 (report).

**Step 6 — Stage 5: Integration Tests**

Invoke `probekit-integration-test` on the target.
Pass structured context from code-audit + unit-test:
- Uncovered findings from code-audit that unit-test couldn't reach (need real DB/API)
- Integration boundaries from arch-review (service ↔ DB, service ↔ external API)
- Functions with low unit coverage at service boundaries
Record: {Gate, Score, Blocking, findings_summary}.

If mode is `quality` or `deep` → skip to Step 9 (report).

**Step 7 — Stage 6: E2E/BDD Tests**

Invoke `probekit-e2e-bdd-test` on the target.
Skip if target is a single utility function or has no user-facing endpoints.
Pass structured context:
- User-facing flows with failures in integration tests
- Security findings that need end-to-end validation
Record: {Gate, Score, Blocking, findings_summary}.

**Step 8 — Stage 7: Performance Tests**

Invoke `probekit-perf-test` on the target.
Skip if no HTTP endpoints detected.
Use `smoke` profile for first run; user can request `load`/`stress`/`spike`/`soak`.
Pass structured context:
- Endpoints flagged with N+1 or performance findings from code-audit
- Complexity hotspots from earlier stages
Record: {Gate, Score, Blocking, findings_summary}.

**Step 9 — Produce SUITE-REPORT**

Aggregate all stage results:

```markdown
# SUITE-REPORT — <target> — <date>

## Pipeline Summary

| Stage | Gate | Score | Key Metric | 🔴 | 🟡 | 🟢 | 💎 |
|-------|------|-------|------------|-----|-----|-----|-----|
| Arch Review | PASS/WARN/FAIL/SKIP | X.X/10 | weighted avg | N | N | N | N |
| Arch Review (BOGame) | PASS/WARN/FAIL/SKIP | X.X/10 | proj score | N | N | N | N |
| Code Audit | PASS/WARN/FAIL | X/10 | score | N | N | N | N |
| Security Audit | PASS/WARN/FAIL/SKIP | X/10 | OWASP/secrets | N | N | N | N |
| Dependency Audit | PASS/WARN/FAIL/SKIP | X/10 | pinning/typo | N | N | N | N |
| Unit Tests | PASS/WARN/FAIL | X/10 | N tests, X% cov | N | N | N | N |
| Integration Tests | PASS/WARN/FAIL/SKIP | X/10 | N pass/total | N | N | N | N |
| E2E Tests | PASS/WARN/FAIL/SKIP | X/10 | N scenarios | N | N | N | N |
| Performance | PASS/WARN/FAIL/SKIP | gate | p95/RPS/err | N | N | N | N |

## Overall Quality Gate: PASS / WARN / FAIL

## Architecture Health (if arch stages ran)
[Combined arch findings: top 3 structural issues + top 3 project deviations]

## Code Quality Summary
[Top findings from code-audit]

## Test Coverage Summary
[Pass/fail counts, coverage %, gaps identified]

## 💎 Diamond Patterns Found
[Exceptional patterns discovered across all stages]

## Top Recommendations
[Top 5 actions prioritized by impact across all stages]
```

Save to `{{report_dir}}/SUITE-REPORT-<target>-<YYYYMMDD>.md`
After saving, output brief summary in chat.

**Step 10 — Update audit tracker**

Update `{{report_dir}}/AUDIT-TRACKER.md` with unified format:
| YYYY-MM-DD | test-suite | <target> | combined | N | N | N | N | mode: X stages | new/delta |

## Overall Quality Score

Algorithmic score replaces subjective assessment. Show the calculation in the report.

**Formula:**
```
total_critical = sum of 🔴 across all stages
total_warning  = sum of 🟡 across all stages
total_suggestion = sum of 🟢 across all stages
total_diamond  = sum of 💎 across all stages

deductions = (total_critical × 1.5) + (total_warning × 0.5) + (total_suggestion × 0.1)
diamond_bonus = min(total_diamond × 0.1, 0.5)

raw_score = 10.0 - deductions + diamond_bonus
final_score = max(1, min(10, round(raw_score × 2) / 2))   # round to 0.5, floor 1, ceiling 10
```

Default weights (overridable via `.probekit.yml` → `scoring.weights`):
- `critical`: 1.5 | `warning`: 0.5 | `suggestion`: 0.1 | `diamond`: 0.1 (max 0.5)

**Show in report:**
```
## Overall Quality Score: X.X/10

Calculation: 10.0 - (N×1.5) - (N×0.5) - (N×0.1) + diamond(N×0.1) = X.X → X.X/10
```

## Overall Quality Gate

The suite **PASSES** when:
- All blocking stages pass (code-audit ≥ 4/10)
- No unaddressed 🔴 CRITICAL findings across all stages
- Architecture scores ≥ 3.0/10 (if arch stages ran)

The suite **WARNS** when:
- Architecture score 3.0–4.9/10
- Code audit score 4–6/10
- Non-blocking stages have FAIL gate

The suite **FAILS** when:
- Code audit score < 4/10 (pipeline stopped)
- Any blocking stage has FAIL gate

## Skills NOT in Pipeline

| Skill | Reason |
|-------|--------|
| livemockup-studio | UI prototyping, not testing |
| simplify | Code quality improvement, not testing |

## Inter-Skill Context Protocol

After each stage, build a structured context object to pass to the next stage.
This replaces generic text strings with actionable data.

**Context structure** (mental model — not JSON, just organized passing):
```
source_skill: <skill that just ran>
result: { score: X/10, gate: PASS/WARN/FAIL }
severity_counts: { critical: N, warning: N, suggestion: N, diamond: N }
hotspots: [ { file, reason, finding_count, priority: HIGH/MEDIUM } ]
findings_for_next: [
  { severity, file, line, function, title, test_hint }
]
recommendations: [ "free-text guidance for next skill" ]
```

**What each stage passes forward:**

| From → To | Key context passed |
|-----------|-------------------|
| arch-review → arch-review-bogame | Hotspot modules, structural violations, dependency issues |
| arch-review(s) → code-audit | Files with arch violations to check at code level |
| code-audit → unit-test | Findings with file:line:function + specific test scenarios to generate |
| code-audit → integration-test | Uncovered findings needing real DB/API, boundary functions |
| unit-test → integration-test | Functions with low coverage at service boundaries |
| integration-test → e2e-bdd-test | User flows with failures, unhappy paths not covered |
| code-audit → security-audit | Security findings (Section 4) for deeper validation, auth-related files |
| security-audit → unit-test | Vulnerability findings needing regression tests (SQL injection inputs, etc.) |
| dependency-audit → (independent) | Reads manifests independently, no upstream context needed |
| e2e-bdd-test → perf-test | Critical user journeys, endpoints with N+1 findings |

**Rules:**
- Only pass 🔴 + 🟡 findings forward (not 🟢 SUGGESTION)
- Each recommendation must be actionable: include file path, function name, what to check/test
- Downstream skill reports coverage: "Covered N of M findings from code-audit context"

## Quick Reference

Invoke:
- `/test-suite <path>` — quality mode (default)
- `/test-suite --full <path>` — all 9 stages
- `/test-suite --quick <path>` — code-audit + unit-test
- `/test-suite --arch <path>` — architecture only
- `/test-suite --deep <path>` — arch + code + security + unit + integration
- `/test-suite --secure <path>` — code-audit + security-audit + dependency-audit
