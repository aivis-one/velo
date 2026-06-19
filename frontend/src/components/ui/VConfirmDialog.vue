<!--
  VELO Frontend -- VConfirmDialog Component (Phase B4.4)

  Confirmation dialog over the shared <VModal> canon (white sheet). Message +
  Cancel/Confirm buttons, danger variant, loading guard (overlay/cancel blocked
  while a request is in-flight).

  Usage:
    <VConfirmDialog
      :open="dlg.visible"
      :message="dlg.message"
      :confirm-label="dlg.confirmLabel"
      :danger="dlg.danger"
      :loading="dlg.loading"
      @confirm="dlg.onConfirm"
      @cancel="dlg.visible = false"
    />
-->

<template>
  <VModal :open="open" :show-close="false" :close-on-overlay="!loading" @close="$emit('cancel')">
    <p class="v-confirm__text">{{ message }}</p>
    <div class="v-confirm__actions">
      <VButton variant="ghost" :disabled="loading" @click="$emit('cancel')">
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
  </VModal>
</template>

<script setup lang="ts">
import VModal from './VModal.vue'
import VButton from './VButton.vue'

withDefaults(
  defineProps<{
    open: boolean
    message: string
    confirmLabel?: string
    cancelLabel?: string
    danger?: boolean
    loading?: boolean
  }>(),
  {
    confirmLabel: 'Подтвердить',
    cancelLabel: 'Отмена',
    danger: false,
    loading: false,
  },
)

defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<style scoped>
.v-confirm__text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  text-align: center;
  line-height: 1.5;
  margin: 0 0 var(--space-4);
}

.v-confirm__actions {
  display: flex;
  gap: var(--space-3);
}

.v-confirm__actions > * {
  flex: 1;
}
</style>
