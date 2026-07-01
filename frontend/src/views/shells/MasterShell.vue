<!--
  VELO Frontend -- MasterShell (Phase F2.2)

  Layout wrapper for all /master/* routes.
  MobileLayout provides header slot + scrollable content + tab bar.
-->

<template>
  <MobileLayout
    :tabs="MASTER_TABS"
    :active-tab="activeTab"
    :fog="isFogRoute"
    :hide-tab-bar="hideTabBar"
    v-bind="fogTuning"
    @navigate="router.push($event)"
  >
    <RouterView />
  </MobileLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MobileLayout } from '@/components/layout'
import { MASTER_TABS } from '@/router/tabs'
import { useKeyboardOpen } from '@/composables/useKeyboardOpen'

const route = useRoute()
const router = useRouter()

// Hide the floating tab bar while the soft keyboard is open, so it does not ride
// up over a focused input (parity with UserShell — e.g. the «Мои ученики» search).
const { keyboardOpen } = useKeyboardOpen()

const activeTab = computed(() => {
  const path = route.path
  const match = MASTER_TABS.find((tab) => path.startsWith(tab.to))
  return match?.to ?? MASTER_TABS[0]?.to ?? ''
})

// Edge-to-edge fog on the long scrolling master LIST/feed screens, matching the
// User zone (operator tester-fix 2026-06-17, scope А). Forms / profile / create-
// edit / single-detail / message-thread composer stay CRISP (DS rule: their
// CTAs/footers must not fade) — so notifications (settings toggles) and finance
// (payout form + «Запросить вывод» CTA) are deliberately NOT fogged.
// Every hideTabBar list below gets the compact bottom fade automatically:
// MobileLayout substitutes --velo-fog-list-z3/z4 when fog && hideTabBar, so the
// dissolve lands at the real content bottom (this also fixes the latent
// practice-reviews bottom clip the previous comment flagged).
const FOG_ROUTES = [
  'master-practices',
  'master-dashboard',
  'master-analytics',
  'master-practice-reviews',
  'master-students',
  'master-messages',
  'master-promocodes',
  'master-summary',
  'master-attendance-roster',
  // Check-ins list (the same per-practice attendance feed as the roster) — fog
  // for parity with master-attendance-roster (WS-1, 2026-06-19).
  'master-attendance',
  // Scrolling profile (check-ins + feedbacks lists) — fog so the floating header
  // doesn't collide with content on scroll (operator tester-fix 2026-06-17).
  'master-student-profile',
  // Notifications: long settings list — fog so the «Уведомления» header doesn't
  // overlap the rows on scroll (operator 2026-06-19).
  'master-notifications',
  // Detail / form screens with a transparent floating header — fog so content
  // doesn't collide with the header on scroll (the white «solid» plate was
  // dropped 2026-06-29). practice-detail + finance + the 3 Stage-2 forms
  // (create / edit practice, new promocode) carry an IN-FLOW bottom CTA, so they
  // take the CTA-safe pd-tuning below (softer top / tighter bottom) — the button
  // sits above the fade and stays solid. The profile hub has no in-flow CTA
  // (logout in a modal) + keeps its tab bar, so default fog clears its last row.
  // KEYBOARD-SAFE (operator-mandate 2026-06-29): fog over a form input no longer
  // clips it — the keyboard-aware mask (global.css `html.is-keyboard-open` +
  // `--velo-vvh`, commit e95e05a) shrinks the masked area to the visible viewport
  // on keyboard-open, so create/edit/promocode forms join finance under the same
  // (de-solid → fog, keyboard-safe) rationale. Support is now re-fogged too (SP-2,
  // 2026-07-01) — see its CTA-safe entry below.
  'master-practice-detail',
  'master-finance',
  'master-practice-new',
  'master-practice-edit',
  'master-promocode-new',
  'master-profile',
  // Edit-profile + language/timezone: fog so content doesn't smudge under the
  // floating header on scroll (operator FOG-1, 2026-06-30). Both are keyboard
  // screens — keyboard-safe via the e95e05a viewport mask (ships in this batch),
  // so this follows the same de-solid → fog, keyboard-safe rationale as the forms.
  'master-edit-profile',
  'master-language-timezone',
  // Support (SP-2, 2026-07-01): RE-FOGGED after being un-fogged in #8/#9 (5d74c8c,
  // where the pre-keyboard-aware fog clipped the form into a band). Safe now: the
  // «убрать туман при вводе» rule (global.css) drops the mask while typing, and the
  // CTA-safe bottom (below) keeps the «Отправить» button crisp at rest. Fixes the
  // header-overlap-on-scroll the operator flagged.
  'master-support',
  // Chat thread (MC-1, 2026-07-01, fork Q2=В — header only): fog so the floating
  // «peer name» title stops overlapping the thread on scroll. The composer is a
  // sticky bottom bar (a fill-mode refactor for it = MC-2, DEFERRED to the real
  // messaging rebuild), so this route takes chatFog() below: TOP fade only, ZERO
  // bottom fade, so the composer is never dissolved.
  'master-chat',
]
const isFogRoute = computed(() => FOG_ROUTES.includes(route.name as string))

// Read a numeric px CSS custom property off :root (callers pass a cached `cs`).
function fogPx(cs: CSSStyleDeclaration, name: string, fallback: number): number {
  const n = parseInt(cs.getPropertyValue(name), 10)
  return Number.isFinite(n) ? n : fallback
}

// CTA-safe fog tuning: a softer top dissolve + the full pd bottom via the shared
// --velo-fog-pd-* tokens, so an in-flow bottom action button clears the bottom
// fade and stays crisp. Read once + memoized. Finance keeps this full pd bottom;
// the create/edit/promocode forms moved to the COMPACT bottom (ПРОМТ №233 — the
// full 140px read as a too-wide fog band; see COMPACT_BOTTOM_FOG_ROUTES).
const CTA_SAFE_FOG_ROUTES = ['master-finance', 'master-support']
let pdFogCache: {
  topGap: number
  fogTopHard: number
  fogBotFade: number
  fogBotHard: number
} | null = null
function ctaSafeFog() {
  if (pdFogCache) return pdFogCache
  const cs = getComputedStyle(document.documentElement)
  pdFogCache = {
    topGap: fogPx(cs, '--velo-fog-pd-top-gap', 25),
    fogTopHard: fogPx(cs, '--velo-fog-pd-top-hard', 60),
    fogBotFade: fogPx(cs, '--velo-fog-pd-bot-fade', 50),
    fogBotHard: fogPx(cs, '--velo-fog-pd-bot-hard', 90),
  }
  return pdFogCache
}

// Compact-bottom fog: soft pd TOP + the COMPACT list bottom (--velo-fog-list-z3/z4)
// for hideTabBar screens whose in-flow CTA sits just above a short bottom fade.
//   • master-practice-detail (FOG-2, 2026-06-30): the pd bottom (fade 50 + hard 90
//     = 140px, sized for a tab bar the screen hides) wasted screen; the past-state
//     «Посещаемость» CTA still clears the 48px fade.
//   • create / edit practice + new promocode (ПРОМТ №233): same 140px read as a
//     "too-wide" bottom fog band; the in-flow «Создать …» CTA clears the shorter
//     48px fade the same way. Master-scoped; finance keeps the full pd bottom.
// Reuses existing tokens, no new token. Device-tunable via --velo-fog-list-z3/z4.
let compactBottomFogCache: {
  topGap: number
  fogTopHard: number
  fogBotFade: number
  fogBotHard: number
} | null = null
function compactBottomFog() {
  if (compactBottomFogCache) return compactBottomFogCache
  const cs = getComputedStyle(document.documentElement)
  compactBottomFogCache = {
    topGap: fogPx(cs, '--velo-fog-pd-top-gap', 25),
    fogTopHard: fogPx(cs, '--velo-fog-pd-top-hard', 60),
    fogBotFade: fogPx(cs, '--velo-fog-list-z3', 48),
    fogBotHard: fogPx(cs, '--velo-fog-list-z4', 0),
  }
  return compactBottomFogCache
}

// Screens on the compact-bottom fog above (soft top, short bottom fade).
const COMPACT_BOTTOM_FOG_ROUTES = [
  'master-practice-detail',
  'master-practice-new',
  'master-practice-edit',
  'master-promocode-new',
]

// master-dashboard (DB-1, 2026-06-30): the greeting was removed, leaving an
// oversized top band; shrink the top clearance from the default --velo-fog-z1 (16)
// to --space-2 (8). Per-screen, reuses an existing token; tunable on device.
let dashFogCache: { topGap: number } | null = null
function dashboardFog() {
  if (dashFogCache) return dashFogCache
  const cs = getComputedStyle(document.documentElement)
  dashFogCache = { topGap: fogPx(cs, '--space-2', 8) }
  return dashFogCache
}

// master-profile (PE-1, 2026-07-01): the profile hub is HEADERLESS (no VHeader →
// islandH=0), so MobileLayout applies the 88px HEADER_FALLBACK + the default z1 gap
// ≈104px empty band above the first card. A NEGATIVE top-gap pulls that clearance
// down (top = HEADER_FALLBACK + this); the fog fade still lands the card crisp
// because its opaque boundary tracks the reduced paddingTop. Bottom fog unchanged
// (the hub keeps its tab bar). Reuses the fogPx reader; value in --velo-fog-mp-top-gap.
// Does NOT touch MobileLayout shared logic / the HEADER_FALLBACK constant.
let mpFogCache: { topGap: number } | null = null
function masterProfileFog() {
  if (mpFogCache) return mpFogCache
  const cs = getComputedStyle(document.documentElement)
  mpFogCache = { topGap: fogPx(cs, '--velo-fog-mp-top-gap', -40) }
  return mpFogCache
}

// master-chat (MC-1, 2026-07-01): TOP fade only. The default top (z1/z2) dissolves
// the thread under the floating title on scroll (fixes the header overlap); the
// bottom fade is set to 0 so the sticky composer bar is never dissolved. 0 = "no
// bottom fade" (structural, not a design value), so MobileLayout's fog+hideTabBar
// bottom padding collapses to 0 and the composer rests at the bottom edge. The
// composer's mid-page float (MC-2) is a separate, deferred fill-mode refactor.
const chatFogTuning = { fogBotFade: 0, fogBotHard: 0 }

const fogTuning = computed(() => {
  const name = route.name as string
  if (COMPACT_BOTTOM_FOG_ROUTES.includes(name)) return compactBottomFog()
  if (name === 'master-dashboard') return dashboardFog()
  if (name === 'master-profile') return masterProfileFog()
  if (name === 'master-chat') return chatFogTuning
  return CTA_SAFE_FOG_ROUTES.includes(name) ? ctaSafeFog() : {}
})

// Hide the bottom tab bar on detail routes that opt in via `meta.hideTabBar`
// (the design omits the tab bar on master detail screens), OR while the soft
// keyboard is open so it never rides up over a focused input.
const hideTabBar = computed(() => route.meta.hideTabBar === true || keyboardOpen.value)
</script>
