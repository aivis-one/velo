<!--
  VELO Frontend -- VChip Component (Phase B4.3)

  Glass pill chip. Two roles:
    - static tag (default): non-interactive label (e.g. master methods).
    - selectable (clickable + active): filter chips inside modals.

  Sizes: sm (default, compact tag) | md (roomier, filter chips).

  Usage:
    <VChip>Медитация</VChip>
    <VChip size="md" clickable :active="on" @click="toggle">Заметки</VChip>
-->

<template>
  <component
    :is="clickable ? 'button' : 'span'"
    :type="clickable ? 'button' : undefined"
    class="v-chip"
    :class="{
      'v-chip--md': size === 'md',
      'v-chip--clickable': clickable,
      'v-chip--active': active,
    }"
    @click="clickable && $emit('click', $event)"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: 'sm' | 'md'
    active?: boolean
    clickable?: boolean
  }>(),
  {
    size: 'sm',
    active: false,
    clickable: false,
  },
)

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<style scoped>
.v-chip {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  background: var(--velo-glass-blue-15);
  border: 1px solid var(--velo-glass-border);
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-primary);
  white-space: nowrap;
}

.v-chip--md {
  padding: var(--space-2) var(--space-4);
}

.v-chip--clickable {
  /* Selectable (filter) chips read as muted until active. */
  color: var(--velo-text-secondary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.v-chip--clickable:hover {
  opacity: 0.85;
}

.v-chip--active {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: var(--velo-white);
}
</style>
