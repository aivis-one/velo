// =============================================================================
// VELO Frontend -- Practices API (Phase F3.1, updated F4.1, F6)
// =============================================================================
//
// Typed wrappers over api methods for practice endpoints.
//
// Public endpoints (role=any):
//   GET /api/v1/practices          -- public feed (scheduled + live)
//   GET /api/v1/practices/{id}     -- single practice detail
//
// Master endpoints (role=master):
//   POST   /api/v1/practices              -- create practice
//   PATCH  /api/v1/practices/{id}         -- edit / status transition
//   DELETE /api/v1/practices/{id}         -- soft-delete (draft only -> deleted)
//   POST   /api/v1/practices/{id}/cancel  -- cancel with full refund
//   POST   /api/v1/practices/{id}/finalize -- resolve attendance (live/scheduled -> completed)
//   GET    /api/v1/practices/{id}/attendance -- attendance list + aggregates
//   GET    /api/v1/practices/{id}/reviews    -- paginated named reviews (E1)
//
// F4.1: buildQuery extracted to @/api/utils (shared with bookings.ts).
// F6:   master CRUD methods added.
// E1:   getPracticeReviews -- de-anonymised named reviews.
// =============================================================================

import { api } from '@/api/client'
import { buildQuery } from '@/api/utils'
import type {
  PaginatedPracticesResponse,
  PracticeFilters,
  PracticeResponse,
  CreatePracticeRequest,
  UpdatePracticeRequest,
  AttendanceResponse,
  PaginatedReviewsResponse,
} from '@/api/types'

// ============================================================================
// Public
// ============================================================================

/**
 * Fetch paginated list of public practices.
 *
 * Maps PracticeFilters + pagination params to backend query params.
 * Backend uses `status` alias for the status filter query param.
 */
export function getPractices(
  filters: PracticeFilters = {},
  limit = 20,
  offset = 0,
): Promise<PaginatedPracticesResponse> {
  const query = buildQuery({
    limit,
    offset,
    practice_type: filters.practice_type,
    direction: filters.direction,
    difficulty: filters.difficulty,
    style: filters.style,
    duration_bucket: filters.duration_bucket,
    time_of_day: filters.time_of_day,
    status: filters.status,
    master_id: filters.master_id,
    date_from: filters.date_from,
    date_to: filters.date_to,
    sort_by: filters.sort_by,
    sort_order: filters.sort_order,
  })
  return api.get<PaginatedPracticesResponse>(`/api/v1/practices${query}`)
}

/**
 * Fetch a single practice by ID.
 */
export function getPractice(id: string): Promise<PracticeResponse> {
  return api.get<PracticeResponse>(`/api/v1/practices/${id}`)
}

// ============================================================================
// Master CRUD (role=master)
// ============================================================================

/**
 * Create a new practice (status defaults to 'draft' until published).
 *
 * Backend state machine: draft -> scheduled (via PATCH status='scheduled').
 * scheduled_at must be a future UTC ISO 8601 string.
 */
export function createPractice(body: CreatePracticeRequest): Promise<PracticeResponse> {
  return api.post<PracticeResponse>('/api/v1/practices', body)
}

/**
 * Edit practice fields and/or trigger a status transition.
 *
 * Status transitions allowed via PATCH:
 *   draft       -> scheduled (publish)
 *   scheduled   -> live      (start)
 *   live        -> completed (end)
 *
 * "cancelled" is NOT reachable here -- use cancelPractice() instead.
 * "deleted"   -> use deletePractice() (soft-delete, draft only).
 */
export function updatePractice(id: string, body: UpdatePracticeRequest): Promise<PracticeResponse> {
  return api.patch<PracticeResponse>(`/api/v1/practices/${id}`, body)
}

/**
 * Soft-delete a practice (draft only -> status=deleted).
 * Returns 204 No Content on success.
 */
export function deletePractice(id: string): Promise<void> {
  return api.delete(`/api/v1/practices/${id}`)
}

/**
 * Cancel a practice with full refund to all participants.
 *
 * Allowed statuses: scheduled, live -> cancelled.
 * Backend triggers refund for all confirmed bookings atomically.
 */
export function cancelPractice(id: string): Promise<PracticeResponse> {
  return api.post<PracticeResponse>(`/api/v1/practices/${id}/cancel`)
}

/**
 * Finalize a practice: resolve attendance, release frozen funds.
 *
 * Allowed statuses: live, scheduled -> completed.
 * Should be called by master after the session ends.
 */
export function finalizePractice(id: string): Promise<PracticeResponse> {
  return api.post<PracticeResponse>(`/api/v1/practices/${id}/finalize`)
}

/**
 * Fetch attendance list and aggregates for a specific practice.
 *
 * Returns total, attended, no_show, pending counts + per-booking items.
 */
export function getAttendance(id: string): Promise<AttendanceResponse> {
  return api.get<AttendanceResponse>(`/api/v1/practices/${id}/attendance`)
}

/**
 * Fetch paginated named reviews for a practice (E1).
 *
 * The de-anonymised counterpart to the anonymous rating distribution: each
 * item carries the reviewer's name, avatar and comment. `rating` arrives
 * pre-mapped to the three UI buckets ('fire' | 'good' | 'confused') by the
 * backend, so the frontend reuses the same rating icons/labels it already
 * renders for the anonymous distribution.
 */
export function getPracticeReviews(
  id: string,
  limit = 20,
  offset = 0,
): Promise<PaginatedReviewsResponse> {
  const query = buildQuery({ limit, offset })
  return api.get<PaginatedReviewsResponse>(`/api/v1/practices/${id}/reviews${query}`)
}
