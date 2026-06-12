<!--
  VELO Frontend -- VInput Component (Phase F2.1)

  Text input with label. VELΘ minimal style: no border at rest, focus ring.
  `required` (Phase-3 master DS) -> renders the pink IconRequired seal in the
  right gutter, paired with the legend banner on the form. Replaces the inline
  "*"-asterisk pattern; old `label="… *"` usages keep working until migrated.

  Usage:
    <VInput v-model="email" label="Email" type="email" placeholder="you@example.com" />
    <VInput v-model="name" label="Название" required />
-->

<template>
  <div class="v-input" :class="{ 'v-input--error': !!error }">
    <label v-if="label" class="v-input__label">{{ label }}</label>

    <div class="v-input__row">
      <!-- Affix path: prefix/suffix slots (€ amount, inline action, …). The box
           carries the border/bg; the input goes bare inside. -->
      <div v-if="$slots.prefix || $slots.suffix" class="v-input__box">
        <span v-if="$slots.prefix" class="v-input__affix"><slot name="prefix" /></span>
        <input
          ref="inputEl"
          class="v-input__field v-input__field--bare"
          :type="type"
          :value="modelValue"
          :placeholder="placeholder"
          :disabled="disabled"
          v-bind="$attrs"
          @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        />
        <span v-if="$slots.suffix" class="v-input__affix"><slot name="suffix" /></span>
      </div>

      <!-- Plain path (default) — unchanged for every existing usage. -->
      <input
        v-else
        ref="inputEl"
        class="v-input__field"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        v-bind="$attrs"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />

      <!-- Required marker (DS pattern): pink seal in the right gutter. -->
      <IconRequired v-if="required" class="v-input__seal" :size="22" />
    </div>

    <span v-if="error" class="v-input__error">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { IconRequired } from '@/components/icons'

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
    /** Show the pink IconRequired seal in the right gutter (DS required marker). */
    required?: boolean
  }>(),
  {
    modelValue: '',
    label: '',
    placeholder: '',
    type: 'text',
    error: '',
    disabled: false,
    required: false,
  },
)

defineEmits<{
  'update:modelValue': [value: string]
}>()

// Expose focus() so callers can programmatically focus the field
// (e.g. autofocus on reveal). Works for both the plain and affix paths.
const inputEl = ref<HTMLInputElement | null>(null)
defineExpose({ focus: () => inputEl.value?.focus() })
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

/* Row = field (flex:1) + optional required seal in the right gutter. */
.v-input__row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.v-input__field {
  flex: 1;
  min-width: 0;
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

/* -- Affix box (prefix/suffix slots) -- */
.v-input__box {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 40px;
  padding: 0 var(--space-4);
  background: var(--velo-bg-card-solid);
  border: 2px solid transparent;
  border-radius: 5px;
  transition: border-color var(--transition-base);
}

.v-input__box:focus-within {
  border-color: var(--velo-border-input-focus);
}

.v-input--error .v-input__box {
  border-color: var(--velo-error);
}

.v-input__affix {
  flex-shrink: 0;
  font-size: var(--text-base);
  color: var(--velo-text-muted);
}

.v-input__field--bare {
  height: auto;
  flex: 1;
  min-width: 0;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0;
}

.v-input__field--bare:disabled {
  background: transparent;
}

/* Required seal — pink (--velo-error), sits beside the field, never shrinks. */
.v-input__seal {
  flex-shrink: 0;
  display: flex;
  color: var(--velo-error);
}

.v-input__error {
  display: block;
  font-size: var(--text-xs);
  color: var(--velo-error);
  margin-top: var(--space-1);
}
</style>
