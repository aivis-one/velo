<!--
  VELO Frontend -- VCheckbox Component (Phase-3 master DS)

  Square checkbox + label. DS-token control (the DS had only VSwitch; the
  practice "Повторение" section needs a real checkbox). Checked = primary fill
  + white IconCheck, matching the operator SVG (2026-06-11).

  Usage:
    <VCheckbox v-model="isRecurring" label="Сделать регулярной" />
-->

<template>
  <button
    type="button"
    role="checkbox"
    :aria-checked="modelValue"
    class="v-checkbox"
    :class="{ 'v-checkbox--disabled': disabled }"
    :disabled="disabled"
    @click="toggle"
  >
    <span class="v-checkbox__box" :class="{ 'v-checkbox__box--on': modelValue }">
      <IconCheck v-if="modelValue" class="v-checkbox__check" :size="14" />
    </span>
    <span v-if="label || $slots.default" class="v-checkbox__label"
      ><slot>{{ label }}</slot></span
    >
  </button>
</template>

<script setup lang="ts">
import { IconCheck } from '@/components/icons'

const props = withDefaults(
  defineProps<{
    modelValue?: boolean
    label?: string
    disabled?: boolean
  }>(),
  {
    modelValue: false,
    label: '',
    disabled: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

function toggle(): void {
  if (props.disabled) return
  emit('update:modelValue', !props.modelValue)
}
</script>

<style scoped>
.v-checkbox {
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

.v-checkbox--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.v-checkbox__box {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 5px;
  border: 1.5px solid var(--velo-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-fast);
}

.v-checkbox__box--on {
  background: var(--velo-primary);
}

.v-checkbox__check {
  color: var(--velo-white);
}

.v-checkbox__label {
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
}
</style>
