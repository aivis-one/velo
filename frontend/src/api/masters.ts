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
  MasterPublicResponse,
  PaginatedPracticesResponse,
  PayoutDetails,
  PaginatedWithdrawalsResponse,
  WithdrawalResponse,
  PaginatedStudentsResponse,
  StudentDetailResponse,
  IncomeResponse,
  PaginatedTransactionsResponse,
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
 * Fetch a verified master's PUBLIC profile (S-4).
 * Callable by any authenticated user. Only verified masters resolve;
 * pending / rejected / non-master ids return 404. Carries no financial
 * or contact data -- safe public subset + practices_count / reviews_count.
 */
export function getPublicMaster(userId: string): Promise<MasterPublicResponse> {
  return api.get<MasterPublicResponse>(`/api/v1/masters/${userId}`)
}

/**
 * Fetch paginated list of practices owned by the current master.
 * Only callable by users with role='master'.
 */
export function getMyPractices(limit = 20, offset = 0): Promise<PaginatedPracticesResponse> {
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
export function updatePayoutDetails(body: PayoutDetails): Promise<PayoutDetails> {
  return api.patch<PayoutDetails>('/api/v1/masters/me/payout', body)
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
export function getMyWithdrawals(limit = 20, offset = 0): Promise<PaginatedWithdrawalsResponse> {
  const query = buildQuery({ limit, offset })
  return api.get<PaginatedWithdrawalsResponse>(`/api/v1/masters/me/withdrawals${query}`)
}

// =============================================================================
// E5: Students / CRM endpoints
//   GET /api/v1/masters/me/students       -- paginated list (needs_attention)
//   GET /api/v1/masters/me/students/{id}  -- per-student aggregate
// =============================================================================

/**
 * Fetch the master's students — everyone who attended their practices.
 * Paginated; search is applied client-side over the loaded page.
 * Only callable by users with role='master'.
 */
export function getStudents(limit = 50, offset = 0): Promise<PaginatedStudentsResponse> {
  const query = buildQuery({ limit, offset })
  return api.get<PaginatedStudentsResponse>(`/api/v1/masters/me/students${query}`)
}

/**
 * Fetch one student's aggregate (practices_count, hours, satisfaction_pct,
 * recent check-ins and feedbacks) over THIS master's practices.
 * Note: the response carries no name/avatar — the calling list passes those.
 */
export function getStudent(id: string): Promise<StudentDetailResponse> {
  return api.get<StudentDetailResponse>(`/api/v1/masters/me/students/${id}`)
}

// =============================================================================
// E2: Finance — income (by period) + transaction feed
//   GET /api/v1/masters/me/income?period=week|month  -- gross booked turnover
//   GET /api/v1/masters/me/transactions              -- paginated ledger feed
// =============================================================================

/**
 * Fetch the master's gross booked turnover for the current calendar period
 * plus the previous-period total and the signed delta_pct (null when the
 * previous period had no net-positive turnover).
 */
export function getIncome(period: 'week' | 'month' = 'week'): Promise<IncomeResponse> {
  const query = buildQuery({ period })
  return api.get<IncomeResponse>(`/api/v1/masters/me/income${query}`)
}

/**
 * Fetch the master's transaction feed (title-tagged master_ledger rows,
 * newest first). amount_cents is signed: + sale, − commission/refund.
 */
export function getTransactions(limit = 20, offset = 0): Promise<PaginatedTransactionsResponse> {
  const query = buildQuery({ limit, offset })
  return api.get<PaginatedTransactionsResponse>(`/api/v1/masters/me/transactions${query}`)
}
