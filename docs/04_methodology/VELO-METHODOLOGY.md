# VELO Methodology

> **Single source of truth for the VELO project.**
> This document defines how we build the VELO design system, how we assemble
> screen mockups, and how we hand off completed screens to development.
>
> It replaces three universal methodologies (DS, LIVEMOCKUP, HANDOFF) with
> one project-specific instrument. If a universal rule conflicts with VELO
> reality, this file is authoritative.
>
> **Audience:** the operator (you, architect), Cowork (Figma + HTML work),
> Claude Code (frontend code generation), the backend developer (consumer
> of the handoff package).
>
> **Anchor:** `[VELO-METHODOLOGY.md | v1.2 | 2026-05-17]`

---

## Table of Contents

1. Principles and Scope
2. Project Context
3. Folder Structure — Canonical Layout
4. Workflow Pipeline — End to End
5. Roles and Responsibilities
6. Design System Layer (DS)
7. Mockup Layer (Visual Verification)
8. Handoff Layer (Screen Specs)
9. Cowork Prompt Templates
10. Quality Gates
11. Anti-Patterns and Hard Prohibitions
12. INDEX Maintenance Protocol
13. Versioning and Changelog Discipline
14. What This Methodology Does NOT Cover

---

## 1. Principles and Scope

### 1.1 Five Foundational Principles

**P1 — Single source of truth per artifact type.**
Tokens have one master location. Components have one master location. Screen
specs have one master location. Copies for delivery are clearly marked as
copies. No parallel masters.

**P2 — Visual before contract.**
A screen specification is written **after** its HTML mockup is approved by
the operator. Approved mockup is the visual ground truth that the spec
references. Spec describes "what the code does", not "what the code looks
like" — the mockup already shows that.

**P3 — Methodology is preventive, not corrective.**
This document encodes rules that prevent known failure modes. Each
prohibition has a recorded cause. Following the methodology stops the
project from repeating mistakes.

**P4 — Figma is an input, not a workspace.**
Figma serves as a one-time extraction source for tokens, icons, and
screenshots. After extraction, all design work happens in HTML/CSS within
the `docs/` folder. The Figma file is read-only and never modified.

**P5 — Each layer can be inspected and verified independently.**
Tokens can be verified via a styleguide HTML. Mockups can be verified
visually against Figma screenshots. Screen specs can be reviewed by reading
them. Each layer has its own verify gate. No layer is "done" until its gate
passes.

### 1.2 Scope of This Document

In scope:
- Design tokens (extraction, naming, two-layer architecture, file split)
- UI components (tier classification, naming, file location)
- HTML mockups (assembly from tokens and components, visual verification)
- Screen specifications (template, contents, when written, by whom)
- Handoff package (what goes to the developer, structure, README)
- Quality gates (criteria, who validates, what passes)
- Cowork prompts (templates for repeatable tasks)

Out of scope (see §14 for full list):
- Code review practices for frontend implementation
- Backend contract design (we consume OpenAPI, we do not design it)
- Product strategy or feature prioritization
- Testing methodology (unit, E2E)
- Deployment, release, environments

### 1.3 Relationship to Other Documents

This methodology is the operating manual for VELO design and handoff work.
It coexists with:

- **`docs/06_project-inputs/ARCHITECTURE.md`** — frontend code rules
  (how the developer writes Vue components, store patterns, API wrapper).
  This methodology does not duplicate ARCHITECTURE rules; it references
  them where relevant. When in conflict, ARCHITECTURE wins for code-level
  rules and this methodology wins for design-and-handoff process.
- **`docs/06_project-inputs/api-openapi.json`** — the contract between
  frontend and backend. Screen specs reference operation IDs and schemas
  from this file. We do not invent types; we consume them.
- **`docs/05_roadmap/ROADMAP.md`** — sequence of work, sprint breakdown,
  current status. The methodology defines **how** to do work; the roadmap
  defines **when** to do which piece.

---

## 2. Project Context

### 2.1 Product

VELO is a wellness practice marketplace. The primary surface is the
Telegram WebApp; a PWA fallback exists for users without Telegram. Three
user roles exist — `user`, `master`, `admin` — each with its own UI shell
and screen set.

Approximate screen count at planning time: ~120 screens across all three
roles.

### 2.2 Frontend Stack

| Layer | Technology |
|---|---|
| Framework | Vue 3 + Composition API (`<script setup lang="ts">`) |
| Language | TypeScript 5.x, strict mode, `noUncheckedIndexedAccess` |
| Build | Vite |
| Router | Vue Router 4.x |
| State | Pinia |
| Styles | Plain CSS with CSS custom properties (no preprocessor, no Tailwind) |
| Token prefix | `--velo-*` (no exceptions) |
| Component prefix | `V*` (VButton, VInput, etc.) |
| i18n | vue-i18n, Russian primary, English secondary |
| Surface | Telegram WebApp (primary), PWA (fallback) |
| Mobile viewport baseline | 402×874 (Telegram WebApp) |

### 2.3 Figma Source

Figma file URL: `https://www.figma.com/design/F7PD5isLfLdyc0q1Bd5n5c/VELO`

Relevant pages in this file:

| Page | State | How we use it |
|---|---|---|
| `Mockups` | Complete vector frames | Primary source for screen visuals, colors, spacing, icons (mockup-mining) |
| `Design System` | Partial | If present, **primary source** for systematized tokens (states, hover, disabled). Read this FIRST before mockup-mining |
| `Mockups_NEW` | In progress | Partial reassembly work. Inventory only — do not duplicate effort |
| `VELO Documentation` | Abandoned | Do not use |

> **Important rule on Figma usage:** Figma is read-only. All extraction
> happens through MCP read tools (`get_design_context`, `get_variable_defs`,
> `get_screenshot`). After Phase 1 extraction is complete, no further Figma
> calls are needed for downstream work.

### 2.4 Three Roles and Their UI

Each role has a distinct UI shell with its own navigation, screen set, and
permission model. A spec must always declare which role(s) the screen
serves.

| Role | Shell | Approx. screen count | Examples |
|---|---|---|---|
| `user` | UserShell with bottom tab bar (4 tabs) | ~40 | Dashboard, Practice Detail, Bookings, Calendar, Profile, Waitlist, Diary |
| `master` | MasterShell with bottom tab bar (4 tabs) | ~35 | Master Dashboard, Practices, Practice Create/Edit, Analytics, Finance, Profile, Apply flow |
| `admin` | AdminShell with bottom tab bar (3 tabs) | ~25 | Admin Dashboard, Masters Review, Reports, Withdrawals, Consistency |
| Shared | (Onboarding, Auth, Error screens) | ~20 | Welcome, Login, Register, OAuth, Loading, 404, generic error |

### 2.5 VELO-Specific Invariants

These rules are project-specific and must be observed across all design,
mockup, and spec work. They are derived from VELO's domain model and
backend contract.

**I1 — Money is integer cents.**
Every monetary value at the API level is an integer field suffixed with
`_cents` (e.g., `price_cents`, `balance_cents`, `paid_cents`,
`discount_cents`). Never `parseFloat`. Conversion utilities live in
`frontend/src/utils/currency.ts` (`eurStringToCents`, `centsToEurString`).
Display via `formatMoney(cents, currency, locale, allowZero)` from
`frontend/src/utils/format.ts`.

**I2 — Timezone is per-entity, not browser-local.**
Practices carry their own `practice.timezone` field (IANA string) — used
for all practice-related date/time formatting. The user also carries a
`user.timezone` field — used for aggregate views (dashboard, diary,
calendar) when no practice context is available. Format via
`formatDate(iso, timezone, locale)` from utils. Never use the browser's
default timezone.

OpenAPI declares `timezone` as plain `string` (no `pattern` constraint
on IANA shape); validity is enforced server-side. Specs that render
times must explicitly state **which** timezone source they consume
(`practice.timezone` vs `user.timezone`).

**I3 — Role vs viewMode are distinct.**
The user's actual role lives in `user.role` (`user` | `master` | `admin`)
and is the **only** field permitted for security gates (e.g., admin-only
mutations). The `viewMode` field on the UI store is a **display**
preference (a master may temporarily view the app "as user"). Never use
`viewMode` for permission checks.

**I4 — Three error formats from the backend.**
The API wrapper (`api/client.ts`) normalizes three distinct error formats:
- `VeloError`: `{ error: string, message: string }` — domain error,
  most common. The `error` code is a stable identifier for switching;
  the `message` is human-readable.
- `Pydantic 422`: `{ detail: [{loc, msg, type}, ...] }` — request
  validation failure. Each entry maps to a specific field.
- `Network / timeout`: thrown as `ApiNetworkError` or `ApiTimeoutError`.
  No backend payload; show a generic "connection lost" toast and offer
  retry.

Screen specs must declare which error codes the screen handles and how
each is presented.

> **Implementation note.** `VeloError` is a **code-only contract**: its
> shape is enforced by `frontend/src/api/client.ts` parsing logic and by
> backend exception handlers, but it is **not declared in OpenAPI**.
> Therefore changes to VeloError shape are not caught by `vue-tsc` or by
> `velo gen-types` regen — they must be coordinated manually between
> backend and frontend. See I8 for the broader code-only-contract risk.
> Only `HTTPValidationError` / `ValidationError` (the Pydantic 422
> format) are formally declared in `api-openapi.json`.

**I5 — Telegram deep links survive auth.**
Telegram start parameters arrive on
`Window.Telegram.WebApp.initDataUnsafe.start_param` and are accessed via
`platform.getStartParam()`. The auth flow (`/loading`) must preserve
them across the redirect. Screen specs that are deep-link entry points
must declare which startParam pattern they accept and how the parameter
maps to route params or store state.

**Canonical startParam patterns (v1.1 initial set, extendable):**

| Pattern | Target screen | Param meaning |
|---|---|---|
| `open_practice__{uuid}` | user-practice-detail (or master view) | Practice UUID |
| `open_master__{uuid}` | master profile (public view) | Master UUID |
| `open_booking__{uuid}` | booking detail | Booking UUID |
| `open_topup` | user-topup | No param (literal string) |

Additions to this list bump the methodology to the next minor version
(per §13.1) and update both this table and `frontend/src/platform/`
JSDoc.

**I6 — Waitlist FSM has six states.**
The waitlist for a practice progresses through:

```
waiting ──► notified ──► confirmed
   │           │     └─► declined
   │           └────────► expired
   └─► left
```

Source of truth: `frontend/src/api/types.ts` `WaitlistStatus` union and
OpenAPI `WaitlistEntryResponse.notified_at` field name. The token
`offered` (used in pre-v1.1 drafts) is **wrong** — the canonical name
is `notified`.

Transitions:
- `waiting → notified` — backend offers a seat; `notified_at` is set;
  user receives push
- `notified → confirmed` — user accepts within deadline
  (`confirm_waitlist` endpoint)
- `notified → declined` — user explicitly declines
- `notified → expired` — deadline (`expires_at`) passes without action
- `waiting → left` — user leaves the waitlist before any offer
  (`leave_waitlist` endpoint)

`WaitlistStatus` is a **code-only contract** — OpenAPI types
`WaitlistEntryResponse.status` as a plain `string` without enum
constraint. See I8.

Any spec that touches waitlist state must reference this FSM (defined
once in §8.7 of this document and referenced by ID from individual
specs).

**I7 — Dark theme is deferred but architecturally prepared.**
The two-layer token system supports dark theme via a second mode block
on Layer 2. Currently we ship light theme only. Open TODO logged once
in `docs/02_design-system/INDEX.md`; specs and mockups assume light.

**I8 — Status enums are code-only contracts.**
Only **four** enums are formally declared in `api-openapi.json`:
- `UserRole`: `['user', 'master', 'admin']`
- `SemaphoreResult.status`: `['OK', 'ALERT']`
- `SemaphoreResult.criticality`: `['critical', 'warning', 'info']`
- `CreateReportRequest.target_type`: `['user', 'master', 'practice']`

All other status fields (`BookingStatus`, `PracticeStatus`,
`MasterStatus`, `WithdrawalStatus`, `WaitlistStatus`, `PurchaseStatus`,
`PracticeType`, `AttendanceBookingStatus`, `Mood`, `FeedbackRating`,
etc.) are typed as plain `string` in OpenAPI. Their real values live
only in `frontend/src/api/types.ts` as TypeScript unions. Code-only
unions used in VELO (authoritative source):

| Union | Values |
|---|---|
| `BookingStatus` | `pending` / `confirmed` / `attended` / `no_show` / `cancelled` |
| `PracticeStatus` | `draft` / `scheduled` / `live` / `completed` / `cancelled` / `deleted` |
| `PracticeStatusTransition` | `scheduled` / `live` / `completed` / `deleted` (allowed transitions only) |
| `PracticeType` | `live` / `series` / `one_on_one` / `replay` |
| `MasterStatus` | `pending` / `verified` / `rejected` |
| `WithdrawalStatus` | `pending` / `approved` / `rejected` |
| `WaitlistStatus` | `waiting` / `notified` / `confirmed` / `left` / `expired` / `declined` (see I6) |
| `PurchaseStatus` | `pending` / `completed` / `refunded` / `failed` |
| `AttendanceBookingStatus` | `pending` / `confirmed` / `attended` / `no_show` |
| `Mood` | `low` / `mid` / `high` |
| `FeedbackRating` | `fire` / `good` / `confused` |

Risk: changes to these enums on the backend are not caught by `vue-tsc`
or by `velo gen-types` regen. Mitigations:

1. Specs reference enums by exact name; if backend adds a new value,
   the spec must be updated.
2. Status-bearing components (BookingCard, PracticeCard, WaitlistCard,
   etc.) must use an **exhaustive** `switch` and treat unknown values
   as an explicit error state, never silently render a blank or
   default branch.
