<!--
  VELO Frontend -- VTag Component (DS-3)

  Pill-shaped category tag. VELΘ glass tint design.

  Variants: blue | pink | sand
  Usage:
    <VTag variant="blue">Йога</VTag>
    <VTag variant="pink">Медитация</VTag>
    <VTag variant="sand">Дыхание</VTag>
-->

<template>
  <span class="v-tag" :class="`v-tag--${variant}`">
    <slot />
  </span>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'blue' | 'pink' | 'sand'
  }>(),
  {
    variant: 'blue',
  },
)
</script>

<style scoped>
.v-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  font-size: var(--text-xs);
  font-weight: 400;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.v-tag--blue {
  background: var(--velo-blue-100);
  color: var(--velo-primary);
}

.v-tag--pink {
  background: var(--velo-pink-100);
  color: var(--velo-pink-300);
}

.v-tag--sand {
  background: var(--velo-sand-100);
  color: var(--velo-peach-700);
}
</style>
