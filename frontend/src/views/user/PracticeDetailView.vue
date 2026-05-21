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
    - Not booked + available  -> "Забронировать" / "Записаться бесплатно"
    - Booked + in check-in window  -> "Check-in перед практикой"
    - Booked + in feedback window  -> "Оставить feedback"
    - Booked + outside any window  -> "Вы записаны" (disabled)
    - Booked (cancellable)         -> "Отменить бронирование"
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
      <!-- Hero card (shared component) -->
      <div class="detail__hero">
        <PracticeHeroCard
          :title="practice.title"
          :date="formattedDate"
          :duration="formattedDuration"
          :participants="!booked ? formattedParticipants : null"
        >
          <template #badge>
            <VBadge v-if="booked && myBooking?.purchase_id" variant="success">
              <IconCheck :size="12" /> Оплачено
            </VBadge>
            <VBadge v-else-if="practice.status === 'live'" variant="success">
              LIVE
            </VBadge>
          </template>
        </PracticeHeroCard>
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

        <!-- Master card (shared component) -->
        <section class="detail__section">
          <h3 class="detail__section-title">Мастер</h3>
          <MasterCard
            :master-name="practice.master_name"
            :methods="practice.master_methods"
          />
        </section>

        <!-- Contraindications banner -->
        <div v-if="practice.contraindications" class="detail__contraindications">
          <span class="detail__contraindications-icon">
            <IconWarning :size="22" />
          </span>
          <div class="detail__contraindications-text">
            <div class="detail__contraindications-title">ПРОТИВОПОКАЗАНИЯ</div>
            <div class="detail__contraindications-body">{{ practice.contraindications }}</div>
          </div>
        </div>

      </div>
    </div>

    <!-- Footer: price + action (static, not fixed) -->
    <div class="detail__actions">
      <!-- Price row: only for the catalog (not-booked) view. In the booked
           "Моя практика" view (Figma 15) the practice is already paid for,
           so the price row is hidden. -->
      <div v-if="!booked" class="detail__price-row">
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
        Check-in перед практикой
      </VButton>

      <!-- F9.1: Feedback button (attended booking in feedback window) -->
      <VButton
        v-else-if="booked && inFeedbackWindow"
        variant="primary"
        size="lg"
        block
        @click="onFeedback"
      >
        Оставить feedback
      </VButton>

      <!-- Already booked, no active window -->
      <VButton
        v-else-if="booked"
        variant="secondary"
        size="lg"
        block
        disabled
      >
        Вы записаны
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
import { VLoader, VEmptyState, VButton, VBadge, VAccordion } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import BookingPopup from '@/components/shared/BookingPopup.vue'
import PracticeHeroCard from '@/components/shared/PracticeHeroCard.vue'
import MasterCard from '@/components/shared/MasterCard.vue'
import {
  formatDate,
  formatDuration,
  formatMoney,
  formatParticipants,
  isFull,
} from '@/utils/format'
import { IconCheck, IconWarning } from '@/components/icons'

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

const formattedParticipants = computed(() => {
  if (!practice.value) return ''
  return formatParticipants(
    practice.value.current_participants,
    practice.value.max_participants,
  )
})

const formattedPrice = computed(() => {
  if (!practice.value) return ''
  return formatMoney(practice.value.price_cents, practice.value.currency)
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
    // The store returns { ok, error } but does not raise a toast itself.
    toast.error(result.error)
    return
  }
  toast.success('Бронирование отменено')
  justPurchased.value = false
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
      justPurchased.value = false
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

/* ===== Hero (shared PracticeHeroCard wrapper) ===== */
.detail__hero {
  margin: var(--space-4) var(--space-4) 0;
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

/* Override VAccordion: white card style matching design */
:deep(.v-accordion) {
  background: #ffffff;
  border-radius: var(--radius-md);
  border-bottom: none;
  overflow: hidden;
}

:deep(.v-accordion__header) {
  padding: var(--space-3) var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
}

:deep(.v-accordion__body) {
  padding: 0 var(--space-4) var(--space-3);
}

:deep(.v-accordion__arrow) {
  font-size: 20px;
  color: var(--velo-text-primary);
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

/* ===== Contraindications banner ===== */
.detail__contraindications {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  background: var(--velo-glass-peach-40);
  border: 2px solid var(--velo-peach-300);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  margin-top: var(--space-2);
}

.detail__contraindications-icon {
  display: inline-flex;
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--velo-peach-700);
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
