<!--
  VELO Frontend -- VInput Component (Phase F2.1)

  Text input with label. VELΘ minimal style: no border at rest, focus ring.

  Usage:
    <VInput v-model="email" label="Email" type="email" placeholder="you@example.com" />
    <VInput v-model="name" label="Имя" />
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
      v-bind="$attrs"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <span v-if="error" class="v-input__error">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
// inheritAttrs:false — forward native attrs (min/max/step/inputmode/…) onto the
// inner <input>, not the wrapper div. Keeps VInput at parity with VSelect/VTextarea.
defineOptions({ inheritAttrs: false })

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
  /* Figma form spec (2 Edit Profile.svg): label Marmelad 18, primary colour. */
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-2);
}

.v-input__field {
  width: 100%;
  height: 40px;
  padding: 0 var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  /* Figma: form fields are SOLID WHITE plates (was glass-blue, which read as
     "transparent" on the photo background). This is the single field standard. */
  background: var(--velo-bg-card-solid);
  border: 2px solid transparent;
  border-radius: 5px;
  transition: border-color var(--transition-base);
}

.v-input__field:focus {
  outline: none;
  border-color: var(--velo-border-input-focus);
}

.v-input__field::placeholder {
  color: var(--velo-text-muted);
}

.v-input__field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--velo-bg-subtle);
}

.v-input--error .v-input__field {
  border-color: var(--velo-error);
}

.v-input__error {
  display: block;
  font-size: var(--text-xs);
  color: var(--velo-error);
  margin-top: var(--space-1);
}
</style>
