// =============================================================================
// VELO Frontend -- Bookings Store (Phase F4.1)
// =============================================================================
//
// Pinia store for the current user's bookings. Uses usePagination
// composable for load-more pattern (same as practices store).
//
// Data flow:
//   1. fetchMyBookings() — initial load (skips if already loaded)
//   2. loadMore()        — next page
//   3. setStatusFilter() — change filter, auto-refresh
//   4. cancelBooking()   — cancel + refresh list
//
// Balance refresh after cancel is handled by the view (calls
// balanceStore.refresh() after successful cancellation).
// =============================================================================

import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { getMyBookings, cancelBooking as apiCancelBooking } from '@/api/bookings'
import { usePagination } from '@/composables/usePagination'
import type { BookingWithPracticeResponse, BookingStatus } from '@/api/types'

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
   * Returns true on success, false on error.
   * Caller is responsible for showing toast messages.
   */
  async function cancelBooking(bookingId: string): Promise<boolean> {
    try {
      await apiCancelBooking(bookingId)
      // Refresh bookings list to reflect new status.
      await pagination.refresh()
      return true
    } catch {
      return false
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
