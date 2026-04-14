---
name: inter-skill-context
description: "Protocol for passing structured context between pipeline stages"
---

# Inter-Skill Context Protocol

After each stage, build a structured context object to pass to the next stage.
This replaces generic text strings with actionable data.

**Context structure** (mental model — not JSON, just organized passing):
```
source_skill: {skill that just ran}
result: { score: X/10, gate: PASS/WARN/FAIL }
severity_counts: { critical: N, warning: N, suggestion: N, diamond: N }
hotspots: [ { file, reason, finding_count, priority: HIGH/MEDIUM } ]
findings_for_next: [
  { severity, file, line, function, title, test_hint }
]
recommendations: [ "free-text guidance for next skill" ]
```

**What each stage passes forward:**

| From -> To | Key context passed |
|-----------|-------------------|
| arch-review -> arch-review-bogame | Hotspot modules, structural violations, dependency issues |
| arch-review(s) -> code-audit | Files with arch violations to check at code level |
| code-audit -> code-audit-bogame | All findings with file:line, security for governance check, error handling for resilience |
| code-audit-bogame -> security-audit | BOGame identity/governance findings for deeper security validation |
| code-audit-bogame -> unit-test | BOGame-specific findings + test scenarios (e.g., "DAL-01: test dual-backend switching") |
| code-audit -> unit-test | Findings with file:line:function + specific test scenarios to generate |
| code-audit -> integration-test | Uncovered findings needing real DB/API, boundary functions |
| unit-test -> integration-test | Functions with low coverage at service boundaries |
| integration-test -> e2e-bdd-test | User flows with failures, unhappy paths not covered |
| code-audit -> security-audit | Security findings (Section 4) for deeper validation, auth-related files |
| security-audit -> unit-test | Vulnerability findings needing regression tests (SQL injection inputs, etc.) |
| dependency-audit -> (independent) | Reads manifests independently, no upstream context needed |
| e2e-bdd-test -> perf-test | Critical user journeys, endpoints with N+1 findings |

**Rules:**
- Only pass CRITICAL + WARNING findings forward (not SUGGESTION)
- Each recommendation must be actionable: include file path, function name, what to check/test
- Downstream skill reports coverage: "Covered N of M findings from code-audit context"
