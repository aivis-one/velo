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
  /* Full viewport height; children size against 100% of this (below padding). */
  min-height: 100dvh;
  min-height: 100vh; /* fallback */
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background: transparent;
}

/* The single child (one of the gated screens) fills the remaining height. */
.app-frame > :deep(*) {
  flex: 1 1 auto;
  min-height: 0;
}
</style>
