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
    <main
      class="mobile-layout__main"
      :class="{
        'mobile-layout__main--fill': fill,
        'mobile-layout__main--has-header': !fill && headerCount > 0,
      }"
    >
      <slot />
    </main>
    <!-- Floating header island (G-1): VHeader teleports itself here so it sits
         ABOVE the masked feed instead of being eaten by the fog. Empty until a
         screen's VHeader mounts; the layer is click-through, the header's own
         interactive bits re-enable taps. -->
    <div class="mobile-layout__island" />
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
import { provideFloatingHeader } from '@/components/layout/useFloatingHeader'

// Headers (VHeader) teleport into __island and register here; while one is
// mounted the main gets extra top clearance under the island.
const headerCount = provideFloatingHeader()

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
     under the floating tab bar. The 4 zone sizes come from the --velo-fog-*
     table in variables.css; we alias them locally so the --has-header modifier
     can swap only the top two (bigger clearance under the header island).
     Padding clears the fade zones (top hard+fade, bottom fade+hard). */
  --fog-top-hard: var(--velo-fog-z1);
  --fog-top-fade: var(--velo-fog-z2);
  --fog-bot-fade: var(--velo-fog-z3);
  --fog-bot-hard: var(--velo-fog-z4);
  padding: calc(var(--fog-top-hard) + var(--fog-top-fade)) var(--velo-rail-pad-x)
    calc(var(--fog-bot-fade) + var(--fog-bot-hard));
  -webkit-mask-image: linear-gradient(
    to bottom,
    transparent 0,
    transparent var(--fog-top-hard),
    #000 calc(var(--fog-top-hard) + var(--fog-top-fade)),
    #000 calc(100% - var(--fog-bot-fade) - var(--fog-bot-hard)),
    transparent calc(100% - var(--fog-bot-hard)),
    transparent 100%
  );
  mask-image: linear-gradient(
    to bottom,
    transparent 0,
    transparent var(--fog-top-hard),
    #000 calc(var(--fog-top-hard) + var(--fog-top-fade)),
    #000 calc(100% - var(--fog-bot-fade) - var(--fog-bot-hard)),
    transparent calc(100% - var(--fog-bot-hard)),
    transparent 100%
  );
}

/* Screens with a floating VHeader island: bigger top clearance/fade so the feed
   emerges from under the island instead of colliding with the header (G-1). */
.mobile-layout__main--has-header {
  --fog-top-hard: var(--velo-fog-header-z1);
  --fog-top-fade: var(--velo-fog-header-z2);
}

/* Floating header island layer: pinned to the top of the (padded) frame,
   OUTSIDE the masked __main so the fog never eats the header. Click-through;
   VHeader's interactive bits (back button, action slot) re-enable taps. */
.mobile-layout__island {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: var(--z-sticky, 200);
  pointer-events: none;
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
