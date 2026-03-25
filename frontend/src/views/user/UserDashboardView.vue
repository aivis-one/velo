<!--
  VELO Frontend -- UserDashboardView (Phase F3.1, updated DS-dashboard)

  Main user screen. Shows:
    - Greeting with user's first name
    - Check-in alert banner (amber) -- confirmed booking in check-in window
    - Feedback alert banner (teal)  -- attended booking in feedback window
    - "Ближайшая практика" -- nearest confirmed booking card with Zoom + Check-in
    - "Ваш прогресс"       -- attended count + hours, derived from bookingsStore
    - "AI-саммари"         -- placeholder card with week/month toggle

  Check-in window:  scheduled_at - CHECKIN_WINDOW_H  .. scheduled_at
  Feedback window:  scheduled_at + duration_minutes   .. + FEEDBACK_WINDOW_H

  Progress stats are derived from the already-loaded bookingsStore (limit 20).
  For users with >20 attended practices the numbers will be partial -- acceptable for MVP.
-->

<template>
  <div class="dashboard">

    <!-- Greeting -->
    <div class="dashboard__greeting">
      <p class="dashboard__greeting-text">{{ greetingText }}</p>
      <h2 class="dashboard__greeting-name">{{ userName }} 👋</h2>
    </div>

    <!-- Check-in alert banner -->
    <div
      v-if="checkinAlert"
      class="dashboard__alert dashboard__alert--checkin"
      @click="goToCheckin(checkinAlert.practice_id)"
    >
      <div class="dashboard__alert-content">
        <span class="dashboard__alert-icon">⏰</span>
        <div class="dashboard__alert-text">
          <h4>Пора на check-in!</h4>
          <p>{{ checkinAlert.practice.title }}{{ checkinAlertTime }}</p>
        </div>
      </div>
    </div>

    <!-- Feedback alert banner -->
    <div
      v-if="feedbackAlert"
      class="dashboard__alert dashboard__alert--feedback"
      @click="goToFeedback(feedbackAlert.practice_id)"
    >
      <div class="dashboard__alert-content">
        <span class="dashboard__alert-icon">💬</span>
        <div class="dashboard__alert-text">
          <h4>Оставьте feedback!</h4>
          <p>{{ feedbackAlert.practice.title }} · Вчера</p>
        </div>
      </div>
    </div>

    <!-- ================================================================
         NEAREST PRACTICE
         ================================================================ -->
    <section class="dashboard__section">
      <h3 class="dashboard__section-title">Ближайшая практика</h3>

      <!-- Loading -->
      <div v-if="bookingsStore.loading && !nearestBooking" class="dashboard__loader">
        <VLoader />
      </div>

      <!-- Empty -->
      <div
        v-else-if="!bookingsStore.loading && !nearestBooking"
        class="dashboard__empty"
      >
        <p class="dashboard__empty-text">Нет предстоящих практик</p>
        <VButton
          size="sm"
          variant="outline"
          @click="router.push({ name: 'user-calendar' })"
        >
          Найти практику
        </VButton>
      </div>

      <!-- Practice card -->
      <div
        v-else-if="nearestBooking"
        class="dashboard__practice-card"
        @click="router.push({ name: 'practice-detail', params: { id: nearestBooking.practice_id } })"
      >
        <!-- Header: emoji + title + master -->
        <div class="dashboard__practice-header">
          <span class="dashboard__practice-icon">{{ nearestPracticeEmoji }}</span>
          <div class="dashboard__practice-info">
            <h4 class="dashboard__practice-title">{{ nearestBooking.practice.title }}</h4>
            <p class="dashboard__practice-master">
              {{ nearestBooking.practice.master_name ?? 'Мастер' }}
              <span class="dashboard__practice-verified">✓</span>
            </p>
          </div>
        </div>

        <!-- Meta row: date, duration, paid badge -->
        <div class="dashboard__practice-meta">
          <span class="dashboard__practice-meta-item">📅 {{ nearestPracticeDate }}</span>
          <span class="dashboard__practice-meta-item">⏱ {{ nearestPracticeDuration }}</span>
          <VBadge v-if="nearestBooking.purchase_id" variant="success">
            ✓ Оплачено
          </VBadge>
        </div>

        <!-- Action buttons -->
        <div class="dashboard__practice-actions" @click.stop>
          <VButton
            variant="outline"
            size="sm"
            class="dashboard__practice-btn"
            @click="router.push({ name: 'practice-detail', params: { id: nearestBooking.practice_id } })"
          >
            Zoom
          </VButton>
          <VButton
            variant="primary"
            size="sm"
            class="dashboard__practice-btn"
            @click="goToCheckin(nearestBooking.practice_id)"
          >
            Check-in
          </VButton>
        </div>
      </div>
    </section>

    <!-- ================================================================
         PROGRESS
         ================================================================ -->
    <section class="dashboard__section">
      <h3 class="dashboard__section-title">Ваш прогресс</h3>
      <div class="dashboard__stats-grid">
        <div class="dashboard__stat-card">
          <div class="dashboard__stat-value">{{ attendedCount }}</div>
          <div class="dashboard__stat-label">Практик пройдено</div>
        </div>
        <div class="dashboard__stat-card">
          <div class="dashboard__stat-value">{{ practiceHours }}</div>
          <div class="dashboard__stat-label">Часов в практике</div>
        </div>
      </div>
    </section>

    <!-- ================================================================
         AI SUMMARY (placeholder)
         ================================================================ -->
    <section class="dashboard__section">
      <div class="dashboard__ai-header">
        <h3 class="dashboard__section-title">AI-саммари</h3>
        <div class="dashboard__period-toggle">
          <button
            class="dashboard__period-btn"
            :class="{ 'dashboard__period-btn--active': aiPeriod === 'week' }"
            @click="aiPeriod = 'week'"
          >
            Неделя
          </button>
          <button
            class="dashboard__period-btn"
            :class="{ 'dashboard__period-btn--active': aiPeriod === 'month' }"
            @click="aiPeriod = 'month'"
          >
            Месяц
          </button>
        </div>
      </div>

      <div class="dashboard__ai-card">
        <p class="dashboard__ai-text">
          <template v-if="aiPeriod === 'week'">
            На этой неделе вы посетили <strong>{{ attendedCount }}</strong> практик
            и провели в практике <strong>{{ practiceHours }}</strong> часов.
          </template>
          <template v-else>
            В этом месяце вы посетили <strong>{{ attendedCount }}</strong> практик
            и провели в практике <strong>{{ practiceHours }}</strong> часов.
          </template>
        </p>
        <p v-if="attendedCount > 0" class="dashboard__ai-text dashboard__ai-text--secondary">
          Ваш уровень энергии вырос 🙂
        </p>
        <button
          class="dashboard__ai-arrow"
          @click.stop="router.push({ name: 'user-ai-summary' })"
        >
          →
        </button>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBookingsStore } from '@/stores/bookings'
