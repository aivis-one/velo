---
name: scoring-formula
description: "Overall quality score formula and quality gate rules"
---

# Overall Quality Score

Algorithmic score replaces subjective assessment. Show the calculation in the report.

**Formula:**
```
total_critical = sum of CRITICAL across all stages
total_warning  = sum of WARNING across all stages
total_suggestion = sum of SUGGESTION across all stages
total_diamond  = sum of DIAMOND across all stages

deductions = (total_critical x 1.5) + (total_warning x 0.5) + (total_suggestion x 0.1)
diamond_bonus = min(total_diamond x 0.1, 0.5)

raw_score = 10.0 - deductions + diamond_bonus
final_score = max(1, min(10, round(raw_score x 2) / 2))   # round to 0.5, floor 1, ceiling 10
```

Default weights (overridable via `.probekit.yml` -> `scoring.weights`):
- `critical`: 1.5 | `warning`: 0.5 | `suggestion`: 0.1 | `diamond`: 0.1 (max 0.5)

**Show in report:**
```
## Overall Quality Score: X.X/10

Calculation: 10.0 - (Nx1.5) - (Nx0.5) - (Nx0.1) + diamond(Nx0.1) = X.X -> X.X/10
```

# Overall Quality Gate

The suite **PASSES** when:
- All blocking stages pass (code-audit >= 4/10)
- No unaddressed CRITICAL findings across all stages
- Architecture scores >= 3.0/10 (if arch stages ran)

The suite **WARNS** when:
- Architecture score 3.0-4.9/10
- Code audit score 4-6/10
- Non-blocking stages have FAIL gate

The suite **FAILS** when:
- Code audit score < 4/10 (pipeline stopped)
- Any blocking stage has FAIL gate
