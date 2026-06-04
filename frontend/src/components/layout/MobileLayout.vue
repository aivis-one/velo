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
      :class="{
        'mobile-layout__main--fill': fill,
        'mobile-layout__main--fog': fog && !fill,
      }"
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
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import VTabBar, { type TabItem } from '@/components/layout/VTabBar.vue'
import { provideFloatingHeader } from '@/components/layout/useFloatingHeader'

// Host the floating-header island; headers teleport into it (see useFloatingHeader).
provideFloatingHeader()

// Measure the island so the feed clears EXACTLY its height -- any header content
// (a short greeting or a tall title+weekstrip) gets the right top clearance with
// no hardcoded per-screen numbers.
//
// We watch the island with BOTH a ResizeObserver (size changes) AND a
// MutationObserver (children added/removed). Screen headers arrive via <Teleport>
// AFTER mount, so the island grows from 0 -> content height as a child insertion;
// a ResizeObserver alone can miss/throttle that (e.g. a backgrounded tab), which
// left the feed underlapping the header. The MutationObserver catches the teleport
// insertion reliably, and we also measure once on nextTick after mount.
const islandEl = ref<HTMLElement | null>(null)
const islandH = ref(0)
let ro: ResizeObserver | null = null
let mo: MutationObserver | null = null
function measureIsland(): void {
  islandH.value = islandEl.value?.offsetHeight ?? 0
}
onMounted(() => {
  if (!islandEl.value) return
  ro = new ResizeObserver(measureIsland)
  ro.observe(islandEl.value)
  mo = new MutationObserver(measureIsland)
  mo.observe(islandEl.value, { childList: true, subtree: true, characterData: true })
  void nextTick(measureIsland)
})
onBeforeUnmount(() => {
  ro?.disconnect()
  mo?.disconnect()
  ro = null
  mo = null
})

const props = defineProps<{
  tabs: TabItem[]
  activeTab?: string
  fill?: boolean
  /** Hide the bottom tab bar (e.g. the diary is an immersive full-screen mode
   *  that has its own exit in the "..." menu instead of tab navigation). */
  hideTabBar?: boolean
  /** Edge-to-edge fog mask: content dissolves at the top/bottom edges. ONLY for
   *  long scrolling lists/feeds (dashboard, calendar, bookings, ...). Detail
   *  screens, forms and the profile opt OUT — their footers/actions must stay
   *  crisp, not fade into the mask. Clearance (top island + bottom tab bar) is
   *  applied regardless of fog; this flag only toggles the fade mask. */
  fog?: boolean
}>()

// Vertical padding + fog zones for __main. CLEARANCE is always applied so the
// content never hides under the floating header island (top) or the floating
// tab bar (bottom); the FADE MASK is layered on top only when `fog` is set
// (see .mobile-layout__main--fog). Horizontal rail padding lives in the CSS.
//
//   top    -> measured island height + gap (floating header), else a small base
//   bottom -> clear the floating tab bar when present, else a small base
//   fog-*  -> mask fade zones, aligned to the clearances (used only with --fog)
const mainStyle = computed(() => {
  const top = islandH.value > 0 ? islandH.value + 16 : (props.fog ? 60 : 16)
  const bottom = props.hideTabBar ? 24 : 160
  return {
    paddingTop: `${top}px`,
    paddingBottom: `${bottom}px`,
    '--fog-top-hard': '40px',
    '--fog-top-fade': `${Math.max(0, top - 40)}px`,
    '--fog-bot-fade': '70px',
    '--fog-bot-hard': '90px',
  }
})

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
  /* Hide the scrollbar (same as the diary feed — "scrollbar hidden app-wide").
     Otherwise the scrollbar gutter (global.css thin 4px) insets the SCROLLING
     content on the right, while the floating header island and the tab bar live
     in non-scrolling absolute layers at the true rail — so cards/selectors drift
     ~scrollbar-width to the right of the chrome. Hiding it keeps every element on
     the single --velo-rail-pad-x rail. */
  scrollbar-width: none;       /* Firefox / standard */
  -ms-overflow-style: none;    /* legacy Edge */
  /* 24px content rail on both sides (Figma). Vertical padding (top island
     clearance + bottom tab-bar clearance) comes from mainStyle inline so it can
     react to the measured island height. */
  padding-left: var(--velo-rail-pad-x);
  padding-right: var(--velo-rail-pad-x);
}

.mobile-layout__main::-webkit-scrollbar {
  display: none;               /* WebKit / Blink (Telegram webview) */
}

/* Edge-to-edge fog: top/bottom fade mask for long scrolling lists ONLY. Opt-in
   via the `fog` prop. The fade zones (--fog-*) are set by mainStyle and aligned
   to the clearance padding, so content dissolves exactly at the padded edges.
   Detail screens, forms and the profile do NOT get this class -- their footers
   and actions stay fully opaque. */
.mobile-layout__main--fog {
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