import { VLoader, VButton, VBadge } from '@/components/ui'
import { PRACTICE_TYPE_EMOJI } from '@/utils/displayHelpers'
import { formatDateShort, formatTime, formatDuration } from '@/utils/format'
import { isInCheckinWindow, isInFeedbackWindow } from '@/composables/usePracticeWindows'
import { CHECKIN_WINDOW_H } from '@/utils/constants'
import type { BookingWithPracticeResponse } from '@/api/types'

// CHECKIN_WINDOW_H is imported but only used implicitly via isInCheckinWindow.
// Keeping import to document the dependency (mirrors usePracticeWindows).
void CHECKIN_WINDOW_H

const router = useRouter()
const authStore = useAuthStore()
const bookingsStore = useBookingsStore()

// -- Reactive clock: updated every 60s so alert computeds re-evaluate --
const now = ref(Date.now())
let clockInterval: ReturnType<typeof setInterval> | null = null

// -- Period toggle for AI summary (visual only, no API) --
const aiPeriod = ref<'week' | 'month'>('week')

// =========================================================================
// Greeting
// =========================================================================

const userName = computed(() => authStore.user?.first_name ?? 'Друг')

const greetingText = computed((): string => {
  const hour = new Date().getHours()
  if (hour < 6)  return 'Доброй ночи,'
  if (hour < 12) return 'Доброе утро,'
  if (hour < 18) return 'Добрый день,'
  return 'Добрый вечер,'
})

