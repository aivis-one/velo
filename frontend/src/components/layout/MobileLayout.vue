<!--
  VELO Frontend -- MobileLayout Component (Phase F2.1)

  Full-screen layout for user and master roles.
  Wraps: VHeader (optional) + scrollable content slot + VTabBar.
  Matches mockup mobile screen structure.

  Usage:
    <MobileLayout :tabs="userTabs" :active-tab="route.path">
      <template #header>
        <VHeader title="Дашборд" />
      </template>
      <DashboardContent />
    </MobileLayout>
-->

<template>
  <div class="mobile-layout">
    <slot name="header" />
    <main class="mobile-layout__main">
      <slot />
    </main>
    <VTabBar
      :items="tabs"
      :active="activeTab"
      @navigate="$emit('navigate', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import VTabBar, { type TabItem } from '@/components/layout/VTabBar.vue'

defineProps<{
  tabs: TabItem[]
  activeTab?: string
}>()

defineEmits<{
  navigate: [to: string]
}>()
</script>

<style scoped>
.mobile-layout {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  min-height: 100vh; /* fallback */
  background: linear-gradient(135deg, var(--velo-bg-start) 0%, var(--velo-bg-end) 100%);
}

.mobile-layout__main {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  -webkit-overflow-scrolling: touch;
}
</style>
