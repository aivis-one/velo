<!--
  VELO Frontend -- BookingCard Component (screen 17, My reservations)

  Dumb presentation card for a single booking. The parent (MyBookingsView)
  owns the product logic of which section a booking belongs to and which
  badge to show -- it passes a ready `badge` prop. The card just renders.

  Layout (Figma 17):
    - Practice-type icon in a circle (left)
    - Title + master (mini avatar initial + verified check)
    - Date row
    - Status badge (right): "Завтра" / "Завершена" / "Отменена" / "Неявка"

  Usage:
    <BookingCard :booking="b" :badge="badgeFor(b)" @click="openDetail(b)" />
-->

<template>
  <div
    class="booking-card"
    :class="{ 'booking-card--clickable': clickable }"
    @click="$emit('click')"
  >
    <div class="booking-card__main">
      <span class="booking-card__icon">
        <component :is="typeIcon" :size="26" />
      </span>

      <div class="booking-card__info">
        <h4 class="booking-card__title">{{ booking.practice.title }}</h4>
        <p class="booking-card__master">
          <span class="booking-card__master-avatar">{{ masterInitial }}</span>
          <span class="booking-card__master-name">
            {{ booking.practice.master_name ?? 'Мастер' }}
          </span>
          <span class="booking-card__verified"><IconCheck :size="11" /></span>
        </p>
      </div>
    </div>

    <div class="booking-card__footer">
      <span class="booking-card__date">{{ formattedDate }}</span>

      <span
        v-if="badge"
        class="booking-card__badge"
        :class="`booking-card__badge--${badge.variant}`"
      >
        <span v-if="badge.variant === 'live'" class="booking-card__live-dot" />
        <component :is="badgeIcon" v-else :size="12" />
        {{ badge.label }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatDate } from '@/utils/format'
import {
  IconMeditation,
  IconBreathwork,
  IconCheck,
  IconClock,
  IconClose,
} from '@/components/icons'
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

// -- Practice-type icon. NOTE: the backend practice_type enum is
//    live / series / one_on_one / replay -- there is NO "breathwork" type.
//    Breathwork is a content category not modelled in the schema, so we
//    detect it via a title heuristic and fall back to the meditation glyph. --
const typeIcon = computed(() =>
  props.booking.practice.title.toLowerCase().includes('breathwork')
    ? IconBreathwork
    : IconMeditation,
)

// -- Master initial for the mini avatar --
const masterInitial = computed(() => {
  const name = props.booking.practice.master_name?.trim()
  return name ? name.charAt(0).toUpperCase() : 'М'
})

// -- Badge icon by variant --
const badgeIcon = computed(() => {
  if (!props.badge) return null
  switch (props.badge.variant) {
    case 'live':      return null
    case 'today':     return IconClock
    case 'tomorrow':  return IconClock
    case 'done':      return IconCheck
    case 'cancelled': return IconClose
    case 'no_show':   return IconClose
    default:          return null
  }
})

const formattedDate = computed(() =>
  formatDate(props.booking.practice.scheduled_at, props.booking.practice.timezone),
)
</script>

<style scoped>
.booking-card {
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  transition: opacity var(--transition-fast);
}

.booking-card--clickable {
  cursor: pointer;
}

.booking-card--clickable:hover {
  opacity: 0.9;
}

/* Top row: icon + title/master */
.booking-card__main {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.booking-card__icon {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}

.booking-card__info {
  flex: 1;
  min-width: 0;
}

.booking-card__title {
  font-family: var(--font-body);
  font-weight: 400;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  line-height: 1.3;
  margin: 0 0 var(--space-1);
}

.booking-card__master {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin: 0;
}

.booking-card__master-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  color: var(--velo-text-secondary);
  font-size: 9px;
  flex-shrink: 0;
}

.booking-card__verified {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
  flex-shrink: 0;
}

/* Bottom row: date + badge */
.booking-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.booking-card__date {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

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
