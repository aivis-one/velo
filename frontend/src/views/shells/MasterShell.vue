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

const route = useRoute()
const router = useRouter()

const activeTab = computed(() => {
  const path = route.path
  const match = MASTER_TABS.find((tab) => path.startsWith(tab.to))
  return match?.to ?? MASTER_TABS[0]?.to ?? ''
})

// Edge-to-edge fog on the long scrolling master content screens (design shows
// the edge dissolve on practices / dashboard / analytics / a practice's reviews).
// Forms and short detail screens stay crisp. NOTE: master-practice-reviews also
// sets meta.hideTabBar, which collapses MobileLayout's bottom clearance to 24px
// while the default fog bottom zone is ~160px — verify on device and add a custom
// fog tuning (fogBotFade/fogBotHard) if the bottom fade clips content.
const FOG_ROUTES = [
  'master-practices',
  'master-dashboard',
  'master-analytics',
  'master-practice-reviews',
]
const isFogRoute = computed(() => FOG_ROUTES.includes(route.name as string))

// Hide the bottom tab bar on detail routes that opt in via `meta.hideTabBar`
// (the design omits the tab bar on master detail screens). Opt-in per route —
// the remaining master detail screens migrate later in the SHELL pass.
const hideTabBar = computed(() => route.meta.hideTabBar === true)
</script>
