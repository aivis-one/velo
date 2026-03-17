<!--
  VELO Frontend -- PracticeDetailView (Phase F3.2, updated F4.1, F5, F9.1)

  Full practice detail screen. Matches mockup practice-detail layout:
    - Hero header: emoji + title + meta (date, duration, spots)
    - Sections: description, master info
    - Sticky footer: price + action button

  F4.1: BookingPopup (purchase flow with promo).
  F5 review fix:
    W-21: booked state derived from bookingsStore instead of local ref.
          Survives navigation (back/forward).
  F9.1: Sticky footer action is now context-aware:
    - Not booked + available  → "Забронировать" / "Записаться бесплатно"
    - Booked + in check-in window  → "✅ Check-in перед практикой"
    - Booked + in feedback window  → "💬 Оставить feedback"
    - Booked + outside any window  → "✓ Вы записаны" (disabled)

  Check-in window:  scheduled_at - 3h  ..  scheduled_at
  Feedback window:  scheduled_at + duration_minutes  ..  + 72h

  Route: /user/practices/:id
  Param: id (practice UUID)
-->

<template>
  <!-- Loading -->
  <div v-if="store.selectedLoading" class="detail__loader">
    <VLoader size="lg" />
  </div>

  <!-- Error -->
  <VEmptyState
    v-else-if="store.selectedError"
    icon="⚠️"
    title="Практика не найдена"
    :description="store.selectedError"
  >
    <VButton size="sm" @click="router.back()">Назад</VButton>
  </VEmptyState>

  <!-- Content -->
  <div v-else-if="practice" class="detail">
    <!-- Hero header -->
    <div class="detail__hero">
      <div class="detail__emoji">{{ typeEmoji }}</div>
      <h1 class="detail__title">{{ practice.title }}</h1>
      <div class="detail__meta">
        <span>📅 {{ formattedDate }}</span>
        <span>⏱️ {{ formattedDuration }}</span>
        <span>👥 {{ formattedParticipants }}</span>
      </div>
      <VBadge v-if="practice.status === 'live'" variant="success">
        LIVE
      </VBadge>
    </div>

    <!-- Body -->
    <div class="detail__body">
      <!-- Description -->
      <section v-if="practice.description" class="detail__section">
        <h3 class="detail__section-title">О практике</h3>
        <p class="detail__section-content">{{ practice.description }}</p>
      </section>

      <!-- Master -->
      <section class="detail__section">
        <h3 class="detail__section-title">Мастер</h3>
        <div class="detail__master-card">
          <div class="detail__master-avatar">🧘‍♂️</div>
          <div class="detail__master-info">
            <div class="detail__master-name">
              {{ practice.master_name ?? 'Мастер' }}
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Sticky footer: price + action -->
    <div class="detail__actions">
      <div class="detail__price-row">
        <span class="detail__price-label">Стоимость</span>
        <span
          class="detail__price-value"
          :class="{ 'detail__price-value--free': practice.is_free }"
        >
          {{ formattedPrice }}
        </span>
      </div>

      <!-- F9.1: Check-in button (confirmed booking in check-in window) -->
      <VButton
        v-if="booked && inCheckinWindow"
        variant="primary"
        size="lg"
        block
        @click="onCheckin"
      >
        ✅ Check-in перед практикой
      </VButton>

      <!-- F9.1: Feedback button (attended booking in feedback window) -->
      <VButton
        v-else-if="booked && inFeedbackWindow"
        variant="primary"
        size="lg"
        block
        @click="onFeedback"
      >
        💬 Оставить feedback
      </VButton>

      <!-- Already booked, no active window -->
      <VButton
        v-else-if="booked"
        variant="secondary"
        size="lg"
        block
        disabled
      >
        ✓ Вы записаны
      </VButton>

      <!-- Not booked: book button -->
      <VButton
        v-else
        variant="primary"
        size="lg"
        block
        :disabled="full"
        @click="onBook"
      >
        {{ bookButtonText }}
      </VButton>
    </div>

    <!-- Booking popup -->
    <BookingPopup
      :practice="practice"
      :open="showBookingPopup"
      @close="showBookingPopup = false"
      @purchased="onPurchased"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePracticesStore } from '@/stores/practices'
import { useBookingsStore } from '@/stores/bookings'
import { VLoader, VEmptyState, VButton, VBadge } from '@/components/ui'
import BookingPopup from '@/components/shared/BookingPopup.vue'
import {
  formatDate,
  formatDuration,
  formatMoney,
  formatParticipants,
  isFull,
} from '@/utils/format'
import { PRACTICE_TYPE_EMOJI } from '@/utils/displayHelpers'

const route = useRoute()
const router = useRouter()
const store = usePracticesStore()
const bookingsStore = useBookingsStore()

const practice = computed(() => store.selected)

// -- Booking state --
const showBookingPopup = ref(false)

// W-21: Derive booked state from bookingsStore (survives navigation).
// Falls back to local flag for immediate feedback after purchase.
const justPurchased = ref(false)

const booked = computed(() => {
  if (justPurchased.value) return true
  if (!practice.value) return false
  return bookingsStore.bookings.some(
    (b) =>
      b.practice_id === practice.value!.id &&
      (b.status === 'confirmed' || b.status === 'pending' || b.status === 'attended'),
  )
})

