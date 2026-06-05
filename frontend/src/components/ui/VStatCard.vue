<!--
  VELO Frontend -- VStatCard Component (Phase F2.1)

  Numeric stat card. Matches mockup .stat-card styles.
  Used in dashboards (user stats, admin stats, master analytics).

  Usage:
    <VStatCard value="156" label="участников" icon="👥" />
    <VStatCard value="€1,280" label="доход" />
-->

<template>
  <div
    class="v-stat"
    :class="{ 'v-stat--clickable': clickable }"
    :role="clickable ? 'button' : undefined"
    :tabindex="clickable ? 0 : undefined"
    @click="clickable ? $emit('click') : undefined"
    @keydown.enter.space.prevent="clickable ? $emit('click') : undefined"
  >
    <span v-if="icon" class="v-stat__icon">{{ icon }}</span>
    <div class="v-stat__value">{{ value }}</div>
    <div class="v-stat__label">{{ label }}</div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    value: string | number
    label: string
    icon?: string
    clickable?: boolean
  }>(),
  {
    icon: '',
    clickable: false,
  },
)

defineEmits<{
  click: []
}>()
</script>

<style scoped>
.v-stat {
  /* White surface standard (Figma 2026-06), matching the shipped user-dashboard
     stat cards: opaque white + 1px white border + radius-md, content centred.
     Replaces the old glass fill + blue border + radius-lg. */
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 9px;
  text-align: center;
  transition: all var(--transition-base);
}

.v-stat--clickable {
  cursor: pointer;
}

.v-stat--clickable:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.v-stat__icon {
  display: block;
  font-size: 24px;
}

.v-stat__value {
  /* Match shipped user-dashboard stat value: heading font, 32px, primary. */
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.64px;
  line-height: 1.1;
}

.v-stat__label {
  /* 13px (slightly under --text-xs) + secondary, no-wrap — matches user dash. */
  font-size: 13px;
  color: var(--velo-text-secondary);
  white-space: nowrap;
}
</style>
