# Live Mockup Methodology

> Universal methodology for building single-file clickable HTML mockups.
> Output is one self-contained HTML file with a device preview shell, a
> Navigation Map, microinteractions, realistic data, and a defined level
> of fidelity. No frameworks, no build step, no external dependencies
> beyond versioned CDN URLs (Google Fonts and similar are OK).
>
> Tools-agnostic, framework-agnostic. The methodology is the instruction.

---

## §0. Principles (invariants)

| # | Rule | Why |
|---|---|---|
| 1 | **Output is one self-contained HTML file.** CSS and JS inline. | Stable artifact; the user receives one file, not a folder. |
| 2 | **Device preview shell is mandatory** (phone / tablet / desktop wrapper, or a documented shell profile). | Without the shell it is just HTML, not a mockup. |
| 3 | **Realistic data only.** No Lorem ipsum, no placeholder names. | A mockup should look like a product, not a stub. |
| 4 | **Every action produces feedback** (toast, state change, or screen transition). | Otherwise it is unclear whether the click registered. |
| 5 | **Navigation Map is mandatory** for Walkthrough and Prototype levels (📍 button + popup with screen tree). | Visibility of all paths; explicit endpoint marking. |
| 6 | **Test protocol is mandatory before delivery** (level-appropriate quality gates, 0 BLOCKER, ≤ 2 MAJOR). | Quality gate; sanitize → fix cycle on FAIL. |
| 7 | **Mockup level is declared in the Brief** (Demo / Walkthrough / Prototype) and drives scope. | Without a declared level, Demo work scope-creeps into Prototype work. |
| 8 | **Accessibility floor is enforced** (semantic HTML, visible focus, keyboard reachability, no traps). | A mockup that fails the floor cannot be usability-tested. |

---

## §1. Pipeline (the map)

```
User brief
        │
        ▼
BRIEF — collect requirements (purpose, level, screens, interactions, data plan)
        │
        ▼
DESIGN — define tokens (colors / typography / radius) + interaction map (Saffer 4-part)
        │
        ▼
BUILD — generate HTML with shell + screens (level-appropriate)
        │
        ▼
POLISH — animations, feedback, realistic data, state triad (loading/empty/error)
        │
        ▼
TEST — level-appropriate quality gates, 0 BLOCKER, ≤ 2 MAJOR
        │
        ▼
DELIVER — UAT checklist + versioned final file
        │
        ▼  (if file gets corrupted later)
        ▼
SANITIZE — recover from CDN injection / truncation / encoding
        │
        ▼
TEST → DELIVER
```

The phases are described in detail in §17.

---

## §2. Mockup Levels

Methodology applies to projects of vastly different complexity. Pretending a
single-flow pitch demo and a fifteen-screen handoff prototype share the same
workflow is how Lean projects die under enterprise scope. The axis that
matters is **purpose × interactivity**, because purpose dictates audience and
interactivity dictates scope.

Three levels. Pick one in the Brief; do not float.

### 2.1 Level matrix

| Property | DEMO | WALKTHROUGH | PROTOTYPE |
|---|---|---|---|
| **Audience** | Pitch / stakeholder show | Usability test participants | Developers, handoff |
| **Screens** | 1–3 | 5–15 | 15+ |
| **Flows** | single happy-path | multiple flows, dead-ends marked | full clickable system |
| **Shell** | required, baseline only | required, full | required, full + optional shell profile |
| **Navigation Map** | optional | required | required |
| **Endpoint pattern** | optional | required | required |
| **State triad (loading/empty/error)** | happy-path only | empty state required per list | all three required per data-driven view |
| **Realistic data** | required (believable values) | required (believable values + spread) | required (values + spread + edge cases per §9.4) |
| **Microinteractions** | hover + screen transition | full Saffer model (§8) | full Saffer model + persisted state (§12) |
| **Accessibility floor** | applies (§11) | applies (§11) | applies (§11) |
| **Quality gates** | Demo subset (33 checks) | Full set + state-triad subset (68 checks) | Full set + handoff checks (76 checks) |
| **Performance budget (§15)** | ≤ 200 KB | ≤ 500 KB | ≤ 1 MB |
| **Deliverable extras** | mockup file only | mockup + UAT checklist | mockup + UAT checklist + interaction-map comment block (§12.3) |

### 2.2 Level triggers (when to step up)

| From → To | Trigger |
|---|---|
| Demo → Walkthrough | Stakeholder asks "can users try it themselves?" |
| Demo → Walkthrough | Mockup will be sent to a usability-testing tool |
| Walkthrough → Prototype | Engineering is starting the build and needs handoff |
| Walkthrough → Prototype | More than ~15 distinct screens accumulate |
| Walkthrough → Prototype | Data-driven views appear that need empty + error states distinct |

### 2.3 Anti-triggers (when NOT to step up)

| Symptom | Why this is NOT a reason to step up |
|---|---|
| "Let's add more screens just in case" | Adds quality-gate load; cut scope instead |
| "The CEO wants it to look more polished" | Polish belongs in POLISH phase, not a level change |
| "We might do a usability test someday" | Step up when the test is scheduled, not before |
| "More interactivity feels better" | Interactivity costs time; only add what supports the purpose |

### 2.4 Level is declared in Phase 1 (BRIEF)

The first question is not "what screens?". It is "what is this mockup
**for**?". From the answer the level is derived, and from the level the
quality gates and budget are derived. See §17.1.

---

## §3. Device Preview Shell

The shell wraps mockup content and adds device switching, zoom, and the
Navigation Map. The same shell architecture supports plain mobile/tablet/
desktop and specialized **shell profiles** (Telegram WebApp, PWA-like, etc.).

### 3.1 Frame baselines (2026)

| Device | Width | Height | Frame radius | Notes |
|---|---|---|---|---|
| Phone (default) | 393 | 852 | 44px | iPhone 15/16/16 Pro CSS viewport |
| Phone (large) | 430 | 932 | 44px | iPhone 15/16 Plus / Pro Max |
| Tablet | 820 | 1180 | 24px | iPad-class CSS viewport |
| Desktop | 1280 | 800 | 12px | Generic laptop |

The older `390×844` (iPhone 13/14) baseline is acceptable but no longer the
recommended default. Custom widths override the baseline.

### 3.2 Structure

