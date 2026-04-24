<!--
  VELO Frontend -- VAccordion Component (DS-3)

  Expandable row with header and collapsible content.

  Usage:
    <VAccordion title="Подробности">
      <p>Hidden content here</p>
    </VAccordion>
-->

<template>
  <div class="v-accordion" :class="{ 'v-accordion--open': open }">
    <button class="v-accordion__header" :aria-label="open ? 'Свернуть' : 'Развернуть'" :aria-expanded="open" @click="open = !open">
      <span class="v-accordion__title">{{ title }}</span>
      <span class="v-accordion__arrow">›</span>
    </button>
    <div v-if="open" class="v-accordion__body">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  title: string
}>()

const open = ref(false)
</script>

<style scoped>
.v-accordion {
  border-bottom: 1px solid var(--border-subtle);
}

.v-accordion__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: var(--space-3) 0;
  font-size: var(--text-sm);
  color: var(--text-primary);
  text-align: left;
}

.v-accordion__arrow {
  font-size: var(--text-lg);
  color: var(--text-muted);
  transition: transform var(--transition-fast);
}

.v-accordion--open .v-accordion__arrow {
  transform: rotate(90deg);
}

.v-accordion__body {
  padding: 0 0 var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
</style>
