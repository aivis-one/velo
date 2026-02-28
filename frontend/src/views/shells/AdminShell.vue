<!--
  VELO Frontend -- AdminShell (Phase F2.2)

  Layout wrapper for all /admin/* routes.
  AdminLayout provides header slot + scrollable content + 3-tab bar.
-->

<template>
  <AdminLayout
    :tabs="ADMIN_TABS"
    :active-tab="activeTab"
    @navigate="router.push($event)"
  >
    <RouterView />
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { AdminLayout } from '@/components/layout'
import { ADMIN_TABS } from '@/router/tabs'

const route = useRoute()
const router = useRouter()

const activeTab = computed(() => {
  const path = route.path
  const match = ADMIN_TABS.find((tab) => path.startsWith(tab.to))
  return match?.to ?? ADMIN_TABS[0]?.to ?? ''
})
</script>
