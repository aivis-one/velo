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
    <span
      v-if="icon"
      class="v-stat__icon"
    >{{ icon }}</span>
    <div class="v-stat__value">
      {{ value }}
    </div>
    <div class="v-stat__label">
      {{ label }}
    </div>
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
  background: var(--surface-elevated);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
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
  margin-bottom: var(--space-2);
}

.v-stat__value {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  line-height: 1.2;
}

.v-stat__label {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
}
</style>
