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
import { ref, watch } from 'vue'
import { getMyBookings, cancelBooking as apiCancelBooking } from '@/api/bookings'
import { usePagination } from '@/composables/usePagination'
import { ApiResponseError } from '@/api/client'
import { extractApiError } from '@/composables/useApiError'
import type { BookingWithPracticeResponse, BookingStatus } from '@/api/types'

export interface CancelResult {
  ok: boolean
  error: string
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
  }
})
