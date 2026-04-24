<!--
  VELO Frontend -- VInput Component (Phase F2.1)

  Text input with label. VELΘ minimal style: no border at rest, focus ring.

  Usage:
    <VInput v-model="email" label="Email" type="email" placeholder="you@example.com" />
    <VInput v-model="name" label="Имя" />
-->

<template>
  <div class="v-input">
    <label v-if="label" class="v-input__label">{{ label }}</label>
    <input
      class="v-input__field"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue?: string
    label?: string
    placeholder?: string
    type?: string
    disabled?: boolean
  }>(),
  {
    modelValue: '',
    label: '',
    placeholder: '',
    type: 'text',
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
  font-weight: 400;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.v-input__field {
  width: 100%;
  height: 40px;
  padding: 0 var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--surface-steel-alpha-15);
  border: 2px solid transparent;
  border-radius: 5px;
  transition: border-color var(--transition-base);
}

.v-input__field:focus {
  outline: none;
  border-color: var(--steel-muted);
}

.v-input__field::placeholder {
  color: var(--text-muted);
}

.v-input__field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--surface-subtle);
}
</style>
