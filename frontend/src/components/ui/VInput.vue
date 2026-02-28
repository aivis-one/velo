<!--
  VELO Frontend -- VInput Component (Phase F2.1)

  Text input with label and error message. Matches mockup .form-input styles.

  Usage:
    <VInput v-model="email" label="Email" type="email" placeholder="you@example.com" />
    <VInput v-model="name" label="Имя" :error="nameError" />
-->

<template>
  <div class="v-input" :class="{ 'v-input--error': !!error }">
    <label v-if="label" class="v-input__label">{{ label }}</label>
    <input
      class="v-input__field"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <span v-if="error" class="v-input__error">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue?: string
    label?: string
    placeholder?: string
    type?: string
    error?: string
    disabled?: boolean
  }>(),
  {
    modelValue: '',
    label: '',
    placeholder: '',
    type: 'text',
    error: '',
    disabled: false,
  },
)

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<style scoped>
.v-input {
  margin-bottom: var(--space-4);
}

.v-input__label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-2);
}

.v-input__field {
  width: 100%;
  padding: 12px var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  background: white;
  border: 2px solid var(--velo-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}

.v-input__field:focus {
  outline: none;
  border-color: var(--velo-primary);
  box-shadow: 0 0 0 3px rgba(51, 77, 110, 0.1);
}

.v-input__field::placeholder {
  color: var(--velo-text-muted);
}

.v-input__field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--velo-bg-subtle);
}

/* Error state */
.v-input--error .v-input__field {
  border-color: var(--velo-error);
}

.v-input--error .v-input__field:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.v-input__error {
  display: block;
  font-size: var(--text-xs);
  color: var(--velo-error);
  margin-top: var(--space-1);
}
</style>