```
<!DOCTYPE html>
├── <head>
│   ├── viewport meta (with viewport-fit=cover for safe-area support)
│   ├── Google Fonts <link>
│   └── <style>
│       ├── Shell CSS (toolbar, frame)
│       ├── Navigation Map CSS
│       ├── Mobile Toolbar CSS
│       ├── Clickability Fix CSS
│       ├── Safe-area CSS (env(safe-area-inset-*))
│       └── Mockup CSS (content styles)
└── <body>
    ├── Preview Toolbar (fixed, top:0)
    │   └── Map Button
    ├── Preview Container (below toolbar)
    │   └── Device Frame
    │       ├── Notch / Dynamic Island (phone only)
    │       ├── Screen (flex column, overflow:auto)
    │       │   └── .mockup-content (flex:1, flex column)
    │       │       └── .screen.active (flex:1, flex column)
    │       │           ├── header (sticky top)
    │       │           ├── main (flex:1)
    │       │           └── tab-bar (sticky bottom)
    │       └── Home Indicator (phone only)
    ├── Navigation Map Popup
    ├── Toast Container
    └── <script> (controller + nav map + URL hash router per level — see §12.1)
```

### 3.3 Shell CSS variables

```css
:root {
  --shell-bg: #0f172a;
  --shell-surface: #1e293b;
  --shell-border: #334155;
  --shell-text: #ffffff;
  --shell-text-dim: rgba(255,255,255,0.5);
  --shell-accent: #3b82f6;
  --shell-accent-glow: rgba(59,130,246,0.3);

  --frame-bg: #374151;
  --frame-radius-phone: 44px;
  --frame-radius-tablet: 24px;
  --frame-radius-desktop: 12px;
  --frame-padding: 12px;

  --screen-radius-phone: 38px;
  --screen-radius-tablet: 16px;
  --screen-radius-desktop: 8px;
}
```

### 3.4 Safe-area handling

Modern phones have notches, Dynamic Islands, and home indicators. Inside the
`.device-screen`, sticky elements respect the safe area:

```css
.header {
  padding-top: max(12px, env(safe-area-inset-top));
}
.tab-bar {
  padding-bottom: max(8px, env(safe-area-inset-bottom));
}
```

For the mockup-inside-a-shell case, `env()` returns 0 (we are not against the
real notch), but the pattern is correct for when the mockup is later rendered
on a real device. The viewport meta must include `viewport-fit=cover`.

### 3.5 Keyboard shortcuts

| Key | Action |
|---|---|
| `1` | Phone (393) |
| `2` | Tablet (820) |
| `3` | Desktop (1280) |
| `+` / `=` | Zoom in |
| `-` | Zoom out |
| `0` | Reset zoom to 100% |
| `M` | Open Navigation Map |
| `Tab` / `Shift+Tab` | Move keyboard focus (a11y, §11) |
| `Esc` | Close popup / Navigation Map |

### 3.6 Shell profiles

A **shell profile** is a named variant of the shell that imitates a specific
embedding environment. Profiles do not replace the base shell — they extend it
with environment-specific UI affordances and theme bindings.

| Profile | Imitates | Width × Height | Notable additions |
|---|---|---|---|
| `default-phone` | Generic mobile | 393×852 | — |
| `default-tablet` | Generic tablet | 820×1180 | — |
| `default-desktop` | Generic desktop | 1280×800 | — |
| `telegram-webapp` | Telegram Mini App | 402×874 | MainButton, BackButton, theme params as CSS vars (§3.7), BottomSheet drag behavior may be stubbed |
| `pwa-standalone` | Installed PWA | 393×852 | No browser chrome; `theme-color` meta; status bar tinting |

Only declare a profile when the mockup will actually be embedded in that
environment. Otherwise use the default profile for the device.

### 3.7 Telegram WebApp profile — minimum requirements

When `shell-profile: telegram-webapp` is declared:

- Theme params exposed as CSS variables: `--tg-theme-bg-color`,
  `--tg-theme-text-color`, `--tg-theme-button-color`,
  `--tg-theme-button-text-color`, `--tg-theme-accent-text-color`,
  `--tg-theme-hint-color`, `--tg-theme-section-bg-color`. Defaults provided
  for both light and dark.
- A persistent MainButton at the bottom of the viewport (above any
  safe-area inset), full-width, using `--tg-theme-button-color`.
- An optional SecondaryButton position (left/right of MainButton).
- A BackButton in the top-left, hidden on the root screen.
- BottomSheet behavior is stubbed: the shell looks like an embedded sheet
  but is not draggable — the mockup runs in a fixed window.

These are imitations, not the live Telegram SDK. The mockup remains a single
static HTML file with no external Telegram dependencies.

---

## §4. Layout — critical rules

The shell only works if these five patterns are correct. Any one missing
produces a visible bug.

### 4.1 Container alignment

```css
/* CRITICAL: flex-start prevents top clipping on tall devices */
.preview-container {
  display: flex;
  align-items: flex-start;  /* NOT center */
  justify-content: center;
  overflow: auto;
}

/* CRITICAL: margin: auto centers when frame fits in viewport */
.device-frame {
  margin: auto;
}
```

**Why:** `align-items: center` clips the top when the frame is taller than
the viewport. `margin: auto` centers when the frame is shorter than the
viewport. Both behaviors are needed simultaneously.

### 4.2 Sticky vs fixed (inside `.device-screen`)

| Element | Correct | Wrong |
|---|---|---|
| Header | `position: sticky; top: 0` | `position: fixed` |
| Tab Bar | `position: sticky; bottom: 0` | `position: fixed` |
| Sidebar | `position: sticky; top: 0` | `position: fixed` |
| Telegram MainButton | `position: sticky; bottom: 0` | `position: fixed` |
| Popup overlay | `position: fixed` (OK, outside device frame) | — |

**Why:** `position: fixed` is relative to the viewport, not `.device-screen`.
Header / tab-bar with `fixed` escape the device frame.

### 4.3 Flex layout chain

The chain from `.device-screen` down to `.tab-bar` must be unbroken. Any
missing `flex: 1` lets the tab-bar float upward.

```css
.device-screen {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
}

.mockup-content {
  min-height: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.screen.active {
  display: flex;
  flex: 1;
  flex-direction: column;
}

.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
}

.main {
  flex: 1;  /* pushes tab-bar to bottom */
}

.tab-bar {
  position: sticky;
  bottom: 0;
  z-index: 100;
  background: white;
}
```

### 4.4 Clickability fix

Children of a clickable container block the parent's `onclick`. Required CSS:

```css
.alert-card[onclick] *,
.stat-card[onclick] *,
.card[onclick] *,
.metric-row[onclick] *,
.list-item[onclick] *,
table tr[onclick] * {
  pointer-events: none;
}

/* Re-enable for nested interactive elements */
button, input, select, textarea, a,
.checkbox, .doc-checkbox {
  pointer-events: auto;
}
```

**Why:** Text / icons / progress bars inside a card intercept clicks and
prevent the card's `onclick` from firing.

### 4.5 Scroll reset

`scrollTop = 0` alone is not reliable across browsers. Use aggressive reset
on every device switch and navigation:

```javascript
function resetScroll() {
  const screen = document.getElementById('deviceScreen');
  screen.scrollTop = 0;
  screen.scrollTo({ top: 0, behavior: 'instant' });
}

resetScroll();
requestAnimationFrame(resetScroll);
setTimeout(resetScroll, 100);
setTimeout(resetScroll, 400);
```

