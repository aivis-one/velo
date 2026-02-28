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
  font-weight: 600;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.v-badge--success {
  background: #DCFCE7;
  color: #166534;
}

.v-badge--warning {
  background: #FEF3C7;
  color: #92400E;
}

.v-badge--error {
  background: #FEE2E2;
  color: #DC2626;
}

.v-badge--info {
  background: #DBEAFE;
  color: #1E40AF;
}
</style>
