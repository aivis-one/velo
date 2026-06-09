<!--
  VELO Frontend -- VTabBar Component (Figma redesign, node 541:6649)

  Bottom tab navigation. Per-role tab items (user 4 / master 4 / admin 4).

  Visual spec (Figma node 2212:292 / 2212:390):
    - Inactive tab: 63x63 circle, 1.26px white border, glass-blue fill
      (--velo-nav-inactive-bg = rgba(98,122,156,0.15)), backdrop-blur,
      monochrome icon in --velo-text-primary.
    - Active tab: same circle slot, same border + blur as inactive, but
      a soft blue-grey fill (--velo-nav-active-bg-glass = rgba(98,122,
      156,0.60)) with a white icon. Per Figma the only difference
      between states is the fill alpha (.15 -> .60); border, blur and
      shape stay the same. Do NOT use --velo-nav-active-bg here — that
      token is opaque #627a9c, used by VMenu/VMenuItem.
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
  /* Floats over the edge-to-edge feed (MobileLayout is the positioned anchor),
     so content scrolls UNDER it and dissolves into the bottom fog. */
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  /* Spread the buttons across the 24px content rail (space-between), so the
     outer buttons sit exactly on the same left/right lines as the content and
     headers on every screen width. */
  justify-content: space-between;
  padding: var(--space-2) var(--velo-rail-pad-x);
  /* Lift the bar away from the screen edge (Figma 2212:292) -- 33px keeps it
     comfortably above the home indicator on iOS and visually detached from
     the very bottom on Android. */
  padding-bottom: calc(var(--space-8) + env(safe-area-inset-bottom, 0px));
  background: transparent;
  z-index: var(--z-sticky);
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
  border: 1.26px solid var(--velo-glass-border);
  backdrop-filter: blur(2.52px);
  -webkit-backdrop-filter: blur(2.52px);
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

/*
 * Active state (Figma 2212:390): same circle, same border + blur as inactive,
 * a darker semi-transparent fill, white icon. Only the fill and icon color
 * change. The fill is primary with 60% alpha (-> soft blue-grey on the light
 * page bg), NOT the fully opaque --velo-nav-active-bg.
 */
.v-tabbar__item--active {
  background: var(--velo-nav-active-bg-glass);
  color: var(--velo-white);
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
