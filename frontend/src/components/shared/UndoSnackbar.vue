<!--
  VELO Frontend — UndoSnackbar (S2-S3 SPEEDRUN MEGA-2 §C43)

  Floating bottom snackbar with action button. Auto-dismisses after timeout.
  Emits 'action' on button click; emits 'timeout' when auto-dismissed.
-->

<template>
  <div
    class="snack"
    role="status"
    aria-live="polite"
  >
    <span class="snack__msg">{{ message }}</span>
    <button
      type="button"
      class="snack__action"
      @click="onAction"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    message: string
    actionLabel: string
    timeout?: number
  }>(),
  { timeout: 3000 },
)

const emit = defineEmits<{
  (e: 'action'): void
  (e: 'timeout'): void
}>()

const timer = ref<ReturnType<typeof setTimeout> | null>(null)

function onAction(): void {
  if (timer.value) clearTimeout(timer.value)
  emit('action')
}

onMounted(() => {
  timer.value = setTimeout(() => {
    emit('timeout')
  }, props.timeout)
})

onUnmounted(() => {
  if (timer.value) clearTimeout(timer.value)
})
</script>

<style scoped>
.snack {
  position: fixed;
  bottom: var(--space-4);
  left: var(--space-4);
  right: var(--space-4);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--pink-primary, var(--text-primary));
  border-radius: var(--radius-full);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
}

.snack__msg {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.snack__action {
  background: transparent;
  border: 0;
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
  border: 1px solid var(--text-primary);
}
</style>
