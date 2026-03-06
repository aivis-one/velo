// =============================================================================
// VELO Frontend -- Masters API (Phase F6)
// =============================================================================
//
// Typed wrappers over api.get/post for master endpoints.
//
// Backend endpoints:
//   POST /api/v1/masters/apply          -- submit application (role=user)
//   GET  /api/v1/masters/me             -- my master profile (role=master)
//   GET  /api/v1/masters/me/practices   -- my practices list (role=master)
// =============================================================================

import { api } from '@/api/client'
import { buildQuery } from '@/api/utils'
import type {
  MasterApplyRequest,
  MasterApplyResponse,
  MasterProfileResponse,
  PaginatedPracticesResponse,
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
