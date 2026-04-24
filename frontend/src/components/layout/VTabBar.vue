<!--
  VELO Frontend -- VTabBar Component (Phase F2.1)

  Bottom tab navigation. Matches mockup .tab-bar / .bottom-nav styles.
  Configurable items per role (user 4 tabs, master 4 tabs, admin 3 tabs).

  Usage:
    <VTabBar :items="tabs" :active="currentRoute" @navigate="router.push($event)" />
-->

<template>
  <nav class="v-tabbar">
    <button
      v-for="item in items"
      :key="item.to"
      class="v-tabbar__item"
      :class="{ 'v-tabbar__item--active': active === item.to }"
      @click="$emit('navigate', item.to)"
    >
      <span class="v-tabbar__icon">
        <component v-if="typeof item.icon !== 'string'" :is="item.icon" :size="20" />
        <template v-else>{{ item.icon }}</template>
      </span>
      <span class="v-tabbar__label">{{ item.label }}</span>
      <span v-if="item.badge" class="v-tabbar__badge">{{ item.badge }}</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

export interface TabItem {
  icon: string | Component
  label: string
  to: string
  badge?: number | string
}

defineProps<{
  items: TabItem[]
  active?: string
}>()

defineEmits<{
  navigate: [to: string]
}>()
</script>

<style scoped>
.v-tabbar {
  position: sticky;
  bottom: 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: rgba(255, 255, 255, 0.85);
  padding: var(--space-2) var(--space-3);
  padding-bottom: calc(var(--space-2) + env(safe-area-inset-bottom, 0px));
  z-index: var(--z-sticky, 200);
}

.v-tabbar__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: var(--space-1) 0;
  color: var(--text-muted);
  background: var(--nav-inactive-bg);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
  position: relative;
}

.v-tabbar__item--active {
  background: var(--steel-button);
  color: white;
}

.v-tabbar__icon {
  font-size: 20px;
  line-height: 1;
}

.v-tabbar__label {
  font-size: 10px;
  font-weight: 400;
}

.v-tabbar__badge {
  position: absolute;
  top: 0;
  right: 50%;
  transform: translateX(16px);
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--pink-primary);
  color: white;
  font-size: 9px;
  font-weight: 400;
  border-radius: var(--radius-full);
}
</style>
