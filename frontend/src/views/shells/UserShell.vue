<!--
  VELO Frontend -- UserShell (Phase F2.2)

  Layout wrapper for all /user/* routes.
  MobileLayout provides header slot + scrollable content + tab bar.
  Child views render inside <RouterView />.
-->

<template>
  <MobileLayout
    :tabs="USER_TABS"
    :active-tab="activeTab"
    :fill="isFillRoute"
    :hide-tab-bar="isDiaryRoute || isFormRoute || keyboardOpen"
    :fog="isFogRoute"
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
import { USER_TABS } from '@/router/tabs'
import { useKeyboardOpen } from '@/composables/useKeyboardOpen'

const route = useRoute()
const router = useRouter()

// Hide the floating tab bar while the soft keyboard is open, so it does not ride
// up over a focused input (e.g. the "запрос мастеру" field on booking-confirmed).
const { keyboardOpen } = useKeyboardOpen()

// Active tab: a route may pin one via meta.activeTab (e.g. the post-booking
// screen lights up Calendar). Otherwise match the path to the closest tab
// (e.g. /user/practices/123 -> /user).
const activeTab = computed(() => {
  const metaTab = route.meta.activeTab as string | undefined
  if (metaTab) return metaTab
  const path = route.path
  const match = USER_TABS.find((tab) => path.startsWith(tab.to))
  return match?.to ?? USER_TABS[0]?.to ?? ''
})

// Chat-style screens that manage their own internal scroll + a fixed bottom
// composer use the layout's fill mode. Currently only the diary feed.
const isFillRoute = computed(() => route.name === 'user-diary')

// The diary is an immersive full-screen mode: no bottom tab bar (the feed,
// the entry view and the check-in/feedback detail all hide it). Exit is via
// the "..." menu inside the diary, not tab navigation.
const DIARY_ROUTES = ['user-diary', 'user-diary-entry', 'user-diary-detail']
const isDiaryRoute = computed(() =>
  DIARY_ROUTES.includes(route.name as string),
)

// Focused full-screen form flows (check-in / feedback) hide the tab bar too:
// they have their own "Close" + submit/skip actions, and an in-flow tab bar
// rides up over the textarea when the keyboard opens.
const FORM_ROUTES = ['user-checkin', 'user-feedback']
const isFormRoute = computed(() =>
  FORM_ROUTES.includes(route.name as string),
)

// Edge-to-edge fog mask: the long scrolling lists/feeds + the practice-detail
// screen (operator 2026-06-09: dissolve its hero under the header and its CTA
// over the tabbar instead of a hard collision). Forms and the profile still
// opt out (their footers/actions must stay crisp). The diary owns its own fog
// via fill mode, so it is not listed here.
const FOG_ROUTES = [
  'user-dashboard',
  'user-calendar',
  'user-bookings',
  'user-master-public',
  'practice-detail',
]
const isFogRoute = computed(() =>
  FOG_ROUTES.includes(route.name as string),
)

// Per-screen fog tuning. The list feeds keep MobileLayout's defaults
// (16/40/70/90 — omitted = unchanged). practice-detail uses a softer top
// dissolve + tighter bottom so the «Записаться бесплатно» CTA stays crisp above
// the tab bar. The four numbers live as --velo-fog-pd-* tokens (variables.css,
// single reusable source); read once here since the values flow through JS into
// MobileLayout. Confirmed on the .tmp preview 2026-06-09.
let pdFogCache: {
  topGap: number; fogTopHard: number; fogBotFade: number; fogBotHard: number
} | null = null
function practiceDetailFog() {
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
  route.name === 'practice-detail' ? practiceDetailFog() : {},
)
</script>
