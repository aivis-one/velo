<!--
  VELO Frontend -- AdminLayout Component (Phase F2.1)

  Full-screen layout for admin role. Structurally same as MobileLayout
  but semantically separate for future admin-specific styling
  (e.g. desktop sidebar layout in Phase F10).

  Admin has 3 tabs: Дашборд, Мастера, Модерация.

  Usage:
    <AdminLayout :tabs="adminTabs" :active-tab="route.path">
      <template #header>
        <VHeader title="Админ-панель" />
      </template>
      <AdminDashboardContent />
    </AdminLayout>
-->

<template>
  <div class="admin-layout">
    <slot name="header" />
    <main class="admin-layout__main">
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
.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  min-height: 100vh;
  background: transparent;
  /* Anchor for the floating (position:absolute) VTabBar. Without this the bar
     resolves its bottom:0 against an ancestor further up the tree and "flies
     off". MobileLayout already does this; AdminLayout was missed when the tab
     bar switched from sticky to absolute. */
  position: relative;
}

.admin-layout__main {
  flex: 1;
  overflow-y: auto;
  /* Bottom padding clears the floating tab bar so admin content scrolls fully
     into view instead of hiding under it. */
  padding: var(--space-4) var(--space-4)
    calc(112px + env(safe-area-inset-bottom, 0px));
  -webkit-overflow-scrolling: touch;
}
</style>