// =========================================================================
// F9.1: Time window helpers
// =========================================================================

const CHECKIN_WINDOW_H  = 3   // hours before scheduled_at
const FEEDBACK_WINDOW_H = 72  // hours after practice ends

// Reactive clock -- updated every 60s so window computeds re-evaluate
// without requiring a page reload (C-1 fix).
const now = ref(Date.now())

/**
 * Returns the booking matching this practice (any active-ish status).
 * Used to read status for window checks.
 */
const myBooking = computed(() => {
  if (!practice.value) return null
  return (
    bookingsStore.bookings.find(
      (b) => b.practice_id === practice.value!.id,
    ) ?? null
  )
})

/**
 * True when now is in the check-in window and booking is confirmed.
 */
const inCheckinWindow = computed((): boolean => {
  if (!practice.value || !myBooking.value) return false
  if (myBooking.value.status !== 'confirmed') return false
  const scheduledMs   = new Date(practice.value.scheduled_at).getTime()
  const windowStartMs = scheduledMs - CHECKIN_WINDOW_H * 60 * 60 * 1000
  return now.value >= windowStartMs && now.value <= scheduledMs
})

/**
 * True when now is in the feedback window and booking is attended.
 */
const inFeedbackWindow = computed((): boolean => {
  if (!practice.value || !myBooking.value) return false
  if (myBooking.value.status !== 'attended') return false
  const scheduledMs   = new Date(practice.value.scheduled_at).getTime()
  const practiceEndMs = scheduledMs + practice.value.duration_minutes * 60 * 1000
  const feedbackEndMs = practiceEndMs + FEEDBACK_WINDOW_H * 60 * 60 * 1000
  return now.value >= practiceEndMs && now.value <= feedbackEndMs
})

// =========================================================================
// Formatted fields
// =========================================================================

const typeEmoji = computed(() =>
  practice.value ? PRACTICE_TYPE_EMOJI[practice.value.practice_type] ?? '🧘' : '🧘',
)

const formattedDate = computed(() => {
  if (!practice.value) return ''
  return formatDate(practice.value.scheduled_at, practice.value.timezone)
})

const formattedDuration = computed(() => {
  if (!practice.value) return ''
  return formatDuration(practice.value.duration_minutes)
})

const formattedPrice = computed(() => {
  if (!practice.value) return ''
  return formatMoney(practice.value.price_cents, practice.value.currency)
})

const formattedParticipants = computed(() => {
  if (!practice.value) return ''
  return formatParticipants(
    practice.value.current_participants,
    practice.value.max_participants,
  )
})

const full = computed(() => {
  if (!practice.value) return false
  return isFull(
    practice.value.current_participants,
    practice.value.max_participants,
  )
})

const bookButtonText = computed(() => {
  if (full.value) return 'Мест нет'
  if (practice.value?.is_free) return 'Записаться бесплатно'
  return 'Забронировать'
})

// =========================================================================
// Actions
// =========================================================================

function onBook(): void {
  showBookingPopup.value = true
}

function onPurchased(): void {
  showBookingPopup.value = false
  justPurchased.value = true
  const id = route.params.id as string
  store.fetchPractice(id)
  bookingsStore.refreshBookings()
}

function onCheckin(): void {
  if (!practice.value) return
  router.push({ name: 'user-checkin', params: { practiceId: practice.value.id } })
}

function onFeedback(): void {
  if (!practice.value) return
  router.push({ name: 'user-feedback', params: { practiceId: practice.value.id } })
}

// =========================================================================
// Lifecycle
// =========================================================================

// Reactive clock: re-evaluate window computeds every minute so the button
// switches without requiring a page reload.
let clockInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  const id = route.params.id as string
  store.fetchPractice(id)
  bookingsStore.fetchMyBookings()
  // Refresh window checks every 60s.
  clockInterval = setInterval(() => {
    now.value = Date.now()
  }, 60_000)
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
})
</script>

<style scoped>
.detail__loader {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 40vh;
}

.detail {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  padding-bottom: 120px;
}

/* Hero */
.detail__hero {
  padding: var(--space-6) var(--space-4) var(--space-4);
  text-align: center;
  border-bottom: 1px solid var(--velo-border-light);
}

.detail__emoji {
  font-size: 64px;
  margin-bottom: var(--space-3);
}

.detail__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-3);
}

.detail__meta {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--space-3);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-3);
}

/* Body */
.detail__body {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.detail__section {
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--velo-border-light);
}

.detail__section:last-child {
  border-bottom: none;
}

.detail__section-title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin-bottom: var(--space-2);
}

.detail__section-content {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  line-height: 1.6;
}

.detail__master-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.detail__master-avatar {
  font-size: 36px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--velo-glass-blue-15);
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.detail__master-name {
  font-weight: 400;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

/* Sticky footer */
.detail__actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: var(--space-4);
  background: var(--velo-glass-blue-60);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  border-top: 1px solid #ffffff;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  z-index: 10;
}

.detail__price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail__price-label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.detail__price-value {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
}

.detail__price-value--free {
  color: var(--velo-success);
}
</style>
