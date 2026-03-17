<!--
  VELO Frontend -- VToggle Component (DS-3)

  Segmented control (tab-like toggle).

  Usage:
    <VToggle v-model="activeTab" :options="['День', 'Неделя', 'Месяц']" />
-->

<template>
  <div class="v-toggle">
    <button
      v-for="option in options"
      :key="option"
      class="v-toggle__item"
      :class="{ 'v-toggle__item--active': modelValue === option }"
      @click="$emit('update:modelValue', option)"
    >
      {{ option }}
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  options: string[]
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<style scoped>
.v-toggle {
  display: inline-flex;
  background: var(--velo-glass-blue-15);
  border-radius: var(--radius-full);
  padding: 2px;
}

.v-toggle__item {
  padding: 6px 16px;
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}

.v-toggle__item--active {
  background: var(--velo-nav-active-bg);
  color: white;
}
</style>
