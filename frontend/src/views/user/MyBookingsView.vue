<!--
  VELO Frontend -- MyBookingsView (screen 17, My reservations)

  Two sections instead of status tabs (Figma 17):
    - "Предстоящие": active bookings (confirmed/pending). Tomorrow's ones are
      sorted to the top and get a "Завтра" badge; the rest have no badge.
    - "Прошедшие": attended / no_show / cancelled, with a status badge.

  All bookings are loaded at once (no status filter) and grouped on the
  client. For the MVP volume this is simpler than server-side pagination
  per status. Cancellation now lives on the detail screens (15/18), so the
  card is a plain link to the booking detail (screen 18).

  Route: /user/bookings (name: 'user-bookings')
-->

<template>
  <div class="bookings">
    <VHeader title="Мои бронирования" show-back @back="router.back()" />

    <!-- Loading (initial) -->
    <div v-if="store.loading && store.bookings.length === 0" class="bookings__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error -->
    <VEmptyState
      v-else-if="store.error && store.bookings.length === 0"
      icon="warning"
      title="Ошибка загрузки"
      :description="store.error"
    >
      <VButton size="sm" @click="store.refreshBookings()">Попробовать снова</VButton>
    </VEmptyState>

    <!-- Empty (no bookings at all) -->
    <VEmptyState
      v-else-if="upcoming.length === 0 && past.length === 0"
      icon="list"
      title="Бронирований нет"
      description="Здесь появятся ваши бронирования после записи на практику"
    />

    <!-- Content -->
    <div v-else class="bookings__content">
      <!-- Upcoming -->
      <section v-if="upcoming.length" class="bookings__section">
        <h3 class="bookings__section-title">Предстоящие</h3>
        <div class="bookings__list">
          <BookingCard
            v-for="booking in upcoming"
            :key="booking.id"
            :booking="booking"
            :badge="badgeFor(booking)"
            @click="openDetail(booking)"
          />
        </div>
      </section>

      <!-- Past -->
      <section v-if="past.length" class="bookings__section">
        <h3 class="bookings__section-title">Прошедшие</h3>
        <div class="bookings__list">
          <BookingCard
            v-for="booking in past"
            :key="booking.id"
            :booking="booking"
            :badge="badgeFor(booking)"
            @click="openDetail(booking)"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { useBookingsStore } from '@/stores/bookings'
import BookingCard, { type BookingBadge } from '@/components/shared/BookingCard.vue'
import type { BookingWithPracticeResponse } from '@/api/types'

const router = useRouter()
const store = useBookingsStore()

// -- Grouping --

/** Active bookings the user is going to (or might still go to). */
const UPCOMING_STATUSES = ['confirmed', 'pending'] as const

/**
 * True once the practice has ENDED (scheduled_at + duration < now).
 *
 * A booking whose practice is over belongs in "Прошедшие" even while its status
 * is still confirmed/pending: the backend deliberately keeps that status until
 * the practice is finalized (manually by the master, or by the +24h
 * auto-finalizer) — a settlement grace window, NOT a signal the practice is
 * still upcoming. So "upcoming vs past" is a TIME question here, decided on the
 * client; the booking status drives only the past-section badge.
 */
function hasEnded(b: BookingWithPracticeResponse): boolean {
  const start = new Date(b.practice.scheduled_at).getTime()
  const end = start + (b.practice.duration_minutes ?? 0) * 60_000
  return end < Date.now()
}

function isUpcoming(b: BookingWithPracticeResponse): boolean {
  return (
    (UPCOMING_STATUSES as readonly string[]).includes(b.status) && !hasEnded(b)
  )
}

/** True if the practice is in progress (status live). */
function isLive(b: BookingWithPracticeResponse): boolean {
  return b.practice.status === 'live'
}

/**
 * Calendar-date comparison helpers. S-1: dates are compared in the
 * practice's own timezone (the same one formatDate renders), not the
 * browser's local timezone -- otherwise "Завтра" could disagree with the
 * shown date near midnight across timezones. Same en-CA + timeZone pattern
 * as formatDateShort in utils/format.ts.
 */
