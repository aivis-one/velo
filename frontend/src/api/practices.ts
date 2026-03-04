// =============================================================================
// VELO Frontend -- Practices API (Phase F3.1, updated F4.1)
// =============================================================================
//
// Typed wrappers over api.get() for practice endpoints.
//
// Backend endpoints:
//   GET /api/v1/practices          — public feed (scheduled + live)
//   GET /api/v1/practices/{id}     — single practice detail
//
// F4.1: buildQuery extracted to @/api/utils (shared with bookings.ts).
// =============================================================================

import { api } from '@/api/client'
import { buildQuery } from '@/api/utils'
import type {
  PaginatedPracticesResponse,
  PracticeFilters,
  PracticeResponse,
} from '@/api/types'

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
