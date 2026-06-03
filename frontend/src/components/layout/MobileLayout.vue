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
    <!-- Floating header island (G-1): VHeader (and tab-screen headings) teleport
         themselves here so they sit ABOVE the masked feed instead of being eaten
         by the fog. MUST be rendered BEFORE <main> so the teleport target exists
         in the DOM before the slotted view (which teleports into it) mounts.
         The views also use <Teleport defer> as a second safeguard, but keeping
         the target first in source order makes the dependency explicit and
         avoids the first-mount "Invalid Teleport target" crash. The layer is
         absolutely positioned, so its DOM order does not change where it paints.
         Empty until a screen's header mounts; click-through, the header's own
         interactive bits re-enable taps. Its measured height drives the feed's
         top clearance (see mainStyle). -->
    <div ref="islandEl" class="mobile-layout__island" />
    <main
      class="mobile-layout__main"
      :class="{ 'mobile-layout__main--fill': fill }"
      :style="fill ? undefined : mainStyle"
    >
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import VTabBar, { type TabItem } from '@/components/layout/VTabBar.vue'
import { provideFloatingHeader } from '@/components/layout/useFloatingHeader'

// Host the floating-header island; headers teleport into it (see useFloatingHeader).
provideFloatingHeader()

// Measure the island so the feed clears EXACTLY its height -- any header content
// (a short greeting or a tall title+weekstrip) gets the right fog clearance with
// no hardcoded per-screen numbers.
const islandEl = ref<HTMLElement | null>(null)
const islandH = ref(0)
let ro: ResizeObserver | null = null
onMounted(() => {
  if (!islandEl.value) return
  ro = new ResizeObserver(() => {
    islandH.value = islandEl.value?.offsetHeight ?? 0
  })
  ro.observe(islandEl.value)
})
onBeforeUnmount(() => {
  ro?.disconnect()
  ro = null
})

// Island present (height > 0) -> override the top fog so content fades in just
// below it. Otherwise the default global fog table (variables.css) applies.
const mainStyle = computed(() => {
  if (islandH.value <= 0) return {}
  const hard = 40
  const fade = Math.max(0, islandH.value + 16 - hard)
  return {
    '--fog-top-hard': `${hard}px`,
    '--fog-top-fade': `${fade}px`,
  }
})

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
     table in variables.css; aliased locally so a screen with an island can
     override the top two via mainStyle (measured island height -> clearance).
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
