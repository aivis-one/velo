<!--
  VELO Frontend -- VRadioGroup Component (Phase-3 master DS)

  Single-choice radio list + labels. DS-token control (the DS had only VSwitch).
  Selected = primary fill + white IconCheck inside a circle, matching the
  operator SVG (2026-06-11) — the selected radio shows a check, not a dot.

  Usage:
    <VRadioGroup v-model="recurrence" :options="[
      { label: 'Каждый день',    value: 'daily' },
      { label: 'Каждую неделю',  value: 'weekly' },
      { label: 'Раз в две недели', value: 'biweekly' },
    ]" />
-->

<template>
  <div class="v-radio-group" role="radiogroup">
    <button
      v-for="opt in options"
      :key="opt.value"
      type="button"
      role="radio"
      :aria-checked="modelValue === opt.value"
      class="v-radio"
      @click="$emit('update:modelValue', opt.value)"
    >
      <span class="v-radio__mark" :class="{ 'v-radio__mark--on': modelValue === opt.value }">
        <IconCheck v-if="modelValue === opt.value" class="v-radio__check" :size="12" />
      </span>
      <span class="v-radio__label">{{ opt.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { IconCheck } from '@/components/icons'

export interface RadioOption {
  value: string
  label: string
}

defineProps<{
  modelValue: string
  options: RadioOption[]
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<style scoped>
.v-radio-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.v-radio {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0;
  border: none;
  background: none;
  font-family: var(--font-body);
  text-align: left;
  cursor: pointer;
}

.v-radio__mark {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1.5px solid var(--velo-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-fast);
}

.v-radio__mark--on {
  background: var(--velo-primary);
}

.v-radio__check {
  color: var(--velo-white);
}

.v-radio__label {
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
}
</style>
