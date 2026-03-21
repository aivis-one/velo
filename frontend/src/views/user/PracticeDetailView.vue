<!--
  VELO Frontend -- PracticeDetailView (Phase F3.2, updated F4.1, F5, F9.1, DS-sprint)

  Full practice detail screen. Matches design Dashboard 2 / booked-practice layout:
    - Hero: white card with IconMeditation SVG + title + meta + "Оплачено" badge
    - Accordions: "О практике" (description), "Что подготовить" (what_to_prepare)
    - Master card: avatar + name + ✓ + methods tags (VTag) + arrow
    - Contraindications banner (if practice.contraindications)
    - Sticky footer: price + action button + cancel booking

  F4.1: BookingPopup (purchase flow with promo).
  F5 review fix:
    W-21: booked state derived from bookingsStore instead of local ref.
  F9.1: Sticky footer action is now context-aware:
    - Not booked + available  → "Забронировать" / "Записаться бесплатно"
    - Booked + in check-in window  → "✅ Check-in перед практикой"
    - Booked + in feedback window  → "💬 Оставить feedback"
    - Booked + outside any window  → "✓ Вы записаны" (disabled)
    - Booked (cancellable)         → "Отменить бронирование"
  DS-sprint: accordions, master methods tags, contraindications banner.

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

    <!-- Back button header -->
    <VHeader title="Моя практика" show-back @back="router.back()" />

    <!-- Scrollable area: hero + body -->
    <div class="detail__scrollable">
      <!-- Hero card (white rounded card matching design) -->
      <div class="detail__hero-card">
        <div class="detail__hero-icon">
          <IconMeditation :size="48" />
        </div>
        <h1 class="detail__title">{{ practice.title }}</h1>
        <div class="detail__meta">
          <span>📅 {{ formattedDate }}</span>
          <span>⏱️ {{ formattedDuration }}</span>
          <VBadge v-if="booked && myBooking?.purchase_id" variant="success">
            ✓ Оплачено
          </VBadge>
        </div>
        <VBadge v-if="practice.status === 'live'" variant="success">
          LIVE
        </VBadge>
      </div>

      <!-- Body -->
      <div class="detail__body">

        <!-- О практике accordion -->
        <VAccordion v-if="practice.description" title="О практике">
          <p class="detail__accordion-text">{{ practice.description }}</p>
        </VAccordion>

        <!-- Что подготовить accordion -->
        <VAccordion v-if="practice.what_to_prepare" title="Что подготовить">
          <p class="detail__accordion-text">{{ practice.what_to_prepare }}</p>
        </VAccordion>

        <!-- Master card -->
        <section class="detail__section">
          <h3 class="detail__section-title">Мастер</h3>
          <div class="detail__master-card">
            <div class="detail__master-avatar">
              <span class="detail__master-avatar-emoji">🧘</span>
            </div>
            <div class="detail__master-info">
              <div class="detail__master-name">
                {{ practice.master_name ?? 'Мастер' }}
                <span class="detail__master-verified">✓</span>
              </div>
              <div v-if="practice.master_methods?.length" class="detail__master-tags">
                <VTag
                  v-for="method in practice.master_methods"
                  :key="method"
                  :label="method"
                />
              </div>
            </div>
            <button
              class="detail__master-arrow"
              aria-label="Профиль мастера"
              @click="onMasterProfile"
            >
              →
            </button>
          </div>
        </section>

        <!-- Contraindications banner -->
        <div v-if="practice.contraindications" class="detail__contraindications">
          <span class="detail__contraindications-icon">⚠️</span>
          <div class="detail__contraindications-text">
            <div class="detail__contraindications-title">ПРОТИВОПОКАЗАНИЯ</div>
            <div class="detail__contraindications-body">{{ practice.contraindications }}</div>
          </div>
        </div>

      </div>
    </div>

    <!-- Footer: price + action (static, not fixed) -->
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

      <!-- Not booked: book button (hidden for practice owner) -->
      <VButton
        v-else-if="!isMaster"
        variant="primary"
        size="lg"
        block
        :disabled="full"
        @click="onBook"
      >
        {{ bookButtonText }}
      </VButton>
      <!-- Cancel booking button (visible when booked and cancellable) -->
      <VButton
        v-if="booked && canCancel"
        variant="ghost"
        size="lg"
        block
        :loading="cancelling"
        class="detail__cancel-btn"
        @click="onCancelBooking"
      >
        Отменить бронирование
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
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePracticesStore } from '@/stores/practices'
import { useBookingsStore } from '@/stores/bookings'
import { VLoader, VEmptyState, VButton, VBadge, VAccordion, VTag } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import BookingPopup from '@/components/shared/BookingPopup.vue'
import {
  formatDate,
  formatDuration,
  formatMoney,
  formatParticipants,
  isFull,
} from '@/utils/format'
import IconMeditation from '@/components/icons/IconMeditation.vue'