---

## §5. Forms Pattern

Use `div` + `onclick`, NOT `form` + `onsubmit`.

### 5.1 Correct

```html
<div class="form">
  <input type="email" value="user@example.com" readonly>
  <button type="button" onclick="handleLogin()">Login</button>
</div>
```

### 5.2 Wrong

```html
<form onsubmit="handleLogin(event)">
  <button type="submit">Login</button>
</form>
```

**Why:** Form `onsubmit` handlers are unreliable inside the device preview
context (page reload, propagation issues).

### 5.3 Inputs respect the a11y floor

Inputs use real `<input>` elements (not `<div contenteditable>`) and have
associated `<label>` — see §11. This is both an accessibility requirement and
a tab-order requirement.

---

## §6. Navigation Map

A 📍 Map button in the toolbar that opens a popup showing the full screen
tree. Mandatory for Walkthrough and Prototype levels (invariant 5).

### 6.1 Popup contains

| Section | Content |
|---|---|
| Stats | screens count, full paths count, endpoints count |
| Legend | traffic light: 🟢 screen, 🟡 tab, 🔴 endpoint |
| Tree | L0 (entry) → L1 (hub) → L2 (list) → L3 (detail/tab/endpoint) with collapsible sections |

### 6.2 Tree item types

| Type | Icon | Action | Toast |
|---|---|---|---|
| Screen | 🟢 (green dot) | navigate to screen | none or transition |
| Tab | 🟡 (yellow dot) | navigate to parent + toast | `🟡 Tab "{name}" — switches content` |
| Endpoint | 🔴 (red dot) | navigate to parent + toast | `📌 {name} — final point` |

### 6.3 Default state

All sections collapsed by default. User opens what they need.

### 6.4 Level badges

| Badge | Meaning |
|---|---|
| L0, L1, L2, L3 | Tree depth |
| HUB | Section entry hub (L1) |
| TAB | Tab inside a screen |
| END | Endpoint (no further navigation) |

### 6.5 Compatibility with industry vocabularies

The L0–L3 / HUB / TAB / END notation is internal to this methodology. Teams
familiar with Jesse James Garrett's visual vocabulary for IA diagrams can
read the Navigation Map directly — the concepts (hierarchy depth, hub pages,
dead ends) are the same, the symbols differ. Use the internal notation; the
mention is only for orientation when handing the map to an IA practitioner.

---

## §7. Endpoint Pattern

The problem: users click elements expecting navigation, but the mockup
doesn't have that screen implemented. They think it is a bug.

The solution: a clear Toast that marks the element as a planned-feature
endpoint.

### 7.1 Toast format

```
📌 {Element Name} — final point
```

(Localize per project: in Russian-language projects use `финальная точка`.)

### 7.2 When to use

| Situation | Toast |
|---|---|
| Card without detail screen | `📌 {Card Title} — final point` |
| Tab without content | `📌 {Tab Name} — final point` (or yellow tab toast) |
| Button without action screen | `📌 {Button Label} — final point` |
| Metric without drill-down | `📌 {Metric Name} — final point` |
| Feature placeholder | `📌 {Feature Name} — final point` |

### 7.3 Endpoint counting (for Navigation Map stats)

| Stat | Meaning |
|---|---|
| Screens | full screens with content |
| Full paths | complete navigation chains L0 → L3 |
| Endpoints | every endpoint toast in the file |

### 7.4 Endpoints and testability

Endpoints exist so a usability-test participant does not confuse "not
implemented" with "broken". This directly improves the misclick-rate signal
when the mockup is run through testing tools — see §18.

---

## §8. Microinteractions (Saffer 4-part model)

Every microinteraction in the mockup decomposes into **Trigger → Rules →
Feedback → Loops/Modes**. This is Dan Saffer's standard framework
(*Microinteractions: Designing with Details*, 2013), used because it gives
the methodology a checkable grammar instead of a list of patterns.

### 8.1 The four parts

| Part | What it is | Mockup question |
|---|---|---|
| **Trigger** | What starts the interaction (user click, system event, time) | What does the user do, or what happens, to start this? |
| **Rules** | The logic that runs after the trigger | What does the mockup actually do — what changes? |
| **Feedback** | How the user is informed of the result | Toast? State change? Transition? |
| **Loops & Modes** | Repetition, duration, alternate states | Does it repeat? Is there an alt-state (loading, edit mode)? |

Every clickable element in the mockup must answer the first three parts.
Loops & Modes may be "none" — most simple click→toast interactions have no
repetition or alt-state, and that is fine. If "Feedback" is empty, the
element is broken (invariant 4).

### 8.2 Timing guidelines

| Type | Duration | Easing |
|---|---|---|
| Micro (hover) | 150–250ms | `ease` |
| Standard | 250–400ms | `ease-out` |
| Complex | 400–600ms | `cubic-bezier` |

```css
:root {
  --ease-standard:   cubic-bezier(0.4, 0, 0.2, 1);  /* Material */
  --ease-decelerate: cubic-bezier(0, 0, 0.2, 1);    /* Enter */
  --ease-accelerate: cubic-bezier(0.4, 0, 1, 1);    /* Exit */
}
```

### 8.3 Performance — animate transform / opacity only

| Property | GPU | Recommendation |
|---|---|---|
| transform | ✅ | always |
| opacity | ✅ | always |
| box-shadow | ⚠️ | OK for hover |
| background | ⚠️ | OK for state |
| width / height | ❌ | avoid |
| margin / padding | ❌ | avoid |

### 8.4 Hover patterns (Trigger: hover; Rules: lift; Feedback: shadow)

```css
/* Card lift */
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.12);
}

/* Button press */
.btn:hover  { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.btn:active { transform: scale(0.98) translateY(0); }

/* Input focus — also doubles as a11y focus indicator (§11) */
.input:focus,
.input:focus-visible {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  outline: none;
}
```

### 8.5 Toast system (Feedback for actions without screen change)

```javascript
function showToast(message, type = 'info', duration = 3000) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.setAttribute('role', 'status');     // a11y (§11)
  toast.setAttribute('aria-live', 'polite');
  toast.textContent = message;
  document.body.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}
```

```css
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%) translateY(100px);
  background: #333;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  opacity: 0;
  transition: all 0.3s ease;
  z-index: 2000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.toast.show {
  transform: translateX(-50%) translateY(0);
  opacity: 1;
}
```

### 8.6 Loops & Modes

| Pattern | Where it lives |
|---|---|
| Loading spinner | replaces button label during async simulation |
| Skeleton shimmer | placeholder cards / rows during load state (§10) |
| Polling loop | not used in mockups (no real backend) |
| Edit mode | screen flag, e.g. `.screen[data-mode="edit"]` |
| Selection mode | multi-select state in lists |

### 8.7 Screen transitions