3. Long-term: backend declares these enums in OpenAPI; the I8 risk
   then collapses to I4 (VeloError) only.

---

## 3. Folder Structure — Canonical Layout

This is the single canonical structure for the VELO project. All work
happens within these folders. No alternative locations.

```
D:\02_Projects\velo\
│
├── frontend\                          ← code repository (lean, ships to prod)
│   ├── src\
│   ├── docs\                          ← developer-facing docs only
│   │   ├── ARCHITECTURE.md            ← code rules (master)
│   │   ├── ENVIRONMENT.md             ← environment setup
│   │   └── README.md
│   └── package.json
│
└── docs\                              ← design/handoff workspace (kept out of frontend repo)
    │
    ├── INDEX.md                       ← top-level map of the entire docs folder
    │
    ├── 01_deliverable\                ← what the developer receives (the product)
    │   ├── README.md                  ← copy-this-where instructions
    │   ├── styles\
    │   │   ├── variables.css          ← copy of master from 02_design-system/tokens/
    │   │   └── global.css             ← copy of master from 02_design-system/tokens/
    │   ├── assets\
    │   │   ├── icons\                 ← copy from 02_design-system/assets/icons/
    │   │   └── fonts\                 ← if self-hosted fonts are used
    │   └── screens\
    │       ├── INDEX.md               ← screen spec status map
    │       ├── SCR-001-{name}.md
    │       ├── SCR-002-{name}.md
    │       └── ...
    │
    ├── 02_design-system\              ← master source of the design system
    │   ├── INDEX.md
    │   ├── tokens\
    │   │   ├── VELO-DS-INVENTORY.md   ← Figma extraction inventory
    │   │   ├── variables.css          ← MASTER (Layer 1 + Layer 2 tokens)
    │   │   └── global.css             ← MASTER (fonts, reset, .velo-typo-* classes)
    │   ├── assets\
    │   │   ├── icons\                 ← MASTER (PNG + SVG, extracted from Figma)
    │   │   ├── screenshots\           ← Figma screen PNGs (pixel ground truth)
    │   │   └── ASSETS-INDEX.md
    │   └── styleguide\
    │       └── velo-design-system.html ← living styleguide (tokens + components)
    │
    ├── 03_mockups\                    ← operator's visual workspace (not shipped)
    │   ├── INDEX.md
    │   ├── user\
    │   │   ├── user-dashboard.html
    │   │   ├── user-practice-detail.html
    │   │   └── ...
    │   ├── master\
    │   │   └── ...
    │   └── admin\
    │       └── ...
    │
    ├── 04_methodology\                ← this document
    │   └── VELO-METHODOLOGY.md
    │
    ├── 05_roadmap\                    ← planning and tracking
    │   ├── ROADMAP.md                 ← high-level plan
    │   ├── sprint-01.md
    │   ├── sprint-02.md
    │   └── ...
    │
    └── 06_project-inputs\             ← read-only documents from outside the design pipeline
        ├── ARCHITECTURE.md            ← copy of frontend/ARCHITECTURE.md
        ├── api-openapi.json           ← snapshot of backend OpenAPI
        └── ...
```

### 3.1 Folder Purpose at a Glance

| Folder | Purpose | Who writes | Who reads |
|---|---|---|---|
| `01_deliverable\` | Final package handed to developer/Claude Code | Cowork assembles, operator approves | Developer, Claude Code |
| `02_design-system\` | Master source of tokens, assets, styleguide | Cowork (with operator approval) | Cowork, operator, references from specs |
| `03_mockups\` | Visual workspace for verifying design before spec | Cowork generates, operator approves | Operator (sole audience) |
| `04_methodology\` | This document | Operator + Chat (Claude) | Cowork, Claude Code, operator |
| `05_roadmap\` | Plan and progress | Operator + Cowork | All |
| `06_project-inputs\` | External reference documents | Imported, not authored | All |

### 3.2 Three Critical Boundaries

**B1 — `01_deliverable\` is the only thing the developer sees.**
When handing off, the operator copies or references `01_deliverable\`.
Folders 02, 03, 04, 05 are internal. The developer does not navigate
them.

**B2 — Tokens have one master.**
`02_design-system/tokens/variables.css` is the **master**. The copy in
`01_deliverable/styles/variables.css` is regenerated when the master
changes. Never edit the deliverable copy directly.

**B3 — Mockups never contain spec content.**
HTML files in `03_mockups\` are pure visual artifacts. They do not embed
API contracts, error handling rules, or business invariants. Those live
in screen specs under `01_deliverable/screens/`.

---

## 4. Workflow Pipeline — End to End

This is the canonical sequence from "Figma exists" to "developer receives
package." Every screen in the project flows through this pipeline.

```
PHASE 1 — Figma Extraction (one-time per design refresh)
        │
        ▼
PHASE 2 — Token Synthesis (variables.css + global.css)
        │
        ▼  GATE: TOKENS GATE — operator approves styleguide.html
        │
PHASE 3 — Styleguide HTML (living visual catalog)
        │
        ▼  GATE: STYLEGUIDE GATE — operator approves component coverage
        │
PHASE 4 — Mockup Assembly (per screen, parallelizable)
        │
        ▼  GATE: MOCKUP GATE per screen — operator visual-approves
        │
PHASE 5 — Screen Spec Writing (per screen, AFTER mockup approval)
        │
        ▼  GATE: SPEC GATE per screen — operator reviews spec contents
        │
PHASE 6 — Handoff Assembly + Frontend Sync
        │
        ▼  GATE: PACKAGE GATE — deliverable folder complete and consistent
        │
        ▼
Claude Code consumes spec + visuals + tokens, generates Vue code
```

### 4.1 Phase Triggers and Outputs

| Phase | Trigger | Output | Gate |
|---|---|---|---|
| 1. Figma extraction | Project start, or design refresh | `VELO-DS-INVENTORY.md`, icons, screenshots in `02_design-system/` | INVENTORY GATE |
| 2. Token synthesis | After Phase 1 complete | `variables.css` + `global.css` (master + copy) | TOKENS GATE |
| 3. Styleguide HTML | After Phase 2 complete | `velo-design-system.html` | STYLEGUIDE GATE |
| 4. Mockup assembly | Per screen, after styleguide stable | One HTML per screen in `03_mockups\{role}\` | MOCKUP GATE (per screen) |
| 5. Spec writing | Per screen, after mockup approved | One `SCR-NNN-{name}.md` in `01_deliverable/screens/` | SPEC GATE (per screen) |
| 6. Handoff | Periodic (end of sprint) | `01_deliverable\` complete and synced | PACKAGE GATE |

### 4.2 Parallelism

Phases 4 and 5 are per-screen and parallelizable. Multiple screens can be
in different phases simultaneously: one screen's mockup is being built
(Phase 4) while another screen's spec is being written (Phase 5). Phase
gates apply per screen, not per project.

Phases 1, 2, 3 are sequential and project-wide. They cannot be
parallelized — Phase 2 depends on Phase 1 output; Phase 3 depends on
Phase 2 output.

### 4.3 Re-entry into earlier phases

If a token gap is discovered during Phase 4 (mockup assembly) — for
example, a screen needs a hover state color not present in
`variables.css` — the team **re-enters Phase 2**:
1. Token is added to `02_design-system/tokens/variables.css` (master).
2. Token is propagated to `01_deliverable/styles/variables.css` (copy).
3. Styleguide is updated to demonstrate the new token.
4. Token gate is re-validated for the added token only.
5. Mockup work resumes.

Re-entry is logged in `02_design-system/INDEX.md → Iteration Log`.

---

## 5. Roles and Responsibilities

Four actors participate in VELO design and handoff work. Each has a
clearly bounded set of tasks.

### 5.1 Operator (you, the architect)

**Owns:** scope, priorities, design judgment, final approval.

**Does:**
- Approves which screens to build and in what order.
- Validates each gate (TOKENS, STYLEGUIDE, MOCKUP, SPEC, PACKAGE).
- Spots visual regressions against Figma.
- Decides on ambiguous design questions (which color, which spacing,
  what to do when Figma is silent).
- Maintains the methodology — proposes changes, integrates lessons.

**Does not:**
- Hand-write tokens, components, or specs (delegated to Cowork).
- Generate Vue code (delegated to Claude Code).

### 5.2 Cowork (Claude in Claude Cowork)

**Owns:** Figma extraction, HTML/CSS production, screen spec drafting.

**Does:**
- Phase 1: extracts tokens, icons, screenshots from Figma via MCP.
- Phase 2: writes `variables.css` and `global.css`.
- Phase 3: builds `velo-design-system.html` styleguide.
- Phase 4: builds one HTML mockup per screen.
- Phase 5: drafts screen specs per template, using the approved mockup
  + API JSON + ARCHITECTURE.md as inputs.
- Maintains local INDEX.md files inside each folder.

**Does not:**
- Edit `ARCHITECTURE.md` or `api-openapi.json` (those are inputs).
- Generate Vue code (delegated to Claude Code).
- Approve gates (operator's job).

### 5.3 Claude Code (CC, the developer agent)

**Owns:** Vue component code generation, frontend implementation.

**Does:**
- Reads `01_deliverable\` (specs, tokens, assets) + frontend repo
  + ARCHITECTURE.md.
- Generates `.vue`, `.ts` files in `frontend/src/`.
- Copies `variables.css` and `global.css` from `01_deliverable/styles/`
  to `frontend/src/styles/`.

**Does not:**
- Write specs (consumes them).
- Modify mockups (visual reference only).
- Touch Figma or the design-system folder.

### 5.4 Chat (Claude in claude.ai, this conversation)

**Owns:** methodology authorship, planning support.

**Does:**
- Writes and revises this methodology document.
- Helps the operator draft `ROADMAP.md` and sprint plans.
- Reviews handoff artifacts on request.

**Does not:**
- Execute work (no Figma MCP access, no frontend repo access).
- Make decisions the operator must make.

---

## 6. Design System Layer (DS)

This section defines how the VELO design system is built. It is the
project-specific application of design-system best practice, with all
universal rules folded in.

### 6.1 Two-Layer Token Architecture (Mandatory)

```css
:root {
  /* ============================================================== */
  /* LAYER 1 — PRIMITIVES                                            */
  /* Raw values extracted from Figma. Internal only.                 */
  /* Components MUST NOT reference Layer 1 directly.                 */
  /* ============================================================== */
  --velo-color-steel-primary: #4c6589;
  --velo-color-neutral-white: #ffffff;
  --velo-space-1: 4px;
  --velo-space-2: 8px;
  /* ... */

  /* ============================================================== */
  /* LAYER 2 — SEMANTIC TOKENS                                       */
  /* Aliases that describe USE, not VALUE. Components use these.     */
  /* ============================================================== */
  --velo-text-primary: var(--velo-color-steel-primary);
  --velo-bg-screen: var(--velo-color-neutral-white);
  /* ... */
}
```

**The rule:** components consume **only** Layer 2. Layer 1 is invisible
to component code. If a component needs a color that has no Layer 2
alias, the alias is added first.

Why this matters: if the brand color changes, only Layer 1 changes.
Layer 2 aliases keep pointing at the new value. Components don't move.

### 6.2 Token File Separation — Strict Concerns

This rule was added in response to a real bug in the previous extraction
attempt. `variables.css` and `global.css` have **strictly separate**
contents. Mixing them is a hard prohibition (see §11).

**`variables.css` contains ONLY:**
- `:root { ... }` block with `--velo-*` custom properties (Layer 1 + Layer 2)
- Comments grouping tokens by category

**`variables.css` MUST NOT contain:**
- `@import url(...)` statements for fonts → goes to `global.css`
- Universal selectors like `* { box-sizing }` → goes to `global.css`
- Body/html resets like `body { margin: 0 }` → goes to `global.css`
- Utility classes like `.velo-typo-heading-h1 { ... }` → goes to `global.css`
- Component-specific dimensions like `--velo-button-height: 50px` or
  `--velo-back-pill-width: 64px` → goes to component `<style scoped>`
- Single-screen constants like `--velo-screen-width: 402px` → goes to
  layout component `<style scoped>`

**`global.css` contains ONLY:**
1. `@import url(...)` for Google Fonts (or local font-face declarations)
2. Universal reset:
   ```css
   * { box-sizing: border-box; }
   body {
     margin: 0;
     font-family: var(--velo-font-family-primary);
     color: var(--velo-text-primary);
     background: var(--velo-bg-screen);
     -webkit-font-smoothing: antialiased;
   }
   ```
3. Typography utility classes:
   ```css
   .velo-typo-heading-h1 {
     font-size: var(--velo-size-32);
     font-weight: var(--velo-weight-bold);
     line-height: 1.2;       /* concrete number, never "normal" */
     letter-spacing: 0.02em; /* if Figma specifies */
   }
   .velo-typo-body { ... }
   /* etc. */
   ```

**`global.css` MUST NOT contain:**
- `--velo-*` custom property definitions → those live in `variables.css`
- Component-specific styles
- Reset rules beyond the universal `* { box-sizing }` and minimal body reset

### 6.3 Required Token Groups

Tokens that **must** be present in `variables.css`, even if their values
have to be marked MISSING after extraction. The list defines the minimum
semantic vocabulary the design system must offer.

| Group | Layer 2 examples |
|---|---|
| Text | `--velo-text-primary`, `--velo-text-secondary`, `--velo-text-muted`, `--velo-text-inverse`, `--velo-text-footnote` |
| Backgrounds | `--velo-bg-screen`, `--velo-bg-input`, `--velo-bg-button-primary`, `--velo-bg-button-secondary`, `--velo-bg-card`, `--velo-bg-overlay` |
| Borders | `--velo-border-default`, `--velo-border-input`, `--velo-border-button`, `--velo-border-focus` |
| States | `--velo-state-success`, `--velo-state-error`, `--velo-state-warning`, `--velo-state-info`, `--velo-state-destructive` |
| Interactive | `--velo-focus-ring`, `--velo-disabled-bg`, `--velo-disabled-text`, `--velo-hover-overlay`, `--velo-active-overlay` |
| Spacing | `--velo-space-0` (0px) through `--velo-space-25` — 4px base scale (1=4px, 2=8px, 4=16px, etc.) |
| Radius | `--velo-radius-sm`, `--velo-radius-md`, `--velo-radius-lg`, `--velo-radius-pill`, `--velo-radius-full` |
| Shadows | `--velo-shadow-card`, `--velo-shadow-modal`, `--velo-shadow-glow` (project-specific) |
| Font sizes | `--velo-size-12` through `--velo-size-32` — exact px values from Figma |
| Font family | `--velo-font-family-primary` |
| Font weights | `--velo-weight-regular` (400), `--velo-weight-medium` (500), `--velo-weight-semibold` (600), `--velo-weight-bold` (700) |
| Line heights | embedded in `.velo-typo-*` classes; never on raw tokens; never `normal` |

### 6.4 MISSING Token Protocol

A token in §6.3 is required even if Figma does not yet provide a value.
In that case follow the **promote-not-invent** sequence (per v1.2):

1. **Mockup-mine first.** Before declaring MISSING, scan SACRED frames
   on Mockups page (Layer 1) for the value. Often a primitive exists in
   the visual but is not declared in `figma.variables`. Capture it with
   provenance: which SACRED frame, which node, what fill / radius / px.
2. **If found** in Layer 1 mining: add as a Layer 1 primitive with
   provenance comment in `variables.css`, e.g.
   `--velo-state-error: #ef4444; /* found in SACRED 541:1180 (Welcome screen error toast frame 541:1188) */`
