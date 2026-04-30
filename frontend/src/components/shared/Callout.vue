<!--
  VELO Frontend -- Callout (S2 P08 C26+C27+C28)

  Inline info/warning callout box: variant + optional icon + title + body.
  Variants: amber (warnings — Контраиндикации), mint (positive — feedback hint).
-->

<template>
  <div
    class="callout"
    :class="`callout--${variant}`"
  >
    <component
      :is="icon"
      v-if="icon"
      class="callout__icon"
      :size="20"
    />
    <div class="callout__body">
      <div
        v-if="title"
        class="callout__title"
      >
        {{ title }}
      </div>
      <div class="callout__text">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

withDefaults(
  defineProps<{
    variant?: 'amber' | 'mint'
    icon?: Component
    title?: string
  }>(),
  {
    variant: 'amber',
    icon: undefined,
    title: '',
  },
)
</script>

<style scoped>
.callout {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid #ffffff;
}

.callout--amber {
  background: var(--surface-warm-alpha-30, var(--surface-steel-alpha-15));
  color: var(--text-primary);
}

.callout--mint {
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
  color: var(--text-primary);
}

.callout__icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.callout__body {
  flex: 1;
  min-width: 0;
}

.callout__title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.callout__text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  line-height: 1.5;
  color: var(--text-secondary);
}
</style>