```css
.screen { display: none; opacity: 0; }
.screen.active {
  display: block;
  animation: fadeIn 0.25s ease forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### 8.8 Popup / Modal

Overlay with `position: fixed` (OK outside `.device-screen`), centered
content with `transform: scale(0.9) → scale(1)` on open. Body scroll lock via
`document.body.style.overflow = 'hidden'`. Focus is moved into the modal and
trapped while open; Esc closes (§11).

---

## §9. Realistic Data

### 9.1 Data hierarchy

```
Live data > Real data > Realistic-looking > Dummy
```

| Type | Use |
|---|---|
| Live | Testing with real users on a real backend |
| Real | Demo with production data |
| Realistic | Default for mockups |
| Dummy | Layout only (last resort) |

### 9.2 Believability rules

| Rule | What it means |
|---|---|
| Believable values | Names look like names, prices look like prices, addresses look like addresses |
| Believable spread | Realistic distribution (not all "10% off") |
| Believable entities | Each record makes sense as a whole (no Dr. born 15 years ago) |
| Believable relations | Connections are logical (manager assigned to relevant team) |

### 9.3 Bad vs good examples

| ❌ Wrong | ✅ Correct |
|---|---|
| Lorem ipsum dolor | Domain-relevant copy in the target language |
| John Doe | Real-style names for the locale |
| 12345 (price) | Locale-formatted price (`45,990 ₽` / `$45.99` / `€45,99`) |
| placeholder.jpg | Real image or branded placeholder service |
| user@example.com | `name.surname@plausible-domain.tld` |
| 5 min ago | Localized relative time |

### 9.4 Edge cases (Prototype level — required; lower levels — recommended)

A mockup that only shows median data passes the eye but fails real users.
Include at least one of each:

| Edge case | Example | Why it matters |
|---|---|---|
| Long name | "Constantine Augustopoulos-Whitmore" | Layout overflow / truncation bugs |
| Very long word | "Polypropylhexylmethylcarbamate" | Word-break behavior |
| Zero count | "0 items in cart" | Triggers empty state (§10) |
| Negative number | "−$1,247.50" overdraft | Sign rendering, color rules |
| Very large number | "1,234,567 followers" | Truncation / abbreviation rules |
| RTL string | Hebrew / Arabic name in a list | Bidirectional text rendering |
| Emoji in field | "Sarah 🌸 K." | Font fallback, line height |
| Missing avatar | Initials fallback | Image error handling |
| Long list | 50+ rows | Virtual scroll or pagination kicks in |

### 9.5 Placeholder image services

| Type | Service | Pattern |
|---|---|---|
| Avatars | Pravatar | `https://i.pravatar.cc/150?img={1-70}` |
| Random users | RandomUser | `https://randomuser.me/api/` |
| Products / abstract | Placehold | `https://placehold.co/400x300/EEE/999?text=Product` |
| Photo random | Picsum | `https://picsum.photos/400/300?random={n}` |

### 9.6 Format patterns

| Pattern | Example |
|---|---|
| Short date | 21.01.2026 |
| Medium date | January 21, 2026 |
| With time | 21.01.2026, 14:30 |
| Relative | 5 min ago |
| Money | `(value).toLocaleString(locale) + currency` |

---

## §10. State Triad — Loading / Empty / Error

Every data-driven view in the mockup has three states beyond the happy
"content" state. Pretending only the happy state exists is the classic
mockup failure mode: a usability test participant lands on an empty
dashboard and cannot tell whether the system is loading, empty, or broken.

### 10.1 The four states

| State | When | What the user sees |
|---|---|---|
| **Loading** | Data being fetched (simulated) | Skeleton, spinner, or progress |
| **Empty** | Data returned, zero items | Heading + body + next-step button |
| **Error** | Data fetch failed (simulated) | Heading + explanation + retry/escape |
| **Content** | Data returned, ≥ 1 item | The actual view |

### 10.2 Empty state requirements

An empty state is never just blank. It always has:

- **Heading** — what is not here ("No tasks yet", not "Empty")
- **Body** — 1–2 lines explaining why and what to do
- **Primary action** — the next logical step ("Create your first task")
- **Optional secondary** — alternate route ("Import from CSV")

Subtypes:

| Subtype | Trigger | Heading style |
|---|---|---|
| First-use | New user, never created data | Welcoming, instructional |
| Filtered | Search/filter yielded nothing | "No results for {query}" + "Clear filters" |
| Cleared | User finished all items | Congratulatory, optional |

### 10.3 Error state requirements

Error states explain in plain language, then offer recovery:

- **Heading** — "Couldn't load {thing}", not "Error 500"
- **Body** — what likely went wrong (network / server / permission)
- **Primary action** — retry
- **Secondary action** — escape route (back, support)

For network-failure cases, the message acknowledges connectivity and the
retry uses the same control the user just clicked.

### 10.4 Loading state requirements

Loading states confirm something is happening:

- **Skeleton** for content that has known shape (cards, rows, charts)
- **Spinner** for indeterminate actions (button submits)
- **Progress bar** when duration is known
- Loading state never shows "No items" — that confuses users into thinking
  the empty state is the loading state

### 10.5 Level applicability

| State | Demo | Walkthrough | Prototype |
|---|---|---|---|
| Loading | optional | required on initial screen | required on every data view |
| Empty | optional | required for every list | required for every list + filter |
| Error | not required | optional | required for at least one critical action |

### 10.6 Visual templates

```html
<!-- Empty state -->
<div class="state-empty" role="status">
  <div class="state-icon">📭</div>
  <h3 class="state-heading">No tasks yet</h3>
  <p class="state-body">Tasks you create will appear here.</p>
  <button class="btn btn-primary" onclick="createTask()">Create your first task</button>
</div>

<!-- Error state -->
<div class="state-error" role="alert">
  <div class="state-icon">⚠️</div>
  <h3 class="state-heading">Couldn't load tasks</h3>
  <p class="state-body">Check your connection and try again.</p>
  <button class="btn btn-primary" onclick="retryLoad()">Retry</button>
  <button class="btn btn-text" onclick="navigate('home')">Go to home</button>
</div>

<!-- Loading state -->
<div class="state-loading" aria-live="polite" aria-busy="true">
  <div class="skeleton skeleton-card"></div>
  <div class="skeleton skeleton-card"></div>
  <div class="skeleton skeleton-card"></div>
</div>
```

---

## §11. Accessibility Floor

A mockup is not a production product, so full WCAG AA conformance is out of
scope. But a mockup that fails the floor cannot be usability-tested,
keyboard-navigated by power-users, or handed to engineering as a credible
artifact. The floor is the minimum.

### 11.1 What the floor requires

