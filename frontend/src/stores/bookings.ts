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
import {
  getMyBookings,
  getBooking,
  cancelBooking as apiCancelBooking,
  joinBooking as apiJoinBooking,
  leaveBooking as apiLeaveBooking,
  skipCheckin as apiSkipCheckin,
} from '@/api/bookings'
import { usePagination } from '@/composables/usePagination'
import { extractApiError } from '@/composables/useApiError'
// Lazy cross-store use (called only inside actions) -- mirrors diary.ts using
// useBookingsStore(); avoids a top-level circular evaluation.
import { useDiaryStore } from '@/stores/diary'
import type { BookingWithPracticeResponse, BookingDetailResponse, BookingStatus } from '@/api/types'

export interface CancelResult {
  ok: boolean
  error: string
}

/** Result of join/leave actions (same shape as CancelResult). */
export interface ActionResult {
  ok: boolean
  error: string
}

export const useBookingsStore = defineStore('bookings', () => {
  // -- Status filter --
  const statusFilter = ref<BookingStatus | undefined>(undefined)

  // -- Paginated list --
  const pagination = usePagination<BookingWithPracticeResponse>((limit, offset) =>
    getMyBookings(statusFilter.value, limit, offset),
  )

  // -- Single booking detail (screen 18) --
  const selectedBooking = ref<BookingDetailResponse | null>(null)
  const selectedLoading = ref(false)
  const selectedError = ref('')

  // Practices whose check-in the user SKIPPED this session — used to hide the
  // dashboard "Пора на check-in" banner immediately. Session-only: there is no
  // backend skip state yet (logged as a backend task), so it is lost on reload.
  const dismissedCheckins = ref<string[]>([])
  function dismissCheckin(practiceId: string): void {
    if (!dismissedCheckins.value.includes(practiceId)) {
      dismissedCheckins.value.push(practiceId)
    }
  }

  // Practices whose no-show reflection the user SUBMITTED this session — hides
  // the dashboard reflection banner immediately. Session-only: there is no
  // backend `has_reflection` flag yet (TD-REFLECTION, VELO-Backend-Tasks.md),
  // so it is lost on reload. Mirrors dismissedCheckins.
  const dismissedReflections = ref<string[]>([])
  function dismissReflection(practiceId: string): void {
    if (!dismissedReflections.value.includes(practiceId)) {
      dismissedReflections.value.push(practiceId)
    }
  }

  /**
   * Fetch a single booking with full practice details (screen 18).
   * Always refetches -- detail data (status, zoom) may change.
   */
  async function fetchBooking(bookingId: string): Promise<void> {
    selectedLoading.value = true
    selectedError.value = ''
    try {
      selectedBooking.value = await getBooking(bookingId)
    } catch (e) {
      selectedBooking.value = null
      selectedError.value = extractApiError(e, 'Не удалось загрузить бронирование')
    } finally {
      selectedLoading.value = false
    }
  }

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
      // A cancellation projects a "booking_cancelled_by_user" event onto the
      // diary timeline; refresh the feed (best-effort) so it shows up without
      // an app reload.
      void useDiaryStore().refreshFeed()
      return { ok: true, error: '' }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось отменить бронирование')
      return { ok: false, error: message }
    }
  }

  /**
   * Check in to a practice (sets joined_at on the backend).
   * Refreshes the list so joined_at is reflected locally.
   * Returns { ok, error } -- caller decides how to surface errors
   * (e.g. 409 "Already joined" can be treated as a no-op success).
   */
  async function joinBooking(bookingId: string): Promise<ActionResult> {
    try {
      await apiJoinBooking(bookingId)
      await pagination.refresh()
      return { ok: true, error: '' }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось войти в практику')
      return { ok: false, error: message }
    }
  }

  /**
   * Check out from a practice (sets left_at on the backend).
   * Refreshes the list afterwards.
   */
  async function leaveBooking(bookingId: string): Promise<ActionResult> {
    try {
      await apiLeaveBooking(bookingId)
      await pagination.refresh()
      return { ok: true, error: '' }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось покинуть практику')
      return { ok: false, error: message }
    }
  }

  /**
   * Persist the user's choice to skip their PRE check-in for a booking (B2).
   * Refreshes the list so the persisted `checkin_skipped` flag is reflected,
   * keeping the dashboard banner hidden across reloads (not just this session).
   */
  async function skipCheckin(bookingId: string): Promise<ActionResult> {
    try {
      await apiSkipCheckin(bookingId)
      await pagination.refresh()
      return { ok: true, error: '' }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось пропустить check-in')
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

    // Single booking detail (screen 18)
    selectedBooking,
    selectedLoading,
    selectedError,
    fetchBooking,

    // Filter
    statusFilter,
    setStatusFilter,

    // Actions
    cancelBooking,
    joinBooking,
    leaveBooking,
    skipCheckin,

    // Session-only check-in skip tracking
    dismissedCheckins,
    dismissCheckin,

    // Session-only no-show reflection dismiss (TD-REFLECTION)
    dismissedReflections,
    dismissReflection,
  }
})
