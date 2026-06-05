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

    <!-- Greeting removed (static, low-value, took space — operator 2026-06-04). -->

    <!-- Check-in alert banner (shared Banner) -->
    <Banner
      v-if="checkinAlert"
      variant="warning"
      title="Пора на check-in!"
      :body="`${checkinAlert.practice.title}${checkinAlertTime}`"
      :clickable="true"
      class="dashboard__alert"
      @click="goToCheckin(checkinAlert.practice_id)"
    >
      <template #icon><IconClock :size="28" /></template>
    </Banner>

    <!-- Feedback alert banner (shared Banner) -->
    <Banner
      v-if="feedbackAlert"
      variant="success"
      title="Оставьте feedback!"
      :body="`${feedbackAlert.practice.title} • Вчера`"
      :clickable="true"
      class="dashboard__alert"
      @click="goToFeedback(feedbackAlert.practice_id)"
    >
      <template #icon><IconFeedback :size="28" /></template>
    </Banner>

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

      <!-- Practice card (shared PracticeListCard) -->
      <PracticeListCard
        v-else-if="nearestBooking"
        :practice="nearestBooking.practice"
        :title="nearestPracticeTitle"
        :when="nearestPracticeDate"
        :duration="nearestPracticeDuration"
        @click="openNearest"
      >
        <template #badge>
          <VBadge v-if="nearestIsLive" variant="success">
            · В эфире
          </VBadge>
          <VBadge v-else-if="nearestBooking.purchase_id" variant="success">
            <IconCheck :size="12" /> Оплачено
          </VBadge>
        </template>
      </PracticeListCard>

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
          :disabled="nearestCheckedIn"
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
        <VStatCard class="dashboard__stat" :value="attendedCount" label="Практик пройдено" />
        <VStatCard class="dashboard__stat" :value="practiceHours" label="Часов в практике" />
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

      <!-- "Подробнее" → AI-summary screen (16). Единый VMoreLink (слово +
           белый pill со стрелкой) — один вид «Подробнее» на весь проект. -->
      <div class="dashboard__ai-more">
        <VMoreLink @click="router.push({ name: 'user-ai-summary' })" />
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBookingsStore } from '@/stores/bookings'
import { useToast } from '@/composables/useToast'
import { VLoader, VButton, VBadge, VMoreLink, VStatCard } from '@/components/ui'
import {
  IconClock,
  IconFeedback,
  IconCheck,
  IconArrowRight,
  IconMoodMid,
  IconMoodHigh,
} from '@/components/icons'
import PracticeListCard from '@/components/shared/PracticeListCard.vue'
import Banner from '@/components/shared/Banner.vue'
import { formatShortDate, formatTime, formatDuration, isToday } from '@/utils/format'
import { isInCheckinWindow, isInFeedbackWindow } from '@/composables/usePracticeWindows'
import { useViewerTimezone } from '@/composables/useViewerTimezone'
import { CHECKIN_WINDOW_H } from '@/utils/constants'
import type { BookingWithPracticeResponse } from '@/api/types'

// CHECKIN_WINDOW_H is imported but only used implicitly via isInCheckinWindow.
// Keeping import to document the dependency (mirrors usePracticeWindows).
void CHECKIN_WINDOW_H

const router = useRouter()

const bookingsStore = useBookingsStore()
const toast = useToast()

// -- Reactive clock: updated every 60s so alert computeds re-evaluate --
const now = ref(Date.now())
let clockInterval: ReturnType<typeof setInterval> | null = null

// -- Period toggle for AI summary (visual only, no API) --
const aiPeriod = ref<'week' | 'month'>('week')

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
      // Hide if the user skipped this practice's check-in this session.
      if (bookingsStore.dismissedCheckins.includes(b.practice_id)) return false
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

/**
 * Nearest booking the user can still act on.
 *
 * Rule: a booking is shown while its practice has NOT ended yet -- i.e. the
 * booking is still confirmed, the practice is not completed/cancelled, and now
 * is before its END (start + duration_minutes). This keeps the card visible to
 * a booked user during the live session (Zoom / Check-in) and hides it the
 * moment the practice is over. (This is "my session" -- distinct from the
 * bookable calendar feed, which hides a practice once it STARTS.)
 *
 * Selection among the candidates: a practice that is happening RIGHT NOW
 * (already started, not yet over) wins over future ones -- that's where Zoom
 * / Check-in actions matter. Among in-progress ones, the latest start; among
 * future ones, the soonest start.
 */