| # | Rule | Why it matters |
|---|---|---|
| A1 | Use semantic HTML elements (`<button>`, `<a href>`, `<input>`, `<nav>`, `<main>`) for their intended purpose | Native focusability and screen-reader semantics |
| A2 | Every interactive element is reachable by Tab in a logical order | Keyboard-only users (and many usability-test participants) cannot proceed otherwise |
| A3 | Visible focus indicator on every interactive element | `:focus-visible` outline never set to `none` without replacement |
| A4 | No keyboard traps — `Esc` always returns to a known state | Modal trapping focus is OK while open; trapping forever is not |
| A5 | Form inputs have an associated `<label>` or `aria-label` | Screen reader announces what the field is for |
| A6 | Color is not the only signal — pair it with icon, text, or shape | Color-blind users, low-contrast environments |
| A7 | Live regions (`role="status"`, `aria-live="polite"`) for toasts | Screen readers announce feedback |
| A8 | `alt` text on `<img>` (empty `alt=""` for decorative) | Images are at minimum non-blocking |
| A9 | Heading hierarchy is sane (`<h1>` → `<h2>` → `<h3>`, no skipping) | Document outline makes sense |
| A10 | Touch targets ≥ 44×44 px | Standard mobile usability minimum |

### 11.2 What the floor does NOT require

| Out of scope | Why |
|---|---|
| Full WCAG 2.2 AA compliance | Mockup is not for end users |
| ARIA roles on every custom widget | Adds noise; native elements suffice for mockup level |
| Screen-reader-perfect dynamic updates | Tested with the real product, not the mockup |
| Color contrast ratio ≥ 4.5:1 audited everywhere | Designer responsibility, mockup just renders the tokens |
| Internationalization framework | Localized strings are data (§9), not infrastructure |

### 11.3 Quick keyboard test (Phase 5)

Unplug the mouse. Open the mockup. Use only the keyboard:

- Can you reach every clickable element with Tab? (A2)
- Can you see where focus is at every step? (A3)
- Can you open the Navigation Map (M key) and close it (Esc)? (A4)
- Can you submit a form with Enter? (A1)
- Can you escape every modal/popup? (A4)

If any answer is "no", the mockup fails the floor and Phase 5 fails.

---

## §12. Persistence & Deep Links

Single-file mockups have no backend, but the browser provides two free
persistence mechanisms that dramatically improve testability and review
workflows.

### 12.1 URL hash routing (Demo: optional / Walkthrough: required / Prototype: required)

The current screen is encoded in the URL hash. Sharing a link to a specific
screen lets a stakeholder say "this is broken on the cart screen" by sending
a URL, not a screenshot with an arrow.

```javascript
// On navigate
function navigate(screenId) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-' + screenId).classList.add('active');
  location.hash = '#screen=' + screenId;
  resetScroll();
}

// On load — restore screen from hash
window.addEventListener('DOMContentLoaded', () => {
  const match = location.hash.match(/screen=([\w-]+)/);
  const target = match ? match[1] : 'home';
  navigate(target);
});

// On back / forward — keep history navigable
window.addEventListener('hashchange', () => {
  const match = location.hash.match(/screen=([\w-]+)/);
  if (match) navigate(match[1]);
});
```

### 12.2 localStorage for ephemeral form state (Prototype: recommended)

When a participant fills a form in a usability test, then navigates away and
back, the form should not be empty. Use `localStorage` for that:

```javascript
function persistForm(formId) {
  const form = document.getElementById(formId);
  form.querySelectorAll('input, textarea, select').forEach(el => {
    const key = `mockup:${formId}:${el.name}`;
    if (localStorage.getItem(key)) el.value = localStorage.getItem(key);
    el.addEventListener('input', () => localStorage.setItem(key, el.value));
  });
}
```

Restriction: never persist anything that looks like real PII or credentials.
A mockup that asks a participant to type their real password and stores it in
localStorage is a security hazard, not a feature.

### 12.3 Interaction-map comment block (Prototype level — required)

For dev handoff, embed a structured comment block in the HTML head, after
the meta tags and before the `<style>`. This is read by humans and is the
single source of truth for what the mockup says the product should do.

```html
<!--
INTERACTION MAP
================
project: tasks-app
version: 2.3
level: prototype
shell-profile: default-phone

screens:
  - id: home
    role: L0
    elements:
      - selector: .btn-create
        trigger: click
        rules: opens task-create modal
        feedback: modal slides up
        loops: none
  - id: task-create
    role: L1
    elements:
      - selector: button[data-action="save"]
        trigger: click
        rules: validate title non-empty
        feedback: toast "Task created" + navigate home
        loops: none

tokens:
  --primary: #2563eb
  --radius-md: 10px

endpoints:
  - settings-billing
  - settings-team-permissions
-->
```

Developer copies this block into the project's spec and the mockup becomes
self-documenting. No duplicate document drifts away from the file.

---

## §13. Components Catalog

Reusable patterns for mockup content. All depend on the Clickability Fix
(§4.4) when wrapped in clickable containers and the accessibility floor
(§11).

### 13.1 Component design tokens (defaults)

```css
:root {
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --accent: #f59e0b;
  --bg: #ffffff;
  --bg-subtle: #f8fafc;
  --bg-elevated: #f1f5f9;
  --text: #1e293b;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;
  --border: #e2e8f0;
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
  --shadow-xl: 0 20px 25px rgba(0,0,0,0.15);
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}
```

### 13.2 Catalog

| Component | Notes |
|---|---|
| Button (primary / secondary / sizes sm-md-lg) | hover lift, active scale, transitions; `<button>` not `<div>` (A1) |
| Card | hover lift + shadow; clickability fix required if `[onclick]` |
| Metric Row | label + bar + value; clickability fix required |
| Form Input / Select / Textarea | focus ring (A3), `<label>` associated (A5) |
| Header (sticky top) | logo + nav + actions; never `fixed` |
| Stat Card | icon + value + label + change (positive / negative) |
| List Item | avatar + content + meta; clickability fix |
| Table | clickable rows with pointer-events fix; `<th>` headers |
| Tab Bar (mobile, sticky bottom) | icon + label, active state, badge support |
| Empty / Error / Loading slot | per §10; required at applicable level |

### 13.3 Tab Bar — critical reminders

1. `position: sticky`, NOT `fixed`
2. Parent must have `flex: 1` for sticky bottom to work
3. Touch targets ≥ 44×44 (A10)

```css
.tab-item {
  min-width: 64px;
  min-height: 44px;
}
```

### 13.4 Screen structure (for sticky tab-bar to work)

```html
<div class="screen active" id="screen-home">
  <header class="header">...</header>
  <main class="main">...</main>      <!-- flex:1 pushes tab-bar down -->
  <nav class="tab-bar">...</nav>     <!-- sticky bottom works -->
</div>
```

```css
.screen { display: none; flex-direction: column; min-height: 100%; }
.screen.active { display: flex; flex: 1; }
.main { flex: 1; }
```

### 13.5 Responsive component prefixes