3. **If genuinely not found** in any SACRED frame: only then add the
   token with a sensible neutral placeholder value and an inline comment
   `/* MISSING: not found in Figma DS canon nor in any SACRED frame — neutral placeholder */`.
4. Log in `02_design-system/INDEX.md → Open TODOs`.
5. Continue work. Do not stop.
6. At INVENTORY GATE, report all MISSING tokens (with placeholder reason)
   in the summary, plus any newly-mined primitives with their provenance.

Acceptable neutral placeholders:
- `--velo-focus-ring: rgba(76, 101, 137, 0.4)` (derived from primary)
- `--velo-state-success: #22c55e`
- `--velo-state-error: #ef4444`
- `--velo-state-warning: #f59e0b`
- `--velo-state-info: #3b82f6`
- `--velo-hover-overlay: rgba(0, 0, 0, 0.04)`

> **Never** invent a brand-specific value. Placeholder is **always**
> neutral (industry-standard or derived from primitives), never a guess
> at brand intent.

### 6.5 Figma Extraction Sequence

Order of operations during Phase 1. Must be followed strictly — out-of-order
extraction caused real defects in the previous attempt.

**Step 1.1 — Locate the Design System frame.**
First call: `get_design_context` on the Figma page named `Design System`.
If a systematized DS frame exists with declared tokens, color styles,
text styles — **this is the primary source**.

If `Design System` page is empty or does not exist, log this fact in
`VELO-DS-INVENTORY.md` and proceed to mockup-mining as the only source.

**Step 1.2 — Inventory existing variables.**
Call `get_variable_defs` on the Figma file. Record:
- All color variables: name → hex value
- All number variables (spacing, radius, sizes)
- All text styles (font family, size, weight, line-height — line-height
  always as a concrete number, never `auto` or `normal`)

**Step 1.3 — Extract all screen frames as PNG.**
Iterate every top-level frame on the `Mockups` page. For each:
- `get_screenshot` → PNG, save as
  `02_design-system/assets/screenshots/{role}-{screen-name}.png`
- Record in `ASSETS-INDEX.md`: source node ID, target file path

**Step 1.4 — Extract all icons.**
Identify all icon nodes (typically ~24×24 vector groups). For each:
- `get_screenshot` → PNG at 2× scale, save as
  `02_design-system/assets/icons/icon-{name}.png`
