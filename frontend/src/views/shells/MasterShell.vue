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
  // Scrolling profile (check-ins + feedbacks lists) — fog so the floating header
  // doesn't collide with content on scroll (operator tester-fix 2026-06-17).
  'master-student-profile',
  // Notifications: long settings list — fog so the «Уведомления» header doesn't
  // overlap the rows on scroll (operator 2026-06-19).
  'master-notifications',
]
const isFogRoute = computed(() => FOG_ROUTES.includes(route.name as string))

// Hide the bottom tab bar on detail routes that opt in via `meta.hideTabBar`
// (the design omits the tab bar on master detail screens), OR while the soft
// keyboard is open so it never rides up over a focused input.
const hideTabBar = computed(() => route.meta.hideTabBar === true || keyboardOpen.value)
</script>
