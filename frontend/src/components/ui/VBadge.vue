<!--
  VELO Frontend -- VBadge Component (Phase F2.1)

  Pill-shaped status badge. Matches mockup .badge styles.

  Usage:
    <VBadge variant="success">Подтверждено</VBadge>
    <VBadge variant="warning">Ожидание</VBadge>
    <VBadge variant="error">Отменено</VBadge>
    <VBadge variant="info">Новое</VBadge>
-->

<template>
  <span class="v-badge" :class="`v-badge--${variant}`">
    <slot />
  </span>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'success' | 'warning' | 'error' | 'info'
  }>(),
  {
    variant: 'info',
  },
)
</script>

<style scoped>
.v-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: var(--text-xs);
  font-weight: 400;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.v-badge--success {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}

.v-badge--warning {
  background: var(--velo-glass-peach-40);
  color: var(--velo-peach-700);
}

.v-badge--error {
  background: var(--velo-pink-100);
  color: var(--velo-pink-300);
}

.v-badge--info {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}
</style>
