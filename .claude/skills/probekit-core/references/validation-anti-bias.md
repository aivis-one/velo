---
name: validation-anti-bias
description: "Family-wide anti-bias rules for audit conclusions: firsthand reads, prove-zero, narrow-grep false-negatives, stale-carry reconciliation. Every probekit audit skill applies these before lowering a severity or asserting absence."
---

# Validation Anti-Bias (family-wide)

Meta-rules that govern HOW audit conclusions are reached, regardless of which skill runs.
Home for the rules; skills carry one-line pointers here. Applies to every probekit-* audit
skill (arch-review, code-audit, health-audit, motherboard-audit, legacy-detection,
pipeline-trace, deploy-readiness, spec-audit — and their -bogame variants).

## Rule 1 — FIRSTHAND: never conclude from a summary

A sub-agent report, a scout draft, a backlog row, or a doc claim is a HYPOTHESIS, not a
finding. Before recording any finding (or retiring one), open the cited file:line with the
Read tool and paste the verbatim evidence. A conclusion whose evidence chain ends at
"another agent said so" is not verified.

## Rule 2 — PROVE-ZERO: absence needs wide patterns + a live read

Never assert "0 occurrences", "not used anywhere", or lower a severity on the strength of
ONE grep. A narrow pattern silently misses variants and produces confident false-negatives.

Protocol for any zero-claim:
1. Grep at least two independent pattern formulations (synonyms, key-name variants,
   quoted/unquoted, singular/plural).
2. Read the live definition site (the schema, the config model, the consuming code) —
   vocabulary can diverge between definition and data.
3. State the patterns used in the finding, so the zero is reproducible.

Canonical case (2026-07-02, this family's own upgrade run): a structure scout grepped
motherboard boards for `"mode"` and reported guardrail modes = `{blocking}` only; a second
reader greppped `default_mode` and found `"advisory"` in a live board — the exact vocabulary
divergence the audit was hunting. One narrow grep nearly buried the finding.

## Rule 3 — STALE-CARRY: reconcile re-flags against the newest decision log

Before re-raising a previously-known finding (backlog row, ADR status, "impl-stale" flag),
check the NEWEST decision record first — sprint SNAPSHOT, decision log (Реш.NN class), or
protocol log. A carry that contradicts a later explicit decision is stale, not a finding.
Whichever row contradicts the newest decision log loses.

Canonical case: S18 Brain-Next re-flagged ADR-031/032 as "impl-stale" although Реш.51
(recorded in S18-SNAPSHOT) had already ratified them roadmap-credible and gated the unbuilt
APIs on S20+ multi-tenant onboarding. The re-flag was carry noise; the SNAPSHOT was the
tie-breaker.

## Rule 4 — Counts and paths cited in a rubric are hints, not truth

Any concrete number a skill's own reference file carries (node counts, service counts,
alert counts, validator counts) decays. When a check hinges on the number, re-derive it
firsthand (the rubric should name the derivation command) and score against the derived
value. If derived ≠ written, the finding is "rubric stale", not "code wrong".

## Anchor

[*] validation-anti-bias.md * family-wide audit-conclusion rules * pointed-to by audit skills
