<!--
  VELO Frontend -- UserDashboardView (Phase F3.1, updated DS-dashboard)

  Main user screen. Shows:
    - Greeting with user's first name
    - Check-in alert banner (amber) -- confirmed booking in check-in window
    - Feedback alert banner (teal)  -- attended booking in feedback window
    - "Ближайшая практика" -- nearest confirmed booking card with Zoom + Check-in
    - "Ваш прогресс"       -- attended count + hours, derived from bookingsStore
    - "AI-саммари"         -- placeholder card with week/month toggle,
                              mood trend indicator and a "Подробнее" link

  Check-in window:  scheduled_at - CHECKIN_WINDOW_H  .. scheduled_at
  Feedback window:  scheduled_at + duration_minutes   .. + FEEDBACK_WINDOW_H

  Progress stats are derived from the already-loaded bookingsStore (limit 20).
  For users with >20 attended practices the numbers will be partial -- acceptable for MVP.

  Screen 16 (AI-summary): the "Подробнее" link navigates to 'user-ai-summary'
  (currently a placeholder screen -- the user AI backend does not exist yet).
  The mood trend indicator stays static (illustration, not a control).
-->

<template>
  <div class="dashboard">

    <!-- Greeting -->
    <div class="dashboard__greeting">
      <p class="dashboard__greeting-text">{{ greetingText }}</p>
      <h2 class="dashboard__greeting-name">{{ userName }}</h2>
    </div>

    <!-- Check-in alert banner -->
    <div
      v-if="checkinAlert"
      class="dashboard__alert dashboard__alert--checkin"
      @click="goToCheckin(checkinAlert.practice_id)"
    >
      <div class="dashboard__alert-content">
        <span class="dashboard__alert-icon"><IconClock :size="28" /></span>
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
        <span class="dashboard__alert-icon"><IconFeedback :size="28" /></span>
        <div class="dashboard__alert-text">
          <h4>Оставьте feedback!</h4>
          <p>{{ feedbackAlert.practice.title }} • Вчера</p>
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
        @click="openNearest"
      >
        <!-- Header: meditation icon + title + master -->
        <div class="dashboard__practice-header">
          <span class="dashboard__practice-icon">
            <component :is="nearestPracticeIcon" :size="46" />
          </span>
          <div class="dashboard__practice-info">
            <h4 class="dashboard__practice-title">{{ nearestPracticeTitle }}</h4>
            <p class="dashboard__practice-master">
              <span class="dashboard__practice-master-avatar">{{ masterInitial }}</span>
              <span class="dashboard__practice-master-name">
                {{ nearestBooking.practice.master_name ?? 'Мастер' }}
              </span>
              <span class="dashboard__practice-verified"><IconCheck :size="11" /></span>
            </p>
          </div>
        </div>

        <!-- Meta row: date, duration, paid / live badge -->
        <div class="dashboard__practice-meta">
          <span class="dashboard__practice-meta-item">
            <IconCalendar :size="14" /> {{ nearestPracticeDate }}
          </span>
          <span class="dashboard__practice-meta-item">
            <IconClock :size="14" /> {{ nearestPracticeDuration }}
          </span>
          <VBadge v-if="nearestIsLive" variant="success">
            · В эфире
          </VBadge>
          <VBadge v-else-if="nearestBooking.purchase_id" variant="success">
            <IconCheck :size="12" /> Оплачено
          </VBadge>
        </div>
      </div>

      <!-- Action buttons (outside the card, per Figma) -->
      <div
        v-if="nearestBooking"
        class="dashboard__practice-actions"
      >
        <VButton
          variant="secondary"
          block
          @click="onZoomClick"
        >
          Zoom
        </VButton>
        <VButton
          variant="primary"
          block
          @click="goToCheckin(nearestBooking.practice_id)"
        >
          Check-in
        </VButton>
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

        <!-- Mood trend indicator: from -> to. Non-clickable (static). -->
        <div v-if="attendedCount > 0" class="dashboard__ai-mood">
          <span class="dashboard__ai-mood-label">с</span>
          <IconMoodMid :size="40" />
          <IconArrowRight :size="16" class="dashboard__ai-mood-arrow" />
          <IconMoodHigh :size="40" />
          <span class="dashboard__ai-mood-label">до</span>
        </div>
      </div>

      <!-- "Подробнее" link -> AI-summary screen (16). -->
      <div
        class="dashboard__ai-more"
        @click="router.push({ name: 'user-ai-summary' })"
      >
        <IconArrowRight :size="20" class="dashboard__ai-more-icon" />
        <span class="dashboard__ai-more-label">Подробнее</span>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBookingsStore } from '@/stores/bookings'
