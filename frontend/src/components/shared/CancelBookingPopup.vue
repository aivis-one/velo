<!--
  VELO Frontend -- CancelBookingPopup Component (Phase F4.1)

  Confirmation popup for cancelling a booking. Built on VModal.

  Dynamic refund warning:
    - If practice starts in > 24h: green "Средства вернутся на баланс"
    - If practice starts in <= 24h: red "Средства НЕ будут возвращены"

  Props:
    booking  — BookingWithPracticeResponse (for title + scheduled_at)
    open     — controls visibility

  Emits:
    close    — user dismissed the popup
    confirm  — user confirmed cancellation (parent calls store.cancelBooking)
-->

<template>
  <VModal :open="open" @close="$emit('close')">
    <h2 class="cancel__title">Отменить бронирование?</h2>

    <p class="cancel__text">
      Вы уверены, что хотите отменить бронирование на
      <strong>{{ booking.practice.title }}</strong>?
    </p>

    <!-- Dynamic refund warning -->
    <div
      class="cancel__warning"
      :class="willRefund ? 'cancel__warning--safe' : 'cancel__warning--danger'"
    >
      <p class="cancel__warning-text">
        <template v-if="willRefund">
          ✅ Средства вернутся на баланс
        </template>
        <template v-else>
          ⚠️ Средства НЕ будут возвращены (до начала практики менее 24 часов)
        </template>
      </p>
    </div>

    <!-- Actions -->
    <div class="cancel__actions">
      <VButton
        variant="danger"
        block
        @click="$emit('confirm')"
      >
        Да, отменить
      </VButton>
      <VButton
        variant="ghost"
        block
        @click="$emit('close')"
      >
        Нет, оставить
      </VButton>
    </div>
  </VModal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VModal, VButton } from '@/components/ui'
import type { BookingWithPracticeResponse } from '@/api/types'

const REFUND_DEADLINE_HOURS = 24

const props = defineProps<{
  booking: BookingWithPracticeResponse
  open: boolean
}>()

defineEmits<{
  close: []
  confirm: []
}>()

/**
 * True if the practice starts more than 24 hours from now
 * (user will receive a refund on cancellation).
 */
const willRefund = computed(() => {
  const scheduledAt = new Date(props.booking.practice.scheduled_at).getTime()
  const now = Date.now()
  const hoursUntilStart = (scheduledAt - now) / (1000 * 60 * 60)
  return hoursUntilStart > REFUND_DEADLINE_HOURS
})
</script>

<style scoped>
.cancel__title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0 0 var(--space-3);
}

.cancel__text {
  font-size: var(--text-base);
  color: var(--velo-text-secondary);
  line-height: 1.5;
  margin: 0 0 var(--space-4);
}

/* Warning box */
.cancel__warning {
  border-radius: var(--radius-sm);
  padding: var(--space-3);
  margin-bottom: var(--space-5);
}

.cancel__warning--danger {
  background: #FEF3C7;
  border: 1px solid var(--velo-warning);
}

.cancel__warning--safe {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid var(--velo-success);
}

.cancel__warning-text {
  font-size: var(--text-sm);
  margin: 0;
  line-height: 1.4;
}

.cancel__warning--danger .cancel__warning-text {
  color: #92400E;
}

.cancel__warning--safe .cancel__warning-text {
  color: #166534;
}

/* Actions */
.cancel__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
