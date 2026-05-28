<!--
  VELO Frontend -- BookingDetailView (screen 18, Booking Detail)

  Single booking detail. Reuses the shared PracticeHeroCard and MasterCard
  (same building blocks as screen 15). Layout (Figma 18):
    - Header "Бронирование"
    - Hero card (icon, title, date / duration)
    - "Статус" row + status badge
    - "Мастер" section (MasterCard)
    - "ZOOM" section (link-will-be-sent note)
    - "Отменить бронирование" (only while cancellable) + CancelBookingPopup

  Data: bookingsStore.fetchBooking(id) -> BookingDetailResponse (full practice).
  Cancellation reuses bookingsStore.cancelBooking, then navigates back.

  Route: /user/bookings/:id (name: 'booking-detail')
-->

<template>
  <div class="bdetail">
    <VHeader title="Бронирование" show-back @back="router.back()" />

    <!-- Loading -->
    <div v-if="store.selectedLoading" class="bdetail__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error -->
    <VEmptyState
      v-else-if="store.selectedError || !booking"
      icon="⚠️"
      title="Бронирование не найдено"
      :description="store.selectedError"
    >
      <VButton size="sm" @click="router.back()">Назад</VButton>
    </VEmptyState>

    <!-- Content -->
    <template v-else>
      <div class="bdetail__scrollable">
        <!-- Hero -->
        <div class="bdetail__hero">
          <PracticeHeroCard
            :title="practice.title"
            :date="formattedDate"
            :duration="formattedDuration"
          />
        </div>

        <div class="bdetail__body">
          <!-- Status row -->
          <div class="bdetail__status-row">
            <span class="bdetail__status-label">Статус</span>
            <VBadge :variant="statusVariant">
              <component :is="statusIcon" v-if="statusIcon" :size="12" />
              {{ statusLabel }}
            </VBadge>
          </div>

          <!-- Master -->
          <section class="bdetail__section">
            <h3 class="bdetail__section-title">Мастер</h3>
            <MasterCard
              :master-name="practice.master_name"
              :methods="practice.master_methods"
            />
          </section>

          <!-- Zoom -->
          <section class="bdetail__section">
            <h3 class="bdetail__section-title">ZOOM</h3>
            <div class="bdetail__zoom-card">
              Ссылка будет отправлена за 10 минут до начала практики
            </div>
          </section>
        </div>
      </div>

      <!-- Cancel action (only while cancellable) -->
      <div v-if="canCancel" class="bdetail__actions">
        <VButton
          variant="danger"
          size="lg"
          block
          @click="showCancelPopup = true"
        >
          Отменить бронирование
        </VButton>
      </div>

      <!-- Cancel confirmation -->
      <CancelBookingPopup
        v-if="booking"
        :booking="booking"
        :open="showCancelPopup"
        :loading="cancelling"
        @close="showCancelPopup = false"
        @confirm="onConfirmCancel"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VLoader, VEmptyState, VButton, VBadge } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { useBookingsStore } from '@/stores/bookings'
import { useToast } from '@/composables/useToast'
import PracticeHeroCard from '@/components/shared/PracticeHeroCard.vue'
import MasterCard from '@/components/shared/MasterCard.vue'
import CancelBookingPopup from '@/components/shared/CancelBookingPopup.vue'
import { formatDate, formatDuration } from '@/utils/format'
import { IconCheck, IconClose } from '@/components/icons'
import type { BookingStatus } from '@/api/types'

const route = useRoute()
const router = useRouter()
const store = useBookingsStore()
const toast = useToast()

const booking = computed(() => store.selectedBooking)
// Guarded by v-else (content renders only when booking is present).
const practice = computed(() => booking.value!.practice)

// -- Formatted fields --
const formattedDate = computed(() =>
  formatDate(practice.value.scheduled_at, practice.value.timezone),
)
const formattedDuration = computed(() =>
  formatDuration(practice.value.duration_minutes),
)

// -- Status badge --
const STATUS_LABEL: Record<BookingStatus, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждена',
  attended: 'Завершена',
  no_show: 'Неявка',
  cancelled: 'Отменена',
}

const STATUS_VARIANT: Record<BookingStatus, 'success' | 'warning' | 'error' | 'info'> = {
  pending: 'warning',
  confirmed: 'success',
  attended: 'success',
  no_show: 'error',
  cancelled: 'error',
}

const statusLabel = computed(() =>
  booking.value ? STATUS_LABEL[booking.value.status] : '',
)
const statusVariant = computed(() =>
  booking.value ? STATUS_VARIANT[booking.value.status] : 'info',
)
const statusIcon = computed(() => {
  if (!booking.value) return null
  switch (booking.value.status) {
    case 'confirmed':
    case 'attended':
      return IconCheck
    case 'cancelled':
    case 'no_show':
      return IconClose
    default:
      return null
  }
})

// -- Cancel --
const showCancelPopup = ref(false)
const cancelling = ref(false)

const canCancel = computed(
  () =>
    booking.value?.status === 'confirmed' || booking.value?.status === 'pending',
)

async function onConfirmCancel(): Promise<void> {
  if (!booking.value || cancelling.value) return
  cancelling.value = true
  const result = await store.cancelBooking(booking.value.id)
  cancelling.value = false
  showCancelPopup.value = false
  if (!result.ok) {
    toast.error(result.error)
    return
  }
  toast.success('Бронирование отменено')
  router.back()
}

onMounted(() => {
  store.fetchBooking(route.params.id as string)
})
</script>

<style scoped>
.bdetail {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.bdetail__loader {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 40vh;
}

.bdetail__scrollable {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.bdetail__hero {
  /* F-5.2 sync: horizontal margin снят — MobileLayout даёт screen-padding 33.
   * Hero card в Figma booking-detail.svg на x=33 (ровно screen edge). */
  margin: var(--space-4) 0 0;
}

.bdetail__body {
  /* F-5.2 sync: horizontal padding снят (MobileLayout уже 33). Status row,
   * MasterCard, ZOOM card в Figma на x=33. */
  padding: var(--space-4) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Status row */
.bdetail__status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-4);
}

.bdetail__status-label {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

/* Section */
.bdetail__section-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-3);
}

/* Zoom card */
.bdetail__zoom-card {
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  line-height: 1.5;
}

/* Actions footer */
.bdetail__actions {
  /* F-5.2 sync: horizontal padding снят (MobileLayout уже 33). */
  padding: var(--space-4) 0;
}
</style>
