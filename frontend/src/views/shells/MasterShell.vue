<!--
  VELO Frontend -- MasterShell (Phase F2.2)

  Layout wrapper for all /master/* routes.
  MobileLayout provides header slot + scrollable content + tab bar.
-->

<template>
  <MobileLayout
    :tabs="MASTER_TABS"
    :active-tab="activeTab"
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
</script>
