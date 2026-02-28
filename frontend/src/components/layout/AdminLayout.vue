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
  background: linear-gradient(135deg, var(--velo-bg-start) 0%, var(--velo-bg-end) 100%);
}

.admin-layout__main {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  -webkit-overflow-scrolling: touch;
}
</style>
