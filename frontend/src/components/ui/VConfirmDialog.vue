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
  /* Wrap only when the buttons' real content width doesn't fit the row (bug
     4, ПРОМТ №408) -- a global flex-direction: column would restack every
     caller of this component (7 today), including short pairs that fit fine. */
  flex-wrap: wrap;
  gap: var(--space-3);
}

.v-confirm__actions > * {
  /* flex-basis: auto (was `flex: 1` = 0%) so a button's real content size
     counts toward the wrap decision above -- basis:0% hides it entirely from
     the wrap algorithm (same trap fixed in AdminCatalogView, bug 6b below). */
  flex: 1 1 auto;
}
</style>
