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

  Telegram safe area (2026-05): launched from the chat list ("Открыть"),
  Telegram opens the Mini App in fullscreen and draws its own Close/menu
  controls ON TOP of our content (no native header). The content safe-area
  inset (--tg-content-safe-area-inset-top, set live by the SDK) is how far down
  the content must start to clear those controls. Launched from inside the chat
  the inset is 0 (Telegram draws its own header), so the padding is a no-op
  there. Verified on device: fullscreen inset = 46px, in-chat inset = 0px.
  box-sizing:border-box keeps the padding INSIDE the height so 100dvh never
  overflows (including the --fill branch below).
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
  /* Push all content below Telegram's native controls in fullscreen; no-op in
     chat mode (inset 0). See file header for the device-verified values. */
  box-sizing: border-box;
  padding-top: var(--tg-content-safe-area-inset-top, 0px);
}

/* Fill mode needs a DEFINITE root height (not just min-height), otherwise the
   flex chain below has nothing to resolve flex:1 / height:100% against and the
   content area collapses to its content -- which is exactly why the composer
   used to stick under the last card instead of the bottom. Locking the root to
   the viewport height makes `main` (flex:1) take "viewport - header - tabbar",
   and the diary view fills that, pinning the composer above the tab bar.
   With box-sizing:border-box the safe-area padding-top above stays INSIDE this
   height, so the column is "100dvh minus inset minus header minus tabbar" and
   the composer remains pinned above the tab bar in both launch modes. */
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
