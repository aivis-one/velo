<!--
  VELO Frontend -- VBadge Component (Phase F2.1)

  Pill-shaped status badge. Matches mockup .badge styles.

  Usage:
    <VBadge variant="success">Подтверждено</VBadge>
    <VBadge variant="warning">Ожидание</VBadge>
    <VBadge variant="error">Отменено</VBadge>
    <VBadge variant="info">Новое</VBadge>
    <VBadge variant="blue">Бесплатно</VBadge>

  `blue` is the calm price/free tone (blue-100 / primary), shared by the
  practice-card "Бесплатно"/price badges so they no longer hand-roll their own
  span. Same 4×10 / radius-badge shape as every other variant.
-->

<template>
  <span class="v-badge" :class="`v-badge--${variant}`">
    <slot />
  </span>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'success' | 'warning' | 'error' | 'info' | 'blue'
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
  border-radius: var(--velo-radius-badge);
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

/* Blue -- calm price / "free" tone (matches VTag blue colours) */
.v-badge--blue {
  background: var(--velo-blue-100);
  color: var(--velo-primary);
}
</style>
