// =============================================================================
// VELO Frontend -- Bookings Store (Phase F4.1, fixed F5 review)
// =============================================================================
//
// Pinia store for the current user's bookings. Uses usePagination
// composable for load-more pattern (same as practices store).
//
// F5 review fix:
//   W-25: cancelBooking returns { ok, error } instead of boolean,
//         so caller gets specific error message for toast.
// =============================================================================

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { getMyBookings, cancelBooking as apiCancelBooking } from '@/api/bookings'
import { usePagination } from '@/composables/usePagination'
import { extractApiError } from '@/composables/useApiError'
import type { BookingWithPracticeResponse, BookingStatus } from '@/api/types'

export interface CancelResult {
  ok: boolean
  error: string
}

export type StatusChipVariant = 'amber' | 'mint' | 'pink' | 'gray'

export interface StatusChip {
  label: string
  variant: StatusChipVariant
}

export const useBookingsStore = defineStore('bookings', () => {
  // -- Status filter --
  const statusFilter = ref<BookingStatus | undefined>(undefined)

  // -- Paginated list --
  const pagination = usePagination<BookingWithPracticeResponse>(
    (limit, offset) => getMyBookings(statusFilter.value, limit, offset),
  )

  /**
   * Initial load. Called once from view onMounted.
   * Skips if already loaded (e.g. navigating back).
   */
  async function fetchMyBookings(): Promise<void> {
    if (pagination.items.value.length > 0) return
    await pagination.refresh()
  }

  /**
   * Change status filter and reload from scratch.
   */
  function setStatusFilter(status: BookingStatus | undefined): void {
    statusFilter.value = status
  }

  // Auto-refresh when status filter changes.
  watch(statusFilter, () => {
    pagination.refresh()
  })

  /**
   * Cancel a booking by ID, then refresh the list.
   *
   * W-25: Returns { ok, error } with specific error message
   * instead of silent boolean. Caller shows toast with error detail.
   */
  async function cancelBooking(bookingId: string): Promise<CancelResult> {
    try {
      await apiCancelBooking(bookingId)
      // Refresh bookings list to reflect new status.
      await pagination.refresh()
      return { ok: true, error: '' }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось отменить бронирование')
      return { ok: false, error: message }
    }
  }

  // ----------------------------------------------------------------------
  // S2 P09 C33 + Phase 13 C52: status getters + chip helper.
  // PracticeSummary uses scheduled_at (post-C15 regen).
  // ----------------------------------------------------------------------

  const upcomingBookings = computed<BookingWithPracticeResponse[]>(() => {
    const now = Date.now()
    return pagination.items.value.filter((b) => {
      if (b.status !== 'confirmed') return false
      const start = new Date(b.practice.scheduled_at).getTime()
      return start >= now
    })
  })

  const pastBookings = computed<BookingWithPracticeResponse[]>(() => {
    const now = Date.now()
    return pagination.items.value.filter((b) => {
      if (b.status === 'attended' || b.status === 'no_show' || b.status === 'cancelled') return true
      if (b.status === 'confirmed') {
        const start = new Date(b.practice.scheduled_at).getTime()
        return start < now
      }
      return false
    })
  })

  function statusChipVariant(b: BookingWithPracticeResponse): StatusChip {
    if (b.status === 'cancelled') return { label: 'Отменена', variant: 'pink' }
    if (b.status === 'no_show') return { label: 'Пропущена', variant: 'pink' }
    if (b.status === 'attended') return { label: 'Завершена', variant: 'mint' }
    const startMs = new Date(b.practice.scheduled_at).getTime()
    const dayMs = 24 * 60 * 60 * 1000
    const dayDiff = Math.floor((startMs - Date.now()) / dayMs)
    if (dayDiff === 0) return { label: 'Сегодня', variant: 'amber' }
    if (dayDiff === 1) return { label: 'Завтра', variant: 'amber' }
    return { label: 'Подтверждена', variant: 'mint' }
  }

  return {
    // List
    bookings: pagination.items,
    total: pagination.total,
    loading: pagination.loading,
    error: pagination.error,
    hasMore: pagination.hasMore,
    fetchMyBookings,
    loadMore: pagination.loadMore,
    refreshBookings: pagination.refresh,

    // Filter
    statusFilter,
    setStatusFilter,

    // Actions
    cancelBooking,

    // Status getters (S2 P09 + Phase 13)
    upcomingBookings,
    pastBookings,
    statusChipVariant,
  }
})
