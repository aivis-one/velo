<!--
  VELO Frontend -- VSegment Component (Phase B4.1)

  Segmented control: pick one option from a set. Covers in-page tab strips
  (Analytics, MasterPractices) and binary form toggles (Free/Paid). Glass pill
  canon: glass-blue-15 rest + primary active. Optional per-option count badge.

  Usage:
    <VSegment v-model="activeTab" :options="[
      { value: 'upcoming', label: 'Предстоящие', badge: 3 },
      { value: 'past',     label: 'Прошедшие' },
    ]" />
-->

<template>
  <div class="v-segment" role="tablist">
    <button
      v-for="opt in options"
      :key="opt.value"
      type="button"
      role="tab"
      :aria-selected="modelValue === opt.value"
      class="v-segment__item"
      :class="{ 'v-segment__item--active': modelValue === opt.value }"
      @click="$emit('update:modelValue', opt.value)"
    >
      {{ opt.label }}
      <span
        v-if="opt.badge !== undefined && opt.badge !== null && opt.badge !== ''"
        class="v-segment__badge"
      >
        {{ opt.badge }}
      </span>
    </button>
  </div>
</template>

<script setup lang="ts">
export interface SegmentOption {
  value: string
  label: string
  /** Optional count/marker shown as a pill after the label. */
  badge?: string | number
}

defineProps<{
  modelValue: string
  options: SegmentOption[]
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<style scoped>
.v-segment {
  display: flex;
  gap: var(--space-2);
}

.v-segment__item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  background: var(--velo-glass-blue-15);
  border: 1px solid var(--velo-glass-border);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.v-segment__item--active {
  color: var(--velo-white);
  background: var(--velo-primary);
  border-color: var(--velo-primary);
}

.v-segment__badge {
  background: rgba(255, 255, 255, 0.3);
  color: inherit;
  font-size: var(--text-xs);
  padding: 1px 6px;
  border-radius: var(--radius-full);
}
</style>
