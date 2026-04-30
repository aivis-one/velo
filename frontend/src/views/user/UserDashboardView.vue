<!--
  VELO Frontend -- UserDashboardView (S2 P07 C22 — refresh per skin 10/11)

  Greeting -> conditional check-in / feedback alerts -> Ближайшая практика
  with Zoom + Check-in CTAs -> Ваш прогресс stats -> AI-саммари teaser link.

  Existing logic preserved:
    - Check-in window (CHECKIN_WINDOW_H) + feedback window via usePracticeWindows
    - Stats derived client-side from bookingsStore (per A.18)

  No emojis (decision #048). Path Y MEDIUM fidelity.
-->

<template>
  <div class="dashboard">
    <header class="dashboard__greet">
      <p class="dashboard__greet-time">
        {{ greetingPrefix }}
      </p>
      <h1 class="dashboard__greet-name">
        {{ userName }}
      </h1>
    </header>

    <button
      v-if="checkinAlert"
      type="button"
      class="dashboard__alert dashboard__alert--amber"
      @click="goCheckin(checkinAlert.practice_id)"
    >
      <IconClock :size="22" />
      <div class="dashboard__alert-text">
        <h4>Пора на check-in</h4>
        <p>{{ checkinAlert.practice.title }}</p>
      </div>
    </button>

    <button
      v-if="feedbackAlert"
      type="button"
      class="dashboard__alert dashboard__alert--mint"
      @click="goFeedback(feedbackAlert.practice_id)"
    >
      <IconFeedback :size="22" />
      <div class="dashboard__alert-text">
        <h4>Оставьте feedback</h4>
        <p>{{ feedbackAlert.practice.title }}</p>
      </div>
    </button>

    <section
      v-if="nearest"
      class="dashboard__section"
    >
      <h3 class="dashboard__section-title">
        Ближайшая практика
      </h3>
      <div class="dashboard__nearest">
        <component
          :is="nearestIcon"
          class="dashboard__nearest-icon"
          :size="32"
        />
        <div class="dashboard__nearest-body">
          <h2 class="dashboard__nearest-name">
            {{ nearest.practice.title }}
          </h2>
          <p class="dashboard__nearest-meta">
            с {{ nearest.practice.master_name ?? 'Мастером' }}
          </p>
          <p class="dashboard__nearest-meta">
            {{ nearestDate }}, {{ nearestTime }} · {{ nearestDuration }}
          </p>
        </div>
      </div>
      <div class="dashboard__nearest-cta">
        <VButton
          variant="ghost"
          size="md"
          block
          @click="openZoomFor(nearest.practice_id)"
        >
          Zoom
        </VButton>
        <VButton
          variant="primary"
          size="md"
          block
          @click="goCheckin(nearest.practice_id)"
        >
          Check-in
        </VButton>
      </div>
    </section>

    <section class="dashboard__section">
      <h3 class="dashboard__section-title">
        Ваш прогресс
      </h3>
      <div class="dashboard__stats">
        <StatCard
          :value="attendedCount"
          label="Практик пройдено"
        />
        <StatCard
          :value="practiceHours"
          label="Часов в практике"
        />
      </div>
    </section>

    <section class="dashboard__section">
      <header class="dashboard__ai-head">
        <h3 class="dashboard__section-title">
          AI-саммари
        </h3>
        <div class="dashboard__period">
          <button
            type="button"
            :class="{ 'dashboard__period-btn--active': period === 'week' }"
            @click="period = 'week'"
          >
            Неделя
          </button>
          <button
            type="button"
            :class="{ 'dashboard__period-btn--active': period === 'month' }"
            @click="period = 'month'"
          >
            Месяц
          </button>
        </div>
      </header>
      <RouterLink
        to="/user/ai-summary"
        class="dashboard__ai-card"
      >
        <p class="dashboard__ai-text">
          Состояние улучшилось — практик стало больше, настроение стабильнее.
        </p>
        <span class="dashboard__ai-link">
          Подробнее
          <IconArrowForward :size="16" />
        </span>
      </RouterLink>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBookingsStore } from '@/stores/bookings'
import { VButton } from '@/components/ui'
import {
  IconClock,
  IconFeedback,
  IconArrowForward,
} from '@/components/icons'
import StatCard from '@/components/shared/StatCard.vue'
import { PRACTICE_TYPE_ICON } from '@/utils/displayHelpers'
import { formatDateShort, formatTime, formatDuration } from '@/utils/format'
import { isInCheckinWindow, isInFeedbackWindow } from '@/composables/usePracticeWindows'
import type { BookingWithPracticeResponse } from '@/api/types'

const router = useRouter()
const auth = useAuthStore()
const bookings = useBookingsStore()

const period = ref<'week' | 'month'>('week')
const now = ref(Date.now())
let tickHandle: ReturnType<typeof setInterval> | undefined

onMounted(() => {
  bookings.fetchMyBookings()
  tickHandle = setInterval(() => {
    now.value = Date.now()
  }, 60_000)
})

onUnmounted(() => {
  if (tickHandle) clearInterval(tickHandle)
})

const userName = computed(() => auth.user?.first_name ?? 'друг')

