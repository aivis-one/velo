// =============================================================================
// VELO Frontend -- Admin API (Phase F8, updated F8-fix S-5)
// =============================================================================
//
// Typed wrappers for all admin endpoints.
// All types live in api/types.ts (S-5: consistent with project convention).
//
// ENDPOINTS:
//   GET  /api/v1/admin/stats
//   GET  /api/v1/admin/masters/pending
//   GET  /api/v1/admin/masters/list
//   GET  /api/v1/admin/masters/{id}          -- single master (W-1 fix)
//   POST /api/v1/admin/masters/{id}/verify
//   POST /api/v1/admin/masters/{id}/reject
//   GET  /api/v1/admin/reports
//   GET  /api/v1/admin/reports/{id}          -- single report (W-2 fix)
//   POST /api/v1/admin/reports/{id}/resolve
//   POST /api/v1/admin/reports/{id}/dismiss
//   GET  /api/v1/admin/consistency
// =============================================================================

import { api } from '@/api/client'
import { buildQuery } from '@/api/utils'
import type {
  AdminStatsResponse,
  AdminMasterListItem,
  PaginatedMastersResponse,
  AdminMasterActionResponse,
  ReportResponse,
  PaginatedReportsResponse,
  ReportStatusFilter,
  ReportTargetTypeFilter,
  ConsistencyResponse,
} from '@/api/types'

// Re-export for views that import from api/admin.ts directly.
export type {
  AdminStatsResponse,
  AdminMasterListItem,
  PaginatedMastersResponse,
  AdminMasterActionResponse,
  ReportResponse,
  PaginatedReportsResponse,
  ReportStatusFilter,
  ReportTargetTypeFilter,
  ConsistencyResponse,
  SemaphoreResult,
} from '@/api/types'

// ============================================================================
// Stats
// ============================================================================

export function getAdminStats(): Promise<AdminStatsResponse> {
  return api.get<AdminStatsResponse>('/api/v1/admin/stats')
}

// ============================================================================
// Masters
// ============================================================================

export function getPendingMasters(
  limit = 20,
  offset = 0,
): Promise<PaginatedMastersResponse> {
  const query = buildQuery({ limit, offset })
  return api.get<PaginatedMastersResponse>(`/api/v1/admin/masters/pending${query}`)
}

export function getMastersList(
  status?: 'pending' | 'verified' | 'rejected',
  limit = 100,
  offset = 0,
): Promise<PaginatedMastersResponse> {
  const query = buildQuery({ limit, offset, status })
  return api.get<PaginatedMastersResponse>(`/api/v1/admin/masters/list${query}`)
}

/**
 * Fetch a single master by user_id.
 * Fallback for AdminMasterReviewView when router state is unavailable.
 */
export function getMasterById(userId: string): Promise<AdminMasterListItem> {
  return api.get<AdminMasterListItem>(`/api/v1/admin/masters/${userId}`)
}

export function verifyMaster(userId: string): Promise<AdminMasterActionResponse> {
  return api.post<AdminMasterActionResponse>(
    `/api/v1/admin/masters/${userId}/verify`,
    {},
  )
}

export function rejectMaster(
  userId: string,
  reason: string,
): Promise<AdminMasterActionResponse> {
  return api.post<AdminMasterActionResponse>(
    `/api/v1/admin/masters/${userId}/reject`,
    { reason },
  )
}

// ============================================================================
// Reports
// ============================================================================

export function getReports(
  status?: ReportStatusFilter,
  target_type?: ReportTargetTypeFilter,
  limit = 20,
  offset = 0,
): Promise<PaginatedReportsResponse> {
  const query = buildQuery({ status, target_type, limit, offset })
  return api.get<PaginatedReportsResponse>(`/api/v1/admin/reports${query}`)
}

/**
 * Fetch a single report by id.
 * Fallback for AdminReportDetailView when router state is unavailable.
 */
export function getReportById(reportId: string): Promise<ReportResponse> {
  return api.get<ReportResponse>(`/api/v1/admin/reports/${reportId}`)
}

export function resolveReport(
  reportId: string,
  resolutionNote: string,
): Promise<ReportResponse> {
  return api.post<ReportResponse>(`/api/v1/admin/reports/${reportId}/resolve`, {
    resolution_note: resolutionNote,
  })
}

export function dismissReport(
  reportId: string,
  resolutionNote?: string,
): Promise<ReportResponse> {
  return api.post<ReportResponse>(`/api/v1/admin/reports/${reportId}/dismiss`, {
    resolution_note: resolutionNote ?? null,
  })
}

// ============================================================================
// Consistency semaphores
// ============================================================================

export function getConsistency(): Promise<ConsistencyResponse> {
  return api.get<ConsistencyResponse>('/api/v1/admin/consistency')
}