```css
/* Desktop default */
.mockup-content .grid { grid-template-columns: repeat(4, 1fr); }
/* Tablet */
.device-frame.tablet .mockup-content .grid { grid-template-columns: repeat(2, 1fr); }
/* Phone */
.device-frame.phone .mockup-content .grid { grid-template-columns: 1fr; }
```

---

## §14. Quality Gates

Run before delivery. Pass criteria: **0 BLOCKER, ≤ 2 MAJOR**.

### 14.1 Criticality levels

| Level | Symbol | Rule |
|---|---|---|
| BLOCKER | 🔴 | 0 allowed |
| MAJOR | 🟡 | ≤ 2 allowed |
| MINOR | 🟢 | no limit |

### 14.2 Categories (counts)

| Category | BLOCKER | MAJOR | MINOR | Total |
|---|---|---|---|---|
| Integrity | 6 | 0 | 0 | 6 |
| Form | 1 | 1 | 0 | 2 |
| Shell | 7 | 0 | 0 | 7 |
| Navigation Map | 5 | 7 | 1 | 13 |
| Endpoint | 3 | 2 | 0 | 5 |
| Mobile Toolbar | 1 | 4 | 0 | 5 |
| Layout | 4 | 3 | 0 | 7 |
| Clickability | 6 | 0 | 0 | 6 |
| Responsive | 3 | 2 | 0 | 5 |
| Interaction | 2 | 1 | 2 | 5 |
| Visual | 0 | 3 | 2 | 5 |
| **Total (full set)** | **38** | **23** | **5** | **66** |

### 14.3 Level-applicable subsets

| Level | Applicable categories | Total checks |
|---|---|---|
| Demo | Integrity (6) + Form (2) + Shell (7) + Layout (7) + Clickability (6) + Visual (5) | 33 |
| Walkthrough | Full set + Walkthrough State Triad subset (§14.5) | 68 |
| Prototype | Full set + Prototype State Triad (§14.5) + A11y Floor (§14.6) + Handoff (§14.7) | 76 |

### 14.4 Highlights (full set)

**Integrity (BLOCKER × 6)** — see §16.

**Shell (BLOCKER × 7)** — toolbar visible at top; no content overlap; phone /
tablet / desktop switching works; scroll resets on device switch; header
visible on all devices at 50% zoom (no top clipping).

**Navigation Map (BLOCKER × 5)** — *applies at Walkthrough and Prototype levels (§6).* Map button visible; popup opens / closes;
screen items navigate; endpoint items show toast; tab items show yellow
toast.

**Layout (BLOCKER × 4)** — content inside frame; no horizontal scroll; tab
bar at bottom (not floating); main fills space between header and tab-bar.

**Clickability (BLOCKER × 6)** — cards with `onclick` respond to clicks on
text / icons / progress bars; nested buttons still work; table rows with
`onclick` work.

**Endpoint (BLOCKER × 3)** — *applies at Walkthrough and Prototype levels (§7).* All dead-ends show endpoint toast; tabs show
yellow toast; list items without detail show endpoint.

**Responsive (BLOCKER × 3)** — phone / tablet / desktop layouts each
readable.

**Interaction (BLOCKER × 2)** — all buttons respond; screen navigation
works.

**Form (BLOCKER × 1)** — form buttons work.

### 14.5 State Triad checks

For **Walkthrough** (subset — 2 BLOCKER):

| Check | Severity |
|---|---|
| Initial screen shows a loading state, not a flash of empty | BLOCKER |
| Every data-driven list has an empty state with heading + body + action | BLOCKER |

For **Prototype** (full — 3 BLOCKER):

| Check | Severity |
|---|---|
| Every data-driven list has an empty state with heading + body + action | BLOCKER |
| At least one critical action has an error state with retry | BLOCKER |
| Initial load shows a loading state, not a flash of empty | BLOCKER |

### 14.6 Accessibility Floor checks (Prototype level addition — 3 BLOCKER, 2 MAJOR)

| Check | Severity |
|---|---|
| Every interactive element is reachable by Tab | BLOCKER |
| Visible focus indicator present (no `outline: none` without replacement) | BLOCKER |
| Esc closes every modal / popup / Navigation Map | BLOCKER |
| Form inputs have associated labels | MAJOR |
| Heading order is sane (no `<h1>` → `<h4>` jumps) | MAJOR |

### 14.7 Handoff checks (Prototype level addition — 2 BLOCKER)

| Check | Severity |
|---|---|
| Interaction-map comment block present in `<head>` (§12.3) | BLOCKER |
| Design tokens defined in `:root` (§13.1) | BLOCKER |

### 14.8 Drift indicators

Symptoms that say the build deviated from the standard. Each row points to a
recovery action.

| Sign | Meaning | Fix |
|---|---|---|
| Multiple files | Single-HTML invariant violated | Consolidate CSS/JS inline |
| No device shell | Shell invariant violated | Add shell from §3 |
| Lorem ipsum present | Realistic-data invariant violated | Apply §9 patterns |
| Action without feedback | Feedback invariant violated | Add toast or state change |
| `position: fixed` inside mockup | Sticky pattern violated | Change to `position: sticky` |
| Test protocol skipped | Quality gate bypassed | Run §14 checklist |
| Clicks not working on cards | Pointer-events fix missing | Apply §4.4 |
| Tab bar floats up | Flex chain broken | Apply §4.3 |
| Scroll not reset | setDevice reset missing | Apply §4.5 |
| Header clipped on tall device | Container alignment wrong | Use `align-items: flex-start` + `margin: auto` (§4.1) |
| No Navigation Map (Walkthrough+) | Nav map invariant violated | Add 📍 button + popup (§6) |
| Toolbar breaks on mobile <480px | Adaptive CSS missing | Add `@media (max-width: 480px)` rules |
| Unclear what is clickable | Endpoints not marked | Add `📌 ... — final point` toasts (§7) |
| Empty dashboard with no message | State triad violated | Apply §10 |
| Can't Tab to a button | A11y floor violated | Apply §11 |
| Level mismatch (Demo doing Prototype work) | Brief unclear | Re-do Phase 1 (§17.1) |

---

## §15. Performance Budget

Single-file mockups can quietly grow into multi-megabyte beasts. A budget
keeps them honest.

### 15.1 Budget by level

| Level | Total file size (uncompressed) | Why |
|---|---|---|
| Demo | ≤ 200 KB | Loads instantly even on slow networks; minimal content |
| Walkthrough | ≤ 500 KB | More screens, more data, more state coverage |
| Prototype | ≤ 1 MB | Full system; still loadable on most devices |

These are uncompressed file-size budgets, not compressed wire-size. They
matter because mockups are often opened from email attachments, Slack
uploads, USB sticks, or zip archives — contexts where gzip is not applied.

### 15.2 What counts against the budget

