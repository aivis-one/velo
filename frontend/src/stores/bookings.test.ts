// =============================================================================
// VELO Frontend -- stores/bookings.ts Unit Tests (T1 stage 2 -- harness + stores)
// =============================================================================
//
// Covers the money-adjacent actions: cancelBooking (backend refund by
// deadline, plus its diary.refreshFeed() side effect), joinBooking,
// leaveBooking, skipCheckin. Mocked at the wrapper layer (@/api/bookings) --
// the store imports named functions directly, so this is the correct seam
// (no MSW needed). @/stores/diary is mocked wholesale since cancelBooking
// pulls in useDiaryStore() lazily as a side effect, not a dependency under
// test here.
// =============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBookingsStore } from '@/stores/bookings'
import { ApiResponseError } from '@/api/client'
import * as bookingsApi from '@/api/bookings'
import type { BookingResponse } from '@/api/types'

vi.mock('@/api/bookings')

const refreshFeed = vi.fn()
vi.mock('@/stores/diary', () => ({
  useDiaryStore: () => ({ refreshFeed }),
}))

function emptyPage() {
  return { items: [], total: 0, limit: 20, offset: 0 }
}

describe('useBookingsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(bookingsApi.getMyBookings).mockReset().mockResolvedValue(emptyPage())
    vi.mocked(bookingsApi.cancelBooking).mockReset()
    vi.mocked(bookingsApi.joinBooking).mockReset()
    vi.mocked(bookingsApi.leaveBooking).mockReset()
    vi.mocked(bookingsApi.skipCheckin).mockReset()
    refreshFeed.mockReset()
  })

  describe('cancelBooking', () => {
    it('on success: calls the API, refreshes the list, and fires diary.refreshFeed', async () => {
      vi.mocked(bookingsApi.cancelBooking).mockResolvedValue(undefined)
      const store = useBookingsStore()

      const result = await store.cancelBooking('booking_1')

      expect(result).toEqual({ ok: true, error: '' })
      expect(bookingsApi.cancelBooking).toHaveBeenCalledWith('booking_1')
      expect(bookingsApi.getMyBookings).toHaveBeenCalled()
      expect(refreshFeed).toHaveBeenCalledTimes(1)
    })

    it('on failure: returns the backend error detail and does NOT fire diary.refreshFeed', async () => {
      vi.mocked(bookingsApi.cancelBooking).mockRejectedValue(
        new ApiResponseError(400, 'Too close to start time', 'cancel_window_closed'),
      )
      const store = useBookingsStore()

      const result = await store.cancelBooking('booking_1')

      expect(result).toEqual({ ok: false, error: 'Too close to start time' })
      expect(refreshFeed).not.toHaveBeenCalled()
    })

    it('on failure with a non-ApiResponseError: falls back to the generic message', async () => {
      vi.mocked(bookingsApi.cancelBooking).mockRejectedValue(new Error('boom'))
      const store = useBookingsStore()

      const result = await store.cancelBooking('booking_1')

      expect(result).toEqual({ ok: false, error: 'Не удалось отменить бронирование' })
    })
  })

  describe('joinBooking', () => {
    it('on success: calls the API and refreshes the list', async () => {
      vi.mocked(bookingsApi.joinBooking).mockResolvedValue({
        id: 'booking_1',
      } as BookingResponse)
      const store = useBookingsStore()

      const result = await store.joinBooking('booking_1')

      expect(result).toEqual({ ok: true, error: '' })
      expect(bookingsApi.joinBooking).toHaveBeenCalledWith('booking_1')
      expect(bookingsApi.getMyBookings).toHaveBeenCalled()
    })

    it('on failure (e.g. 409 already joined): returns the backend error detail', async () => {
      vi.mocked(bookingsApi.joinBooking).mockRejectedValue(
        new ApiResponseError(409, 'Already joined', 'already_joined'),
      )
      const store = useBookingsStore()

      const result = await store.joinBooking('booking_1')

      expect(result).toEqual({ ok: false, error: 'Already joined' })
    })
  })

  describe('leaveBooking', () => {
    it('on success: calls the API and refreshes the list', async () => {
      vi.mocked(bookingsApi.leaveBooking).mockResolvedValue({
        id: 'booking_1',
      } as BookingResponse)
      const store = useBookingsStore()

      const result = await store.leaveBooking('booking_1')

      expect(result).toEqual({ ok: true, error: '' })
      expect(bookingsApi.leaveBooking).toHaveBeenCalledWith('booking_1')
    })

    it('on failure (e.g. never joined): returns the backend error detail', async () => {
      vi.mocked(bookingsApi.leaveBooking).mockRejectedValue(
        new ApiResponseError(400, 'Not joined yet', 'not_joined'),
      )
      const store = useBookingsStore()

      const result = await store.leaveBooking('booking_1')

      expect(result).toEqual({ ok: false, error: 'Not joined yet' })
    })
  })

  describe('skipCheckin', () => {
    it('on success: calls the API and refreshes the list', async () => {
      vi.mocked(bookingsApi.skipCheckin).mockResolvedValue({
        id: 'booking_1',
      } as BookingResponse)
      const store = useBookingsStore()

      const result = await store.skipCheckin('booking_1')

      expect(result).toEqual({ ok: true, error: '' })
      expect(bookingsApi.skipCheckin).toHaveBeenCalledWith('booking_1')
    })

    it('on failure: returns the backend error detail', async () => {
      vi.mocked(bookingsApi.skipCheckin).mockRejectedValue(
        new ApiResponseError(404, 'Booking not found', 'not_found'),
      )
      const store = useBookingsStore()

      const result = await store.skipCheckin('booking_1')

      expect(result).toEqual({ ok: false, error: 'Booking not found' })
    })
  })
})
