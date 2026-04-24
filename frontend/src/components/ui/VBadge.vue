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
  background: var(--surface-teal-alpha-30);
  color: var(--teal-500);
}

.v-badge--warning {
  background: var(--surface-warm-alpha-40);
  color: var(--warm-deep);
}

.v-badge--error {
  background: var(--pink-50);
  color: var(--pink-primary);
}

.v-badge--info {
  background: var(--surface-teal-alpha-30);
  color: var(--teal-500);
}
</style>
