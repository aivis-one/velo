# Mutation Testing Reference

Mutation testing measures test quality by introducing small code changes (mutants)
and checking if tests detect them. A surviving mutant = a test gap.

This is a RECOMMENDATION in reports, not a mandatory step (mutation testing is slow).

## Mutation Operators

| Operator | What it does | Example |
|----------|-------------|---------|
| Arithmetic (AOR) | `+` → `-`, `*` → `/` | `price * rate` → `price / rate` |
| Relational (ROR) | `>` → `>=`, `==` → `!=` | `age >= 18` → `age > 18` |
| Logical (LOR) | `and` → `or`, `not` → remove | `a and b` → `a or b` |
| Boundary (BCR) | Off-by-one shifts | `> 90` → `>= 90` |
| Return Value (RVR) | `return x` → `return None/0/False` | `return total` → `return 0` |
| Void Method (VMR) | Delete entire method call | `logger.info(msg)` → (removed) |
| Exception (EMR) | Remove throw/raise | `raise ValueError()` → (removed) |
| Constant (CMR) | `0` → `1`, `""` → `"x"`, `True` → `False` | `timeout=30` → `timeout=31` |
| Negation (NMR) | Negate condition | `if valid:` → `if not valid:` |

## Thresholds

| Mutation Score | Status | Meaning |
|---------------|--------|---------|
| > 80% | PASS | Tests effectively catch most code changes |
| 60–80% | WARN | Notable gaps — surviving mutants in business logic |
| < 60% | FAIL | Tests provide false confidence — many mutants survive |

## Surviving Mutants — Decision Tree

When a mutant survives, evaluate:

```
Is the mutated code reachable in production?
  NO → Equivalent mutant (ignore)
  YES ↓
Is the mutation in a critical path (auth, payment, data)?
  YES → Missing test (high priority)
  NO  ↓
Does the mutation change observable behavior?
  YES → Missing test (normal priority)
  NO  → Equivalent mutant (ignore)
```

## Tools

### Python — mutmut
```bash
pip install mutmut
mutmut run --paths-to-mutate=src/  # run against entire src
mutmut results                       # show surviving mutants
mutmut show <id>                     # inspect specific mutant
```

### JS/TS — Stryker
```bash
npx stryker init       # setup
npx stryker run         # run mutations
# Results in reports/mutation/html
```

### Go — go-mutesting
```bash
go install github.com/zimmski/go-mutesting/cmd/go-mutesting@latest
go-mutesting ./...
```

## When to Recommend

Recommend mutation testing in the report when:
- Line/branch coverage is high (>80%) but tests feel shallow
- Critical business logic has only happy-path tests
- Test suite passes but bugs keep appearing in the same module

Do NOT recommend when:
- No tests exist yet (generate tests first)
- Coverage is already low (<50%) — fix coverage before mutation
- Project is a prototype or one-off script