| Cost driver | Mitigation |
|---|---|
| Inline base64 images | Use external image-service URLs (§9.5) |
| Inline SVG repeated | Define once with `<symbol>`, reference with `<use>` |
| Huge JS data arrays | Trim to representative samples |
| Inline `<style>` duplication | Consolidate selectors |
| Embedded video / audio | Almost never appropriate in a mockup; use a poster image |

### 15.3 Emergency exits (when the budget is unavoidable)

| Symptom | Action |
|---|---|
| Image-heavy mockup blows budget | Move images to external CDN URLs; cache them |
| Many screens with similar markup | Generate screens from a JS template in a loop |
| Long realistic data tables | Load representative sample only; mark "+ 247 more" |
| Single screen needs huge content | Question whether the mockup level is correct (§2.2 anti-trigger 1) |

### 15.4 Budget check (Phase 5)

```bash
wc -c mockup.html
# Compare against level budget. If over: identify cost driver, apply §15.3.
```

---

## §16. File Integrity

Mockups that travel through external CDNs / pipelines may arrive corrupted.
Detect and recover before testing.

### 16.1 Known corruption patterns

| # | Pattern | Trigger | Detection | Fix |
|---|---|---|---|---|
| 1 | Cloudflare Email Protection injection | File served through Cloudflare CDN | `grep -c "cdn-cgi" file.html` should be `0` | Remove `<script data-cfasync="false" src="/cdn-cgi/.../email-decode.min.js">` |
| 2 | Email obfuscation | Cloudflare Email Protection enabled | `grep -c "__cf_email__" file.html` should be `0` | Replace `[email&#160;protected]` with original emails |
| 3 | File truncation | Large file transfer failure | `tail -1 file.html` should equal `</html>` | Restore closing tags `</script></body></html>` |
| 4 | Encoding corruption | Character encoding mismatch | Visual inspection: text rendered as `????` | Re-save as UTF-8 |

### 16.2 Detection commands

| Check | Command | Expected |
|---|---|---|
| File ends correctly | `tail -1 file.html` | `</html>` |
| No Cloudflare | `grep -c "cdn-cgi" file.html` | `0` |
| No email obfuscation | `grep -c "__cf_email__" file.html` | `0` |
| Script tags balanced | Compare `<script>` vs `</script>` counts | Equal |
| Body closed | `grep -c "</body>" file.html` | `1` |
| HTML closed | `grep -c "</html>" file.html` | `1` |

### 16.3 Recovery script

```bash
#!/bin/bash
FILE=$1
echo "=== Integrity Check: $FILE ==="
[[ $(tail -1 "$FILE") == *"</html>"* ]] && echo "✅ INT1: File ends correctly" || echo "🔴 INT1: FAIL - Truncated"
CF=$(grep -c "cdn-cgi" "$FILE" 2>/dev/null || echo "0")
[[ "$CF" == "0" ]] && echo "✅ INT2: No Cloudflare" || echo "🔴 INT2: FAIL ($CF)"
EM=$(grep -c "__cf_email__" "$FILE" 2>/dev/null || echo "0")
[[ "$EM" == "0" ]] && echo "✅ INT3: No obfuscation" || echo "🔴 INT3: FAIL ($EM)"
OPEN=$(grep -c "<script" "$FILE" 2>/dev/null || echo "0")
CLOSE=$(grep -c "</script>" "$FILE" 2>/dev/null || echo "0")
[[ "$OPEN" == "$CLOSE" ]] && echo "✅ INT4: Balanced ($OPEN)" || echo "🔴 INT4: FAIL ($OPEN/$CLOSE)"
BODY=$(grep -c "</body>" "$FILE" 2>/dev/null || echo "0")
HTML=$(grep -c "</html>" "$FILE" 2>/dev/null || echo "0")
[[ "$BODY" == "1" ]] && echo "✅ INT5: Body closed" || echo "🔴 INT5: FAIL"
[[ "$HTML" == "1" ]] && echo "✅ INT6: HTML closed" || echo "🔴 INT6: FAIL"
```

### 16.4 Sanitize → test → deliver loop

When the integrity gate fails: stop the test protocol, run sanitize (remove
injection / restore tags / re-save UTF-8), then resume the test protocol
from Phase 5 (§17.5) starting at Phase 5.1 Visual pass.

---

## §17. Workflow Phases

Six core phases plus one recovery phase (sanitize). Each phase produces a
named artifact, then the next phase consumes it.

### 17.1 Phase 1 — BRIEF

**Purpose:** collect requirements. Critical question first: **what is this
mockup for?**

| Step | Output |
|---|---|
| Declare purpose (pitch / usability test / dev handoff / other) | purpose statement |
| Derive level (Demo / Walkthrough / Prototype) from purpose (§2) | level declaration |
| Clarify scope (devices, screens, interactions, data source) | answers from user |
| Define interactions (which elements are clickable, what they do) | interaction list |
| Plan data (entities, fields, counts, edge cases per §9.4 if applicable) | data plan |
| Write `brief.md` | requirements doc |

**Gate:** purpose stated; level declared (Demo/Walkthrough/Prototype);
primary device; screen list; interaction map; data entities all defined.

### 17.2 Phase 2 — DESIGN

**Purpose:** define visual style and interaction map before any HTML.

| Step | Output |
|---|---|
| Color palette (primary / accent / neutrals / semantic) | tokens |
| Typography (H1-H3, body, small) | type scale |
| Spacing + radius | scale |
| Interaction map (Saffer 4-part per element per screen — §8.1) | mapping table |
| Component selection (which §13 components are used + variants) | inventory |
| State triad plan (loading/empty/error per applicable view — §10) | states list |
| Write `design.md` | design doc |

**Gate:** primary / accent / text colors defined; all interactions mapped
with Trigger + Rules + Feedback specified (Loops/Modes optional per §8.1);
state triad listed for applicable views.

### 17.3 Phase 3 — BUILD

**Purpose:** generate working HTML mockup with device shell.

| Step | Output |
|---|---|
| HTML skeleton with shell from §3 (level-appropriate; shell profile if any) | structure |
| Screens (one per brief item) with `flex: 1` chain (§4.3) | screen blocks |
| Clickability fix CSS (§4.4) | CSS |
| Forms pattern: `div + onclick`, never `form + onsubmit` (§5) | form blocks |
| Components from §13 selection | rendered |
| Placeholder data (refined in polish) | initial content |
| Basic hover effects from §8 | transitions |
| URL hash router (§12.1) if Walkthrough or Prototype | routing |
| Semantic HTML throughout (a11y floor, §11) | structure |
| Save as `mockup.html` | file |

**Gate:** shell renders; device switching works; flex chain complete;
clickability fix added; tab bar at bottom; basic hover effects; semantic
elements used.

### 17.4 Phase 4 — POLISH

**Purpose:** animations, feedback, realistic data, state triad, loading
states.