import { usePracticesStore } from '@/stores/practices'
import { useToast } from '@/composables/useToast'
import { platform } from '@/platform'
import { VLoader, VButton, VBadge } from '@/components/ui'
import {
  IconClock,
  IconCalendar,
  IconFeedback,
  IconCheck,
  IconArrowRight,
  IconMoodMid,
  IconMoodHigh,
} from '@/components/icons'
import { formatDateShort, formatTime, formatDuration } from '@/utils/format'
import { isInCheckinWindow, isInFeedbackWindow } from '@/composables/usePracticeWindows'
import { CHECKIN_WINDOW_H } from '@/utils/constants'
import { practiceIconFor, DIRECTION_ICON_FALLBACK } from '@/utils/displayHelpers'
import type { BookingWithPracticeResponse } from '@/api/types'

// CHECKIN_WINDOW_H is imported but only used implicitly via isInCheckinWindow.
// Keeping import to document the dependency (mirrors usePracticeWindows).
void CHECKIN_WINDOW_H

const router = useRouter()
const authStore = useAuthStore()
const bookingsStore = useBookingsStore()
const practicesStore = usePracticesStore()
const toast = useToast()

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

/** First confirmed booking currently in the check-in window, not yet done. */
const checkinAlert = computed((): BookingWithPracticeResponse | null => {
  return (
    bookingsStore.bookings.find((b) => {
      if (b.status !== 'confirmed') return false
      // Hide once the user has already checked in (no re-submit via banner).
      if (b.has_checkin) return false
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
  if (diffMinutes <= 0)  return ' • Сейчас'
  if (diffMinutes < 60)  return ` • через ${diffMinutes} мин`
  const hours = Math.floor(diffMinutes / 60)
  return ` • через ${hours} ч`
})

/** First attended booking currently in the feedback window, not yet done. */
const feedbackAlert = computed((): BookingWithPracticeResponse | null => {
  return (
    bookingsStore.bookings.find((b) => {
      if (b.status !== 'attended') return false
      // Hide once the user has already left feedback (no re-submit via banner).
      if (b.has_feedback) return false
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

/** First letter of the master's name for the avatar placeholder. */
const masterInitial = computed((): string => {
  const name = nearestBooking.value?.practice.master_name ?? 'М'
  return (name.trim().charAt(0) || 'М').toUpperCase()
})

/** True when the nearest practice is currently live (status from PracticeSummary). */
const nearestIsLive = computed((): boolean =>
  nearestBooking.value?.practice.status === 'live',
)

/**
 * Practice title without a trailing " (эфир)" marker. Some seeded / manually
 * created practices include "(эфир)" in their title (see seed.py); since the
 * card already shows a "В эфире" badge for live practices, the suffix in the
 * title is redundant — strip it on the client.
 */
const nearestPracticeTitle = computed((): string => {
  const title = nearestBooking.value?.practice.title ?? ''
  return title.replace(/\s*\(эфир\)\s*$/, '')
})

/** Icon for nearest practice — by direction when available (full PracticeResponse),
 *  title-heuristic for PracticeSummary (TODO: backend extends PracticeSummary). */
const nearestPracticeIcon = computed(() => {
  const p = nearestBooking.value?.practice
  return p ? practiceIconFor(p) : DIRECTION_ICON_FALLBACK
})

/**
 * Open the Zoom link directly (not the practice screen).
 *
 * BookingWithPracticeResponse embeds a PracticeSummary (no zoom_link), so we
 * lazy-fetch the full PracticeResponse on click. The https:// guard mirrors
 * PracticeLiveView (AUDIT-0520-02). If the link is missing or invalid, show
 * a toast — we deliberately do NOT navigate to the practice screen, since the
 * whole point of this button is to skip that screen.
 */
async function onZoomClick(): Promise<void> {
  const booking = nearestBooking.value
  if (!booking) return

  // Fetch the full practice if it's not already the currently-selected one.
  if (practicesStore.selected?.id !== booking.practice_id) {
    await practicesStore.fetchPractice(booking.practice_id)
  }

  const zoomLink = practicesStore.selected?.zoom_link
  if (!zoomLink || !zoomLink.startsWith('https://')) {
    toast.error('Ссылка на Zoom ещё не указана')
    return
  }

  try { platform.hapticFeedback('medium') } catch { /* silent fallback */ }
  platform.openLink(zoomLink)
}

/**
 * Open the nearest practice. A live practice goes to the Practice-Live
 * screen (Zoom entry); otherwise to the practice detail. status is now
 * available on PracticeSummary (backend), so no extra fetch is needed.
 */
function openNearest(): void {
  if (!nearestBooking.value) return
  if (nearestIsLive.value) {
    router.push({
      name: 'practice-live',
      params: { practiceId: nearestBooking.value.practice_id },
    })
  } else {
    router.push({
      name: 'practice-detail',
      params: { id: nearestBooking.value.practice_id },
    })
  }
}

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
  border: 2px solid transparent;
  transition: opacity var(--transition-fast);
}

.dashboard__alert:hover {
  opacity: 0.9;
}

.dashboard__alert--checkin {
  background: var(--velo-glass-peach-40);
  border-color: var(--velo-warning-border);
}

.dashboard__alert--feedback {
  background: var(--velo-glass-teal-40);
  border-color: var(--velo-success);
}

.dashboard__alert-content {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dashboard__alert-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.dashboard__alert-text h4 {
  font-weight: 400;
  font-size: var(--text-base);
  margin-bottom: 2px;
}

.dashboard__alert-text p {
  font-size: var(--text-xs);
}

/* Themed colors: check-in (peach) / feedback (teal) */
.dashboard__alert--checkin .dashboard__alert-icon {
  color: var(--velo-peach-700);
}
.dashboard__alert--checkin .dashboard__alert-text h4 {
  color: var(--velo-warning-text);
}
.dashboard__alert--checkin .dashboard__alert-text p {
  color: var(--velo-peach-500);
}

.dashboard__alert--feedback .dashboard__alert-icon {
  color: var(--velo-teal-700);
}
.dashboard__alert--feedback .dashboard__alert-text h4 {
  color: var(--velo-teal-700);
}
.dashboard__alert--feedback .dashboard__alert-text p {
  color: var(--velo-teal-600);
}

/* ===== Sections ===== */
.dashboard__section {
  margin-bottom: var(--space-6);
}

.dashboard__section-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-4);
}

/* ===== Nearest practice card ===== */
.dashboard__practice-card {
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.dashboard__practice-card:active {
  opacity: 0.8;
}

.dashboard__practice-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.dashboard__practice-icon {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Иконка сама несёт circle-обводку (IconMeditation.vue) — без teal-подложки. */
  color: var(--velo-text-primary);
}

.dashboard__practice-info {
  flex: 1;
  min-width: 0;
}

.dashboard__practice-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0 0 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dashboard__practice-master {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin: 0;
}

.dashboard__practice-master-avatar {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--velo-bg-subtle);
  color: var(--velo-primary);
  font-size: 9px;
  line-height: 1;
}

.dashboard__practice-master-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard__practice-verified {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}

.dashboard__practice-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.dashboard__practice-meta-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.dashboard__practice-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

/* Zoom / Check-in buttons use a larger 20px label (Figma 2266:527, 2266:530)
   without changing the base VButton size variants. */
.dashboard__practice-actions :deep(.v-btn) {
  font-size: var(--text-lg);
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
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  text-align: center;
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
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-xl);
  padding: 2px;
}

.dashboard__period-btn {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-primary);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-xl);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dashboard__period-btn--active {
  background: var(--velo-primary);
  color: #ffffff;
}

.dashboard__ai-card {
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.dashboard__ai-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-primary);
  line-height: 1.6;
  margin: 0;
}

/* Mood trend indicator (static, non-clickable) */
.dashboard__ai-mood {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

.dashboard__ai-mood-label {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.dashboard__ai-mood-arrow {
  color: var(--velo-text-muted);
}

/* "Подробнее" link row -> AI-summary screen (16). */
.dashboard__ai-more {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-4);
  color: var(--velo-text-primary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.dashboard__ai-more:hover {
  opacity: 0.8;
}

.dashboard__ai-more-icon {
  color: var(--velo-text-primary);
}

.dashboard__ai-more-label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
}
</style>
