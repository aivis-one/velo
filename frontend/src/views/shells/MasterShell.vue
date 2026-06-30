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
  // (de-solid → fog, keyboard-safe) rationale. Support stays un-fogged for now.
  'master-practice-detail',
  'master-finance',
  'master-practice-new',
  'master-practice-edit',
  'master-promocode-new',
  'master-profile',
]
const isFogRoute = computed(() => FOG_ROUTES.includes(route.name as string))

// CTA-safe fog tuning for the fogged detail/form screens that have an in-flow
// bottom action button (practice-detail, finance, and the create / edit practice
// + new promocode forms). Mirrors UserShell's practice-detail: a softer top
// dissolve + tighter bottom via the shared --velo-fog-pd-* tokens (variables.css,
// single source), so the CTA clears the bottom fade and stays crisp. Read once +
// memoized; values flow through JS into MobileLayout. The profile hub is NOT
// listed here — it uses the default fog (tab-bar clearance already keeps its last
// row solid).
const CTA_SAFE_FOG_ROUTES = [
  'master-practice-detail',
  'master-finance',
  'master-practice-new',
  'master-practice-edit',
  'master-promocode-new',
]
let pdFogCache: {
  topGap: number
  fogTopHard: number
  fogBotFade: number
  fogBotHard: number
} | null = null
function ctaSafeFog() {
  if (pdFogCache) return pdFogCache
  const cs = getComputedStyle(document.documentElement)
  const tok = (name: string, fallback: number): number => {
    const n = parseInt(cs.getPropertyValue(`--velo-fog-pd-${name}`), 10)
    return Number.isFinite(n) ? n : fallback
  }
  pdFogCache = {
    topGap: tok('top-gap', 25),
    fogTopHard: tok('top-hard', 60),
    fogBotFade: tok('bot-fade', 50),
    fogBotHard: tok('bot-hard', 90),
  }
  return pdFogCache
}
const fogTuning = computed(() =>
  CTA_SAFE_FOG_ROUTES.includes(route.name as string) ? ctaSafeFog() : {},
)

// Hide the bottom tab bar on detail routes that opt in via `meta.hideTabBar`
// (the design omits the tab bar on master detail screens), OR while the soft
// keyboard is open so it never rides up over a focused input.
const hideTabBar = computed(() => route.meta.hideTabBar === true || keyboardOpen.value)
</script>
