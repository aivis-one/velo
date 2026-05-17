# Figma Operations Guide — useful rules extracted from operator's v3 methodology

```
Date:     2026-05-17
Source:   06_project-inputs/VELO_METHODOLOGY.md (operator's v3)
Purpose:  Practical Figma rules applicable to our v1.1 design-pipeline.
          Stripped of items that belong only to operator's orchestrator/
          worker/supervisor workflow (Mockups Production Mode).
Anchor:   [FIGMA-OPERATIONS-GUIDE.md | v1.0 | 2026-05-17]
```

> **Why this exists.** The operator runs a separate parallel workflow
> (v3 Mockups Production Mode) for building DS components and REBUILDs
> directly inside Figma. That workflow has accumulated detailed rules for
> safe Figma Plugin API usage — many of which apply to **our** read-only
> extraction (Sprint 1 Phase 1).
>
> This guide extracts ONLY the rules relevant to our v1.1 design-pipeline.
> The full v3 methodology lives at `../06_project-inputs/VELO_METHODOLOGY.md`.

---

## 1. Figma file canonical references

Per v3 §1 (verified by live probe 2026-05-17):

**File key:** `F7PD5isLfLdyc0q1Bd5n5c`

**Pages** (always 4, even if `get_metadata` returns only the active one):

| Page name | Figma ID | Our extraction relevance |
|---|---|---|
| VELO Documentation | `2931:3` | **Not relevant to us.** Operator's project state docs. |
| Design System (dsPage) | `490:12` | **Primary source for Layer 2 tokens** — `figma.variables` + `figma.textStyles` + COMPONENT survivors |
| Mockups | `462:1104` | **Primary source for Layer 1 visuals** — SACRED frames (untouchable, read-only — F-68) |
| Mockups_NEW | `789:2` | **Not directly relevant.** Operator's REBUILD workspace. |

**SACRED root frames on Mockups page** (Layer 1, untouchable — F-68 absolute):

| Section | Root ID | Screen count |
|---|---|---|
| Onboarding | `541:1179` | 8 |
| Dashboard | `541:6648` | 9 |
| Calendar | `541:1553` | 11 |
| Profile | `541:2355` | 7 |
| Diary | `541:2816` | 20 |
| Messages | `541:2717` | 3 |
| Analytics | `758:1529` | 3 |
| Practices | `758:1950` | 15 |
| Dashboard-v2 (master) | `758:3245` | — |
| Onboarding-v2 (master) | `758:4318` | — |

Approximate total: ~76 SACRED screens (close to the ~120 planning target —
the rest will come from auth/error/shared screens).

**DS canon survivors on dsPage** (post-chain-69 catastrophe):

- `4110:316` — DS Scaffold (8-category structure)
- `916:1662` — Mandala Decor Small Blue (COMPONENT)
- `423:125` — back-arrow icon (COMPONENT)
- All 8 COMPONENT_SETs (Photo Background, Primary Button, Checkbox, Input,
  Icon Button Pill, Button, Pagination Dots, Logo) + 3 standalone
  (Or Divider, Brand Mark Large, Brand Mark Small) — **destroyed**.
- 7 color variables and 6 text styles — **survived** (global resources).

---

## 2. Tool choice — Plugin API, not design-context MCP

Two different Figma toolsets are available:

| Toolset | Access | When to use |
|---|---|---|
| `mcp__figma__get_design_context`, `get_metadata`, `get_screenshot`, `get_variable_defs` | Limited read-only (current page only on this Pro account; `get_metadata` returned only 1 of 4 pages during probe) | Quick visual context capture for a single node |
| **`mcp__figma__use_figma`** (Plugin API) | Full programmatic read + write across all pages | **Default for our extraction.** All variable / textStyle / cross-page node queries should use this. |

The Plugin API runs JavaScript through `figma.*` globals, the same surface
that operator's v3 workflow uses.

---

## 3. Safe extraction patterns

### 3.0 — Survival rules for any Figma probe (Sprint 1 critical)

These three are non-negotiable when running `use_figma` Plugin API calls
during Sprint 1 extraction. They apply only during Sprint 1 (Figma is
not used after).

