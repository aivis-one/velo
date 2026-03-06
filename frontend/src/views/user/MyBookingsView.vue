<!--
  VELO Frontend -- MyBookingsView (Phase F4.1, fixed F5 review)

  User's bookings list. Matches mockup screen-bookings layout:
    - Status filter tabs (all, confirmed, cancelled, attended)
    - BookingCard list with load-more
    - Cancel flow via CancelBookingPopup

  F5 review fix:
    W-22: Pass cancelling loading state to CancelBookingPopup

  Route: /user/bookings (name: 'user-bookings')
-->

<template>
  <!-- Loading (initial) -->
  <div v-if="store.loading && store.bookings.length === 0" class="bookings__loader">
    <VLoader size="lg" />
  </div>

  <!-- Error -->
  <VEmptyState
    v-else-if="store.error && store.bookings.length === 0"
    icon="⚠️"
    title="Ошибка загрузки"
    :description="store.error"
  >
    <VButton size="sm" @click="store.refreshBookings()">Попробовать снова</VButton>
  </VEmptyState>

  <!-- Content -->
  <div v-else class="bookings">
    <!-- Status filter -->
    <div class="bookings__filters">
      <button
        v-for="tab in filterTabs"
        :key="tab.value ?? 'all'"
        class="bookings__filter"
        :class="{ 'bookings__filter--active': store.statusFilter === tab.value }"
        @click="store.setStatusFilter(tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Empty state -->
    <VEmptyState
      v-if="store.bookings.length === 0 && !store.loading"
      icon="📋"
      title="Бронирований нет"
      description="Здесь появятся ваши бронирования после записи на практику"
    />

    <!-- Bookings list -->
    <div v-else class="bookings__list">
      <BookingCard
        v-for="booking in store.bookings"
        :key="booking.id"
        :booking="booking"
        @cancel="openCancelPopup(booking)"
      />

      <!-- Load more -->
      <VButton
        v-if="store.hasMore"
        variant="ghost"
        block
        :loading="store.loading"
        @click="store.loadMore()"
      >
        Показать ещё
      </VButton>
    </div>

    <!-- Cancel popup -->
    <CancelBookingPopup
      v-if="cancelTarget"
      :booking="cancelTarget"
      :open="showCancelPopup"
      :loading="cancelling"
      @close="closeCancelPopup"
      @confirm="onConfirmCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import { useBookingsStore } from '@/stores/bookings'
import { useBalanceStore } from '@/stores/balance'
import { useToast } from '@/composables/useToast'
import BookingCard from '@/components/shared/BookingCard.vue'
import CancelBookingPopup from '@/components/shared/CancelBookingPopup.vue'
import type { BookingWithPracticeResponse, BookingStatus } from '@/api/types'

const store = useBookingsStore()
const balanceStore = useBalanceStore()
const toast = useToast()

// -- Filter tabs --
const filterTabs: Array<{ label: string; value: BookingStatus | undefined }> = [
  { label: 'Все', value: undefined },
  { label: 'Подтверждённые', value: 'confirmed' },
  { label: 'Отменённые', value: 'cancelled' },
  { label: 'Завершённые', value: 'attended' },
]

// -- Cancel popup --
const showCancelPopup = ref(false)
const cancelTarget = ref<BookingWithPracticeResponse | null>(null)
const cancelling = ref(false)

function openCancelPopup(booking: BookingWithPracticeResponse): void {
  cancelTarget.value = booking
  showCancelPopup.value = true
}

function closeCancelPopup(): void {
  if (cancelling.value) return
  showCancelPopup.value = false
  cancelTarget.value = null
}

async function onConfirmCancel(): Promise<void> {
  if (!cancelTarget.value || cancelling.value) return

  cancelling.value = true
  const result = await store.cancelBooking(cancelTarget.value.id)

  if (result.ok) {
    toast.success('Бронирование отменено')
    // Refresh balance (refund may have been applied).
    await balanceStore.refresh()
  } else {
    toast.error(result.error)
  }

  cancelling.value = false
  closeCancelPopup()
}

// -- Lifecycle --
onMounted(() => {
  store.fetchMyBookings()
})
</script>

<style scoped>
.bookings__loader {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 40vh;
}

.bookings {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Filter tabs */
.bookings__filters {
  display: flex;
  gap: var(--space-2);
  overflow-x: auto;
  padding-bottom: var(--space-1);
  -webkit-overflow-scrolling: touch;
}

.bookings__filter {
  flex-shrink: 0;
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-full);
  background: white;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.bookings__filter:hover {
  border-color: var(--velo-primary-light);
}

.bookings__filter--active {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: white;
}

/* List */
.bookings__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
</style>
