<!--
  VELO Frontend -- VToast Component (Phase F2.1)

  Renders active toasts. Mount once in App.vue.
  Matches mockup .toast styles: fixed bottom, slide up, auto-dismiss.

  Usage (in App.vue):
    <VToast />
-->

<template>
  <Teleport to="body">
    <TransitionGroup name="v-toast" tag="div" class="v-toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="v-toast"
        :class="`v-toast--${toast.variant}`"
        @click="dismiss(toast.id)"
      >
        <span class="v-toast__icon">{{ icon(toast.variant) }}</span>
        <span class="v-toast__message">{{ toast.message }}</span>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast, type ToastVariant } from '@/composables/useToast'

const { toasts, dismiss } = useToast()

function icon(variant: ToastVariant): string {
  switch (variant) {
    case 'success': return '✓'
    case 'error': return '✕'
    case 'info': return 'ℹ'
  }
}
</script>

<style scoped>
.v-toast-container {
  position: fixed;
  bottom: 80px;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  z-index: var(--z-toast, 500);
  pointer-events: none;
}

.v-toast {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  max-width: 90%;
  text-align: center;
  cursor: pointer;
  pointer-events: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.v-toast--success {
  background: var(--velo-success);
  color: white;
}

.v-toast--error {
  background: var(--velo-error);
  color: white;
}

.v-toast--info {
  background: var(--velo-text-primary);
  color: white;
}

.v-toast__icon {
  font-size: var(--text-base);
  flex-shrink: 0;
}

/* -- Transition -- */
.v-toast-enter-active {
  transition: all var(--transition-slow);
}

.v-toast-leave-active {
  transition: all var(--transition-base);
}

.v-toast-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.v-toast-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
