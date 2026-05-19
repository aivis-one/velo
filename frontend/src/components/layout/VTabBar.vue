<!--
  VELO Frontend -- VTabBar Component (Figma redesign, node 541:6649)

  Bottom tab navigation. Per-role tab items (user 4 / master 4 / admin 4).

  Visual spec (Figma):
    - Inactive tab: 63x63 circle, 1.26px white border, glass-blue fill,
      backdrop-blur, monochrome icon in --velo-text-primary.
    - Active tab: same circle slot, NO border / NO fill / NO blur,
      only a soft white glow around the icon (--velo-shadow-glow).
      Icon color stays the same -- only the ambience changes.
    - No text labels under icons. aria-label preserved for screen readers.

  TabItem.badge is preserved in the interface for future use (notification
  count) but is NOT rendered -- not present in current Figma design.

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
      :aria-label="item.label"
      :aria-current="active === item.to ? 'page' : undefined"
      type="button"
      @click="$emit('navigate', item.to)"
    >
      <span class="v-tabbar__icon">
        <component v-if="typeof item.icon !== 'string'" :is="item.icon" :size="27" />
        <template v-else>{{ item.icon }}</template>
      </span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

export interface TabItem {
  icon: string | Component
  label: string
  to: string
  // Reserved for future use (notification count). Intentionally not rendered
  // -- the current Figma design has no badge slot. Keep field so call sites
  // that already pass `badge` keep type-checking.
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
  justify-content: center;
  /* Figma: 4 circles x 63px with 25px gaps (left positions 37/125/213/301, step 88) */
  gap: 25px;
  padding: var(--space-2) var(--velo-screen-padding);
  padding-bottom: calc(var(--space-2) + env(safe-area-inset-bottom, 0px));
  background: transparent;
  z-index: var(--z-sticky, 200);
}

.v-tabbar__item {
  /* Figma node 541:6760 / 6766 / 6771 -- 63x63 circle */
  width: 63px;
  height: 63px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  color: var(--velo-text-primary);
  /* Inactive (default): glass bubble. Component-specific border-width and
     blur radius come straight from Figma spec -- not reusable elsewhere. */
  background: var(--velo-glass-blue-15);
  border: 1.26px solid #ffffff;
  backdrop-filter: blur(2.52px);
  -webkit-backdrop-filter: blur(2.52px);
  transition:
    background var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    backdrop-filter var(--transition-fast);
}

/*
 * Active state: bubble dissolves, soft white halo appears around the icon.
 * Same icon, different ambience -- per spec the icons differ only by glow.
 */
.v-tabbar__item--active {
  background: transparent;
  border-color: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  box-shadow: var(--velo-shadow-glow);
}

.v-tabbar__item:focus-visible {
  outline: 2px solid var(--velo-primary);
  outline-offset: 2px;
}

.v-tabbar__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 0;
  font-size: 22px;
}
</style>
