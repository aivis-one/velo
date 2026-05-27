<!--
  VELO Frontend -- VTabBar Component (Figma redesign, node 541:6649)

  Bottom tab navigation. Per-role tab items (user 4 / master 4 / admin 4).

  Visual spec (Figma node 2212:292):
    - Inactive tab: 63x63 circle, 1.26px white border, glass-blue fill
      (--velo-nav-inactive-bg = rgba(98,122,156,0.15)), backdrop-blur,
      monochrome icon in --velo-text-primary.
    - Active tab: same circle slot, same border + blur as inactive, but
      a darker fill (--velo-nav-active-bg = #627a9c) with a white icon.
      Per Figma the only difference between states is the fill alpha;
      border, blur and shape stay the same.
    - No text labels under icons. aria-label preserved for screen readers.
    - The bar sits ~25px above the screen edge (space-8 padding-bottom)
      so it doesn't visually stick to the bottom.

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
  /* Lift the bar away from the screen edge (Figma 2212:292) -- 33px keeps it
     comfortably above the home indicator on iOS and visually detached from
     the very bottom on Android. */
  padding-bottom: calc(var(--space-8) + env(safe-area-inset-bottom, 0px));
  background: transparent;
  z-index: var(--z-sticky, 200);
}

.v-tabbar__item {
  /* Figma node 2212:413 (inactive) / 2212:390 (active) -- 63x63 circle */
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
  background: var(--velo-nav-inactive-bg);
  border: 1.26px solid #ffffff;
  backdrop-filter: blur(2.52px);
  -webkit-backdrop-filter: blur(2.52px);
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

/*
 * Active state (Figma 2212:390): same circle, same border + blur as inactive,
 * darker fill, white icon. Only the fill and icon color change.
 */
.v-tabbar__item--active {
  background: var(--velo-nav-active-bg);
  color: #ffffff;
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
