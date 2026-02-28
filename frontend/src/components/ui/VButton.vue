<!--
  VELO Frontend -- VButton Component (Phase F2.1)

  Primary action element. Matches mockup .btn styles exactly.

  Variants: primary | secondary | danger | ghost | outline
  Sizes:    sm | md (default) | lg
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
      `v-btn--${variant}`,
      `v-btn--${size}`,
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
withDefaults(
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
</script>

<style scoped>
.v-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-family: var(--font-body);
  font-weight: 600;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-base);
  text-decoration: none;
  position: relative;
  white-space: nowrap;
  border-radius: var(--radius-md);
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
  min-height: 48px;
}

.v-btn--lg {
  padding: 16px 32px;
  font-size: var(--text-base);
  min-height: 52px;
}

/* -- Variants -- */
.v-btn--primary {
  background: var(--velo-primary);
  color: white;
  border-color: var(--velo-primary);
}

.v-btn--primary:hover:not(:disabled) {
  background: var(--velo-primary-dark);
  border-color: var(--velo-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.v-btn--secondary {
  background: white;
  color: var(--velo-primary);
  border-color: var(--velo-primary);
}

.v-btn--secondary:hover:not(:disabled) {
  background: var(--velo-primary);
  color: white;
}

.v-btn--outline {
  background: white;
  color: var(--velo-primary);
  border-color: var(--velo-border);
}

.v-btn--outline:hover:not(:disabled) {
  border-color: var(--velo-primary-light);
  background: var(--velo-bg-subtle);
}

.v-btn--danger {
  background: white;
  color: var(--velo-error);
  border-color: var(--velo-error);
}

.v-btn--danger:hover:not(:disabled) {
  background: var(--velo-error);
  color: white;
}

.v-btn--ghost {
  background: transparent;
  color: var(--velo-primary);
  border-color: transparent;
}

.v-btn--ghost:hover:not(:disabled) {
  background: rgba(51, 77, 110, 0.1);
}

/* -- Modifiers -- */
.v-btn--block {
  width: 100%;
}

.v-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
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
