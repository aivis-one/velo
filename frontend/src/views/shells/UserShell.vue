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
    :hide-tab-bar="isDiaryRoute"
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

const route = useRoute()
const router = useRouter()

// Match current path to closest tab (e.g. /user/practices/123 -> /user)
const activeTab = computed(() => {
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
</script>
