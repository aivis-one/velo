<!--
  VELO Frontend -- BookingCard Component (Phase F4.1)

  Card for displaying a single booking in MyBookingsView list.
  Matches mockup .booking-item layout:
    - Title with type emoji
    - Date/time + master name
    - Status badge (right side)
    - Cancel button for active (confirmed/pending) bookings

  Usage:
    <BookingCard
      :booking="booking"
      @cancel="onCancel(booking)"
      @click="openDetail(booking)"
    />
-->

<template>
  <div
    class="booking-card"
    :class="{ 'booking-card--clickable': clickable }"
    @click="$emit('click')"
  >
    <div class="booking-card__header">
      <span class="booking-card__title">
        {{ typeEmoji }} {{ booking.practice.title }}
      </span>
      <VBadge :variant="statusVariant">{{ statusLabel }}</VBadge>
    </div>

    <div class="booking-card__meta">
      {{ formattedDate }} · {{ booking.practice.master_name ?? 'Мастер' }}
    </div>

    <button
      v-if="canCancel"
      class="booking-card__cancel"
      @click.stop="$emit('cancel')"
    >
      Отменить
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VBadge } from '@/components/ui'
import { formatDate } from '@/utils/format'
import { PRACTICE_TYPE_EMOJI } from '@/utils/displayHelpers'
import type { BookingWithPracticeResponse, BookingStatus } from '@/api/types'

const props = withDefaults(
  defineProps<{
    booking: BookingWithPracticeResponse
    clickable?: boolean
  }>(),
  {
    clickable: true,
  },
)

defineEmits<{
  click: []
  cancel: []
}>()

// -- Type emoji -- imported from displayHelpers
const typeEmoji = computed(() =>
  PRACTICE_TYPE_EMOJI[props.booking.practice.practice_type] ?? '🧘',
)

// -- Status mapping --
const STATUS_LABEL: Record<BookingStatus, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждено',
  attended: 'Завершена',
  no_show: 'Неявка',
  cancelled: 'Отменена',
}

const STATUS_VARIANT: Record<BookingStatus, 'success' | 'warning' | 'error' | 'info'> = {
  pending: 'warning',
  confirmed: 'success',
  attended: 'info',
  no_show: 'error',
  cancelled: 'error',
}

const statusLabel = computed(() =>
  STATUS_LABEL[props.booking.status] ?? props.booking.status,
)

const statusVariant = computed(() =>
  STATUS_VARIANT[props.booking.status] ?? 'info',
)

// -- Formatted date --
const formattedDate = computed(() =>
  formatDate(props.booking.practice.scheduled_at),
)

// -- Can cancel: only pending or confirmed bookings --
const canCancel = computed(() =>
  props.booking.status === 'pending' || props.booking.status === 'confirmed',
)
</script>

<style scoped>
.booking-card {
  background: var(--velo-bg-card, white);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  transition: all var(--transition-base);
}

.booking-card--clickable {
  cursor: pointer;
}

.booking-card--clickable:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.booking-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.booking-card__title {
  font-weight: 600;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  line-height: 1.3;
}

.booking-card__meta {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
}

.booking-card__cancel {
  display: inline-block;
  margin-top: var(--space-3);
  padding: 0;
  border: none;
  background: none;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-error);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.booking-card__cancel:hover {
  opacity: 0.7;
}
</style>
