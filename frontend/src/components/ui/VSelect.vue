<!--
  VELO Frontend -- VSelect Component (Phase F2.1)

  Native select dropdown. Matches mockup .form-select styles.

  Usage:
    <VSelect v-model="lang" label="Язык" :options="langOptions" />
-->

<template>
  <div class="v-select" :class="{ 'v-select--error': !!error }">
    <label v-if="label" class="v-select__label">{{ label }}</label>
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
    <span v-if="error" class="v-select__error">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
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
  }>(),
  {
    modelValue: '',
    label: '',
    placeholder: '',
    error: '',
    disabled: false,
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
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-2);
}

.v-select__field {
  width: 100%;
  height: 40px;
  padding: 0 40px 0 var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  background: white;
  border: 2px solid transparent;
  border-radius: 5px;
  transition: border-color var(--transition-base);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2394A3B8' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
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

.v-select__error {
  display: block;
  font-size: var(--text-xs);
  color: var(--velo-error);
  margin-top: var(--space-1);
}
</style>
