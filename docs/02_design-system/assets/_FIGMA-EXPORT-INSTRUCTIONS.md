# Figma SACRED Screens — Local Export Instructions

```
Date:        2026-05-17
Purpose:     Bulk-export ~97 SACRED screens as PNG/JPG to local
             02_design-system/assets/screenshots/ folder
Status:      Operator action required (Plugin API sandbox transport
             cap blocks bulk export from this side)
File:        F7PD5isLfLdyc0q1Bd5n5c (VELO Figma file)
```

> **Why this is needed manually.** The `use_figma` Plugin API tool returns
> base64 PNG/JPG via tool response, but the response transport caps at
> ~20KB. A single screen at usable scale exceeds that, so files end up
> truncated. This is the same constraint that DSYS-era hit (D-009);
> bulk export requires local Figma action, not Plugin API streaming.

---

## Option A — Figma UI right-click export (fastest, ~5 minutes total)

This is the simplest path. Operator action only.

### Steps

1. **Open Figma file** in browser:
   `https://www.figma.com/design/F7PD5isLfLdyc0q1Bd5n5c/VELO`

2. **Switch to "Mockups" page** (page id `462:1104`).

3. **Select all top-level SACRED screen frames.** There are 97 child
   frames across 10 SACRED root groups. The roots themselves are:
   - `ОНБОРДИНГ` (id `541:1179`) — 8 screens
   - `ДАШБОРД` (id `541:6648`) — 9 screens
   - `КАЛЕНДАРЬ` (id `541:1553`) — 11 screens
   - `ПРОФИЛЬ` (id `541:2355`) — 7 screens
   - `ДНЕВНИК` (id `541:2816`) — 20 screens
   - `СООБЩЕНИЯ` (id `541:2717`) — 3 screens
   - `АНАЛИТИКА` (id `758:1529`) — 3 screens
   - `ПРАКТИКИ` (id `758:1950`) — 15 screens
   - `Dashboard-v2` (id `758:3245`) — 8 screens (master-side)
   - `Onboarding-v2` (id `758:4318`) — 13 screens (master-side)

   In Figma, **drag-select a SACRED root** in the canvas, then
   **Shift+click each child frame inside**, OR use the Layers panel on
   the left:
   - Expand a root group (e.g. `ОНБОРДИНГ`)
   - Click the first child frame
   - Hold **Shift** and click the last child frame to select all
     children inside that root
   - Repeat for each root group, holding **Shift** across roots to add
     selections from all 10 roots into one selection

4. **Open the Export panel** (right sidebar → `Export` section, or press
   **Ctrl/Cmd + Shift + E**).

5. **Configure export settings:**
   - **Format:** `PNG`
   - **Suffix:** leave blank
   - **Scale:** `1x` (native, best quality)

6. **Click "Export N layers"** (the number will match how many you
   selected, target = 97).

7. **Save destination:** Figma will prompt for download. Choose to
   download as a ZIP, or save directly to
   `D:\02_Projects\velo\docs\02_design-system\assets\screenshots\`.

8. **If ZIP downloads:** extract its contents into
   `02_design-system/assets/screenshots/`.

9. **Rename files** to follow our convention if Figma exports use frame
   names with Cyrillic/special chars:
   - Naming convention: `{section}-{padded-num}-{slug}.png`
   - e.g. `onboarding-01-welcome.png`, `dashboard-10-dashboard-1.png`
   - This is optional — Figma's default names (frame name as filename)
     are also acceptable, as long as they map back to SACRED node IDs
     in `ASSETS-INDEX.md`.

### Result

97 PNG files in `02_design-system/assets/screenshots/`, native
quality, used as visual ground truth for mockup review in Sprints 2+.

---

## Option B — Figma Plugin Console script (single click, ~3 minutes)

If you're comfortable with Figma's plugin console:

1. Open the VELO Figma file.
2. **Plugins → Development → Open Console** (or run a custom plugin).
3. Paste this script and run:

```javascript
// Bulk export all SACRED screens on Mockups page to per-frame PNGs
const SACRED_ROOTS = [
  "541:1179", "541:6648", "541:1553", "541:2355", "541:2816",
  "541:2717", "758:1529", "758:1950", "758:3245", "758:4318"
];
const exports = [];
for (const rootId of SACRED_ROOTS) {
  const root = await figma.getNodeByIdAsync(rootId);
  if (!root || !root.children) continue;
  for (const child of root.children) {
    try {
      const bytes = await child.exportAsync({ format: "PNG", constraint: { type: "SCALE", value: 1 } });
      exports.push({ name: child.name, id: child.id, bytes });
    } catch (e) {
      console.error("Failed:", child.id, child.name, e.message);
    }
  }
}
// Then post results back to plugin UI, which triggers download of each as PNG file.
// (Implementation detail: use figma.ui.postMessage with each Uint8Array.)
figma.notify(`Exported ${exports.length} screens. Check downloads.`);
```

This requires a custom Figma plugin UI to handle the downloads — more
complex than Option A. **Option A is recommended for simplicity.**

---

## After export complete

Once `02_design-system/assets/screenshots/` contains the 97 PNG files:

1. **Update `02_design-system/assets/ASSETS-INDEX.md`** — fill the
   screenshots table mapping `{filename} ↔ {source node ID}`.

2. **Re-trigger INVENTORY GATE (§10.1)** review by Cowork-Chat. Gate
   criteria for screenshots:
   - PNG file present for each top-level SACRED frame ✓
   - File size ≥ G-16 byte sentinel threshold (5000 bytes for native
     402×874, scales down per frame size)
   - File names listed in ASSETS-INDEX.md

3. **Proceed to Sprint 2** — Styleguide HTML uses these PNGs as the
   visual reference for component variant verification.

---

## Anchor

```
[_FIGMA-EXPORT-INSTRUCTIONS.md | v1.0 | 2026-05-17]
Operator-side bulk export instructions for SACRED screens. Replaces
attempted Plugin-API streaming export (blocked by 20KB transport cap).
Same pattern as DSYS-era D-009 workaround (`_DOWNLOAD-ASSETS.sh/.ps1`).
After operator export completes, ASSETS-INDEX.md is filled and INVENTORY
GATE proceeds.
Location: D:\02_Projects\velo\docs\02_design-system\assets\_FIGMA-EXPORT-INSTRUCTIONS.md
```
