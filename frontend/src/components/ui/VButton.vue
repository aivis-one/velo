<!--
  VELO Frontend -- VButton Component (Phase F2.1)

  Primary action element. VELΘ pill-shaped glass design.

  Variants: primary | secondary | danger | ghost | outline (alias → secondary)
  Sizes:    sm | md (default) | lg (alias → md)
  States:   disabled, loading (shows spinner + prevents clicks)

  Usage:
    <VButton variant="primary" @click="save">Save</VButton>
    <VButton variant="danger" size="sm" :loading="saving">Delete</VButton>
    <VButton block>Full width</VButton>
-->

<template>
  <button
    :class="[
      'v-btn',
      `v-btn--${normalizedVariant}`,
      `v-btn--${normalizedSize}`,
      {
        'v-btn--block': block,
        'v-btn--loading': loading,
      },
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="v-btn__spinner" />
    <span :class="{ 'v-btn__content--hidden': loading }">
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline'
    size?: 'sm' | 'md' | 'lg'
    block?: boolean
    disabled?: boolean
    loading?: boolean
  }>(),
  {
    variant: 'primary',
    size: 'md',
    block: false,
    disabled: false,
    loading: false,
  },
)

defineEmits<{
  click: [event: MouseEvent]
}>()

const normalizedVariant = computed(() =>
  props.variant === 'outline' ? 'secondary' : props.variant,
)
const normalizedSize = computed(() =>
  props.size === 'lg' ? 'md' : props.size,
)
</script>

<style scoped>
.v-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-family: var(--font-body);
  font-weight: 400;
  border: 1px solid #ffffff;
  cursor: pointer;
  transition: all var(--transition-base);
  text-decoration: none;
  position: relative;
  white-space: nowrap;
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-glow-white);
}

/* -- Sizes -- */
.v-btn--sm {
  padding: 8px 16px;
  font-size: var(--text-xs);
  min-height: 36px;
}

.v-btn--md {
  padding: 12px 24px;
  font-size: var(--text-sm);
  min-height: 50px;
}

/* -- Variants -- */
.v-btn--primary {
  background: var(--steel-button);
  color: white;
}

.v-btn--primary:hover:not(:disabled) {
  background: var(--steel-primary);
}

.v-btn--secondary {
  background: var(--surface-steel-alpha-60);
  color: var(--text-primary);
}

.v-btn--secondary:hover:not(:disabled) {
  background: var(--surface-steel-alpha-15);
}

.v-btn--danger {
  background: var(--pink-primary);
  color: white;
}

.v-btn--danger:hover:not(:disabled) {
  background: var(--pink-primary);
}

.v-btn--ghost {
  background: transparent;
  color: var(--text-primary);
}

.v-btn--ghost:hover:not(:disabled) {
  background: var(--surface-steel-alpha-15);
}

/* -- Modifiers -- */
.v-btn--block {
  width: 100%;
}

.v-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* -- Loading -- */
.v-btn--loading {
  cursor: wait;
}

.v-btn__content--hidden {
  visibility: hidden;
}

.v-btn__spinner {
  position: absolute;
  width: 18px;
  height: 18px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: v-btn-spin 0.6s linear infinite;
}

@keyframes v-btn-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
