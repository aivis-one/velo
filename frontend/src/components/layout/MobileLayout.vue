<!--
  VELO Frontend -- MobileLayout Component (Phase F2.1)

  Telegram safe area is NO LONGER handled here -- it is applied once, app-wide,
  by AppFrame (see components/layout/AppFrame.vue) which wraps everything in
  App.vue. MobileLayout just lays out header / scrollable main / tab bar inside
  the area AppFrame already padded. Heights are 100% (not 100dvh) so the layout
  fills the space BELOW AppFrame's safe-area padding instead of overflowing it.
-->

<template>
  <div
    class="mobile-layout"
    :class="{ 'mobile-layout--fill': fill }"
  >
    <slot name="header" />
    <main class="mobile-layout__main" :class="{ 'mobile-layout__main--fill': fill }">
      <slot />
    </main>
    <VTabBar
      v-if="!hideTabBar"
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
  fill?: boolean
  /** Hide the bottom tab bar (e.g. the diary is an immersive full-screen mode
   *  that has its own exit in the "..." menu instead of tab navigation). */
  hideTabBar?: boolean
}>()

defineEmits<{
  navigate: [to: string]
}>()
</script>

<style scoped>
.mobile-layout {
  display: flex;
  flex-direction: column;
  /* Fill the height AppFrame gives us (below its safe-area padding). */
  min-height: 100%;
  /* Anchor for the floating tab bar (absolute) so the feed scrolls under it. */
  position: relative;
  background: transparent;
  box-sizing: border-box;
}

.mobile-layout--fill {
  height: 100%;
  min-height: 0;
}

.mobile-layout__main {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  /* Diary-standard: 24px rail + 4-zone fog. Content dissolves at the top and
     under the floating tab bar. Tune the dissolve via the --velo-fog-* table in
     variables.css. Padding clears the fade zones (top z1+z2, bottom z3+z4). */
  padding: calc(var(--velo-fog-z1) + var(--velo-fog-z2)) var(--velo-rail-pad-x)
    calc(var(--velo-fog-z3) + var(--velo-fog-z4));
  -webkit-mask-image: linear-gradient(
    to bottom,
    transparent 0,
    transparent var(--velo-fog-z1),
    #000 calc(var(--velo-fog-z1) + var(--velo-fog-z2)),
    #000 calc(100% - var(--velo-fog-z3) - var(--velo-fog-z4)),
    transparent calc(100% - var(--velo-fog-z4)),
    transparent 100%
  );
  mask-image: linear-gradient(
    to bottom,
    transparent 0,
    transparent var(--velo-fog-z1),
    #000 calc(var(--velo-fog-z1) + var(--velo-fog-z2)),
    #000 calc(100% - var(--velo-fog-z3) - var(--velo-fog-z4)),
    transparent calc(100% - var(--velo-fog-z4)),
    transparent 100%
  );
}

.mobile-layout__main--fill {
  overflow: hidden;
  min-height: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  /* Fill screens (diary) own their layout + fog -- opt out of the shared one. */
  -webkit-mask-image: none;
  mask-image: none;
}
</style>
