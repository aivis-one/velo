<!--
  VELO Frontend -- VSelect Component (Phase F2.1)

  Native select dropdown. Matches mockup .form-select styles.
  White plate canon (Phase-3) — unified with VInput as the single field surface
  (was glass-blue). `required` -> pink IconRequired seal in the right gutter.

  Usage:
    <VSelect v-model="lang" label="Язык" :options="langOptions" />
    <VSelect v-model="dir" label="Направление" :options="opts" required />
-->

<template>
  <div class="v-select" :class="{ 'v-select--error': !!error }">
    <label v-if="label" class="v-select__label">{{ label }}</label>
    <div class="v-select__row">
      <select
        class="v-select__field"
        :value="modelValue"
        :disabled="disabled"
        @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      >
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <option
          v-for="opt in options"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </option>
      </select>
      <!-- Required marker (DS pattern): pink seal in the right gutter. -->
      <IconRequired v-if="required" class="v-select__seal" :size="22" />
    </div>
    <span v-if="error" class="v-select__error">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
import { IconRequired } from '@/components/icons'

export interface SelectOption {
  value: string
  label: string
}

withDefaults(
  defineProps<{
    modelValue?: string
    label?: string
    placeholder?: string
    options: SelectOption[]
    error?: string
    disabled?: boolean
    /** Show the pink IconRequired seal in the right gutter (DS required marker). */
    required?: boolean
  }>(),
  {
    modelValue: '',
    label: '',
    placeholder: '',
    error: '',
    disabled: false,
    required: false,
  },
)

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<style scoped>
.v-select {
  margin-bottom: var(--space-4);
}

.v-select__label {
  display: block;
  /* Figma form spec: label Marmelad 18, primary — unified with VInput/VTextarea. */
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-2);
}

/* Row = field (flex:1) + optional required seal in the right gutter. */
.v-select__row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.v-select__field {
  flex: 1;
  min-width: 0;
  height: 40px;
  padding: 0 40px 0 var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  /* White plate canon — the single field surface, unified with VInput. */
  background: var(--velo-bg-card-solid);
  border: 2px solid transparent;
  border-radius: 5px;
  transition: border-color var(--transition-base);
  appearance: none;
  /* Primary-tinted chevron (operator SVG 2026-06-11). */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23627a9c' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
}

.v-select__field:focus {
  outline: none;
  border-color: var(--velo-border-input-focus);
}

.v-select__field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--velo-bg-subtle);
}

.v-select--error .v-select__field {
  border-color: var(--velo-error);
}

/* Required seal — pink (--velo-error), sits beside the field, never shrinks. */
.v-select__seal {
  flex-shrink: 0;
  display: flex;
  color: var(--velo-error);
}

.v-select__error {
  display: block;
  font-size: var(--text-xs);
  color: var(--velo-error);
  margin-top: var(--space-1);
}
</style>