const greetingPrefix = computed((): string => {
  const h = new Date().getHours()
  if (h < 5) return 'Доброй ночи,'
  if (h < 12) return 'Доброе утро,'
  if (h < 18) return 'Добрый день,'
  return 'Добрый вечер,'
})

const checkinAlert = computed((): BookingWithPracticeResponse | null => {
  return (
    bookings.bookings.find((b) => {
      if (b.status !== 'confirmed') return false
      const ms = new Date(b.practice.scheduled_at).getTime()
      return isInCheckinWindow(ms, now.value)
    }) ?? null
  )
})

const feedbackAlert = computed((): BookingWithPracticeResponse | null => {
  return (
    bookings.bookings.find((b) => {
      if (b.status !== 'attended') return false
      const ms = new Date(b.practice.scheduled_at).getTime()
      return isInFeedbackWindow(ms, b.practice.duration_minutes, now.value)
    }) ?? null
  )
})

const nearest = computed((): BookingWithPracticeResponse | null => {
  const list = bookings.bookings
    .filter((b) => b.status === 'confirmed')
    .slice()
    .sort(
      (a, b) =>
        new Date(a.practice.scheduled_at).getTime() -
        new Date(b.practice.scheduled_at).getTime(),
    )
  return list[0] ?? null
})

const nearestIcon = computed(() => {
  if (!nearest.value) return PRACTICE_TYPE_ICON.live
  return PRACTICE_TYPE_ICON[nearest.value.practice.practice_type] ?? PRACTICE_TYPE_ICON.live
})

const nearestDate = computed((): string => {
  if (!nearest.value) return ''
  return formatDateShort(nearest.value.practice.scheduled_at, nearest.value.practice.timezone)
})

const nearestTime = computed((): string => {
  if (!nearest.value) return ''
  return formatTime(nearest.value.practice.scheduled_at, nearest.value.practice.timezone)
})

const nearestDuration = computed((): string => {
  if (!nearest.value) return ''
  return formatDuration(nearest.value.practice.duration_minutes)
})

const attendedCount = computed(
  () => bookings.bookings.filter((b) => b.status === 'attended').length,
)

const practiceHours = computed(() => {
  const totalMin = bookings.bookings
    .filter((b) => b.status === 'attended')
    .reduce((sum, b) => sum + (b.practice.duration_minutes ?? 0), 0)
  return (totalMin / 60).toFixed(1)
})

function goCheckin(practiceId: string): void {
  router.push(`/user/practices/${practiceId}/checkin`)
}

function goFeedback(practiceId: string): void {
  router.push(`/user/practices/${practiceId}/feedback`)
}

function openZoomFor(practiceId: string): void {
  // PracticeSummary (embedded in BookingWithPracticeResponse) doesn't carry
  // zoom_link — only the full PracticeResponse does. Route to the live view
  // which loads PracticeResponse and handles Zoom externally.
  router.push(`/user/practices/${practiceId}/live`)
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.dashboard__greet {
  margin-bottom: var(--space-2);
}

.dashboard__greet-time {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.dashboard__greet-name {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  margin: 0;
}

.dashboard__alert {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  background: var(--surface-warm-alpha-30, var(--surface-steel-alpha-15));
  cursor: pointer;
  text-align: left;
  font-family: var(--font-body);
}

.dashboard__alert--mint {
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
}

.dashboard__alert-text {
  flex: 1;
}

.dashboard__alert-text h4 {
  font-size: var(--text-base);
  margin: 0 0 2px;
  color: var(--text-primary);
  font-weight: 400;
}

.dashboard__alert-text p {
  font-size: var(--text-sm);
  margin: 0;
  color: var(--text-secondary);
}

.dashboard__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.dashboard__section-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin: 0;
  font-weight: 400;
}

.dashboard__nearest {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  background: var(--surface-steel-alpha-15);
}

.dashboard__nearest-icon {
  flex-shrink: 0;
  color: var(--text-primary);
}

.dashboard__nearest-body {
  flex: 1;
  min-width: 0;
}

.dashboard__nearest-name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  margin: 0 0 var(--space-1);
  font-weight: 400;
  color: var(--text-primary);
}

.dashboard__nearest-meta {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.dashboard__nearest-cta {
  display: flex;
  gap: var(--space-2);
}

.dashboard__stats {
  display: flex;
  gap: var(--space-3);
}

.dashboard__ai-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dashboard__period {
  display: inline-flex;
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  padding: 2px;
  background: var(--surface-steel-alpha-15);
}

.dashboard__period button {
  background: transparent;
  border: none;
  padding: 4px 12px;
  font-size: var(--text-xs);
  cursor: pointer;
  color: var(--text-secondary);
  border-radius: var(--radius-full);
}

.dashboard__period-btn--active {
  background: var(--steel-button) !important;
  color: white !important;
}

.dashboard__ai-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
  text-decoration: none;
  color: var(--text-primary);
}

.dashboard__ai-text {
  margin: 0;
  font-size: var(--text-base);
  line-height: 1.5;
  font-family: var(--font-body);
}

.dashboard__ai-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--steel-button);
}
</style>
