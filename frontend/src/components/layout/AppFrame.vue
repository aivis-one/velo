<!--
  VELO Frontend -- AppFrame

  Single app-wide frame that applies the Telegram top safe-area offset in ONE
  place, so individual screens never deal with insets. Wraps everything the
  user sees (loading, stub, welcome, onboarding, the router) in App.vue.

  The offset comes from useSafeArea() (sum of Telegram's top insets minus the
  overlap; reactive via the @tma.js/sdk viewport signal) and is applied as an
  inline padding-top so it re-renders when the inset arrives. Out of fullscreen
  the offset is 0 and the frame is a transparent passthrough.

  box-sizing:border-box keeps the padding inside the frame's height so a child
  using height:100% fills the area BELOW the safe-area padding rather than
  overflowing past the bottom edge.
-->

<template>
  <div class="app-frame" :style="{ paddingTop: contentSafeTop + 'px' }">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { useSafeArea } from '@/composables/useSafeArea'

const { contentSafeTop } = useSafeArea()
</script>

<style scoped>
.app-frame {
  /* Definite viewport height so children using height:100% resolve against it
     (fill-mode screens like the diary need a bounded height to scroll their
     inner body instead of growing the whole frame). box-sizing:border-box keeps
     the safe-area padding inside this height. */
  height: 100vh; /* fallback for browsers without lvh */
  /* lvh (large viewport height), NOT dvh: the *stable* large height that does
     not shrink when the iOS keyboard opens. With dvh the frame reflowed on
     keyboard open, re-anchoring the fixed #app::before bg layer (the "dancing
     background"). Paired with useBackgroundStabilizer's counter-shift. */
  height: 100lvh;
  min-height: 100vh;
  /* Fixed mobile design frame (Figma 402px). Content never grows wider than the
     design width, so the absolute px geometry taken from the 402px mockups stays
     valid; on phones <=402 the frame is full-width. Centered, with the photo
     background (#app::before, fixed/full-width) showing through any side gutters
     on wide viewports (tablet / desktop Telegram / browser). */
  width: 100%;
  max-width: var(--velo-screen-width);
  margin-inline: auto;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background: transparent;
  /* ROOT-LOCK: nothing may push this frame taller than its own definite
     height (that would drag #app -- and #app::before's bg -- along with it).
     Every screen mounted here owns its OWN internal .velo-kbd-scroll
     container for overflow; the frame itself never scrolls. */
  overflow: hidden;
}

/* The single child (one of the gated screens) fills the remaining height. */
.app-frame > :deep(*) {
  flex: 1 1 auto;
  min-height: 0;
}
</style>