// =========================================================================
// Alert banners
// =========================================================================

/** First confirmed booking currently in the check-in window. */
const checkinAlert = computed((): BookingWithPracticeResponse | null => {
  return (
    bookingsStore.bookings.find((b) => {
      if (b.status !== 'confirmed') return false
      const scheduledMs = new Date(b.practice.scheduled_at).getTime()
      return isInCheckinWindow(scheduledMs, now.value)
    }) ?? null
  )
})

/** Human-readable time hint for check-in banner subtitle. */
const checkinAlertTime = computed((): string => {
  if (!checkinAlert.value) return ''
  const diffMs = new Date(checkinAlert.value.practice.scheduled_at).getTime() - now.value
  const diffMinutes = Math.round(diffMs / 60_000)
  if (diffMinutes <= 0)  return ' · Сейчас'
  if (diffMinutes < 60)  return ` · через ${diffMinutes} мин`
  const hours = Math.floor(diffMinutes / 60)
  return ` · через ${hours} ч`
})

/** First attended booking currently in the feedback window. */
const feedbackAlert = computed((): BookingWithPracticeResponse | null => {
  return (
    bookingsStore.bookings.find((b) => {
      if (b.status !== 'attended') return false
      const scheduledMs = new Date(b.practice.scheduled_at).getTime()
      return isInFeedbackWindow(scheduledMs, b.practice.duration_minutes, now.value)
    }) ?? null
  )
})

// =========================================================================
// Nearest practice
// =========================================================================

/** Nearest confirmed booking sorted ascending by scheduled_at. */
const nearestBooking = computed((): BookingWithPracticeResponse | null => {
  const confirmed = bookingsStore.bookings
    .filter((b) => b.status === 'confirmed')
    .sort(
      (a, b) =>
        new Date(a.practice.scheduled_at).getTime() -
        new Date(b.practice.scheduled_at).getTime(),
    )
  return confirmed[0] ?? null
})

const nearestPracticeEmoji = computed((): string => {
  if (!nearestBooking.value) return '🧘'
  return PRACTICE_TYPE_EMOJI[nearestBooking.value.practice.practice_type] ?? '🧘'
})

/**
 * "Завтра, 07:00" / "5 янв, 10:00"
 * Uses practice.timezone from PracticeSummary (added in DS-sprint).
 */
const nearestPracticeDate = computed((): string => {
  if (!nearestBooking.value) return ''
  const iso = nearestBooking.value.practice.scheduled_at
  const tz = nearestBooking.value.practice.timezone ?? 'Europe/Berlin'
  return `${formatDateShort(iso, tz)}, ${formatTime(iso, tz)}`
})

const nearestPracticeDuration = computed((): string => {
  if (!nearestBooking.value) return ''
  return formatDuration(nearestBooking.value.practice.duration_minutes)
})

// =========================================================================
// Progress stats
// =========================================================================

const attendedBookings = computed(() =>
  bookingsStore.bookings.filter((b) => b.status === 'attended'),
)

const attendedCount = computed(() => attendedBookings.value.length)

/**
 * Total hours in practice.
 * Formatted as integer when whole (12), one decimal otherwise (9,5).
 */
const practiceHours = computed((): string => {
  const totalMinutes = attendedBookings.value.reduce(
    (sum, b) => sum + b.practice.duration_minutes,
    0,
  )
  const hours = totalMinutes / 60
  return hours % 1 === 0 ? String(hours) : hours.toFixed(1).replace('.', ',')
})

