<!--
  VELO Frontend -- VTextarea Component (Phase F2.1)

  Multiline text input. Matches mockup .form-textarea styles.

  Usage:
    <VTextarea v-model="bio" label="О себе" :rows="4" placeholder="Расскажите..." />
-->

<template>
  <div class="v-textarea" :class="{ 'v-textarea--error': !!error }">
    <label v-if="label" class="v-textarea__label">{{ label }}</label>
    <textarea
      class="v-textarea__field"
      :value="modelValue"
      :placeholder="placeholder"
      :rows="rows"
      :disabled="disabled"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
    <span v-if="error" class="v-textarea__error">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue?: string
    label?: string
    placeholder?: string
    rows?: number
    error?: string
    disabled?: boolean
  }>(),
  {
    modelValue: '',
    label: '',
    placeholder: '',
    rows: 3,
    error: '',
    disabled: false,
  },
)

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<style scoped>
.v-textarea {
  margin-bottom: var(--space-4);
}

.v-textarea__label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.v-textarea__field {
  width: 100%;
  padding: 10px var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--surface-steel-alpha-15);
  border: 2px solid transparent;
  border-radius: 5px;
  transition: border-color var(--transition-base);
  min-height: 100px;
  resize: vertical;
}

.v-textarea__field:focus {
  outline: none;
  border-color: var(--steel-muted);
}

.v-textarea__field::placeholder {
  color: var(--text-muted);
}

.v-textarea__field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--surface-subtle);
}

.v-textarea--error .v-textarea__field {
  border-color: var(--pink-primary);
}

.v-textarea__error {
  display: block;
  font-size: var(--text-xs);
  color: var(--pink-primary);
  margin-top: var(--space-1);
}
</style>
