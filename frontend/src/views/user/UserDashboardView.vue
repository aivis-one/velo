<!--
  VELO Frontend -- UserDashboardView (Phase F3.1, updated F9.1)

  Main user screen. Shows:
    - Greeting with user's first name
    - F9.1: Check-in alert banner (amber) -- confirmed booking in check-in window
    - F9.1: Feedback alert banner (blue) -- attended booking in feedback window
    - "Upcoming practices" section (first 5 from catalog)
    - "All practices" link → /user/calendar

  Check-in window:  scheduled_at - CHECKIN_WINDOW_H  .. scheduled_at
  Feedback window:  scheduled_at + duration_minutes   .. + FEEDBACK_WINDOW_H

  Both windows are validated server-side too -- the banners are just UX hints.
  If the user taps a banner outside the window the backend returns 400.
-->

<template>
  <div class="dashboard">
    <!-- Greeting -->
    <div class="dashboard__greeting">
      <p class="dashboard__greeting-text">{{ greetingText }}</p>
      <h2 class="dashboard__greeting-name">{{ userName }} 👋</h2>
    </div>

    <!-- F9.1: Check-in alert banner -->
    <div
      v-if="checkinAlert"
      class="dashboard__alert dashboard__alert--checkin"
      @click="goToCheckin(checkinAlert.practice_id)"
    >
      <div class="dashboard__alert-content">
        <span class="dashboard__alert-icon">⏰</span>
        <div class="dashboard__alert-text">
          <h4>Пора на check-in!</h4>
          <p>{{ checkinAlert.practice.title }} {{ checkinAlertTime }}</p>
        </div>
      </div>
    </div>

    <!-- F9.1: Feedback alert banner -->
    <div
      v-if="feedbackAlert"
      class="dashboard__alert dashboard__alert--feedback"
      @click="goToFeedback(feedbackAlert.practice_id)"
    >
      <div class="dashboard__alert-content">
        <span class="dashboard__alert-icon">💬</span>
        <div class="dashboard__alert-text">
          <h4>Оставьте feedback!</h4>
          <p>{{ feedbackAlert.practice.title }}</p>
        </div>
      </div>
    </div>

    <!-- Upcoming practices -->
    <section class="dashboard__section">
      <div class="dashboard__section-header">
        <h3 class="dashboard__section-title">Ближайшие практики</h3>
        <button
          v-if="upcomingPractices.length > 0"
          class="dashboard__link"
          @click="router.push({ name: 'user-calendar' })"
        >
          Все →
        </button>
      </div>

      <!-- Loading -->
      <div v-if="store.loading && upcomingPractices.length === 0" class="dashboard__loader">
        <VLoader />
      </div>

      <!-- Error -->
      <VEmptyState
        v-else-if="store.error"
        icon="⚠️"
        title="Не удалось загрузить"
        :description="store.error"
      >
        <VButton size="sm" @click="store.refreshPractices()">Повторить</VButton>
      </VEmptyState>

      <!-- Empty -->
      <VEmptyState
        v-else-if="!store.loading && upcomingPractices.length === 0"
        icon="📅"
        title="Пока нет практик"
        description="Практики появятся здесь, когда мастера их опубликуют"
      />

      <!-- Practice cards -->
      <div v-else class="dashboard__practices">
        <PracticeCard
          v-for="practice in upcomingPractices"
          :key="practice.id"
          :practice="practice"
          @click="goToDetail"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePracticesStore } from '@/stores/practices'
import { useBookingsStore } from '@/stores/bookings'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import PracticeCard from '@/components/shared/PracticeCard.vue'
import type { BookingWithPracticeResponse } from '@/api/types'

const router = useRouter()
const authStore = useAuthStore()
const store = usePracticesStore()
const bookingsStore = useBookingsStore()

// -- Max cards shown on dashboard --
const DASHBOARD_LIMIT = 5

// -- Time windows (must match backend settings) --
const CHECKIN_WINDOW_H  = 3   // hours before scheduled_at
const FEEDBACK_WINDOW_H = 72  // hours after practice ends

const userName = computed(() => authStore.user?.first_name ?? 'Друг')

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6)  return 'Доброй ночи,'
  if (hour < 12) return 'Доброе утро,'
  if (hour < 18) return 'Добрый день,'
  return 'Добрый вечер,'
})

const upcomingPractices = computed(() =>
  store.practices.slice(0, DASHBOARD_LIMIT),
)

