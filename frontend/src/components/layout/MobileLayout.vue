<!--
  VELO Frontend -- MobileLayout Component (Phase F2.1)

  *** TEMPORARY DIAGNOSTIC BUILD ***
  padding-top is hard-coded to 400px (NOT the safe-area inset) purely to answer
  one question: does pushing the content down by a large fixed amount move it
  OUT from under Telegram's control buttons?
    - If the content clears the buttons at 400px -> the mechanism works, the
      inset value was simply too small; we then wire the real inset back.
    - If the content is STILL under the buttons at 400px -> padding is not the
      right axis (the buttons share the content's coordinate space and move
      with it), and we change approach.
  Revert to the reactive inset (useSafeArea) after reading the result.
-->

<template>
  <div
    class="mobile-layout"
    :class="{ 'mobile-layout--fill': fill }"
    style="padding-top: 400px;"
  >
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
  box-sizing: border-box;
  /* padding-top set inline (temporary 400px diagnostic). */
}

.mobile-layout--fill {
  height: 100dvh;
  height: 100vh; /* fallback */
  min-height: 0;
}

.mobile-layout__main {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4) var(--velo-screen-padding);
  -webkit-overflow-scrolling: touch;
}

.mobile-layout__main--fill {
  overflow: hidden;
  min-height: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}
</style>
