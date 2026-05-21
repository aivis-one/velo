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

function isUpcoming(b: BookingWithPracticeResponse): boolean {
  return (UPCOMING_STATUSES as readonly string[]).includes(b.status)
}

/** True if the practice starts within the next calendar day (== "tomorrow"). */
function isTomorrow(iso: string): boolean {
  const d = new Date(iso)
  const now = new Date()
  const tomorrow = new Date(now)
  tomorrow.setDate(now.getDate() + 1)
  return (
    d.getFullYear() === tomorrow.getFullYear() &&
    d.getMonth() === tomorrow.getMonth() &&
    d.getDate() === tomorrow.getDate()
  )
}

/**
 * Upcoming bookings: tomorrow's first, then the rest, each group sorted by
 * scheduled time ascending.
 */
const upcoming = computed(() => {
  const list = store.bookings.filter(isUpcoming)
  return [...list].sort((a, b) => {
    const aT = isTomorrow(a.practice.scheduled_at)
    const bT = isTomorrow(b.practice.scheduled_at)
    if (aT !== bT) return aT ? -1 : 1
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
  // Upcoming -> only tomorrow's bookings get a badge.
  if (isTomorrow(b.practice.scheduled_at)) {
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
  padding: var(--space-4);
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
