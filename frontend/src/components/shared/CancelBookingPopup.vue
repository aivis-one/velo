<!--
  VELO Frontend -- CancelBookingPopup Component (Phase F4.1, fixed F5 review)

  Confirmation popup for cancelling a booking. Built on VModal.

  Dynamic refund warning:
    - If practice starts in > 24h: green "Средства вернутся на баланс"
    - If practice starts in <= 24h: red "Средства НЕ будут возвращены"

  F5 review fix:
    W-22: Added loading prop + disabled state on confirm button

  Props:
    booking  -- anything with practice.title + practice.scheduled_at
                (BookingWithPracticeResponse or BookingDetailResponse)
    open     -- controls visibility
    loading  -- true while cancel request is in progress

  Emits:
    close    -- user dismissed the popup
    confirm  -- user confirmed cancellation (parent calls store.cancelBooking)
-->

<template>
  <VModal :open="open" @close="onClose">
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
          Средства вернутся на баланс
        </template>
        <template v-else>
          Средства НЕ будут возвращены (до начала практики менее 24 часов)
        </template>
      </p>
    </div>

    <!-- Actions -->
    <div class="cancel__actions">
      <VButton
        variant="danger"
        block
        :loading="loading"
        :disabled="loading"
        @click="$emit('confirm')"
      >
        Да, отменить
      </VButton>
      <VButton
        variant="ghost"
        block
        :disabled="loading"
        @click="onClose"
      >
        Нет, оставить
      </VButton>
    </div>
  </VModal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VModal, VButton } from '@/components/ui'

const REFUND_DEADLINE_HOURS = 24

// Structural minimum: works with both BookingWithPracticeResponse (list)
// and BookingDetailResponse (detail) -- the popup only needs the practice
// title and scheduled_at.
interface CancellableBooking {
  practice: {
    title: string
    scheduled_at: string
  }
}

const props = withDefaults(
  defineProps<{
    booking: CancellableBooking
    open: boolean
    loading?: boolean
  }>(),
  {
    loading: false,
  },
)

const emit = defineEmits<{
  close: []
  confirm: []
}>()

function onClose(): void {
  if (props.loading) return
  emit('close')
}

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
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-3);
}

.cancel__text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
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
  background: var(--velo-glass-peach-40);
  border: 1px solid var(--velo-warning);
}

.cancel__warning--safe {
  background: var(--velo-glass-teal-30);
  border: 1px solid var(--velo-success);
}

.cancel__warning-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  margin: 0;
  line-height: 1.4;
}

.cancel__warning--danger .cancel__warning-text {
  color: var(--velo-warning-text);
}

.cancel__warning--safe .cancel__warning-text {
  color: var(--velo-success-text);
}

/* Actions */
.cancel__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
