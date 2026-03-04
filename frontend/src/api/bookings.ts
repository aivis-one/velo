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
// =============================================================================

import { api } from '@/api/client'
import { buildQuery } from '@/api/utils'
import type {
  PaginatedBookingsResponse,
  BookingStatus,
  PurchaseResponse,
  PreviewPurchaseResponse,
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
 * Cancel a booking by ID.
 *
 * Backend applies refund policy based on cancellation deadline:
 *   > 24h before practice  -> full refund
 *   <= 24h before practice -> no refund (early finalize)
 */
export function cancelBooking(bookingId: string): Promise<void> {
  return api.delete(`/api/v1/bookings/${bookingId}`)
}