**Rule A — L-32 / AP-2: Never throw, always return error objects.**
Figma plugin runtime rolls back ALL writes in a plugin call when a
throw escapes. Even for read-only probes, a throw partway through
loses already-collected data. Always wrap in `try/catch`:

```javascript
const out = { ok: false, partial: null };
try {
  // collect data
  out.ok = true;
} catch (e) {
  out.error = String(e && e.message || e);
}
return out;
```

For multi-step probes, accumulate progress in an object and return it
on error so we don't lose what was collected.

**Rule B — L-37: Chunked manifest reads, no recursive bulk reads.**
Tool transport silently truncates large responses around ~20kb. Also,
in this MCP runtime `figma.loadAllPagesAsync()` is **not supported**
(returns "not a supported API"). Patterns:

- For node trees: **first probe the manifest** (`id + name + type + dims`
  per child), then read bodies in groups of 2-3 by exact id
- For TEXT longer than 15000 chars: slice via `.characters.slice(0, 15000)`
- Cross-page access works without `loadAllPagesAsync` via
  `await figma.getNodeByIdAsync("X:Y")` directly (verified 2026-05-17)

**Rule C — AP-6: Font loading does NOT persist between plugin calls.**
If any plugin call writes to TEXT nodes, `await figma.loadFontAsync(fontName)`
must run at the start of that call — even if a prior call loaded the
same font. For our read-only extraction this is mostly N/A, but if we
ever read multi-style TEXT via `getStyledTextSegments(["fontName"])`,
that read does not require loadFont.

---

### 3.1 Environment probe (run once at start of every Figma session)

Per v3 L-32 no-throw pattern + G-15 cross-page probe:

```javascript
const out = { env: null, crossPage: null };
try {
  const probe = figma.createFrame();
  probe.name = "_env_probe";
  probe.remove();
  out.env = { ok: true };
} catch (e) {
  out.env = { ok: false, error: String(e && e.message || e) };
}
try {
  // Probe a known cross-page node to confirm read access works
  const router = await figma.getNodeByIdAsync("2931:4");
  out.crossPage = router ? { ok: true, name: router.name } : { ok: false };
} catch (e) {
  out.crossPage = { error: String(e && e.message || e) };
}
return out;
```

### 3.2 G-1 + G-2 — SACRED descendant access

- **G-1 (CRITICAL):** NEVER traverse SACRED descendants via `.children`
  recursion. Plugin API raises on certain SACRED subtrees.
- **G-2:** Direct property reads on known SACRED leaf IDs are **safe**:
  `getNodeByIdAsync("541:NNN")` → `.width`, `.height`, `.fills`,
  `.characters`, `.fontSize`, etc.

**For our extraction** (read-only screenshots + mockup-mining):
- Use `getNodeByIdAsync` per known leaf ID (from SACRED Visual Index in v3 docs, or build our own list)
- For aggregating across page: `page.findAllWithCriteria({ types: [...] }).filter(n => n.parent?.id === knownParentId)` (page-level filtered, not recursive)

### 3.3 G-15 — Cross-page node access

`await figma.getNodeByIdAsync("X:Y")` works across all pages without
calling `loadAllPagesAsync` first in this runtime. **Verified by probe
2026-05-17** — `2931:4` (page 2931:3) read successfully from session
started without page-load.

Note: `figma.loadAllPagesAsync()` is **not supported** in this MCP runtime
(returned error during probe). Use cross-page reads via direct IDs instead.

### 3.4 G-3 — TEXT character cap

Any TEXT node with `.characters.length > 20480` silently truncates on
write. Not relevant to our read-only extraction, but if we ever export
text content from SACRED, slice at 15000 chars and emit a manifest.

### 3.5 G-7 — Font name preservation

When reading text styles, font information is available via
`textStyle.fontName` (object with `.family` and `.style`). For TEXT nodes
specifically, use `n.getRangeFontName(0, 1)` for the first character;
multi-style TEXT requires `n.getStyledTextSegments(["fontName"])`.

We need this for `getStyledTextSegments` only if mockup-mining surfaces
TEXT nodes with mixed fonts (likely rare in VELO since everything is
Marmelad Regular).