// =========================================================================
// Actions
// =========================================================================

function goToCheckin(practiceId: string): void {
  router.push({ name: 'user-checkin', params: { practiceId } })
}

function goToFeedback(practiceId: string): void {
  router.push({ name: 'user-feedback', params: { practiceId } })
}

// =========================================================================
// Lifecycle
// =========================================================================

onMounted(() => {
  bookingsStore.fetchMyBookings()
  clockInterval = setInterval(() => { now.value = Date.now() }, 60_000)
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
})
</script>

<style scoped>
/* ===== Greeting ===== */
.dashboard__greeting {
  margin-bottom: var(--space-6);
}

.dashboard__greeting-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin: 0 0 var(--space-1);
}

.dashboard__greeting-name {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

/* ===== Alert banners ===== */
.dashboard__alert {
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
  cursor: pointer;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  border: 1px solid #ffffff;
  transition: opacity var(--transition-fast);
}

.dashboard__alert:hover {
  opacity: 0.9;
}

.dashboard__alert--checkin {
  background: var(--velo-glass-peach-40);
}

.dashboard__alert--feedback {
  background: var(--velo-glass-teal-40);
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
  font-weight: 400;
  font-size: var(--text-sm);
  margin-bottom: 2px;
  color: var(--velo-text-primary);
}

.dashboard__alert-text p {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

/* ===== Sections ===== */
.dashboard__section {
  margin-bottom: var(--space-6);
}

.dashboard__section-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-4);
}

/* ===== Nearest practice card ===== */
.dashboard__practice-card {
  background: var(--velo-bg-card);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  cursor: pointer;
  transition: opacity var(--transition-fast);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.dashboard__practice-card:active {
  opacity: 0.8;
}

.dashboard__practice-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.dashboard__practice-icon {
  font-size: 28px;
  flex-shrink: 0;
  line-height: 1.2;
}

.dashboard__practice-info {
  flex: 1;
  min-width: 0;
}

.dashboard__practice-title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0 0 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dashboard__practice-master {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin: 0;
}

.dashboard__practice-verified {
  color: var(--velo-teal-600);
  margin-left: 2px;
}

.dashboard__practice-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
  margin-bottom: var(--space-4);
}

.dashboard__practice-meta-item {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.dashboard__practice-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.dashboard__practice-btn {
  width: 100%;
}

/* ===== Loader / empty ===== */
.dashboard__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

.dashboard__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6) 0;
  text-align: center;
}

.dashboard__empty-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  margin: 0;
}

/* ===== Progress stats ===== */
.dashboard__stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.dashboard__stat-card {
  background: var(--velo-bg-card);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  text-align: center;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.dashboard__stat-value {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  line-height: 1.1;
}

.dashboard__stat-label {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin-top: var(--space-1);
}

/* ===== AI summary ===== */
.dashboard__ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.dashboard__ai-header .dashboard__section-title {
  margin-bottom: 0;
}

.dashboard__period-toggle {
  display: flex;
  gap: 2px;
  background: var(--velo-bg-card);
  border-radius: var(--radius-xl);
  padding: 2px;
}

.dashboard__period-btn {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-xl);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dashboard__period-btn--active {
  background: var(--velo-glass-blue-60);
  color: var(--velo-text-primary);
}

.dashboard__ai-card {
  background: var(--velo-bg-card);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  padding-bottom: var(--space-8);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  position: relative;
}

.dashboard__ai-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  line-height: 1.6;
  margin: 0 0 var(--space-2);
}

.dashboard__ai-text--secondary {
  color: var(--velo-text-muted);
}

.dashboard__ai-arrow {
  position: absolute;
  bottom: var(--space-4);
  right: var(--space-4);
  background: var(--velo-bg-card);
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.dashboard__ai-arrow:hover {
  opacity: 0.8;
}
</style>
