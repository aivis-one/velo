<!--
  VELO Frontend -- VNotification Component (DS-3)

  Inline notification banner. Replaces inline error states on inputs.

  Variants: warning | success
  Usage:
    <VNotification variant="warning">Заполните все поля</VNotification>
    <VNotification variant="success">Сохранено!</VNotification>
-->

<template>
  <div class="v-notification" :class="`v-notification--${variant}`">
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'warning' | 'success'
  }>(),
  {
    variant: 'warning',
  },
)
</script>

<style scoped>
.v-notification {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
}

.v-notification--warning {
  background: var(--velo-glass-peach-40);
  color: var(--velo-peach-700);
}

.v-notification--success {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-700);
}
</style>