### 3.6 G-16 — PNG byte threshold scales with frame size

When exporting screenshots, minimum acceptable byte size scales:

| Frame size | Minimum bytes |
|---|---|
| 402×874 (full screen) | 5000 |
| 336×179 | ~2000 |
| 160×104 | ~1000 |
| 145×50 | ~300 |
| 64×36 | ~150 |

Anomalously low bytes (<100 for non-trivial frame) — flag for inspection.

### 3.7 G-18 — Cold export anomaly

First `exportAsync` call on a node after plugin runtime warm-up may return
PNG significantly smaller than subsequent calls on the same node. This is
a Figma render cache artifact, not real image deterioration.

**Mitigation:** before measuring or relying on PNG bytes, do one dummy
export on any valid node (result ignored), then take real measurements.
Or: double-export, use the second result.

---

## 4. Variables and text styles extraction

Per probe 2026-05-17, the canonical commands are:

```javascript
const vars = await figma.variables.getLocalVariablesAsync();
// returns array of variables; each has .id, .name, .resolvedType, .valuesByMode

const styles = await figma.getLocalTextStylesAsync();
// returns array of text styles; each has .id, .name, .fontSize, .fontName, .lineHeight
```

For resolving actual color values per mode:

```javascript
const colorVar = vars.find(v => v.name === "steel/primary");
const modeId = colorVar.variableCollectionId; // need to get collection then mode
// OR iterate variable.valuesByMode entries
```

(Full color-value resolution requires probing the variable's collection
and modes — to be done in Sprint 1 Phase 1.)

---

## 5. SACRED untouchable rule (F-68 absolute)

**Hard rule:** under no circumstance does any write operation target a
node under Mockups page `462:1104`. Reads via G-2 only (direct
property reads on known IDs).

Our v1.1 design-pipeline is **read-only** with respect to Figma by
design — we extract, we don't modify. F-68 is therefore satisfied by
default. The rule is here as a guardrail: if we ever feel tempted to
"fix something in Figma while we're there", **don't**. Surface it to the
operator instead.

---

## 6. Rules NOT applicable to us (kept here for reference only)

The operator's v3 contains many rules that govern building inside Figma —
they are NOT applicable to our extraction pipeline but listed here so
nothing accidentally creeps in:

- §2 Roles (orchestrator / worker / supervisor) — we use the v1.1 roles
  (Operator / Cowork / Claude Code / Chat) instead
- §3 Q-N user communication format — our user-facing communication
  follows `claude-code` style; Q-N is an v3 internal convention
- §4 R1-R9 base rules — relevant to **writes** in Figma
- §9 Comparison Block spatial pattern — Figma-native build layout
- §10 Three-Layer Pipeline (Layer 1 SACRED / Layer 2 DS canon /
  Layer 3 REBUILDs) — **conceptually compatible** with our model, but
  Layer 3 (REBUILDs in Figma) is **not our deliverable**; our deliverable
  is HTML/CSS in `01_deliverable/`
- §11 Lifecycle (Phase A / B / C / D, такты) — v3 cycle structure for
  Figma production; we use Sprint 0..10 from ROADMAP instead

If a v3 rule has a useful idea that **also** applies to our pipeline,
extract it into our methodology with a citation back to v3.

---

## References

- Source document: `../06_project-inputs/VELO_METHODOLOGY.md` (operator's v3, 822 lines)
- Our methodology: `../04_methodology/VELO-METHODOLOGY.md` v1.1
- Inventory built from probe: `tokens/VELO-DS-INVENTORY.md`
- Strategic conflict (v3 vs v1.1) — see top-level `../INDEX.md` Recent Changes (TBD)

---

## Anchor

```
[FIGMA-OPERATIONS-GUIDE.md | v1.0 | 2026-05-17]
Practical Figma rules extracted from operator's v3 methodology for use in
our read-only extraction pipeline (Sprint 1 Phase 1). Strategic conflict
with v3 ("Frontend Prep Mode deprecated chain 70") is logged separately
and requires operator decision before continued execution.
Location: D:\02_Projects\velo\docs\02_design-system\FIGMA-OPERATIONS-GUIDE.md
```