| Step | Output |
|---|---|
| Verify build quality (tab-bar at bottom, clickability) | check |
| Enhance animations with cubic-bezier easings (§8.2) | refined transitions |
| Add toast system + connect to every action (§8.5) | feedback layer |
| Replace placeholders with realistic data (§9), include edge cases (§9.4) if Prototype | content |
| Implement state triad (loading/empty/error) per §10 at level-appropriate scope | states |
| Scroll animations (IntersectionObserver) | scroll effects |
| Confirm focus indicators visible everywhere (a11y floor, §11) | a11y |
| Insert interaction-map comment block (§12.3) if Prototype | handoff |
| Save / overwrite `mockup.html` | file |

**Gate:** all hovers + clicks have feedback; data is realistic; no Lorem
ipsum / placeholder images; state triad in place at level-appropriate scope;
keyboard works.

### 17.5 Phase 5 — TEST

**Purpose:** validate against §14 quality gates (level-appropriate subset).

| Phase | Check |
|---|---|
| 5.0 | Integrity gate (§16). Any fail → sanitize → restart |
| 5.1 | Visual pass — page loads, no console errors |
| 5.2 | Shell pass — toolbar, frame, no overlap |
| 5.3 | Resolution pass — phone / tablet / desktop at 50% zoom; scroll resets |
| 5.4 | Layout pass — tab-bar at bottom, no empty gaps, flex chain complete |
| 5.5 | Clickability pass — every `[onclick]` element responds, including clicks on children |
| 5.6 | Interaction pass — buttons, navigation, popups, toasts, hover effects |
| 5.7 | State triad pass (Walkthrough+) — empty / error / loading present at level scope |
| 5.8 | Keyboard pass (Prototype) — Tab reaches everything, Esc closes everything, focus visible |
| 5.9 | Content pass — no Lorem ipsum, real images, text ≥ 14px |
| 5.10 | Budget pass — file size within §15 budget |
| 5.11 | Fix & retest until 0 BLOCKER + ≤ 2 MAJOR |

**Gate:** 0 BLOCKER, ≤ 2 MAJOR, file within budget.

### 17.6 Phase 6 — DELIVER

**Purpose:** UAT checklist + versioned final file.

| Step | Output |
|---|---|
| Generate UAT checklist from brief (Shell / Navigation / Interactions / States — only sections that apply at the chosen level) | checklist |
| Apply versioning: copy file to outputs as `{project}-v{NN}.html` (§17.8) | versioned deliverable |
| Maintain `{project}-CHANGELOG.md` with one line per version | history |
| Present + wait for feedback | UAT |
| If "all good" → done; if "X doesn't work" → fix → new version → re-deliver | iteration |

### 17.7 Phase 0 — SANITIZE (recovery)

**Purpose:** clean up a file that arrived corrupted.

| Step | Action |
|---|---|
| Detect | run §16.2 detection commands |
| Remove injections | delete Cloudflare `<script>` tags |
| Restore truncated | add missing `</script></body></html>` |
| Validate | rerun §16.2 commands |
| Continue | re-enter Phase 5 TEST |

### 17.8 Versioning artifacts

Mockups iterate. Each significant iteration is a new versioned file, not a
Git branch. Pattern:

```
project-tasks-v01.html      ← first deliverable
project-tasks-v02.html      ← after stakeholder feedback round 1
project-tasks-v03.html      ← after usability test round 1
project-tasks-CHANGELOG.md  ← one line per version
```

**Why not Git branches:** mockups are reviewed by stakeholders who want to
click both the old and new versions side-by-side, often months apart. A
folder of versioned files survives this; Git history requires checkout, hurts
review velocity, and complicates hosting on a static CDN.

**Why not overwriting:** the file *is* the artifact. Overwriting loses the
ability to A/B compare against past iterations, which is a common
stakeholder request.

CHANGELOG line format:

```
v03 (2026-04-12) — Reworked checkout to two steps after usability test; misclick rate dropped from 23% to 8%.
```

---

## §18. Testability Metrics

For Walkthrough and Prototype levels, the mockup will likely be run through a
usability-testing tool. Design the mockup so the tool's metrics make sense.

### 18.1 The four metrics that matter

| Metric | What it measures | What the mockup must do |
|---|---|---|
| **Success rate** | % of participants who completed the task | The success-path screens must be reachable end-to-end |
| **Drop-off rate** | % who abandoned mid-task | Endpoints and dead-ends marked (§7) so drop-off ≠ "got stuck on unimplemented" |
| **Misclick rate** | % of clicks outside clickable areas | Every clickable thing is actually clickable (§4.4); inactive areas are not styled to look clickable |
| **Average duration** | Time to complete | Mockup loads fast (§15 budget); transitions don't artificially inflate |

### 18.2 What the mockup adds for tool integration

| Pattern | Purpose |
|---|---|
| `data-expected-path="true"` on success-path elements | Tool can verify the expected path |
| `data-screen-id` on every screen `<div>` | Tool can attribute heatmap to specific screens |
| URL hash routing (§12.1) | Tool can deep-link to mid-task starting screens |
| Endpoint toasts (§7) | Distinguishes "not yet built" from "broken"; cleaner drop-off signal |

### 18.3 What the mockup does NOT do

The mockup is not a testing tool. It does not:

- Capture clicks for analysis (the testing tool does that)
- Send metrics anywhere (no backend)
- Show heatmaps or recordings inside itself

It only structures itself so an external tool can measure cleanly.

---

## §19. What this methodology does NOT do

| ❌ Does not | ✅ Does |
|---|---|
| Replace the design system — mockups consume tokens, they do not define them | Render whatever tokens a design system provides |
| Make decisions about copy, art direction, or product strategy | Structure the file so those decisions are visible |
| Guarantee full WCAG AA — only the floor (§11) | Enforce a minimum a11y floor that supports usability testing |
| Replace user testing — only enable it | Provide a clickable artifact and structure it for testing tools (§18) |
| Require a framework | One HTML file, vanilla JS, inline CSS |
| Need an AI agent | Can be executed by hand with this document and an editor |
| Replace production engineering | Provide a handoff artifact (interaction map per §12.3) that the engineers consume |
| Define backend behavior | Stub backend with realistic data and simulated state |

---

## Anchor

```
[*] LIVEMOCKUP-METHODOLOGY.md v2.0
Universal methodology for single-file clickable HTML mockups.
20 sections (§0–§19): principles → pipeline → levels → shell → layout →
forms → nav map → endpoints → microinteractions → realistic data →
state triad → a11y floor → persistence → components → quality gates →
performance → integrity → workflow → testability → boundaries.
Three levels: Demo / Walkthrough / Prototype, declared in Brief.
Microinteractions framed as Saffer's Trigger-Rules-Feedback-Loops/Modes.
Quality gates: 66 in full set; level-aware totals — Demo 33, Walkthrough 68, Prototype 76.
```
