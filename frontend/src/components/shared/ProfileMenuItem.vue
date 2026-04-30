<!--
  VELO Frontend -- ProfileMenuItem (S2 P09 C33 + S3 P12)

  Single profile-menu row: icon + label + (optional badge) + chevron-right.
  Either renders as <RouterLink :to> if `to` is set, or <button @click>.
-->

<template>
  <component
    :is="to ? 'RouterLink' : 'button'"
    :to="to"
    :type="to ? undefined : 'button'"
    class="pmi"
    :class="{ 'pmi--danger': danger }"
    @click="onClick"
  >
    <component
      :is="icon"
      class="pmi__icon"
      :size="20"
    />
    <span class="pmi__label">{{ label }}</span>
    <span
      v-if="badge"
      class="pmi__badge"
    >{{ badge }}</span>
    <IconChevronRight
      class="pmi__chev"
      :size="18"
    />
  </component>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { IconChevronRight } from '@/components/icons'

const props = defineProps<{
  icon: Component
  label: string
  to?: string
  badge?: string | number
  danger?: boolean
}>()

const emit = defineEmits<{ click: [] }>()

function onClick(): void {
  if (!props.to) emit('click')
}
</script>

<style scoped>
.pmi {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  text-decoration: none;
  cursor: pointer;
  text-align: left;
  transition: background var(--transition-fast);
}

.pmi:hover {
  background: var(--surface-steel-alpha-15);
}

.pmi--danger {
  color: var(--pink-primary);
}

.pmi__icon {
  flex-shrink: 0;
  color: currentColor;
}

.pmi__label {
  flex: 1;
}

.pmi__badge {
  background: var(--pink-primary);
  color: white;
  font-size: var(--text-xs);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.pmi__chev {
  color: var(--text-muted);
  flex-shrink: 0;
}
</style>
