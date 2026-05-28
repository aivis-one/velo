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
  <div class="mobile-layout" :class="{ 'mobile-layout--fill': fill }">
    <slot name="header" />
    <main class="mobile-layout__main" :class="{ 'mobile-layout__main--fill': fill }">
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
  // When true, the content area does NOT scroll itself; it hands its full
  // height to the child view, which manages its own internal scroll. Used by
  // chat-style screens (e.g. the diary) that need a fixed composer pinned
  // above the tab bar with only the feed scrolling between header and composer.
  // Defaults to false -> unchanged behaviour for every other screen.
  fill?: boolean
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
  background: transparent;
}

/* Fill mode needs a DEFINITE root height (not just min-height), otherwise the
   flex chain below has nothing to resolve flex:1 / height:100% against and the
   content area collapses to its content -- which is exactly why the composer
   used to stick under the last card instead of the bottom. Locking the root to
   the viewport height makes `main` (flex:1) take "viewport - header - tabbar",
   and the diary view fills that, pinning the composer above the tab bar. */
.mobile-layout--fill {
  height: 100dvh;
  height: 100vh; /* fallback */
  min-height: 0;
}

.mobile-layout__main {
  flex: 1;
  overflow-y: auto;
  /* Horizontal screen-padding по Figma DS — 33px (--velo-screen-padding).
   * Vertical оставляем --space-4 (16). Точечные экраны могут добавить
   * vertical паддинги поверх, но screen-padding по бокам — единая
   * DS-константа, единое место правки. */
  padding: var(--space-4) var(--velo-screen-padding);
  -webkit-overflow-scrolling: touch;
}

/* Fill mode: the content area becomes a flex host that gives its full height
   to the child view instead of scrolling itself. min-height:0 is the standard
   nested-flex-scroll fix -- it lets the child's own overflow container shrink
   and scroll correctly. No padding here; the child owns its insets. */
.mobile-layout__main--fill {
  overflow: hidden;
  min-height: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}
</style>
