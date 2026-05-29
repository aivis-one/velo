<!--
  VELO Frontend -- MobileLayout Component (Phase F2.1)

  Telegram safe area: padding-top is the reactive content safe-area top inset
  from useSafeArea() (backed by the @tma.js/sdk viewport signal), applied as an
  inline style so it re-renders when the inset arrives/changes. Verified that
  padding on this element DOES move the content (a hard 400px pushed the
  greeting far down), so the only remaining variable is the inset value itself,
  which the SDK provides per launch mode. box-sizing:border-box keeps the
  padding inside the height so 100dvh never overflows (incl. --fill).
-->

<template>
  <div
    class="mobile-layout"
    :class="{ 'mobile-layout--fill': fill }"
    :style="{ paddingTop: contentSafeTop + 'px' }"
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
import { useSafeArea } from '@/composables/useSafeArea'

defineProps<{
  tabs: TabItem[]
  activeTab?: string
  fill?: boolean
}>()

defineEmits<{
  navigate: [to: string]
}>()

// Reactive Telegram content safe-area top inset (px), bound to padding-top.
const { contentSafeTop } = useSafeArea()
</script>

<style scoped>
.mobile-layout {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  min-height: 100vh; /* fallback */
  background: transparent;
  box-sizing: border-box;
  /* padding-top applied inline from useSafeArea (reactive). */
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
