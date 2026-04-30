<!--
  VELO Frontend -- StatCard (S2 P07 C22 / P09 C33)

  Compact metric tile: large value + label below. Used on Dashboard
  ("12 Практик / 9.5 Часов") and Profile.
-->

<template>
  <div class="stat-card">
    <div class="stat-card__value">
      {{ value }}
    </div>
    <div class="stat-card__label">
      {{ label }}
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  value: string | number
  label: string
}>()
</script>

<style scoped>
.stat-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-1);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  flex: 1;
  min-width: 0;
}

.stat-card__value {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  line-height: 1;
}

.stat-card__label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
</style>