const nearestBooking = computed((): BookingWithPracticeResponse | null => {
  const current = now.value

  const candidates = bookingsStore.bookings.filter((b) => {
    if (b.status !== 'confirmed') return false
    if (b.practice.status === 'completed' || b.practice.status === 'cancelled') {
      return false
    }
    // Visible until it ENDS (start + duration): present before & during the
    // session, gone the moment it is over. Epoch ms -> timezone-independent.
    const start = new Date(b.practice.scheduled_at).getTime()
    const endMs = start + b.practice.duration_minutes * 60 * 1000
    return current < endMs
  })

  if (candidates.length === 0) return null

  const startMs = (b: BookingWithPracticeResponse) =>
    new Date(b.practice.scheduled_at).getTime()

  // In-progress = already started (start <= now) and not past the ceiling.
  const inProgress = candidates.filter((b) => startMs(b) <= current)
  if (inProgress.length > 0) {
    // The one that started most recently is the active session.
    // `?? null` satisfies noUncheckedIndexedAccess ([0] is typed T|undefined);
    // length > 0 guarantees an element, so this never actually returns null here.
    return inProgress.sort((a, b) => startMs(b) - startMs(a))[0] ?? null
  }

  // Otherwise the soonest upcoming one (candidates is non-empty, checked above).
  return candidates.sort((a, b) => startMs(a) - startMs(b))[0] ?? null
})

/** True when the nearest practice is currently live (status from PracticeSummary). */
const nearestIsLive = computed((): boolean =>
  nearestBooking.value?.practice.status === 'live',
)

/**
 * True when the nearest booking already has a check-in. Used to disable the
 * "Check-in" action button (one check-in per booking) -- mirrors the banner,
 * which hides itself on has_checkin.
 */
const nearestCheckedIn = computed((): boolean =>
  nearestBooking.value?.has_checkin ?? false,
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

/**
 * Open the Zoom link directly (not the practice screen).
 *
 * BookingWithPracticeResponse embeds a PracticeSummary (no zoom_link), so we
 * lazy-fetch the full PracticeResponse on click. The https:// guard mirrors
 * PracticeLiveView (AUDIT-0520-02). If the link is missing or invalid, show
 * a toast — we deliberately do NOT navigate to the practice screen, since the
 * whole point of this button is to skip that screen.
 */
function onZoomClick(): void {
  // Zoom is intentionally disabled for now (not ready for the public test):
  // show "unavailable" instead of opening a link. The same applies to the live
  // screen's "Войти". Re-enable when Zoom delivery is live.
  toast.info('Zoom пока недоступен')
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
 * F5: rendered in the VIEWER'S own profile timezone (the profile decides),
 * not the practice's timezone. format helpers apply their own neutral
 * default if the profile timezone is somehow absent.
 */
const viewerTz = useViewerTimezone()

// Dashboard "Ближайшая практика": today → time (it's clearly today), any other
// day → the short date — one value, so the user instantly knows when it is.
const nearestPracticeDate = computed((): string => {
  if (!nearestBooking.value) return ''
  const iso = nearestBooking.value.practice.scheduled_at
  return isToday(iso, viewerTz.value)
    ? formatTime(iso, viewerTz.value)
    : formatShortDate(iso, viewerTz.value)
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
/* ===== Alert banner (shared Banner) — only spacing here ===== */
.dashboard__alert {
  margin-bottom: var(--space-4);
}

/* ===== Sections ===== */
.dashboard__section {
  margin-bottom: var(--space-6);
}

.dashboard__section-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  /* Figma 2266:452 — все секционные заголовки 'Marmelad:Regular' (400),
   * не bold. Было 700 — баг-фикс. */
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-4);
}

/* ===== Nearest practice card =====
 * Карточка ближайшей практики — shared PracticeListCard (см.
 * components/shared/PracticeListCard.vue). Все card-стили перенесены туда,
 * здесь остаётся только spacing вокруг actions row под карточкой. */

.dashboard__practice-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  /* Figma: 15 — близко к --space-3 (14), но точно 15 для соответствия */
  gap: 15px;
  margin-top: 15px;
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

/* ===== Progress stats =====
 * Figma 2266:452 — 2 карточки 160×104, gap 16 (--space-4),
 * контент flex-центрирован по обеим осям, gap value→label 9. */
.dashboard__stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

/* Fixed card height (Figma 2266:452 — 160×104); the rest of the look comes
   from the shared VStatCard component. */
.dashboard__stat {
  height: 104px;
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

/* "Подробнее" → AI-summary screen (16). Сам контрол — общий VMoreLink;
 * здесь только отступ от карточки AI-саммари над ним. */
.dashboard__ai-more {
  margin-top: var(--space-4);
}
</style>
