<!--
  VELO Frontend -- ConfirmModal (S4 P14 C60 — extracted from EditPracticeView
  per BACKLOG #48 confirm-modal unification target).

  Teleport-inline modal idiom (NOT VModal) consistent with established codebase
  pattern across Diary overlays + EntryActionMenu + UndoSnackbar (MEGA-2).

  Prop API derived from EditPracticeView's `confirmDialog` reactive shape
  (lines 376/388/392 pre-refresh) plus simpler shape compatible with
  AttendanceView's `confirmVisible` boolean.

  Usage:
    <ConfirmModal
      v-model:visible="confirmDialog.visible"
      :loading="confirmDialog.loading"
      :message="confirmDialog.message"
      :danger="confirmDialog.danger"
      @confirm="confirmDialog.onConfirm()"
      @cancel="confirmDialog.visible = false"
    />

  Path Y MEDIUM (#047). a11y minimum: role/aria-modal + escape-key.
  Focus trap deferred to S5+ a11y cluster (BACKLOG #40).
-->

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="confirm-modal__overlay"
      role="dialog"
      aria-modal="true"
      @click.self="onOverlayClick"
    >
      <div class="confirm-modal__dialog">
        <p
          v-if="title"
          class="confirm-modal__title"
        >
          {{ title }}
        </p>
        <p class="confirm-modal__message">
          {{ message }}
        </p>
        <div class="confirm-modal__actions">
          <VButton
            variant="ghost"
            :disabled="loading"
            @click="$emit('cancel')"
          >
            {{ cancelLabel }}
          </VButton>
          <VButton
            :variant="danger ? 'danger' : 'primary'"
            :loading="loading"
            @click="$emit('confirm')"
          >
            {{ confirmLabel }}
          </VButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import { VButton } from '@/components/ui'

const props = withDefaults(
  defineProps<{
    visible: boolean
    loading?: boolean
    title?: string
    message: string
    danger?: boolean
    confirmLabel?: string
    cancelLabel?: string
  }>(),
  {
    loading: false,
    title: '',
    danger: false,
    confirmLabel: 'Подтвердить',
    cancelLabel: 'Отмена',
  },
)

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'update:visible', v: boolean): void
}>()

function onOverlayClick(): void {
  if (props.loading) return
  emit('cancel')
}

function onEscape(e: KeyboardEvent): void {
  if (e.key === 'Escape' && props.visible && !props.loading) {
    emit('cancel')
  }
}

watch(
  () => props.visible,
  (v) => {
    emit('update:visible', v)
  },
)

onMounted(() => {
  document.addEventListener('keydown', onEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onEscape)
})
</script>

<style scoped>
.confirm-modal__overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: var(--z-modal, 400);
  padding: var(--space-4);
}

.confirm-modal__dialog {
  width: 100%;
  max-width: 480px;
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-xl, var(--radius-lg));
  padding: var(--space-5) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  font-family: var(--font-body);
}

.confirm-modal__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--text-primary);
  margin: 0;
}

.confirm-modal__message {
  font-size: var(--text-base);
  color: var(--text-primary);
  line-height: 1.5;
  margin: 0;
}

.confirm-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-2);
}
</style>