// =========================================================================
// F9.1: Alert banners logic
// =========================================================================

/**
 * Find the first confirmed booking that is currently in the check-in window.
 * Window: scheduled_at - CHECKIN_WINDOW_H  ..  scheduled_at
 */
const checkinAlert = computed((): BookingWithPracticeResponse | null => {
  const now = Date.now()
  return (
    bookingsStore.bookings.find((b) => {
      if (b.status !== 'confirmed') return false
      const scheduledMs   = new Date(b.practice.scheduled_at).getTime()
      const windowStartMs = scheduledMs - CHECKIN_WINDOW_H * 60 * 60 * 1000
      return now >= windowStartMs && now <= scheduledMs
    }) ?? null
  )
})

/**
 * Human-readable time hint for the check-in alert subtitle.
 * "через 30 минут" / "через 2 часа" / "" depending on how close.
 */
const checkinAlertTime = computed((): string => {
  if (!checkinAlert.value) return ''
  const diffMs      = new Date(checkinAlert.value.practice.scheduled_at).getTime() - Date.now()
  const diffMinutes = Math.round(diffMs / 60_000)
  if (diffMinutes <= 0)   return '· Сейчас'
  if (diffMinutes < 60)   return `· через ${diffMinutes} мин`
  const hours = Math.floor(diffMinutes / 60)
  return `· через ${hours} ч`
})

/**
 * Find the first attended booking currently in the feedback window.
 * Window: scheduled_at + duration_minutes  ..  + FEEDBACK_WINDOW_H
 */
const feedbackAlert = computed((): BookingWithPracticeResponse | null => {
  const now = Date.now()
  return (
    bookingsStore.bookings.find((b) => {
      if (b.status !== 'attended') return false
      const scheduledMs     = new Date(b.practice.scheduled_at).getTime()
      const practiceEndMs   = scheduledMs + b.practice.duration_minutes * 60 * 1000
      const feedbackEndMs   = practiceEndMs + FEEDBACK_WINDOW_H * 60 * 60 * 1000
      return now >= practiceEndMs && now <= feedbackEndMs
    }) ?? null
  )
})

// =========================================================================
// Actions
// =========================================================================

function goToDetail(id: string): void {
  router.push({ name: 'practice-detail', params: { id } })
}

function goToCheckin(practiceId: string): void {
  router.push({ name: 'user-checkin', params: { practiceId } })
}

function goToFeedback(practiceId: string): void {
  router.push({ name: 'user-feedback', params: { practiceId } })
}

// -- Lifecycle --
onMounted(() => {
  store.fetchPractices()
  // Ensure bookings are loaded so alert computeds have data.
  bookingsStore.fetchMyBookings()
})
</script>

<style scoped>
.dashboard__greeting {
  margin-bottom: var(--space-6);
}

.dashboard__greeting-text {
  font-size: 14px;
  color: var(--velo-text-secondary);
  margin: 0 0 var(--space-1);
}

.dashboard__greeting-name {
  font-family: var(--font-heading);
  font-size: 26px;
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0;
}

/* ===== Alert banners ===== */
.dashboard__alert {
  border-radius: 12px;
  padding: var(--space-4);
  margin-bottom: var(--space-4);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dashboard__alert:hover {
  transform: translateY(-2px);
}

.dashboard__alert--checkin {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border: 1px solid #F59E0B;
}

.dashboard__alert--checkin:hover {
  box-shadow: 0 8px 24px rgba(245, 158, 11, 0.2);
}

.dashboard__alert--feedback {
  background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
  border: 1px solid #3B82F6;
}

.dashboard__alert--feedback:hover {
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
}

.dashboard__alert-content {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dashboard__alert-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.dashboard__alert-text h4 {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 2px;
}

.dashboard__alert--checkin .dashboard__alert-text h4 {
  color: #92400E;
}

.dashboard__alert--checkin .dashboard__alert-text p {
  font-size: 13px;
  color: #B45309;
}

.dashboard__alert--feedback .dashboard__alert-text h4 {
  color: #1E40AF;
}

.dashboard__alert--feedback .dashboard__alert-text p {
  font-size: 13px;
  color: #1D4ED8;
}

/* ===== Upcoming practices ===== */
.dashboard__section {
  margin-bottom: var(--space-6);
}

.dashboard__section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.dashboard__section-title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0;
}

.dashboard__link {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-primary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.dashboard__link:hover {
  opacity: 0.7;
}

.dashboard__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

.dashboard__practices {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
</style>
