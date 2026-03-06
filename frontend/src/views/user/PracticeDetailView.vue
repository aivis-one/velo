<!--
  VELO Frontend -- PracticeDetailView (Phase F3.2, updated F4.1, fixed F5 review)

  Full practice detail screen. Matches mockup practice-detail layout:
    - Hero header: emoji + title + meta (date, duration, spots)
    - Sections: description, master info
    - Sticky footer: price + "Book" button

  F4.1: BookingPopup (purchase flow with promo).
  F5 review fix:
    W-21: booked state derived from bookingsStore instead of local ref.
          Survives navigation (back/forward).

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

      <!-- Practice type -->
      <section class="detail__section">
        <h3 class="detail__section-title">Тип</h3>
        <VBadge variant="info">{{ typeLabel }}</VBadge>
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
      <VButton
        v-if="booked"
        variant="secondary"
        size="lg"
        block
        disabled
      >
        ✓ Вы записаны
      </VButton>
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
import type { PracticeType } from '@/api/types'

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
  // Check if any active booking matches this practice.
  return bookingsStore.bookings.some(
    (b) =>
      b.practice_id === practice.value!.id &&
      (b.status === 'confirmed' || b.status === 'pending'),
  )
})

// -- Type labels --
const TYPE_EMOJI: Record<PracticeType, string> = {
  live: '🧘',
  series: '🔄',
  one_on_one: '👤',
  replay: '📹',
}

const TYPE_LABEL: Record<PracticeType, string> = {
  live: 'Live-сессия',
  series: 'Серия занятий',
  one_on_one: 'Индивидуальная',
  replay: 'Запись',
}

const typeEmoji = computed(() =>
  practice.value ? TYPE_EMOJI[practice.value.practice_type] ?? '🧘' : '🧘',
)

const typeLabel = computed(() =>
  practice.value ? TYPE_LABEL[practice.value.practice_type] ?? practice.value.practice_type : '',
)

// -- Formatted fields --
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

// -- Actions --
function onBook(): void {
  showBookingPopup.value = true
}

function onPurchased(): void {
  showBookingPopup.value = false
  justPurchased.value = true
  // Refresh practice to update participant count.
  const id = route.params.id as string
  store.fetchPractice(id)
  // Refresh bookings so booked computed works on next visit.
  bookingsStore.refreshBookings()
}

// -- Lifecycle --
onMounted(() => {
  const id = route.params.id as string
  store.fetchPractice(id)
  // Pre-load bookings for booked state check (W-21).
  bookingsStore.fetchMyBookings()
})

onUnmounted(() => {
  store.clearSelected()
})
</script>

<style scoped>
.detail__loader {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.detail {
  display: flex;
  flex-direction: column;
  /* Offset MobileLayout padding to go edge-to-edge for hero */
  margin: calc(-1 * var(--space-4));
  min-height: calc(100vh - 120px); /* approx: header + tabbar */
}

.detail__hero {
  text-align: center;
  padding: var(--space-6);
  background: white;
  border-bottom: 1px solid var(--velo-border);
}

.detail__emoji {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.detail__title {
  font-family: var(--font-heading);
  font-size: 24px;
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0 0 var(--space-2);
}

.detail__meta {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--space-4);
  font-size: 14px;
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-2);
}

/* Body */
.detail__body {
  flex: 1;
  padding: var(--space-4);
}

.detail__section {
  margin-bottom: var(--space-6);
}

.detail__section-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--velo-text-primary);
  margin: 0 0 var(--space-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail__section-content {
  font-size: 15px;
  color: var(--velo-text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* Master card */
.detail__master-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  background: white;
  border: 1px solid var(--velo-border);
  border-radius: 12px;
}

.detail__master-avatar {
  font-size: 48px;
  flex-shrink: 0;
}

.detail__master-info {
  flex: 1;
}

.detail__master-name {
  font-weight: 600;
  font-size: 16px;
  color: var(--velo-text-primary);
}

/* Sticky footer */
.detail__actions {
  position: sticky;
  bottom: 0;
  padding: var(--space-4);
  background: white;
  border-top: 1px solid var(--velo-border);
}

.detail__price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.detail__price-label {
  font-size: 14px;
  color: var(--velo-text-secondary);
}

.detail__price-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--velo-primary);
}

.detail__price-value--free {
  color: var(--velo-success, #16A34A);
}
</style>