function calendarDate(d: Date, timezone: string): string {
  return new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: timezone,
  }).format(d)
}

function isToday(iso: string, timezone: string): boolean {
  return calendarDate(new Date(iso), timezone) === calendarDate(new Date(), timezone)
}

function isTomorrow(iso: string, timezone: string): boolean {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return calendarDate(new Date(iso), timezone) === calendarDate(tomorrow, timezone)
}

/**
 * Sort rank for upcoming bookings: live (0) first, then today (1),
 * tomorrow (2), then everything else (3). Ties broken by time ascending.
 */
function upcomingRank(b: BookingWithPracticeResponse): number {
  const iso = b.practice.scheduled_at
  const tz = b.practice.timezone
  if (isLive(b)) return 0
  if (isToday(iso, tz)) return 1
  if (isTomorrow(iso, tz)) return 2
  return 3
}

/**
 * Upcoming bookings: live first, then today's, then tomorrow's, then the
 * rest, each group sorted by scheduled time ascending.
 */
const upcoming = computed(() => {
  const list = store.bookings.filter(isUpcoming)
  return [...list].sort((a, b) => {
    const rankDiff = upcomingRank(a) - upcomingRank(b)
    if (rankDiff !== 0) return rankDiff
    return (
      new Date(a.practice.scheduled_at).getTime() -
      new Date(b.practice.scheduled_at).getTime()
    )
  })
})

/** Past bookings: attended / no_show / cancelled, most recent first. */
const past = computed(() => {
  const list = store.bookings.filter((b) => !isUpcoming(b))
  return [...list].sort(
    (a, b) =>
      new Date(b.practice.scheduled_at).getTime() -
      new Date(a.practice.scheduled_at).getTime(),
  )
})

// -- Badge logic (lives here -- it depends on the section / status) --
function badgeFor(b: BookingWithPracticeResponse): BookingBadge | null {
  // Past statuses -> status badge.
  if (b.status === 'attended') return { label: 'Завершена', variant: 'done' }
  if (b.status === 'cancelled') return { label: 'Отменена', variant: 'cancelled' }
  if (b.status === 'no_show') return { label: 'Неявка', variant: 'no_show' }
  // Confirmed/pending but the practice is already over (awaiting backend
  // finalize): it sits in "Прошедшие" with NO upcoming badge — no misleading
  // "Сегодня" / "В эфире" on a practice that has ended.
  if (hasEnded(b)) return null
  // Upcoming -> live takes priority, then today / tomorrow; later dates none.
  if (isLive(b)) return { label: 'В эфире', variant: 'live' }
  if (isToday(b.practice.scheduled_at, b.practice.timezone)) {
    return { label: 'Сегодня', variant: 'today' }
  }
  if (isTomorrow(b.practice.scheduled_at, b.practice.timezone)) {
    return { label: 'Завтра', variant: 'tomorrow' }
  }
  return null
}

// -- Navigation: open the unified practice detail (Batch 6). The dedicated
// booking-detail screen is gone; the practice detail now carries the status
// row + ZOOM and handles past/cancelled bookings. Navigate by practice_id. --
function openDetail(b: BookingWithPracticeResponse): void {
  router.push({ name: 'practice-detail', params: { id: b.practice_id } })
}

onMounted(() => {
  store.fetchMyBookings()
})
</script>

<style scoped>
.bookings {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.bookings__loader {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 40vh;
}

.bookings__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  /* F-5 sync: horizontal padding снят — MobileLayout уже даёт
   * var(--velo-screen-padding) (=33). Раньше тут было var(--space-4) (16),
   * cards рендерились 304 wide вместо Figma 336.
   * Vertical паддинг top/bottom 16 оставляем (визуальный отступ от header
   * и от tab-bar; Figma my-reservations.svg gap header→title ≈ 28, у нас
   * MobileLayout 16 + 14 (section-title margin) = 30, расхождение 2px). */
  padding: var(--space-4) 0;
}

.bookings__section-title {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-3);
}

.bookings__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
</style>
