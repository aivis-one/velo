<!--
  VELO Frontend -- AdminShell (Phase F2.2; DS rebuild 2026-06-14)

  Layout wrapper for all /admin/* routes. AdminLayout provides the scrollable
  content + the admin tab bar (VAdminTabBar). The shell injects live badge counts
  (masters awaiting verification + reports awaiting moderation), turns the fog feed
  on for the dashboard, and hides the tab bar on the focused metric/revenue detail
  screens.
-->

<template>
  <AdminLayout
    :tabs="ADMIN_TABS"
    :tab-items="tabItems"
    :active-tab="activeTab"
    :fog="isFogRoute"
    :hide-tab-bar="isDetailRoute"
    @navigate="router.push($event)"
  >
    <RouterView />
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { AdminLayout } from '@/components/layout'
import { ADMIN_TABS } from '@/router/tabs'
import type { TabItem } from '@/components/layout/VTabBar.vue'
import { useAdminStore } from '@/stores/admin'

const route = useRoute()
const router = useRouter()
const adminStore = useAdminStore()

const activeTab = computed(() => {
  const path = route.path
  const match = ADMIN_TABS.find((tab) => path.startsWith(tab.to))
  return match?.to ?? ADMIN_TABS[0]?.to ?? ''
})

// Live count badges (operator SVG): masters awaiting verification on the Мастера
// tab, reports awaiting moderation on the Модерация tab. 0 -> no badge.
const tabItems = computed<TabItem[]>(() =>
  ADMIN_TABS.map((tab) => {
    if (tab.to === '/admin/masters' && adminStore.pendingVerifications > 0)
      return { ...tab, badge: adminStore.pendingVerifications }
    if (tab.to === '/admin/reports' && adminStore.pendingModeration > 0)
      return { ...tab, badge: adminStore.pendingModeration }
    return tab
  }),
)

// Fog feed on the dashboard + the global participants/practices lists (operator
// SVG shows the mandala feed behind them); other admin screens keep plain padding.
const FOG_ROUTES = ['admin-dashboard', 'admin-participants', 'admin-practices']
const isFogRoute = computed(() => FOG_ROUTES.includes(route.name as string))

// Focused back-button screens hide the tab bar: the metric/revenue drill-ins plus
// the participants/practices lists (reached from the dashboard stat cards).
const DETAIL_ROUTES = [
  'admin-checkin-rate',
  'admin-feedback-rate',
  'admin-return-rate',
  'admin-revenue',
  'admin-participants',
  'admin-practices',
]
const isDetailRoute = computed(() => DETAIL_ROUTES.includes(route.name as string))

onMounted(() => {
  void adminStore.fetchDashboard()
})
</script>
