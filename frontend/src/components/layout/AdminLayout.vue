<!--
  VELO Frontend -- AdminLayout Component (Phase F2.1; DS rebuild 2026-06-14)

  Full-screen layout for the admin role: optional header slot + scrollable content
  + the admin tab bar (VAdminTabBar -- stadium pills + count badges, the admin's
  own nav, distinct from the user/master VTabBar).

  `fog` (dashboard feed): edge-to-edge dissolve mask + 24px content rail, matching
  the user/master MobileLayout feed. List/detail admin screens leave it off (their
  footers/actions stay crisp) until they are rebuilt to the new design.

  Usage:
    <AdminLayout :tabs="ADMIN_TABS" :tab-items="withBadges" :active-tab="path" fog>
      <RouterView />
    </AdminLayout>
-->

<template>
  <div class="admin-layout">
    <slot name="header" />
    <main class="admin-layout__main" :class="{ 'admin-layout__main--fog': fog }">
      <slot />
    </main>
    <VAdminTabBar
      :items="tabItems ?? tabs"
      :active="activeTab"
      @navigate="$emit('navigate', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import VAdminTabBar from '@/components/layout/VAdminTabBar.vue'
import type { TabItem } from '@/components/layout/VTabBar.vue'

defineProps<{
  tabs: TabItem[]
  /** Tab items carrying live badge counts. Falls back to `tabs` when omitted. */
  tabItems?: TabItem[]
  activeTab?: string
  /** Edge-to-edge fog mask + 24px rail for the scrolling dashboard feed. */
  fog?: boolean
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
  /* Anchor for the floating (position:absolute) VAdminTabBar. */
  position: relative;
}

.admin-layout__main {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  /* Default (list/detail admin screens, pre-rebuild): plain padding, no fog. */
  padding: var(--space-4) var(--space-4)
    calc(112px + env(safe-area-inset-bottom, 0px));
}

/* Dashboard feed: edge-to-edge fog + 24px rail (matches user/master MobileLayout).
   NB: the fog literals (40/60/160/90) mirror MobileLayout's hardcoded defaults --
   both join the parked FOG-TOKENS-UNIFY pass; not re-tokenised here to avoid a
   second divergent scheme. Admin has no floating header island, so the top
   clearance is a flat 60 (no measured-island math). */
.admin-layout__main--fog {
  padding: 60px var(--velo-rail-pad-x)
    calc(160px + env(safe-area-inset-bottom, 0px));
  scrollbar-width: none;
  -ms-overflow-style: none;
  -webkit-mask-image: linear-gradient(
    to bottom,
    transparent 0,
    transparent 40px,
    #000 60px,
    #000 calc(100% - 160px),
    transparent calc(100% - 90px),
    transparent 100%
  );
  mask-image: linear-gradient(
    to bottom,
    transparent 0,
    transparent 40px,
    #000 60px,
    #000 calc(100% - 160px),
    transparent calc(100% - 90px),
    transparent 100%
  );
}

.admin-layout__main--fog::-webkit-scrollbar {
  display: none;
}
</style>
