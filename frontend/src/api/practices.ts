// =============================================================================
// VELO Frontend -- Practices API (Phase F3.1)
// =============================================================================
//
// Typed wrappers over api.get() for practice endpoints.
//
// Backend endpoints:
//   GET /api/v1/practices          — public feed (scheduled + live)
//   GET /api/v1/practices/{id}     — single practice detail
//
// Query params are built manually because api.get() accepts only a
// path string (no params object). buildQuery() strips undefined values.
// =============================================================================

import { api } from '@/api/client'
import type {
  PaginatedPracticesResponse,
  PracticeFilters,
  PracticeResponse,
} from '@/api/types'

/**
 * Build query string from an object, skipping undefined/null values.
 */
function buildQuery(params: Record<string, string | number | undefined | null>): string {
  const entries = Object.entries(params).filter(
    (entry): entry is [string, string | number] =>
      entry[1] !== undefined && entry[1] !== null,
  )
  if (entries.length === 0) return ''
  const qs = new URLSearchParams(
    entries.map(([k, v]) => [k, String(v)]),
  )
  return `?${qs.toString()}`
}

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
