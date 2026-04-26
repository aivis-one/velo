// =============================================================================
// VELO Frontend -- Masters API (Phase F6, updated F7)
// =============================================================================
//
// Typed wrappers over api.get/post/patch for master endpoints.
//
// Backend endpoints:
//   POST  /api/v1/masters/apply           -- submit application (role=user)
//   GET   /api/v1/masters/me              -- my master profile (role=master)
//   GET   /api/v1/masters/me/practices    -- my practices list (role=master)
//   PATCH /api/v1/masters/me/payout       -- update payout details (F7)
//   POST  /api/v1/masters/me/withdraw     -- create withdrawal request (F7)
//   GET   /api/v1/masters/me/withdrawals  -- list my withdrawals (F7)
// =============================================================================

import { api } from '@/api/client'
import { buildQuery } from '@/api/utils'
import type {
  MasterApplyRequest,
  MasterApplyResponse,
  MasterProfileResponse,
  PaginatedPracticesResponse,
  PayoutDetailsUpdate,
  PayoutDetailsResponse,
  PaginatedWithdrawalsResponse,
  WithdrawalResponse,
} from '@/api/types'

/**
 * Submit a master application (3-step form).
 * Only callable by users with role='user'.
 */
export function applyMaster(body: MasterApplyRequest): Promise<MasterApplyResponse> {
  return api.post<MasterApplyResponse>('/api/v1/masters/apply', body)
}

/**
 * Fetch the current master's profile.
 * Only callable by users with role='master'.
 * F7: response now includes payout field (null if not configured).
 */
export function getMyMasterProfile(): Promise<MasterProfileResponse> {
  return api.get<MasterProfileResponse>('/api/v1/masters/me')
}

/**
 * Fetch paginated list of practices owned by the current master.
 * Only callable by users with role='master'.
 */
export function getMyPractices(
  limit = 20,
  offset = 0,
): Promise<PaginatedPracticesResponse> {
  const query = buildQuery({ limit, offset })
  return api.get<PaginatedPracticesResponse>(`/api/v1/masters/me/practices${query}`)
}

// =============================================================================
// F7: Finance endpoints
// =============================================================================

/**
 * Update master's payout details (bank transfer, PayPal, Revolut).
 * Returns the stored PayoutDetails on success.
 *
 * body.details is freeform -- depends on method:
 *   bank_transfer -> { iban, bank_name?, account_holder?, swift? }
 *   paypal        -> { email }
 *   revolut       -> { tag? } or { phone? }
 */
export function updatePayoutDetails(body: PayoutDetailsUpdate): Promise<PayoutDetailsResponse> {
  return api.patch<PayoutDetailsResponse>('/api/v1/masters/me/payout', body)
}

/**
 * Create a withdrawal request.
 * Freezes amount_cents from available balance until admin decision.
 * Returns 201 on success.
 *
 * Requires payout details to be configured first (400 otherwise).
 * Minimum amount: 5000 cents (EUR 50.00).
 */
export function createWithdrawal(amount_cents: number): Promise<WithdrawalResponse> {
  return api.post<WithdrawalResponse>('/api/v1/masters/me/withdraw', { amount_cents })
}

/**
 * Fetch paginated list of my withdrawal requests (newest first).
 * Only callable by users with role='master'.
 */
export function getMyWithdrawals(
  limit = 20,
  offset = 0,
): Promise<PaginatedWithdrawalsResponse> {
  const query = buildQuery({ limit, offset })
  return api.get<PaginatedWithdrawalsResponse>(`/api/v1/masters/me/withdrawals${query}`)
}
