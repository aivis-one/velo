<!--
  VELO Frontend -- BookingCard Component (screen 17, My reservations)

  Thin wrapper around the shared PracticeListCard. Renders a booking with
  its date in the meta-left slot and a status badge in the badge slot.

  The parent (MyBookingsView) decides which badge to show via the `badge` prop
  (live / today / tomorrow / done / cancelled / no_show). This card just renders.

  Layout / spacing live in PracticeListCard.vue (DS).

  Usage:
    <BookingCard :booking="b" :badge="badgeFor(b)" @click="openDetail(b)" />
-->

<template>
  <PracticeListCard
    :practice="booking.practice"
    :clickable="clickable"
    @click="$emit('click')"
  >
    <template #meta-left>
      <span class="plc-meta-item">{{ formattedDate }}</span>
    </template>
    <template #badge>
      <span
        v-if="badge"
        class="booking-card__badge"
        :class="`booking-card__badge--${badge.variant}`"
      >
        <span v-if="badge.variant === 'live'" class="booking-card__live-dot" />
        <component :is="badgeIcon" v-else-if="badgeIcon" :size="12" />
        {{ badge.label }}
      </span>
    </template>
  </PracticeListCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatDate } from '@/utils/format'
import { IconCheck, IconClock, IconClose } from '@/components/icons'
import PracticeListCard from '@/components/shared/PracticeListCard.vue'
import { useViewerTimezone } from '@/composables/useViewerTimezone'
import type { BookingWithPracticeResponse } from '@/api/types'

/** Badge descriptor passed by the parent (null = no badge). */
export interface BookingBadge {
  label: string
  variant: 'live' | 'today' | 'tomorrow' | 'done' | 'cancelled' | 'no_show'
}

const props = withDefaults(
  defineProps<{
    booking: BookingWithPracticeResponse
    badge?: BookingBadge | null
    clickable?: boolean
  }>(),
  {
    badge: null,
    clickable: true,
  },
)

defineEmits<{
  click: []
}>()

const badgeIcon = computed(() => {
  if (!props.badge) return null
  switch (props.badge.variant) {
    case 'today':     return IconClock
    case 'tomorrow':  return IconClock
    case 'done':      return IconCheck
    case 'cancelled': return IconClose
    case 'no_show':   return IconClose
    default:          return null
  }
})

// F5: render the date in the viewer's own profile timezone (the profile decides).
const viewerTz = useViewerTimezone()

const formattedDate = computed(() =>
  formatDate(props.booking.practice.scheduled_at, viewerTz.value),
)
</script>

<style scoped>
.booking-card__badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 4px 10px;
  border-radius: 5px;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  white-space: nowrap;
}

/* Live -- teal, with a dot (practice in progress) */
.booking-card__badge--live {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-700);
}

.booking-card__live-dot {
  width: 7px;
  height: 7px;
  border-radius: var(--radius-full);
  background: var(--velo-teal-600);
  flex-shrink: 0;
}

/* Today -- teal (most urgent, happening today) */
.booking-card__badge--today {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-700);
}

/* Tomorrow -- peach */
.booking-card__badge--tomorrow {
  background: var(--velo-glass-peach-40);
  color: var(--velo-peach-700);
}

/* Done -- teal */
.booking-card__badge--done {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-700);
}

/* Cancelled / no-show -- pink */
.booking-card__badge--cancelled,
.booking-card__badge--no_show {
  background: var(--velo-pink-100);
  color: var(--velo-pink-300);
}
</style>
