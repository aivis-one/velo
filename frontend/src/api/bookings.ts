// =============================================================================
// VELO Frontend -- Bookings & Purchases API (Phase F4.1)
// =============================================================================
//
// Typed wrappers over api methods for booking and purchase endpoints.
//
// Backend endpoints used:
//   POST /api/v1/practices/{id}/purchase          -- purchase (booking + ledger)
//   POST /api/v1/practices/{id}/preview-purchase   -- pricing preview
//   GET  /api/v1/bookings/me                       -- my bookings (paginated)
//   DELETE /api/v1/bookings/{id}                   -- cancel booking
//   POST /api/v1/bookings/{id}/join                -- check-in (Phase 5.4)
//   POST /api/v1/bookings/{id}/leave               -- check-out (Phase 5.4)
// =============================================================================

import { api } from '@/api/client'
import { buildQuery } from '@/api/utils'
import type {
  PaginatedBookingsResponse,
  BookingStatus,
  BookingResponse,
  BookingDetailResponse,
  PurchaseResponse,
  PreviewPurchaseResponse,
  UserStatsResponse,
} from '@/api/types'

/**
 * Purchase a practice (creates Booking + Purchase + ledger entries).
 *
 * Optional promo_code for discount. Backend validates the promo,
 * checks balance, and creates double-entry ledger records atomically.
 */
export function purchasePractice(
  practiceId: string,
  promoCode?: string,
): Promise<PurchaseResponse> {
  const body = promoCode ? { promo_code: promoCode } : undefined
  return api.post<PurchaseResponse>(
    `/api/v1/practices/${practiceId}/purchase`,
    body,
  )
}

/**
 * Preview purchase pricing with optional promo code.
 *
 * Read-only -- no booking, no purchase, no ledger entries.
 * Shows what the user would pay with/without a promo code.
 */
export function previewPurchase(
  practiceId: string,
  promoCode?: string,
): Promise<PreviewPurchaseResponse> {
  const body = promoCode ? { promo_code: promoCode } : undefined
  return api.post<PreviewPurchaseResponse>(
    `/api/v1/practices/${practiceId}/preview-purchase`,
    body,
  )
}

/**
 * Fetch paginated list of current user's bookings.
 *
 * Each booking includes a PracticeSummary for card rendering.
 * Optional status filter (confirmed, cancelled, attended, etc.).
 */
export function getMyBookings(
  statusFilter?: BookingStatus,
  limit = 20,
  offset = 0,
): Promise<PaginatedBookingsResponse> {
  const query = buildQuery({
    status: statusFilter,
    limit,
    offset,
  })
  return api.get<PaginatedBookingsResponse>(`/api/v1/bookings/me${query}`)
}

/**
 * Fetch the current user's attended-practice stats (profile screen).
 *
 * Returns counts the profile header renders as two cards:
 * practices_attended and hours_attended.
 */
export function getMyStats(): Promise<UserStatsResponse> {
  return api.get<UserStatsResponse>('/api/v1/bookings/me/stats')
}

/**
 * Fetch a single booking with full practice details (screen 18).
 *
 * Backend returns the complete PracticeResponse (zoom_link,
 * contraindications, master_methods, status). Owner-only (404 otherwise).
 */
export function getBooking(bookingId: string): Promise<BookingDetailResponse> {
  return api.get<BookingDetailResponse>(`/api/v1/bookings/${bookingId}`)
}

/**
 * Cancel a booking by ID.
 *
 * Backend applies refund policy based on cancellation deadline:
 *   > 24h before practice  -> full refund
 *   <= 24h before practice -> no refund (early finalize)
 */
export function cancelBooking(bookingId: string): Promise<void> {
  return api.delete(`/api/v1/bookings/${bookingId}`)
}

/**
 * Check in to a practice (sets joined_at). Phase 5.4.
 *
 * Backend rules: booking must be confirmed and the practice scheduled/live.
 * Returns 409 if already joined.
 */
export function joinBooking(bookingId: string): Promise<BookingResponse> {
  return api.post<BookingResponse>(`/api/v1/bookings/${bookingId}/join`)
}

/**
 * Check out from a practice (sets left_at). Phase 5.4.
 *
 * Backend rules: requires joined_at to be set (400 otherwise),
 * returns 409 if already left.
 */
export function leaveBooking(bookingId: string): Promise<BookingResponse> {
  return api.post<BookingResponse>(`/api/v1/bookings/${bookingId}/leave`)
}