const route = useRoute()
const router = useRouter()
const store = usePracticesStore()
const bookingsStore = useBookingsStore()

const practice = computed(() => store.selected)

// -- Booking state --
const showBookingPopup = ref(false)
const authStore = useAuthStore()
const toast = useToast()

// Prevent master from booking their own practice (backend also enforces this,
// but we hide the button entirely to avoid a pointless UX dead-end).
const isMaster = computed(() =>
  !!practice.value && practice.value.master_id === authStore.user?.id,
)

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

// NEW-1: imported from utils/constants -- single source of truth.
import { isInCheckinWindow, isInFeedbackWindow } from '@/composables/usePracticeWindows'

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
  const scheduledMs = new Date(practice.value.scheduled_at).getTime()
  return isInCheckinWindow(scheduledMs, now.value)
})

/**
 * True when now is in the feedback window and booking is attended.
 */
const inFeedbackWindow = computed((): boolean => {
  if (!practice.value || !myBooking.value) return false
  if (myBooking.value.status !== 'attended') return false
  const scheduledMs = new Date(practice.value.scheduled_at).getTime()
  return isInFeedbackWindow(scheduledMs, practice.value.duration_minutes, now.value)
})

// =========================================================================
// Formatted fields
// =========================================================================

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

const cancelling = ref(false)

/**
 * Booking is cancellable when status is confirmed or pending.
 * attended/no_show/cancelled are not cancellable.
 */
const canCancel = computed((): boolean => {
  if (!myBooking.value) return false
  return myBooking.value.status === 'confirmed' || myBooking.value.status === 'pending'
})

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

async function onCancelBooking(): Promise<void> {
  if (!myBooking.value || cancelling.value) return
  cancelling.value = true
  const result = await bookingsStore.cancelBooking(myBooking.value.id)
  cancelling.value = false
  if (!result.ok) {
    // Toast is shown by the store on error; no local handling needed.
    return
  }
  justPurchased.value = false
}

function onMasterProfile(): void {
  // Master public profile route is not yet implemented (future sprint).
  toast.info('Профиль мастера — скоро')
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

// F-01: Vue Router may reuse this component instance when navigating between
// practices (e.g. from search results). onMounted won't fire again, so watch
// the route param and re-fetch when it changes.
watch(
  () => route.params.id as string,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      store.clearSelected()
      store.fetchPractice(newId)
    }
  },
)

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

/* Outer container: flex column filling the shell's scroll area */
.detail {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Scrollable region: grows to fill available space */
.detail__scrollable {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* ===== Hero card ===== */
.detail__hero-card {
  margin: var(--space-4) var(--space-4) 0;
  background: #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-5) var(--space-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-2);
}

.detail__hero-icon {
  color: var(--velo-primary);
  margin-bottom: var(--space-1);
}

.detail__title {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.detail__meta {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--space-3);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

/* ===== Body ===== */
.detail__body {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Accordion text body */
.detail__accordion-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  line-height: 1.6;
}

/* ===== Section (master) ===== */
.detail__section {
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--velo-border-light);
}

.detail__section:last-child {
  border-bottom: none;
}

.detail__section-title {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-3);
}

/* ===== Master card ===== */
.detail__master-card {
  background: #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-3);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  position: relative;
}

.detail__master-avatar {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--velo-glass-blue-15);
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.detail__master-avatar-emoji {
  font-size: 28px;
}

.detail__master-info {
  flex: 1;
  min-width: 0;
}

.detail__master-name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-1);
}

.detail__master-verified {
  color: var(--velo-teal-600);
  margin-left: 4px;
}

.detail__master-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin-top: var(--space-1);
}

.detail__master-arrow {
  position: absolute;
  bottom: var(--space-3);
  right: var(--space-3);
  background: var(--velo-glass-blue-15);
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

.detail__master-arrow:hover {
  opacity: 0.8;
}

/* ===== Contraindications banner ===== */
.detail__contraindications {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  background: var(--velo-glass-peach-40);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  margin-top: var(--space-2);
}

.detail__contraindications-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.detail__contraindications-text {
  flex: 1;
}

.detail__contraindications-title {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-peach-700);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 2px;
}

.detail__contraindications-body {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-peach-500);
  line-height: 1.4;
}

/* ===== Footer ===== */
.detail__actions {
  flex-shrink: 0;
  padding: var(--space-4);
  background: var(--velo-glass-blue-60);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  border-top: 1px solid #ffffff;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
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
  color: var(--velo-success-text);
}

/* Cancel button: ghost with red tint */
.detail__actions .detail__cancel-btn {
  color: var(--velo-error-text);
}
</style>