- Where possible, also export SVG (via Figma's export, if available)
- Record in `ASSETS-INDEX.md`

**Step 1.5 — Mockup mining for tokens.**
For each screen frame:
- Collect all unique fill colors (hex values + occurrences count)
- Collect all unique cornerRadius values
- Collect all auto-layout gap/padding values
- Collect all text node properties (font, size, weight, line-height)
- Collect all dropShadow effects

Aggregate across all screens. The result is the raw token candidate set.

**Step 1.6 — Cross-reference DS frame vs mockup mining.**
Two sources must agree:
- If a value is in DS frame **and** in mockups → confirmed token.
- If a value is only in DS frame → confirmed token (declared but unused
  yet; keep).
- If a value is only in mockups → confirmed token (de facto used; add).
- If a required token (§6.3) is in neither → MISSING token (§6.4).

**Step 1.7 — Produce inventory.**
Write `02_design-system/tokens/VELO-DS-INVENTORY.md` with three sections:

```markdown
## Section A — Layer 1 Primitives
| Token name (proposed) | Value | Source | Occurrences |
|---|---|---|---|
| --velo-color-steel-primary | #4c6589 | DS frame + 14 mockup frames | 14 |
| --velo-color-neutral-white | #ffffff | 22 mockup frames | 22 |
...

## Section B — Layer 2 Semantic Mapping
| Semantic token | Maps to | Usage |
|---|---|---|
| --velo-text-primary | --velo-color-steel-primary | All body text |
...

## Section C — MISSING Tokens
| Required token | Status | Placeholder | Reason |
|---|---|---|---|
| --velo-focus-ring | MISSING | rgba(76,101,137,0.4) | Not in Figma |
...
```

This file is the input for Phase 2 token synthesis.

### 6.6 Component Tier Classification

Components are classified into three tiers by their generality and reuse.
This affects where they live in the styleguide and how rigorously they
are documented.

> **Note on Tier 1 list:** the canonical Tier 1 list for VELO is
> determined **after Phase 1 Figma extraction**, based on actual frequency
> of UI atoms in the mockups. The list below is the **planning target**
> from VELO-DS-PLAN; it will be confirmed or revised after extraction.

**Tier 1 — Primitive UI atoms (planning target):**

| Component | Variants | API connection |
|---|---|---|
| `VButton` | primary / secondary / destructive / ghost; sm/md/lg; default/loading/disabled | Everywhere |
| `VInput` | default / error / disabled; with/without label | All forms |
| `VTextarea` | default / error / disabled | MasterApply, DiaryEntry |
| `VSelect` | default / error / disabled | Filters, practice form |
| `VCheckbox` | default / checked / disabled | Forms, settings |
| `VBadge` | Practice statuses; Booking statuses | PracticeResponse, BookingResponse |
| `VAvatar` | with photo / initials fallback; sm/md/lg | UserResponse.avatar_url |
| `VLoader` | inline / fullscreen overlay | All async states |
| `VToast` | success / error / warning / info | useToast composable |

**Tier 2 — Composite domain components (planning target):**

| Component | Variants | API connection |
|---|---|---|
| `PracticeCard` | Types (per I8): `live` / `series` / `one_on_one` / `replay`; `free` / `paid`; statuses (per I8 `PracticeStatus`): `draft` / `scheduled` / `live` / `completed` / `cancelled` / `deleted`. Component must handle unknown status as explicit error state. | PracticeResponse |
| `BookingCard` | Statuses (per I8 `BookingStatus`): `pending` / `confirmed` / `cancelled` / `attended` / `no_show`. Subset `AttendanceBookingStatus` (`pending` / `confirmed` / `attended` / `no_show`) used by master-practice-attendance. | BookingWithPracticeResponse |
| `WaitlistCard` | Statuses (per I6 + I8 `WaitlistStatus`): `waiting` / `notified` / `confirmed` / `left` / `expired` / `declined`. Component must handle unknown status as explicit error state. | WaitlistEntryResponse / WaitlistWithPracticeResponse |
| `PriceDisplay` | cents → EUR string; with/without discount | `price_cents`, `paid_cents`, `discount_cents` |
| `BalanceChip` | balance amount display | UserResponse.balance_cents |
| `MasterStatusBadge` | Statuses (per I8 `MasterStatus`): `pending` / `verified` / `rejected` | MasterProfileResponse.status |
| `FeedbackWidget` | Values (per I8 `FeedbackRating`): `fire` / `good` / `confused` | FeedbackRequest |
| `MoodWidget` | Values (per I8 `Mood`): `high` / `mid` / `low` | CheckinRequest |
| `WithdrawalRow` | Statuses (per I8 `WithdrawalStatus`): `pending` / `approved` / `rejected` | WithdrawalResponse |
| `PromoRow` | `active` / `inactive` — UI abstraction derived from `PromoResponse.deactivated_at` and/or `is_active` boolean (no formal `PromoStatus` enum exists); usage / limit fields. | PromoResponse |
| `DiaryEntryCard` | content preview, mood indicator, date | DiaryEntryResponse |
| `InsightsChart` | Mood + feedback bars | PracticeInsightsResponse |

**Tier 3 — Layout and navigation:**

| Component | Description |
|---|---|
| `VHeader` | Screen top bar with optional back button and title |
| `VTabBar` | Bottom navigation — user 4 / master 4 / admin 3 tabs |
| `MobileLayout` | Full-screen wrapper for Telegram WebApp |
| `SectionTitle` | Section heading with optional counter |
| `EmptyState` | Empty list state with icon + message |
| `PaginationLoader` | Infinite scroll trigger / "Load more" button |

### 6.7 Component Naming

- Prefix `V*` for Tier 1 primitives (`VButton`, `VInput`).
- Domain components in Tier 2 use plain names (`PracticeCard`,
  `BookingCard`), no `V` prefix — they encode business meaning.
- Tier 3 layout uses `V*` for primitives (`VHeader`, `VTabBar`) and plain
  names for composites (`MobileLayout`, `SectionTitle`, `EmptyState`).
- One concept = one name. `VLoader` is the loader; `VSpinner` is not a
  separate name. If two appearances of "spinner" exist in Figma, they are
  variants of `VLoader`, not separate components.

### 6.8 Styleguide HTML

`02_design-system/styleguide/velo-design-system.html` is the **living
verify gate** for the design system. One self-contained HTML file, opened
in a browser, demonstrates every token and every component.

Structure (top-level tabs):

- **Tokens** — Colors, Semantic, Typography, Spacing, Radius, Shadows, Icons
- **Components** — Tier 1 + Tier 2 with all variants visible
- **Patterns** — Header + TabBar (all role variants), Form pattern, List
  pattern, Modal pattern

Rules:
- Token bridge at top of `<style>` (livemockup-studio conventions →
  VELO tokens) — see §11.3 anti-pattern note for the canonical bridge.
- All VELO tokens inlined in `<style>` (copied from variables.css and
  global.css).
- All sample content in Russian. No Lorem ipsum.
- Every interactive component demonstrates feedback (toast or state
  change on click).
- Navigation Map (📍) with full section tree.
- Mobile device frame at 402px width by default.

Verify-gate criterion: STYLEGUIDE GATE (see §10).

---

[END OF PART 1 — continues with Mockup Layer, Spec Template, Pipeline, Cowork Prompts, Quality Gates, Anti-Patterns]
## 7. Mockup Layer (Visual Verification)

After the design system is stable (tokens + components in styleguide
approved), the team builds one HTML mockup per screen. Mockups live in
`03_mockups\{role}\` and are the operator's visual workspace.

### 7.1 Purpose of a Mockup

A mockup serves three audiences in this order:

1. **The operator** — visual approval before spec writing.
2. **The spec author (Cowork)** — visual reference for Phase 5 spec
   writing.
3. **Claude Code** — visual reference during implementation.

A mockup is **not** a code artifact. It does not implement business
logic, real API calls, or production behavior. It demonstrates layout,
typography, color, spacing, and interactions at a sufficient fidelity to
verify the visual design against Figma.

### 7.2 One HTML File Per Screen

Strict rule. Each screen of the application is one self-contained HTML
file. No multi-screen tab carousels in one file; no monolithic "all
screens" demo. Reasons:

- Easier visual diff against Figma screenshot.
- Easier reference from a screen spec (one URL = one screen).
- Easier parallel editing by Cowork (no merge conflicts).
- Easier handoff to Claude Code (one mockup per spec).

Naming: `{role}-{screen-name}.html`, kebab-case, all lowercase. Examples:
`user-dashboard.html`, `master-practice-create.html`,
`admin-master-review.html`.

### 7.3 Mockup File Structure

Each mockup HTML follows this skeleton:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VELO — {Screen Name}</title>
  <style>
    /* 1. VELO tokens inlined from 02_design-system/tokens/variables.css */
    :root { --velo-color-steel-primary: #4c6589; /* ... */ }

    /* 2. VELO global styles inlined from 02_design-system/tokens/global.css */
    @import url('...');
    * { box-sizing: border-box; }
    body { /* ... */ }
    .velo-typo-heading-h1 { /* ... */ }

    /* 3. Token bridge for livemockup-studio shell compatibility */
    :root {
      --primary: var(--velo-bg-button-primary);
      --bg: var(--velo-bg-screen);
      --text: var(--velo-text-primary);
      /* see §11.3 for full bridge */
    }

    /* 4. Screen-specific styles (BEM, scoped to this mockup) */
    .dashboard-stats { /* ... */ }
  </style>
</head>
<body>
  <!-- Device shell wrapper (mobile 402px, livemockup-studio convention) -->
  <div class="device-frame phone">
    <div class="device-screen">
      <!-- Screen content using VELO components -->
    </div>
  </div>

  <!-- Toolbar with device switcher, zoom, Navigation Map -->
  <!-- ... livemockup-studio standard shell ... -->

  <script>
    /* Realistic VELO sample data (see §7.6) */
    /* Interaction handlers (see §7.5) */
  </script>
</body>
</html>
```

### 7.4 Device Baseline

VELO targets Telegram WebApp on mobile. The default mockup viewport is
**402×874** (not the universal 390×844 — this is a VELO-specific override
because Telegram's WebApp viewport is slightly wider).

Three device frames are available in the toolbar:
- Phone — 402×874 (default, shown first)
- Tablet — 820×600 (secondary, for testing)
- Desktop — 1280×800 (rarely used; some admin screens may benefit)

### 7.5 Interactions on Mockups

Mockups are **clickable** but not **functional**. Every interactive
element responds visually:

| Element | Mockup behavior |
|---|---|
| Navigation link within the same mockup | Scrolls to or shows the target section |
| Navigation link to another screen | Toast: `🟢 Переход на: {target-screen}` |
| Form submit button | Toast: `📌 {Action name} — финальная точка` |
| Tab switch (within screen) | Toast: `🟡 Таб "{name}" — переключает контент` and shows alternate content if mocked |
| External link (OAuth, deep link) | Toast: `📌 {Provider} — финальная точка` |
| Destructive action (delete, cancel) | Confirm dialog or toast: `⚠️ {Action} — финальная точка` |

> **Russian localization note:** all toast text is in Russian since the
> operator is the audience and the product is Russian-primary. English
> versions are not generated for mockups.

### 7.6 Realistic VELO Sample Data

No Lorem ipsum, no placeholder names. Mockups demonstrate the design
system with content that matches the actual product domain. This catches
visual issues that abstract data hides (long names truncation, currency
formatting, date overflows).

Standard sample set:

```javascript
const masters = [
  { name: "Анна Соколова", title: "Преподаватель медитации",
    experience: "8 лет", rating: 4.9, reviews: 142,
    avatar: "https://i.pravatar.cc/150?img=5" },
  { name: "Михаил Петров", title: "Мастер дыхательных практик",
    experience: "12 лет", rating: 4.8, reviews: 89,
    avatar: "https://i.pravatar.cc/150?img=12" },
  { name: "Елена Иванова", title: "Йога-инструктор",
    experience: "6 лет", rating: 4.7, reviews: 67,
    avatar: "https://i.pravatar.cc/150?img=20" },
];

const practices = [
  { title: "Утренняя медитация", master: "Анна Соколова",
    duration_minutes: 30, level: "Начинающий",
    slot: "Завтра, 07:30", price_cents: 1500, type: "live" },
  { title: "Дыхательные практики", master: "Михаил Петров",
    duration_minutes: 45, level: "Средний",
    slot: "21 января, 18:00", price_cents: 2500, type: "series" },
  { title: "Вечерняя растяжка", master: "Елена Иванова",
    duration_minutes: 60, level: "Любой",
    slot: "Сегодня, 20:00", price_cents: 0, type: "live" }, // free
];

const balance_cents = 6750; // €67.50
const booking_statuses = ["confirmed", "attended", "pending"];
const moods = ["high", "mid", "low"];
const ratings = ["fire", "good", "confused"];
```

### 7.7 State Triad on Mockups

Where applicable, a mockup demonstrates the three primary states of any
data-bearing screen by toggling between them in the same file:

- **Loading state** — skeleton loaders or VLoader overlay
- **Empty state** — EmptyState component with role-appropriate copy
- **Populated state** — full data using §7.6 sample set
- **Error state** — toast or inline error message

A small toolbar control (or three buttons) allows switching between
states in the mockup. The operator can verify each state visually before
spec is written.

### 7.8 Navigation Map

Each mockup includes a 📍 Navigation Map (livemockup-studio convention):
a collapsible legend showing:
- All clickable elements on the screen
- Where each link leads (other screen, toast, modal)
- Color-coded by type: 🟢 cross-screen, 🟡 in-screen tab, 📌 endpoint, ⚠️ destructive

Russian labels:

| Symbol | Type | Label |
|---|---|---|
| 🟢 | Screen | Экран |
| 🟡 | Tab | Табы |
| 📌 | Endpoint | Тупик |
| ⚠️ | Destructive | Деструктивное действие |

The Navigation Map count appears at the top of the legend:
`X экранов, Y финальных точек, Z деструктивных`.

### 7.9 Mockup Quality Check (Before Operator Review)

Before submitting a mockup for operator approval, Cowork runs an internal
check (livemockup-studio test protocol) and must report:

- 0 BLOCKER issues (broken layout, missing critical content)
- ≤ 2 MAJOR issues (visual inconsistencies that don't block use)
- Any number of MINOR/NIT (cosmetic)

If BLOCKER or 3+ MAJOR found, Cowork fixes before submitting. Operator
reviews the mockup against the matching Figma screenshot from
`02_design-system/assets/screenshots/`.

### 7.10 Mockup Approval Recording

After visual approval, the operator records the approval in
`03_mockups/INDEX.md`:

```markdown
| Screen file | Status | Approved on | Notes |
|---|---|---|---|
| user/user-dashboard.html | ✅ approved | 2026-05-22 | Per Figma node 1234 |
| master/master-practices.html | 🔄 in revision | — | Spacing too tight in card list |
```

Approval unlocks Phase 5 — spec writing — for that screen.

---

## 8. Handoff Layer (Screen Specs)

This is the section that defines **what** is handed to development and
**how** it is documented. Every screen of the application receives one
spec file in `01_deliverable/screens/SCR-NNN-{name}.md`.

### 8.1 What a Screen Spec Is and Is Not

A screen spec **is**:
- A **contract** between design intent and code implementation.
- A **machine-readable-enough** document for Claude Code to consume
  without further clarification.
- A **stable identifier** (SCR-NNN) for the screen across the project.
- A **delta over global rules** — does not repeat what's in
  ARCHITECTURE.md, this methodology, or the OpenAPI schema.

A screen spec **is not**:
- A description of how the screen looks (the mockup HTML shows that).
- A copy of the OpenAPI schema (it references operation IDs by name).
- A copy of ARCHITECTURE rules (it references sections by number).
- A history of decisions (those live in the project's decisions log).

### 8.2 Spec Identifier Format

`SCR-NNN-{kebab-case-name}.md`

- `SCR-` is the literal prefix.
- `NNN` is a 3-digit zero-padded integer, assigned in increasing order as
  specs are created. Not reused. Not reorganized.
- `{kebab-case-name}` is a short identifier matching the mockup file
  name (without `.html`).

Examples:
- `SCR-001-user-dashboard.md`
- `SCR-002-user-practice-detail.md`
- `SCR-003-master-apply.md`
- `SCR-004-admin-master-review.md`

Numbering is project-wide, not per-role. The first screen approved gets
SCR-001 regardless of role.

### 8.3 Required Spec Structure (12 Sections)

Every spec follows this structure. Sections are mandatory. If a section
does not apply to a particular screen, the section is included with the
content `N/A — {one-line reason}`. Empty sections are not allowed.

`````markdown
---
# YAML front-matter
id: SCR-001
name: user-dashboard
status: draft | active | superseded | archived
last-updated: 2026-05-22
mockup: 03_mockups/user/user-dashboard.html
mockup-approved-on: 2026-05-22
figma-screenshot: 02_design-system/assets/screenshots/user-dashboard.png
roles: [user]
route: /
priority: P1
---

# SCR-001 — User Dashboard

## 1. Context

One paragraph: what the screen does in the product. The "what", not the
"why". The why lives in product documents, not here.

## 2. Visual Reference

- Mockup HTML: `03_mockups/user/user-dashboard.html`
- Figma screenshot: `02_design-system/assets/screenshots/user-dashboard.png`
- Approved on: 2026-05-22

## 3. Route & Access

- **URL:** `/`
- **Route name:** `user-dashboard`
- **Shell:** `UserShell`
- **Params:** none
- **Query:** none
- **Role guard:** `user.role === 'user'` OR `viewMode === 'user'`
- **Auth guard:** required (session must exist)
- **On 401:** redirect to `/loading` (preserves Telegram start param)
- **On role mismatch:** redirect to the user's own dashboard for their role

## 4. Layout Structure

Brief structural map (NOT visual description — the mockup shows that).
List blocks in render order top-to-bottom:

1. Header (VHeader): title "Главная", no back button
2. Balance section (BalanceChip + "пополнить" button)
3. Practice list (PracticeCard × N from `practices` data)
4. Pagination loader at bottom (PaginationLoader)
5. Bottom tab bar (VTabBar, role=user)

## 5. Data Contract

GET-style endpoints used for initial render. List in fetch order.

| Order | OpenAPI operationId | Method + path | Response type | Mapped to |
|---|---|---|---|---|
| 1 | getUserMe | GET /api/v1/users/me | UserResponse | userStore.user |
| 2 | listPractices | GET /api/v1/practices | PaginatedPracticesResponse | practicesStore.items |

**Initial query params for listPractices:**
- `limit=20`
- `offset=0`
- `status=scheduled`

Pagination strategy: infinite scroll (PaginationLoader triggers next
`listPractices` with `offset += 20`).

## 6. Action Contract

POST/PATCH/DELETE endpoints triggered by user interactions.

| Trigger | OpenAPI operationId | Method + path | Request type | Success reaction | Error reactions |
|---|---|---|---|---|---|
| Tap "пополнить" | none — navigates to `/topup` | — | — | Route change | N/A |
| Tap PracticeCard | none — navigates to `/practice/:id` | — | — | Route change | N/A |
| Pull to refresh | listPractices (re-fetch) | GET /api/v1/practices | — | Replace list | Toast "Не удалось обновить" |

(If the screen has actual mutations like Withdrawal/Purchase, the table
expands.)

## 7. State Map

| State | When | What to render |
|---|---|---|
| loading | Initial fetch in flight | VLoader fullscreen, no content |
| empty | listPractices returns `items: []` | EmptyState with copy `practices.empty.title` + `practices.empty.subtitle` |
| error | listPractices throws non-401 | EmptyState with copy `practices.error.title` + retry button |
| populated | items.length > 0 | Practice list rendered |
| loading-more | Infinite scroll triggered, page > 0 | Existing list + bottom skeleton |

## 8. Store Dependencies

| Store | Read | Write (via actions) | Watch |
|---|---|---|---|
| userStore | `user`, `balance_cents` | `loadMe()` on mount | `user.role` (for guard) |
| practicesStore | `items`, `hasMore`, `isLoading` | `loadInitial()`, `loadMore()` | — |
| uiStore | `viewMode` | — | `viewMode` (for guard) |

## 9. i18n Keys

New keys to add to `frontend/src/i18n/locales/ru.json`:

```json
{
  "userDashboard": {
    "title": "Главная",
    "balance": "Баланс: {amount}",
    "topup": "Пополнить",
    "empty": {
      "title": "Пока нет практик",
      "subtitle": "Загляните позже"
    },
    "error": {
      "title": "Не удалось загрузить",
      "retry": "Повторить"
    }
  }
}
```

Existing keys reused: `common.refresh`, `common.retry` (already in locale).

## 10. Business Rules & Validations

- Balance displayed via `formatMoney(balance_cents, 'EUR', 'ru-RU')`.
  See VELO Invariant I1 (§2.5 of methodology).
- Practice card date uses `practice.timezone`, never browser timezone.
  See I2.
- Free practices (price_cents === 0) show "Бесплатно" instead of
  formatted price. Reuse logic from `formatMoney` with `allowZero=true`.
- Role guard uses `user.role`, NOT `viewMode`. See I3.

## 11. Error Code Map

VeloError codes the screen explicitly handles. Other codes fall through
to generic error toast.

| Error code | When | Reaction |
|---|---|---|
| `unauthorized` | 401 on any endpoint | Trigger api/client onUnauthorized callback (redirects to /loading) |
| `forbidden` | 403 on listPractices | Toast `errors.forbidden`, log to console |
| `rate_limited` | 429 on listPractices | Toast `errors.rateLimit`, disable refresh for 30s |
| (no code, network) | ApiNetworkError | Toast `errors.network`, allow retry |
| (no code, timeout) | ApiTimeoutError | Toast `errors.timeout`, allow retry |

See VELO Invariant I4 (§2.5) for error format reference.

## 12. Acceptance Criteria

The screen is "done" when all of the following pass.

- [ ] Layout matches mockup HTML at 402×874 within ±2px.
- [ ] BalanceChip displays `formatMoney(user.balance_cents)` exactly.
- [ ] Practice list renders with correct sort (date ascending).
- [ ] Empty state appears when items array is empty.
- [ ] Infinite scroll loads next 20 items at scroll-to-bottom.
- [ ] All Russian copy renders from i18n, no hardcoded Cyrillic in `.vue`.
- [ ] 401 redirects to `/loading` via api client callback.
- [ ] 403, 429 trigger their specific toasts.
- [ ] Network error allows retry.
- [ ] Role guard blocks `master.role === 'master'` user (redirects them
      to `/master`).
- [ ] No console errors in dev build.
- [ ] vue-tsc --noEmit passes.

## Changelog

- 2026-05-22 — Initial spec (operator + Cowork).
`````

### 8.4 Section Guidelines

**Section 1 (Context).** Maximum 3 sentences. If you need a paragraph,
the screen is probably too complex and should be split.

**Section 2 (Visual Reference).** Just links. Do not describe the visual.

**Section 3 (Route & Access).** Be explicit about every guard. If the
screen is publicly accessible (no auth), say so. If it's role-restricted,
specify the exact field check.

**Section 4 (Layout Structure).** A bulleted top-to-bottom list of
**block-level** sections. Not "header has 16px padding" — that's visual,
goes in the mockup. Just "Header → Balance → List → Footer".

**Section 5 (Data Contract).** Tabular. Reference operation IDs from
`api-openapi.json` by exact name. Do not paste schemas — Claude Code
reads `generated.ts` for shapes.

For `list_*` and paginated endpoints, declare the **initial query
params** explicitly: `limit` (default 20), `offset` (default 0), and
any filters (`status=`, `master_id=`, `date_from=`, `date_to=`,
`sort_by=`) that are passed on initial render. Declare the pagination
strategy (infinite scroll vs page-by-page). If the spec is silent on
query params, CC will pick defaults that likely mismatch product intent.

**Section 6 (Action Contract).** Same tabular discipline. Each row is
one user action with one or zero API calls. If an action triggers two
API calls in sequence (e.g., preview-purchase then purchase), give it
two rows or one row with "→" notation.

**Section 7 (State Map).** Five states is the default: loading, empty,
error, populated, loading-more. Some screens have more (e.g., a form
has "submitting" state); fewer states are unusual.

For screens with **multi-endpoint initial render** (dashboards
aggregating ≥2 endpoints in parallel), the State Map must include an
explicit **`partial-error`** state declaring what to render when some
endpoints succeed and others fail. Two patterns:
- **Best-effort:** render successful sections with their data; show
  inline error in failed sections (with retry).
- **All-or-nothing:** if any required endpoint fails, render full-screen
  error with retry.

The spec must declare which pattern this screen uses.

**Section 8 (Store Dependencies).** Be honest. If the screen only
reads, write "—" in the write column. If a watcher is needed (e.g.,
listening to `viewMode` to switch the layout), note it.

**Section 9 (i18n Keys).** Distinguish **new** keys (to add) from
**reused** keys (referencing existing locale). Use nested JSON
structure scoped under a screen-specific namespace.

For every state in Section 7 that surfaces UI copy (`empty`, `error`,
`loading-with-message`, `partial-error`), the i18n key + the proposed
Russian text **must** be enumerated here — no implicit "use a generic
empty state." Example:

```json
{
  "dashboard": {
    "upcoming": {
      "empty": "Нет запланированных практик",
      "emptyCta": "Посмотреть каталог"
    }
  }
}
```

**Section 10 (Business Rules).** Cross-reference VELO Invariants from
§2.5 of this methodology by ID (I1, I2, etc.). Do not restate them.

**Section 11 (Error Code Map).** Only codes the screen handles
explicitly. The generic fallback (any other error → generic toast) is
implicit and need not be listed.

Baseline (every spec includes the applicable rows; the spec is the
source of truth for which rows actually apply):

| Error code | Source | Default reaction |
|---|---|---|
| `unauthorized` | 401 on any endpoint | Trigger `setOnUnauthorized` callback → redirect to `/loading` |
| `forbidden` | 403 | Toast `errors.forbidden`; log to console |
| `not_found` | 404 on resource fetch | Redirect to parent listing or show 404 view |
| `rate_limited` | 429 | Toast `errors.rateLimit`; disable retry for 30s |
| `validation_failed` | 422 (Pydantic) | Inline field-level errors from `detail[]` |
| (network) | `ApiNetworkError` | Toast `errors.network`; offer retry |
| (timeout) | `ApiTimeoutError` (15s default) | Toast `errors.timeout`; offer retry |

Plus screen-specific VeloError codes (`error` field of the VeloError
shape; see I4) the spec explicitly handles.

**Section 12 (Acceptance Criteria).** Phrased as testable assertions.
"Layout matches mockup" is testable; "looks good" is not. Aim for
8-15 criteria; fewer means weak coverage, more means the screen
is overgrown.

### 8.5 Front-Matter Fields (YAML)

Required fields:

| Field | Type | Notes |
|---|---|---|
| `id` | string | `SCR-NNN` |
| `name` | string | kebab-case |
| `status` | enum | `draft` \| `active` \| `superseded` \| `archived` |
| `last-updated` | date | ISO date |
| `mockup` | path | Relative path to mockup HTML |
| `mockup-approved-on` | date | When operator approved the mockup |
| `figma-screenshot` | path | Relative path to Figma PNG |
| `roles` | array | One or more of `user`, `master`, `admin` |
| `route` | string | URL path |
| `priority` | enum | `P0` \| `P1` \| `P2` \| `P3` |

Optional fields:

| Field | Type | Notes |
|---|---|---|
| `superseded-by` | string | If status=`superseded`, points to replacement SCR-NNN |
| `depends-on` | array | Other SCR-NNN that must be implemented first |
| `flow` | string | If screen is part of a multi-screen flow (e.g., `master-apply`) |

### 8.6 The 12-Section Rule for Simple Screens

The 12 sections look heavy for a simple screen (e.g., a static "About"
page). The rule remains: include all 12, mark the inapplicable ones as
`N/A — {reason}` in one line.

Why: uniformity. Claude Code learns to expect 12 sections. Skipping
sections by absence creates parse ambiguity. Skipping by `N/A`
explicitly declares intent.

Example for a static screen:

```markdown
## 5. Data Contract
N/A — static content, no API calls.

## 6. Action Contract
N/A — no interactive elements.
```

### 8.7 Cross-Spec References — Shared FSMs and Tables

Some entities have state machines that span multiple screens. Defining
the FSM once and referencing it from each spec prevents drift.

**Waitlist FSM** (VELO Invariant I6):

```
States: waiting → notified → confirmed | declined | expired
                    waiting → left

Transitions:
  waiting  → notified   (backend offers a seat; notified_at is set; user receives push)
  notified → confirmed  (user accepts within deadline — confirm_waitlist endpoint)
  notified → declined   (user explicitly declines)
  notified → expired    (deadline passed — expires_at elapsed without action)
  waiting  → left       (user leaves waitlist before any offer — leave_waitlist endpoint)
```

Source of truth: `frontend/src/api/types.ts` `WaitlistStatus` union and
OpenAPI `WaitlistEntryResponse.notified_at` field name. `WaitlistStatus`
is a **code-only contract** (see I8) — backend types
`WaitlistEntryResponse.status` as plain `string`.

Specs reference this FSM by its anchor: see §8.7 of methodology, or
include a one-line note "Waitlist FSM applies — see methodology §8.7".

Other shared FSMs that may emerge during the project:
- Practice booking lifecycle (pending → confirmed → attended | no_show
  | cancelled)
- Master application lifecycle (draft → submitted → in_review →
  approved | rejected)
- Withdrawal lifecycle (pending → approved | rejected)

These are added to this section as they are defined. Each FSM is defined
**once**, here, and referenced by ID from individual specs.

### 8.8 Spec Status Lifecycle

```
draft → active → (superseded | archived)
```

- **draft** — Cowork has authored, operator has not yet approved.
- **active** — Approved. This is the version Claude Code consumes.
- **superseded** — A new spec under a different SCR-NNN replaces this
  one (major redesign). The `superseded-by` field points to the new
  spec.
- **archived** — Screen removed from the product entirely.

Status transitions are recorded in the spec's Changelog and in
`01_deliverable/screens/INDEX.md`.

### 8.9 Spec Versioning Within One ID

Within a single SCR-NNN, edits are made **in place**. The Changelog at
the end records each material change. Git provides exact history.

When NOT to keep the same SCR-NNN:
- The screen's URL or role changes fundamentally.
- The screen's primary purpose changes (e.g., a profile screen becomes
  a settings screen).
- The screen is split into multiple new screens.

In these cases, mark the old spec as `superseded`, create new SCR-NNN
spec(s), set `superseded-by`.

When to keep the same SCR-NNN:
- Adding a new field to the form.
- Adding a new error code to the error map.
- Updating wording of i18n keys.
- Refining acceptance criteria.

Rule of thumb: same screen identity = same SCR-NNN. Material change of
purpose = new SCR-NNN.

### 8.10 INDEX.md for Screens

`01_deliverable/screens/INDEX.md` is maintained continuously. Updated
**every time** a spec is added, status changes, or major edits are made.

Template:

```markdown
# Screens — Index

Last updated: 2026-05-22

| SCR ID | Name | Role | Route | Status | Mockup | Spec | Notes |
|---|---|---|---|---|---|---|---|
| SCR-001 | user-dashboard | user | / | active | ✅ | ✅ | — |
| SCR-002 | user-practice-detail | user | /practice/:id | active | ✅ | ✅ | — |
| SCR-003 | master-apply | master | /master/apply | draft | ✅ | 🔄 | Awaiting operator review |
| SCR-004 | master-pending | master | /master/pending | superseded | ✅ | ⛔ | superseded-by: SCR-009 |

## Summary
- Total specs: 4
- Active: 2
- Draft: 1
- Superseded: 1
- Archived: 0
```

---

[END OF PART 2 — continues with Cowork Prompts, Quality Gates, Anti-Patterns, INDEX Protocol, Versioning, Out-of-Scope]
## 9. Cowork Prompt Templates

Cowork executes the bulk of the work (Figma extraction, token writing,
mockup assembly, spec drafting). Each task is initiated by the operator
with a prompt that follows a template. Templates are kept in this
methodology so they can be reused verbatim.

### 9.1 General Rules for Cowork Prompts

- One prompt = one task = one output. Do not bundle "extract tokens AND
  build styleguide" in one prompt.
- Every prompt includes a reference to this methodology section (e.g.,
  "follow §6.5 of VELO-METHODOLOGY").
- Every prompt declares the **input** (what Cowork reads) and the
  **output** (what Cowork produces, where).
- Every prompt names the **gate** Cowork must pass before declaring done.
- Russian or English is acceptable in the prompt; outputs follow rules of
  the specific artifact (mockups are in Russian, methodology is English,
  etc.).

### 9.2 Prompt — Phase 1: Figma Extraction

```
Task: VELO Figma Extraction (Phase 1)

Methodology: VELO-METHODOLOGY §6.5 (Figma Extraction Sequence)
Figma file: https://www.figma.com/design/F7PD5isLfLdyc0q1Bd5n5c/VELO

Steps to execute in order:

1. Locate Design System frame on the "Design System" Figma page.
   - Call get_design_context on the page root.
   - If a systematized DS frame exists with tokens/styles: record as
     primary source.
   - If empty/absent: log this in VELO-DS-INVENTORY.md.

2. Inventory existing Figma variables via get_variable_defs.
   - Record all color, number, and text variables.
   - For text variables: line-height MUST be a concrete number. If
     Figma shows "auto", record the computed value (typically 1.2×
     font-size).

3. Extract every screen frame on the "Mockups" page as PNG.
   - Call get_screenshot per top-level frame.
   - Save to 02_design-system/assets/screenshots/{role}-{name}.png
   - Record source node ID + target path in
     02_design-system/assets/ASSETS-INDEX.md.

4. Extract every icon as PNG (2× scale) + SVG where supported.
   - Save to 02_design-system/assets/icons/icon-{name}.png
   - Record in ASSETS-INDEX.md.

5. Mockup-mining across all screen frames:
   - Aggregate unique fill colors with occurrence counts.
   - Aggregate unique cornerRadius values.
   - Aggregate unique auto-layout gap/padding values.
   - Aggregate unique text node properties (font, size, weight, line-height).
   - Aggregate unique dropShadow effects.

6. Cross-reference DS frame results vs mockup-mining results.
   - Confirmed token = present in both, or only in DS frame, or
     occurring 3+ times in mockups.
   - One-off colors (single occurrence in one mockup) flagged for
     operator decision.

7. Produce VELO-DS-INVENTORY.md with three sections:
   - Section A: Layer 1 primitives (name, value, source, occurrences)
   - Section B: Layer 2 semantic mapping (semantic token → primitive)
   - Section C: MISSING tokens (required by §6.3 but not found)

Output:
- 02_design-system/tokens/VELO-DS-INVENTORY.md
- 02_design-system/assets/screenshots/*.png
- 02_design-system/assets/icons/icon-*.png
- 02_design-system/assets/ASSETS-INDEX.md
- 02_design-system/INDEX.md updated (Token Status, Asset Index sections)

Gate: INVENTORY GATE (VELO-METHODOLOGY §10.1)
- All three sections of inventory filled.
- All screenshots and icons present in assets/.
- ASSETS-INDEX.md complete.
- All MISSING tokens logged in 02_design-system/INDEX.md → Open TODOs.

Do not proceed to Phase 2 until operator confirms gate pass.
```

### 9.3 Prompt — Phase 2: Token Synthesis

```
Task: VELO Token Synthesis (Phase 2)

Methodology: VELO-METHODOLOGY §6.1, §6.2, §6.4
Input: 02_design-system/tokens/VELO-DS-INVENTORY.md

Produce two files:

1. 02_design-system/tokens/variables.css
   - Contents per §6.2: ONLY :root { --velo-* } definitions.
   - Layer 1 (primitives) block first.
   - Layer 2 (semantic) block second.
   - Each Layer 2 token defined as alias: --velo-text-primary: var(--velo-color-steel-primary);
   - MISSING tokens included with /* MISSING: ... */ comment.
   - NO @import, NO reset, NO utility classes, NO component-specific
     constants, NO single-screen dimensions.

2. 02_design-system/tokens/global.css
   - Contents per §6.2:
     a) @import url(...) for Google Fonts (or @font-face if self-hosted)
     b) Universal reset:
        * { box-sizing: border-box; }
        body { margin: 0; font-family: var(--velo-font-family-primary);
               color: var(--velo-text-primary);
               background: var(--velo-bg-screen);
               -webkit-font-smoothing: antialiased; }
     c) Typography utility classes: .velo-typo-* per text style found.
        line-height MUST be a concrete decimal, never "normal".
        Letter-spacing in em where Figma specifies (typically 0.02em).
   - NO :root variable definitions.
   - NO component-specific styles.

Strict prohibitions (VELO-METHODOLOGY §11):
- var() + 2px without calc() — wrap in calc() or use literal value.
- line-height: normal anywhere — always a concrete decimal.
- Citing ARCHITECTURE.md rules that don't exist — verify section
  references before quoting.
- Component dimensions in global tokens (e.g., button-height).
- Single-screen viewport constants in global tokens.

After both files generated:
- Copy 02_design-system/tokens/variables.css → 01_deliverable/styles/variables.css
- Copy 02_design-system/tokens/global.css → 01_deliverable/styles/global.css

Gate: TOKENS GATE (VELO-METHODOLOGY §10.2)
- variables.css: zero hardcoded colors in any rule outside :root,
  zero "line-height: normal", zero @import, zero utility classes,
  zero component dimensions.
- global.css: imports in correct order, all typography classes
  using var(--velo-*).
- Both files mirrored in 01_deliverable/styles/.
- Operator reviews and confirms.
```

### 9.4 Prompt — Phase 3: Styleguide HTML

```
Task: VELO Styleguide HTML (Phase 3)

Methodology: VELO-METHODOLOGY §6.8
Skill: invoke livemockup-studio (v2.0+) directly.
Input: variables.css, global.css, VELO-DS-INVENTORY.md, icons/

Produce one file:
02_design-system/styleguide/velo-design-system.html

Shell: device preview, mobile 402px width by default.
Top-level tabs: Tokens | Components | Patterns

Tab "Tokens":
- Colors: swatches for every --velo-color-* primitive (square + name + hex)
- Semantic: table mapping Layer 2 → Layer 1 → resolved value
- Typography: live example of every .velo-typo-* class
- Spacing: visual bar scale per --velo-space-N
- Radius: rounded box per --velo-radius-*
- Shadows: card sample per --velo-shadow-*
- Icons: grid of all PNG icons with file names

Tab "Components":
- Render all Tier 1 components with all variants × all states
- Render all Tier 2 components with sample VELO data (see §7.6)
- Each component group labeled with name + brief variant matrix

Tab "Patterns":
- Header + TabBar with all 3 role variants
- Form pattern: VInput + VSelect + VButton + error state
- List pattern: 3 PracticeCards + PaginationLoader
- Modal pattern: overlay + content + close

Token bridge at top of <style> (VELO-METHODOLOGY §11.3 canonical bridge).
All VELO tokens and global rules inlined in <style>.
All sample text in Russian.
Every interactive element gives visual feedback.

Test protocol: livemockup-studio internal check.
Required result: 0 BLOCKER, ≤2 MAJOR. Fix BLOCKERs before submitting.

Gate: STYLEGUIDE GATE (VELO-METHODOLOGY §10.3)
- All sections populated.
- All Tier 1 + Tier 2 components present with all declared variants.
- Test protocol passes.
- Operator reviews and confirms.
```

### 9.5 Prompt — Phase 4: Mockup Assembly (Per Screen)

This prompt is reused for every screen. The operator fills in the
`{screen-name}` and `{role}` placeholders and runs it.

```
Task: VELO Mockup Assembly — {screen-name}

Methodology: VELO-METHODOLOGY §7
Skill: invoke livemockup-studio directly.
Inputs:
- 02_design-system/styleguide/velo-design-system.html (component reference)
- 02_design-system/assets/screenshots/{role}-{screen-name}.png (visual ground truth)
- 02_design-system/tokens/variables.css + global.css (inline these in mockup)

Build one HTML file:
03_mockups/{role}/{screen-name}.html

Requirements (VELO-METHODOLOGY §7.3):
- HTML skeleton per §7.3 (tokens inlined, bridge present, device shell)
- Mobile 402×874 default viewport
- All VELO components used as defined in styleguide (no inline rewrites)
- Realistic VELO sample data per §7.6 (Russian, domain-correct)
- State triad demonstrated per §7.7 (loading / empty / populated / error)
- Toolbar with device switcher + zoom + Navigation Map (📍)
- Toast feedback for every interactive element per §7.5
- Russian text only

Test protocol: livemockup-studio internal check.
Required: 0 BLOCKER, ≤2 MAJOR.

After test passes:
- Update 03_mockups/INDEX.md (add row, status "🔄 awaiting review")

Gate: MOCKUP GATE for this screen (VELO-METHODOLOGY §10.4)
- HTML opens at 402px without horizontal scroll
- Visual matches Figma screenshot within reasonable AA-rendering deltas
- All states (loading/empty/populated/error) visible via toolbar toggle
- Navigation Map shows correct screen and endpoint counts
- Operator reviews visually side-by-side with Figma PNG and approves

Do not write a spec for this screen until MOCKUP GATE passes.
```

### 9.6 Prompt — Phase 5: Screen Spec Writing (Per Screen)

```
Task: VELO Screen Spec — SCR-{NNN} — {screen-name}

Methodology: VELO-METHODOLOGY §8 (full section)
Spec ID: SCR-{NNN} (next available, see 01_deliverable/screens/INDEX.md)

Inputs (in priority order):
1. Approved mockup: 03_mockups/{role}/{screen-name}.html
2. ARCHITECTURE.md: docs/06_project-inputs/ARCHITECTURE.md
3. OpenAPI: docs/06_project-inputs/api-openapi.json
4. VELO-METHODOLOGY §2.5 (VELO Invariants I1-I7)
5. VELO-METHODOLOGY §8.7 (Shared FSMs)

Produce one file:
01_deliverable/screens/SCR-{NNN}-{screen-name}.md

Structure: exactly 12 sections per §8.3. Front-matter required per §8.5.

Section-by-section requirements:
1. Context: 1-3 sentences, "what", not "why".
2. Visual Reference: paths to mockup and Figma screenshot.
3. Route & Access: URL, role guard, auth guard, error redirects.
4. Layout Structure: top-to-bottom block list (no visual description).
5. Data Contract: GET-style endpoints, operationId from api-openapi.json,
   response types by name, mapping to store.
6. Action Contract: POST/PATCH/DELETE per user interaction.
7. State Map: loading, empty, error, populated, (optionally) others.
8. Store Dependencies: read/write/watch matrix.
9. i18n Keys: new keys to add (nested JSON) + reused existing keys.
10. Business Rules: cross-reference VELO Invariants by ID (I1-I7).
11. Error Code Map: VeloError codes the screen explicitly handles.
12. Acceptance Criteria: testable assertions, 8-15 items.

For each section that does not apply: write
"N/A — {one-line reason}" inside the section. Do not omit sections.

Cross-reference rules:
- ARCHITECTURE.md citations: include exact section number, e.g.
  "ARCHITECTURE.md §6.2". Verify the section exists.
- VELO Invariants: cite as "I1", "I2", etc. (from §2.5).
- Shared FSMs: cite as "Waitlist FSM, methodology §8.7".

Status on creation: draft.
Front-matter `last-updated`: today's date.

After spec generated:
- Update 01_deliverable/screens/INDEX.md (add row).
- Update Changelog at end of spec: "{date} — Initial spec".

Gate: SPEC GATE for this screen (VELO-METHODOLOGY §10.5)
- All 12 sections present (including N/A markers where applicable).
- Front-matter complete.
- All operationId references match an entry in api-openapi.json.
- All VELO Invariant references match §2.5 IDs.
- All ARCHITECTURE.md references point to existing sections.
- All i18n key namespaces follow nesting convention.
- Acceptance criteria are testable (not "looks good", not "works").
- Operator reviews and changes status to "active" upon approval.
```

### 9.7 Prompt — Phase 6: Handoff Package Assembly

```
Task: VELO Handoff Package Assembly (Phase 6)

Methodology: VELO-METHODOLOGY §3, §10.6
Inputs:
- 02_design-system/tokens/variables.css (master)
- 02_design-system/tokens/global.css (master)
- 02_design-system/assets/icons/ (master)
- 01_deliverable/screens/*.md (active specs only)

Steps:

1. Synchronize copies from master to deliverable:
   - cp 02_design-system/tokens/variables.css 01_deliverable/styles/variables.css
   - cp 02_design-system/tokens/global.css 01_deliverable/styles/global.css
   - rsync 02_design-system/assets/icons/ 01_deliverable/assets/icons/

2. Verify 01_deliverable/screens/:
   - Every spec has status=active or status=archived. No drafts in delivery.
   - INDEX.md is up to date with all active specs.
   - Every spec's mockup-approved-on date is present.

3. Write/update 01_deliverable/README.md per template (§9.7.1 below).

4. Update 01_deliverable/INDEX.md (if used) or the top-level
   docs/INDEX.md with package version and date.

Gate: PACKAGE GATE (VELO-METHODOLOGY §10.6)
- All files in 01_deliverable/ present.
- README.md template fully filled (no placeholders).
- No draft specs in delivery.
- Tokens in deliverable match master (no drift).
```

### 9.7.1 Deliverable README Template

````markdown
# VELO — Frontend Deliverable Package

Date: {ISO date}
Source: D:\02_Projects\velo\docs\01_deliverable\
Target: D:\02_Projects\velo\frontend\

## What's in this package

| Path | Purpose | Action |
|---|---|---|
| styles/variables.css | Design tokens (Layer 1 + Layer 2) | Copy to frontend/src/styles/variables.css |
| styles/global.css | Fonts, reset, .velo-typo-* classes | Copy to frontend/src/styles/global.css |
| assets/icons/ | All UI icons (PNG + SVG) | Copy to frontend/src/assets/icons/ |
| assets/fonts/ | Self-hosted fonts (if applicable) | Copy to frontend/src/assets/fonts/ |
| screens/ | Screen specifications (SCR-NNN-*.md) | Reference during implementation |
| screens/INDEX.md | Spec catalog with statuses | Use as the to-do list |

## How to use tokens

In any Vue component `<style scoped>`:

```css
.my-card {
  background: var(--velo-bg-card);
  border: 1px solid var(--velo-border-default);
  border-radius: var(--velo-radius-md);
  padding: var(--velo-space-4);
}
.my-card__title {
  color: var(--velo-text-primary);
  font-size: var(--velo-size-16);
}
```

## Hard rules

- Components use ONLY Layer 2 tokens (`--velo-text-*`, `--velo-bg-*`, etc.).
- Never reference Layer 1 primitives (`--velo-color-*`) from components.
- All user-facing strings go through `t('key')` via vue-i18n.
- Prices are integer cents at API level — use `formatMoney()` from utils.
- `line-height` is always a numeric value, never `normal`.
- Token arithmetic must use `calc()`. Example:
  `calc(var(--velo-space-12) + 2px)`. Never `var(...) + Npx` without
  `calc()` — browsers silently drop such declarations.

## Implementing a screen

1. Open the relevant SCR-NNN spec.
2. Open the matching mockup in `docs/03_mockups/{role}/`.
3. Implement the screen per spec section by section.
4. Validate against the spec's Acceptance Criteria.

## Active specs

See `screens/INDEX.md` for the current list and statuses.

## Questions / changes

If a spec is ambiguous or a token is missing, contact the operator.
Do not implement guesswork. Track open questions in
`docs/02_design-system/INDEX.md → Open TODOs`.
````

---

## 10. Quality Gates

Each phase ends in a gate the operator validates. A gate is **binary**:
pass or fail. There is no "85% pass." Either the criterion is met or the
phase is not done.

### 10.1 INVENTORY GATE (after Phase 1)

Criteria:
- `02_design-system/tokens/VELO-DS-INVENTORY.md` exists.
- All three sections (A, B, C) are present.
- Section A: every row has token name, value, source, occurrences. No
  empty cells.
- Section B: every required Layer 2 token (per §6.3) has a mapping.
- Section C: explicitly states either MISSING tokens or "no MISSING
  tokens found".
- `02_design-system/assets/screenshots/` contains a PNG per top-level
  screen frame in Figma.
- `02_design-system/assets/icons/` contains every icon used in any
  screen.
- `02_design-system/assets/ASSETS-INDEX.md` lists every asset with
  source node ID.
- `02_design-system/INDEX.md` updated.

Operator action: review inventory + spot-check 3-5 screenshots and 3-5
icons against Figma. Approve or request revision.

### 10.2 TOKENS GATE (after Phase 2)

Criteria:
- `02_design-system/tokens/variables.css` exists and contains ONLY
  `:root { ... }` block(s).
- `02_design-system/tokens/global.css` exists and contains imports,
  reset, and typography classes only.
- Zero `line-height: normal` in either file.
- Zero `var(--velo-...) + Npx` constructs without `calc()` wrapper.
- Zero `@import` in variables.css.
- Zero `:root` variable definitions in global.css.
- Zero component-specific tokens (button-height, dot-size, etc.) in
  variables.css.
- All §6.3 required tokens present (with MISSING placeholders if
  needed).
- Both files copied to `01_deliverable/styles/`.

Operator action: open both files, scroll, verify structure. Spot-check
5-10 token values against inventory. Approve or request revision.

### 10.3 STYLEGUIDE GATE (after Phase 3)

Criteria:
- `02_design-system/styleguide/velo-design-system.html` exists.
- Opens in a modern browser without console errors.
- All three top-level tabs (Tokens, Components, Patterns) populated.
- Every Tier 1 component visible with declared variants.
- Every Tier 2 component visible with sample data.
- Navigation Map (📍) shows all sections.
- Test protocol (livemockup-studio) result: 0 BLOCKER, ≤ 2 MAJOR.
- **Adjacent re-probe (v1.2):** if the styleguide change touches a
  component group, the operator also spot-checks **at least 2 unrelated
  component groups** for accidental regressions. Single-file styleguide
  means side-effects propagate via shared `<style>` rules and shared
  data fixtures.

Operator action: open in browser at 402px width. Walk through each tab.
Verify components match what's in Figma's "Design System" page (if any)
and how they appear in mockups. Adjacent re-probe (v1.2). Approve or
request revision.

### 10.4 MOCKUP GATE (per screen, after Phase 4)

Criteria for one screen:
- HTML file at `03_mockups/{role}/{screen-name}.html` exists.
- Opens at 402×874 without horizontal scroll.
- Visual matches Figma screenshot in
  `02_design-system/assets/screenshots/{role}-{name}.png` within
  acceptable rendering deltas (AA, font fallback, sub-pixel).
- State triad (loading/empty/populated/error) accessible via toolbar.
- All interactions produce visual feedback (toast or state change).
- Navigation Map shows expected screens/endpoints/destructive counts.
- All text in Russian, no Lorem ipsum, no placeholder names.
- 0 BLOCKER per livemockup-studio test protocol.
- **Adjacent re-probe (v1.2):** the operator additionally re-opens
  **the previously-approved adjacent mockup** in the same role-block
  (e.g., when reviewing `user-bookings`, also re-open `user-dashboard`)
  to confirm shared-token / shared-component changes did not cause
  regression. This catches Sprint-N-edit-breaks-Sprint-N-1 issues that
  per-mockup review misses.

Operator action: open mockup at 402px side-by-side with Figma PNG.
Toggle through states. Click every interactive element. Adjacent
re-probe (v1.2). Approve or request revision. Update
`03_mockups/INDEX.md` status to ✅.

### 10.5 SPEC GATE (per screen, after Phase 5)

Criteria for one spec:
- `01_deliverable/screens/SCR-NNN-{name}.md` exists.
- Front-matter complete with all required fields (§8.5).
- All 12 sections present (§8.3). N/A sections explicitly marked.
- Every `operationId` referenced exists in
  `06_project-inputs/api-openapi.json`.
- Every VELO Invariant reference (I1-I7) is valid (§2.5).
- Every ARCHITECTURE.md section reference exists and matches the cited
  rule.
- i18n keys are nested under a screen-specific namespace, distinguished
  new vs. reused.
- Acceptance criteria are testable assertions (verifiable Y/N).
- Spec's `mockup` field points to an approved mockup (per §10.4).
- Spec's status is `draft` (will become `active` upon this gate's
  pass).

Operator action: read spec end-to-end. Cross-check operationIds against
api-openapi.json. Verify acceptance criteria are testable. Change status
to `active` and update screens INDEX.md.

### 10.6 PACKAGE GATE (after Phase 6)

Criteria:
- `01_deliverable/README.md` complete with no placeholders.
- `01_deliverable/styles/variables.css` equals
  `02_design-system/tokens/variables.css` byte-for-byte (or with a
  documented diff).
- `01_deliverable/styles/global.css` equals master.
- `01_deliverable/assets/icons/` mirrors master.
- `01_deliverable/screens/INDEX.md` reflects current spec catalog.
- No spec with status=`draft` in delivery (only `active` and `archived`).
- `docs/INDEX.md` updated with package version + date.

Operator action: diff master vs deliverable for tokens. Walk through
README. Verify INDEX.md. Approve and notify Claude Code that a fresh
package is ready.

### 10.7 Gate Failure Protocol

If a gate fails:
1. Operator documents the failure with severity and root cause.
   - For Phase 1, 2, 3 (project-wide gates): log in
     `02_design-system/INDEX.md → Iteration Log`.
   - For Phase 4, 5 (per-screen gates): log in
     `docs/05_roadmap/sprint-NN.md` (current sprint file) and update
     status in the corresponding INDEX.md (mockups or screens).
   - For Phase 6 (package gate): log in top-level
     `docs/INDEX.md → Recent Changes`.
2. The phase output is **not** consumed downstream until fixed.
3. Cowork (or the relevant author) revises.
4. Re-validation against the same criteria.
5. Iteration count incremented in the relevant log.

Gates do not move; the artifact moves.

---

## 11. Anti-Patterns and Hard Prohibitions

This section is preventive. Each prohibition is tied to a real defect
that occurred in the project (or in similar projects) and prevents
recurrence. Cowork and Claude Code are expected to know this list.

### 11.1 Design-System Anti-Patterns

**AP-DS-1 — Mixing `variables.css` and `global.css`.**
Symptom: a single CSS file containing tokens AND fonts AND reset AND
utility classes.
Why bad: `variables.css` should be a pure token vocabulary, swappable
across themes/projects. `global.css` is the project-specific styling
foundation. Mixing them prevents reuse and makes diffs noisy.
Fix: enforce the strict split per §6.2.

**AP-DS-2 — `var() + Npx` without `calc()` wrapper.**
Symptom: `--velo-button-height: var(--velo-space-12) + 2px;`
Why bad: this is **not valid CSS**. Browser silently drops the
declaration. The button renders without a height.
Fix: `calc(var(--velo-space-12) + 2px)`. Or use the literal value with
a comment.

**AP-DS-3 — `line-height: normal`.**
Symptom: typography classes with `line-height: normal`.
Why bad: `normal` is browser- and font-dependent. Layout shifts between
Safari/Chrome/Firefox. Figma always has a concrete value (sometimes
labeled "auto" — that's a computed `1.2 × font-size`).
Fix: always a concrete decimal (1.2, 1.4, 1.5) per Figma text style.

**AP-DS-4 — Component dimensions in global tokens.**
Symptom: `--velo-button-height: 50px;`,
`--velo-back-pill-width: 64px;` in variables.css.
Why bad: these are component-specific constants. Putting them in the
global namespace pollutes it. Within a month there are dozens of
`--velo-{component}-{prop}` tokens cluttering the file.
Fix: dimensions live inside `<style scoped>` of the component.

**AP-DS-5 — Single-screen viewport constants in global tokens.**
Symptom: `--velo-screen-width: 402px;` (Figma canvas size).
Why bad: 402px is the iPhone 14 Pro / Telegram WebApp viewport, not a
design-system token. It belongs to the MobileLayout component.
Fix: layout dimensions live in MobileLayout `<style scoped>`.

**AP-DS-6 — Citing non-existent rules from ARCHITECTURE.md.**
Symptom: a generated file's header comment says "Per ARCHITECTURE.md
§6.2 ...", but ARCHITECTURE.md §6.2 has no such rule.
Why bad: erodes trust in citations. Reader cannot tell which rules are
real.
Fix: every cited section is verified before quoting. If unsure, omit
the citation.

**AP-DS-7 — Narrow extraction scope.**
Symptom: tokens extracted from one screen (e.g., onboarding) lack
destructive, success, error, warning, focus-ring, disabled, hover/active
colors.
Why bad: when the team moves to other screens, these tokens are
discovered missing and have to be added piecemeal.
Fix: at Phase 1, the inventory must cover all §6.3 required token
groups, with MISSING placeholders for those not yet visible.

**AP-DS-8 — Inventing brand values.**
Symptom: a "guessed" hex color appears in `variables.css` because the
designer hadn't specified one.
Why bad: when the real color arrives later, every place using the
guess must be migrated.
Fix: use neutral industry-standard placeholders, mark as MISSING, log
in TODOs. Never guess at brand intent.

### 11.2 Mockup Anti-Patterns

**AP-M-1 — Lorem ipsum or placeholder names in mockups.**
Symptom: "Master Jane Doe" in a mockup.
Why bad: visual issues that real data exposes (long names truncation,
currency formatting) are hidden.
Fix: §7.6 sample data set.

**AP-M-2 — Multiple screens in one HTML file.**
Symptom: a single `mockup.html` with tabs switching between 8
screens.
Why bad: harder to diff against Figma, harder to reference from specs,
harder to parallelize.
Fix: one HTML per screen.

**AP-M-3 — Mockup embeds business logic.**
Symptom: mockup HTML calls real API, conditionally renders based on
fetched data.
Why bad: mockup becomes a partial prototype, not a visual
specification. It can drift from the spec and become a parallel source
of truth.
Fix: mockup uses static `const` sample data. Interactions produce
toasts, not API calls.

**AP-M-4 — Static visuals only (no state triad).**
Symptom: mockup shows the populated state but not loading, empty, or
error.
Why bad: operator can't verify those states visually before spec is
written. Edge cases get missed.
Fix: §7.7 state triad toggle.

**AP-M-5 — Hardcoded color or spacing in mockup.**
Symptom: mockup `<style>` contains `background: #4c6589;` instead of
`background: var(--velo-color-steel-primary);`.
Why bad: when tokens change, mockup drifts.
Fix: every visual value references a VELO token. Inline the token
definitions at top of `<style>`.

### 11.3 Token Bridge for Mockups (Required)

`livemockup-studio` shells use generic token names (`--primary`, `--bg`).
To keep mockups using VELO tokens while leveraging the shell, every
mockup includes this bridge **verbatim** at the top of `<style>`:

```css
/* Bridge: livemockup-studio shell tokens → VELO design system */
:root {
  --primary:        var(--velo-bg-button-primary);
  --primary-dark:   var(--velo-bg-button-primary);
  /* hover variant token not yet defined; update bridge when added */
  --accent:         var(--velo-state-info);
  --bg:             var(--velo-bg-screen);
  --bg-subtle:      var(--velo-bg-card);
  --text:           var(--velo-text-primary);
  --text-secondary: var(--velo-text-secondary);
  --border:         var(--velo-border-default);
  --success:        var(--velo-state-success);
  --warning:        var(--velo-state-warning);
  --danger:         var(--velo-state-destructive);
}
```

When new shell tokens appear in future livemockup-studio versions, the
bridge is updated here and propagated to all mockups.

### 11.4 Spec Anti-Patterns

**AP-S-1 — Skipping inapplicable sections.**
Symptom: spec has only 9 of 12 sections; the rest just absent.
Why bad: parse ambiguity. Reader can't tell "no actions on this screen"
from "author forgot section 6".
Fix: include all 12 sections; mark inapplicable as `N/A — {reason}`.

**AP-S-2 — Visual descriptions in the spec.**
Symptom: "the button is rounded and has 16px padding".
Why bad: that's the mockup's job. Spec drifts from mockup if visual is
duplicated.
Fix: spec lists blocks in render order (§8.4 guidance for Section 4).

**AP-S-3 — Pasting OpenAPI schemas into the spec.**
Symptom: spec contains the full TypeScript interface of `UserResponse`.
Why bad: drift. The schema lives in `api-openapi.json`. Claude Code
reads `generated.ts`.
Fix: reference by `operationId` and response type name.

**AP-S-4 — Restating VELO Invariants in every spec.**
Symptom: each spec re-explains "money is integer cents".
Why bad: 120 specs × 7 invariants = 840 redundant restatements. When
an invariant changes, 120 places update.
Fix: reference by ID (I1, I2, etc.) per §2.5.

**AP-S-5 — Untestable acceptance criteria.**
Symptom: "looks good on mobile", "feels fast", "works".
Why bad: not validatable. Done state is undefined.
Fix: every criterion is a Y/N assertion. "Renders at 402px without
horizontal scroll." "Toast appears within 200ms after submit."

**AP-S-6 — Hardcoded Russian copy in spec instead of i18n key.**
Symptom: spec says "show 'Не удалось загрузить'".
Why bad: copy that ends up hardcoded in `.vue` violates the i18n rule
declared in ARCHITECTURE.md (all user-facing strings via `t('key')`).
Spec is supposed to be the source of i18n keys, not a place where copy
is stranded as inline strings.
Fix: spec lists the i18n key and the proposed Russian text, formatted
as the JSON entry to add to locale.

**AP-S-7 — Stale spec consumed by Claude Code.**
Symptom: spec status is `superseded` but Claude Code generates code
from it.
Why bad: wasted implementation; potentially deployed wrong screen.
Fix: only `active` specs in deliverable; `superseded` and `archived`
remain for history but flagged in INDEX.md.

### 11.5 Process Anti-Patterns

**AP-P-1 — Writing spec before mockup approved.**
Symptom: SCR-005 spec exists but the mockup is still in revision.
Why bad: spec references a moving target. If mockup changes, spec is
already stale.
Fix: §4 pipeline order — spec follows mockup approval.

**AP-P-2 — Editing token master via deliverable copy.**
Symptom: developer edits `01_deliverable/styles/variables.css` to add
a token.
Why bad: master at `02_design-system/tokens/` becomes stale. Next
sync overwrites the developer's change.
Fix: master is the single source of truth for tokens. Changes flow
master → copy.

**AP-P-3 — Skipping INDEX.md updates.**
Symptom: new spec created; `01_deliverable/screens/INDEX.md` not
updated.
Why bad: catalog drift. Hard to know what specs exist.
Fix: every spec addition/status change updates the local INDEX
immediately (§12).

**AP-P-4 — Generating Vue code from a draft spec.**
Symptom: Claude Code reads a `draft` spec and implements it.
Why bad: draft = not approved. Implementation may be discarded after
operator review.
Fix: Claude Code consumes only `active` specs.

**AP-P-5 — Methodology changes recorded only in chat.**
Symptom: operator and Cowork agree on a rule change in conversation,
but VELO-METHODOLOGY.md is not updated.
Why bad: future sessions can't see the agreement.
Fix: methodology changes go into the document with a Changelog entry
at the end.

### 11.6 Forbidden Constructs Quick Reference

| Construct | Where | Reason |
|---|---|---|
| Hardcoded hex outside `:root` | Any CSS file | Tokens only |
| `line-height: normal` | Any CSS file | Browser-dependent |
| `var() + Npx` (no calc) | Any CSS file | Invalid CSS |
| `--velo-{component}-*` | variables.css | Component-scoped only |
| `--velo-screen-width` | variables.css | Layout-scoped only |
| `@import` | variables.css | Goes to global.css |
| Lorem ipsum / placeholder names | Mockups | Use §7.6 sample data |
| Raw fetch() | Vue components | Use api/client.ts wrapper |
| Hardcoded Russian strings | Vue components | Use t() via vue-i18n |
| `parseFloat(price)` on money | Anywhere | Cents are integer; use utils/currency.ts |
| `viewMode` in permission check | Anywhere | Use `user.role`; see I3 |
| Browser timezone for practice dates | Anywhere | Use practice.timezone; see I2 |
| Direct Pinia state mutation | Anywhere | Use store actions |
| Spec section omitted | screen spec | Use N/A marker |

---

## 12. INDEX Maintenance Protocol

INDEX.md files are the navigational backbone. Without them, 120 screens
and 200+ tokens become a swamp. Discipline matters.

### 12.1 INDEX Files in the Project

| Path | Scope | Update frequency |
|---|---|---|
| `docs/INDEX.md` | Top-level map of `docs/` | End of sprint or major milestone |
| `docs/01_deliverable/screens/INDEX.md` | Spec catalog with statuses | Every spec change |
| `docs/02_design-system/INDEX.md` | DS state: tokens, components, assets, TODOs, iterations | Every DS change |
| `docs/02_design-system/assets/ASSETS-INDEX.md` | Every extracted asset with source node ID | Phase 1 only (rare updates) |
| `docs/03_mockups/INDEX.md` | Mockup files with approval status | Every mockup change |

### 12.2 Hybrid Update Strategy

**Local indexes** (the four lower-level ones) update **immediately**
after any change inside their scope. Cowork must update the index in
the same task that creates the underlying artifact. This is
non-optional.

**Top-level `docs/INDEX.md`** updates **at sprint boundaries** or major
milestones. It's a sweep through the local indexes producing a
high-level summary. This is a planned operation, typically once per
1-2 weeks.

### 12.3 Top-Level docs/INDEX.md Template

```markdown
# VELO docs — Master Index

Last updated: {ISO date}
Sprint reference: sprint-NN

## Folder Map

| Folder | Purpose | Local INDEX |
|---|---|---|
| 01_deliverable/ | Handoff package for developer | screens/INDEX.md |
| 02_design-system/ | DS master source | INDEX.md |
| 03_mockups/ | Visual workspace | INDEX.md |
| 04_methodology/ | This methodology | — |
| 05_roadmap/ | Plans and tracking | ROADMAP.md |
| 06_project-inputs/ | External references | — |

## Status Summary

- Tokens: M of N defined (P % complete)
- Components: M of N built (P % complete)
- Mockups: M of ~120 done (P % complete)
- Specs: M of ~120 written (P % complete)
- Implementation (frontend): see project ROADMAP

## Open TODOs (high-level)

- ...

## Recent Changes (since last update)

- {date} — {summary}
- ...
```

### 12.4 Design-System INDEX Template

`docs/02_design-system/INDEX.md`:

```markdown
# VELO Design System — Index

Last updated: {ISO date}
Iteration: {N}

## Token Status

| Group | Tokens defined | Source | Missing |
|---|---|---|---|
| Colors / Primitives | 12 | DS frame + mining | — |
| Text semantic | 5 | mining | — |
| Background semantic | 4 | mining | --velo-bg-overlay |
| Borders | 4 | mining | — |
| States | 0 | — | All 5 (success, error, warning, info, destructive) |
| Interactive | 0 | — | All (focus-ring, disabled, hover, active) |
| Spacing | 11 | mining | — |
| Radius | 4 | mining | --velo-radius-full |
| Shadows | 1 | mining | --velo-shadow-card, --velo-shadow-modal |
| Font sizes | 7 | mining | — |
| Weights | 1 | mining | medium, semibold |

## Component Status

| Component | Tier | Status | Styleguide | Vue file |
|---|---|---|---|---|
| VButton | 1 | ✅ done | ✅ | frontend/src/components/ui/VButton.vue |
| VInput | 1 | ✅ done | ✅ | frontend/src/components/ui/VInput.vue |
| VCheckbox | 1 | 🔄 in progress | — | — |
| PracticeCard | 2 | ⬜ pending | — | — |
| ... | | | | |

## Asset Index

See assets/ASSETS-INDEX.md for full asset list with source node IDs.
Asset count: M icons, N screenshots.

## Open TODOs

- [ ] Dark theme — deferred, architecture ready
- [ ] --velo-state-* tokens — MISSING placeholders pending Figma
- [ ] --velo-shadow-card — confirm value with operator
- ...

## Iteration Log

| Iteration | Date | What was done |
|---|---|---|
| 1 | 2026-05-17 | Initial Figma audit, token inventory, folder setup |
| 2 | ... | ... |
```

### 12.5 Screens INDEX Template

`docs/01_deliverable/screens/INDEX.md`:

```markdown
# Screens — Index

Last updated: {ISO date}

| SCR ID | Name | Role | Route | Status | Mockup | Spec | Priority | Notes |
|---|---|---|---|---|---|---|---|---|
| SCR-001 | user-dashboard | user | / | active | ✅ | ✅ | P1 | — |
| SCR-002 | user-practice-detail | user | /practice/:id | active | ✅ | ✅ | P1 | — |
| SCR-003 | master-apply | master | /master/apply | draft | ✅ | 🔄 | P2 | Operator review pending |
| SCR-004 | admin-master-review | admin | /admin/masters/:id | draft | ✅ | 🔄 | P3 | — |

Status legend:
- ✅ ready / approved
- 🔄 in progress / awaiting review
- ⛔ blocked
- — not yet started

## Summary
- Total specs: 4
- active: 2
- draft: 2
- superseded: 0
- archived: 0
```

### 12.6 Mockups INDEX Template

`docs/03_mockups/INDEX.md`:

```markdown
# Mockups — Index

Last updated: {ISO date}

## User block

| Screen file | Status | Approved on | Notes |
|---|---|---|---|
| user/user-dashboard.html | ✅ approved | 2026-05-22 | — |
| user/user-practice-detail.html | ✅ approved | 2026-05-22 | — |
| user/user-bookings.html | 🔄 in revision | — | Spacing too tight |
| user/user-calendar.html | ⬜ pending | — | — |

## Master block
...

## Admin block
...
```

---

## 13. Versioning and Changelog Discipline

### 13.1 Methodology Versioning

This document is versioned via the anchor at the bottom of the file.
Format: `[VELO-METHODOLOGY.md | vM.m | YYYY-MM-DD]`.

- Major version (M) bump: structural change to pipeline, gate criteria,
  or spec template.
- Minor version (m) bump: clarifications, new anti-patterns added,
  templates refined.

Every version bump includes a Changelog entry at the bottom of the
document (§13.4).

### 13.2 Token File Versioning

`variables.css` and `global.css` are not numbered. They evolve via git.
The master copy in `02_design-system/tokens/` is the source of truth.
The deliverable copy in `01_deliverable/styles/` is regenerated.

If a breaking change is made (a token removed or renamed), it is logged
in `02_design-system/INDEX.md → Iteration Log` and in this methodology's
Changelog if relevant.

### 13.3 Spec Versioning

Per §8.9: in-place edits within a SCR-NNN, status transitions via
front-matter, history via git. The Changelog at the end of each spec
records material changes for human readers.

### 13.4 This Document's Changelog

```markdown
## Methodology Changelog

- 2026-05-17 — **v1.2** — Cross-pollination from operator's v3 Figma-native methodology
  (`06_project-inputs/VELO_METHODOLOGY.md`). Three targeted amendments, all
  applicable to our HTML-only pipeline (after Sprint 1 Figma extraction completes,
  Figma is read-only reference forever — methodology stays HTML/CSS-centric):
  - §6.4 — **Promote-not-invent** sequence added to MISSING Token Protocol.
    Before declaring a token MISSING with a neutral placeholder, mockup-mine
    SACRED frames for the value first. Placeholder is last resort, with
    explicit "not found in any SACRED frame" provenance comment. Source:
    v3 §10 Three-Layer Pipeline → "Promote-not-invent" principle adapted to
    our extraction model.
  - §10.3 — **Adjacent re-probe** added to STYLEGUIDE GATE. Single-file
    styleguide means component changes can regress unrelated groups via
    shared `<style>` / data fixtures. Operator spot-checks ≥2 unrelated
    groups after each change. Source: v3 R5 (re-probe ALL touched plus
    adjacent state).
  - §10.4 — **Adjacent re-probe** added to MOCKUP GATE. Re-open
    previously-approved adjacent mockup in same role-block during gate.
    Catches shared-token regressions across sprints. Source: same as above.
  - Companion: `02_design-system/FIGMA-OPERATIONS-GUIDE.md` extended with
    L-32 (no-throw return), L-37 (chunked manifest reads), AP-6 (font
    loading per call) — these apply during Sprint 1 Figma extraction only.
- 2026-05-17 — **v1.1** — Validation pass against `api-openapi.json`,
  `ARCHITECTURE.md` (frontend root), and `CC-REPORT-2.txt`. Findings
  recorded in `06_project-inputs/VALIDATION-REPORT-2026-05-17.md`.
  Changes:
  - §2.5 I2 — expanded to cover `user.timezone` in addition to
    `practice.timezone`; noted OpenAPI types `timezone` as plain
    `string` (no IANA pattern constraint).
  - §2.5 I4 — added implementation note: `VeloError` is a code-only
    contract, not declared in OpenAPI; only `HTTPValidationError`
    (Pydantic 422) is formal.
  - §2.5 I5 — fixed canonical startParam namespace to 4 patterns:
    `open_practice__{uuid}`, `open_master__{uuid}`,
    `open_booking__{uuid}`, `open_topup`. Reference to
    `Window.Telegram.WebApp.initDataUnsafe.start_param` API path
    added.
  - §2.5 I6 — replaced wrong state name `offered` with the canonical
    `notified` (matches `frontend/src/api/types.ts` `WaitlistStatus`
    and OpenAPI `WaitlistEntryResponse.notified_at`). Added explicit
    state diagram and transition list.
  - §2.5 — added new **I8 (Status enums are code-only contracts)**
    documenting that only `UserRole`, `SemaphoreResult.status`,
    `SemaphoreResult.criticality`, and `CreateReportRequest.target_type`
    are declared as enums in OpenAPI; all other status fields are
    plain `string` and their values live only in
    `frontend/src/api/types.ts`. Full table of code-only unions
    included. Required mitigation: exhaustive `switch` with explicit
    error branch for unknown values.
  - §3 — corrected `frontend/docs/ARCHITECTURE.md` →
    `frontend/ARCHITECTURE.md` (canonical file lives at the
    frontend root; `frontend/docs/` does not exist).
  - §6.6 Tier 2 — `PracticeCard` statuses enumerated (per I8
    `PracticeStatus`); `BookingCard` cross-referenced to
    `AttendanceBookingStatus`; `WaitlistCard` updated to all 6
    `WaitlistStatus` values (was 4, including wrong `offered`);
    `FeedbackWidget`, `MoodWidget`, `MasterStatusBadge`,
    `WithdrawalRow` cross-referenced to I8; `PromoRow` clarified as
    a UI abstraction (no formal `PromoStatus` enum exists).
  - §8.4 — expanded Section 5 guidance (require explicit initial
    query params + pagination strategy for list_* endpoints);
    Section 7 guidance (require `partial-error` state for
    multi-endpoint screens); Section 9 guidance (require explicit
    empty / error / partial-error copy in i18n); Section 11
    guidance (baseline error code table with 7 standard rows).
  - §8.7 — Waitlist FSM block updated to match I6 (`notified`
    semantics, explicit transition list, source-of-truth reference).
  - §14 — corrected `frontend/docs/ARCHITECTURE.md` →
    `frontend/ARCHITECTURE.md`.
- 2026-05-17 — v1.0 — Initial methodology authored. Replaces three
  universal methodologies (DS, LIVEMOCKUP, HANDOFF) with a unified
  VELO-specific document.
```

---

## 14. What This Methodology Does NOT Cover

Clarity about scope prevents the methodology from being misused as a
catch-all. The following are explicitly out of scope and should be
addressed in other documents.

| Topic | Where it belongs |
|---|---|
| Frontend code rules (Vue syntax, naming, file location) | `frontend/ARCHITECTURE.md` |
| API contract design (endpoints, schemas) | Backend team, OpenAPI |
| Product strategy, feature prioritization, business value | Product documents (outside this folder) |
| Sprint planning, time estimates, burndown | `docs/05_roadmap/sprint-NN.md` |
| Unit testing, E2E testing approach | Frontend testing strategy doc (not yet written) |
| Deployment, environments, release procedures | `frontend/docs/ENVIRONMENT.md` |
| Accessibility audit (WCAG specifics, screen-reader testing) | Not yet in scope; future addition |
| Performance budgets (bundle size, FCP, LCP targets) | Not yet in scope; future addition |
| Dark theme | Deferred per §2.5 I7; architecture ready |
| Internationalization beyond Russian + English | Not yet in scope |
| Multi-product reuse of the DS | Possible per §3 design (02_design-system is self-contained); not currently a goal |

If a question arises that this methodology does not answer, the operator
makes a decision and either:
1. Records it in `docs/05_roadmap/decisions.md` (project-specific), or
2. Amends this methodology if the question is reusable.

---

## Anchor

```
[VELO-METHODOLOGY.md | v1.2 | 2026-05-17]
Single source of truth for VELO design and handoff work.
Replaces three universal methodologies with one project-specific document.
v1.1: validation pass against api-openapi.json + ARCHITECTURE.md + CC-REPORT-2.
v1.2: cross-pollination from operator's v3 Figma methodology — promote-not-invent
in §6.4, adjacent re-probe in §10.3/§10.4. Companion FIGMA-OPERATIONS-GUIDE.md
extended with L-32/L-37/AP-6 for Sprint 1 Figma extraction.
Audience: operator, Cowork, Claude Code, frontend developer.
Location: D:\02_Projects\velo\docs\04_methodology\VELO-METHODOLOGY.md
```
