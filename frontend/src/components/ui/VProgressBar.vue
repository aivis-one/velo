<!--
  VELO Frontend -- VProgressBar Component (Phase F2.1)

  Horizontal progress bar. Matches mockup .metric-bar fill pattern.

  Usage:
    <VProgressBar :value="75" :max="100" />
    <VProgressBar :value="42" :max="100" color="var(--velo-warning)" />
-->

<template>
  <div class="v-progress">
    <div class="v-progress__track">
      <div
        class="v-progress__fill"
        :style="{ width: pct + '%', background: color }"
      />
    </div>
    <span v-if="showLabel" class="v-progress__label">{{ pct }}%</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    value: number
    max?: number
    color?: string
    showLabel?: boolean
  }>(),
  {
    max: 100,
    color: 'var(--velo-primary)',
    showLabel: false,
  },
)

const pct = computed(() => {
  if (props.max <= 0) return 0
  return Math.round(Math.min((props.value / props.max) * 100, 100))
})
</script>

<style scoped>
.v-progress {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.v-progress__track {
  flex: 1;
  height: 8px;
  background: var(--velo-bg-subtle);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.v-progress__fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

.v-progress__label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--velo-text-secondary);
  min-width: 36px;
  text-align: right;
}
</style>
