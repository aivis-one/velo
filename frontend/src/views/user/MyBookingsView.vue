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
      icon="⚠️"
      title="Ошибка загрузки"
      :description="store.error"
    >
      <VButton size="sm" @click="store.refreshBookings()">Попробовать снова</VButton>
    </VEmptyState>

    <!-- Empty (no bookings at all) -->
    <VEmptyState
      v-else-if="upcoming.length === 0 && past.length === 0"
      icon="📋"
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
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { useBookingsStore } from '@/stores/bookings'
import BookingCard, { type BookingBadge } from '@/components/shared/BookingCard.vue'
import { useViewerTimezone } from '@/composables/useViewerTimezone'
import { PRACTICE_MAX_DURATION_H } from '@/utils/constants'
import type { BookingWithPracticeResponse } from '@/api/types'

const router = useRouter()
const store = useBookingsStore()

// F5: the timezone in which THIS VIEWER sees practice times (their profile).
// Falls back to 'UTC' (never the browser) at the call sites that need a
// concrete string, matching the format helpers' default.
const viewerTz = useViewerTimezone()

// Reactive clock so the upcoming/past split (which uses a 24h time ceiling,
// the same rule B as the dashboard) re-evaluates without a reload. 60s is
// enough granularity for a day-level boundary. Mirrors UserDashboardView.
const now = ref(Date.now())
let clockInterval: ReturnType<typeof setInterval> | null = null

// -- Grouping --

/** Active bookings the user is going to (or might still go to). */
const UPCOMING_STATUSES = ['confirmed', 'pending'] as const

/**
 * A booking is "upcoming" when its status is still active AND the practice
 * has not finished yet. "Not finished" follows the same rule B as the
 * dashboard: the practice is not completed/cancelled and we are still within
 * PRACTICE_MAX_DURATION_H hours of its start (the 24h ceiling). This keeps
 * MyBookings consistent with the dashboard's "nearest practice": a practice
 * that has passed the ceiling drops to Past even if a forgetful master has
 * not finalized it yet (the auto-finalizer will catch up shortly after).
 */
function isUpcoming(b: BookingWithPracticeResponse): boolean {
  if (!(UPCOMING_STATUSES as readonly string[]).includes(b.status)) return false
  if (b.practice.status === 'completed' || b.practice.status === 'cancelled') {
    return false
  }
  const ceilingMs = PRACTICE_MAX_DURATION_H * 60 * 60 * 1000
  const start = new Date(b.practice.scheduled_at).getTime()
  return now.value < start + ceilingMs
}

/** True if the practice is in progress (status live). */
function isLive(b: BookingWithPracticeResponse): boolean {
  return b.practice.status === 'live'
}

/**
 * Calendar-date comparison helpers. F5: dates are compared in the VIEWER'S
 * own profile timezone (the same one formatDate renders in MyBookings), not
 * the practice's timezone and not the browser's -- otherwise "Завтра" could
 * disagree with the shown date near midnight across timezones. The viewer tz
 * is passed in by the callers (helpers stay pure); callers use 'UTC' as the
 * concrete fallback when the profile tz is absent. Same en-CA + timeZone
 * pattern as formatDateShort in utils/format.ts.
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
  const tz = viewerTz.value ?? 'UTC'
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
  // Upcoming -> live takes priority, then today / tomorrow; later dates none.
  if (isLive(b)) return { label: 'В эфире', variant: 'live' }
  const tz = viewerTz.value ?? 'UTC'
  if (isToday(b.practice.scheduled_at, tz)) {
    return { label: 'Сегодня', variant: 'today' }
  }
  if (isTomorrow(b.practice.scheduled_at, tz)) {
    return { label: 'Завтра', variant: 'tomorrow' }
  }
  return null
}

// -- Navigation: open booking detail (screen 18). --
function openDetail(b: BookingWithPracticeResponse): void {
  router.push({ name: 'booking-detail', params: { id: b.id } })
}

onMounted(() => {
  store.fetchMyBookings()
  // Tick the clock so the upcoming/past split updates as practices cross the
  // 24h ceiling while the screen is open. Mirrors UserDashboardView.
  clockInterval = setInterval(() => { now.value = Date.now() }, 60_000)
})

onUnmounted(() => {
  if (clockInterval !== null) {
    clearInterval(clockInterval)
    clockInterval = null
  }
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
  gap: var(--space-6);
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
