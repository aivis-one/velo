<!--
  VELO Frontend -- VCheckbox Component (Phase F2.1)

  Custom checkbox with label. Matches mockup .checkbox styles.

  Usage:
    <VCheckbox v-model="agreed" label="Я согласен с условиями" />
-->

<template>
  <label class="v-checkbox" :class="{ 'v-checkbox--disabled': disabled }">
    <span class="v-checkbox__box" :class="{ 'v-checkbox__box--checked': modelValue }">
      <svg v-if="modelValue" viewBox="0 0 12 12" class="v-checkbox__icon">
        <path d="M10 3L4.5 8.5L2 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </span>
    <span v-if="label" class="v-checkbox__label">{{ label }}</span>
    <input
      type="checkbox"
      :checked="modelValue"
      :disabled="disabled"
      class="v-checkbox__input"
      @change="$emit('update:modelValue', ($event.target as HTMLInputElement).checked)"
    />
  </label>
</template>

<script setup lang="ts">
withDefaults(
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

defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>

<style scoped>
.v-checkbox {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
  user-select: none;
}

.v-checkbox--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.v-checkbox__input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.v-checkbox__box {
  width: 22px;
  height: 22px;
  border: 2px solid var(--velo-border);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.v-checkbox__box--checked {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: white;
}

.v-checkbox__icon {
  width: 12px;
  height: 12px;
}

.v-checkbox__label {
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  line-height: 1.4;
}
</style>
