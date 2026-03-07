// =============================================================================
// VELO Frontend -- Admin API (Phase F8)
// =============================================================================
//
// Typed wrappers for all admin endpoints:
//   GET  /api/v1/admin/stats                      -- platform statistics
//   GET  /api/v1/admin/masters/pending             -- pending applications list
//   GET  /api/v1/admin/masters/list                -- all masters with filter
//   POST /api/v1/admin/masters/{id}/verify         -- approve application
//   POST /api/v1/admin/masters/{id}/reject         -- reject application
//   GET  /api/v1/admin/reports                     -- reports list with filters
//   POST /api/v1/admin/reports/{id}/resolve        -- resolve report
//   POST /api/v1/admin/reports/{id}/dismiss        -- dismiss report
//   GET  /api/v1/admin/consistency                 -- data consistency semaphores
// =============================================================================

import { api } from '@/api/client'
import { buildQuery } from '@/api/utils'

// ============================================================================
// Types
// ============================================================================

export interface AdminStatsResponse {
  users_count: number
  masters_count: number
  practices_count: number
  pending_verifications: number
}

// Item returned by /admin/masters/pending and /admin/masters/list.
// Contains only User + master_status -- no JSONB profile data.
export interface AdminMasterListItem {
  id: string
  telegram_id: number | null
  first_name: string | null
  last_name: string | null
  avatar_url: string | null
  role: string
  is_active: boolean
  master_status: 'pending' | 'verified' | 'rejected'
}

export interface PaginatedMastersResponse {
  items: AdminMasterListItem[]
  total: number
  limit: number
  offset: number
}

export interface AdminMasterActionResponse {
  user_id: string
  status: string
}

// Report item -- same schema used by user-facing and admin endpoints.
export interface ReportResponse {
  id: string
  reporter_id: string
  target_type: 'user' | 'master' | 'practice'
  target_id: string
  reason: string
  status: 'pending' | 'resolved' | 'dismissed'
  resolved_by: string | null
  resolution_note: string | null
  resolved_at: string | null
  created_at: string
  updated_at: string | null
}

export interface PaginatedReportsResponse {
  items: ReportResponse[]
  total: number
  limit: number
  offset: number
}

// Single semaphore check result.
export interface SemaphoreResult {
  name: string
  category: string
  status: 'OK' | 'ALERT'
  expected: string
  actual: string
  details: Record<string, unknown> | null
  criticality: 'critical' | 'warning' | 'info'
}

export interface ConsistencyResponse {
  items: SemaphoreResult[]
  total: number
  ok_count: number
  alert_count: number
  run_at: string
}

// ============================================================================
// Stats
// ============================================================================

/**
 * Fetch platform-wide statistics for admin dashboard.
 */
export function getAdminStats(): Promise<AdminStatsResponse> {
  return api.get<AdminStatsResponse>('/api/v1/admin/stats')
}

// ============================================================================
// Masters
// ============================================================================

/**
 * Fetch pending master applications (shortcut endpoint).
 */
export function getPendingMasters(
  limit = 20,
  offset = 0,
): Promise<PaginatedMastersResponse> {
  const query = buildQuery({ limit, offset })
  return api.get<PaginatedMastersResponse>(`/api/v1/admin/masters/pending${query}`)
}

/**
 * Fetch masters list with optional status filter.
 * Used as fallback fetch in AdminMasterReviewView when router state is missing.
 */
export function getMastersList(
  status?: 'pending' | 'verified' | 'rejected',
  limit = 100,
  offset = 0,
): Promise<PaginatedMastersResponse> {
  const query = buildQuery({ limit, offset, status })
  return api.get<PaginatedMastersResponse>(`/api/v1/admin/masters/list${query}`)
}

/**
 * Approve a pending master application.
 * Promotes user role to 'master' and sets profile status to 'verified'.
 */
export function verifyMaster(userId: string): Promise<AdminMasterActionResponse> {
  return api.post<AdminMasterActionResponse>(
    `/api/v1/admin/masters/${userId}/verify`,
    {},
  )
}

/**
 * Reject a pending master application.
 * User keeps role='user' and can reapply later.
 */
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

export type ReportStatusFilter = 'pending' | 'resolved' | 'dismissed'
export type ReportTargetTypeFilter = 'user' | 'master' | 'practice'

/**
 * Fetch reports list with optional filters and pagination.
 */
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
 * Resolve a pending report with a required resolution note.
 */
export function resolveReport(
  reportId: string,
  resolutionNote: string,
): Promise<ReportResponse> {
  return api.post<ReportResponse>(`/api/v1/admin/reports/${reportId}/resolve`, {
    resolution_note: resolutionNote,
  })
}

/**
 * Dismiss a pending report. Resolution note is optional.
 */
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

/**
 * Run all 21 data consistency semaphores and return results.
 * Read-only -- safe to run in production at any time.
 */
export function getConsistency(): Promise<ConsistencyResponse> {
  return api.get<ConsistencyResponse>('/api/v1/admin/consistency')
}
