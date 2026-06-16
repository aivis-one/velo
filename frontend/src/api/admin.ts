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
//   GET  /api/v1/admin/metrics/check-in     -- engagement metric (E9)
//   GET  /api/v1/admin/metrics/feedback     -- engagement metric (E9)
//   GET  /api/v1/admin/metrics/return       -- engagement metric (E9)
//   GET  /api/v1/admin/practices            -- global practices list (E9)
//   GET  /api/v1/admin/practices/{id}       -- practice detail + roster (E9)
//   GET  /api/v1/admin/revenue              -- revenue/commission/payout (E9)
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
  AdminWithdrawalResponse,
  PaginatedAdminWithdrawalsResponse,
  WithdrawalStatus,
  CheckinMetricResponse,
  FeedbackMetricResponse,
  ReturnMetricResponse,
  PaginatedAdminPracticesResponse,
  AdminPracticeDetailResponse,
  AdminRevenueResponse,
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
  AdminWithdrawalResponse,
  PaginatedAdminWithdrawalsResponse,
  WithdrawalStatus,
  PayoutDetails,
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

export function getPendingMasters(limit = 20, offset = 0): Promise<PaginatedMastersResponse> {
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
  return api.post<AdminMasterActionResponse>(`/api/v1/admin/masters/${userId}/verify`, {})
}

export function rejectMaster(userId: string, reason: string): Promise<AdminMasterActionResponse> {
  return api.post<AdminMasterActionResponse>(`/api/v1/admin/masters/${userId}/reject`, { reason })
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

export function resolveReport(reportId: string, resolutionNote: string): Promise<ReportResponse> {
  return api.post<ReportResponse>(`/api/v1/admin/reports/${reportId}/resolve`, {
    resolution_note: resolutionNote,
  })
}

export function dismissReport(reportId: string, resolutionNote?: string): Promise<ReportResponse> {
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

// ============================================================================
// Withdrawals (payout approval)
// ============================================================================

export function getAdminWithdrawals(
  status?: WithdrawalStatus,
  limit = 20,
  offset = 0,
): Promise<PaginatedAdminWithdrawalsResponse> {
  const query = buildQuery({ limit, offset, status })
  return api.get<PaginatedAdminWithdrawalsResponse>(`/api/v1/admin/withdrawals${query}`)
}

export function approveWithdrawal(
  withdrawalId: string,
  note?: string,
): Promise<AdminWithdrawalResponse> {
  return api.post<AdminWithdrawalResponse>(`/api/v1/admin/withdrawals/${withdrawalId}/approve`, {
    note: note ?? null,
  })
}

export function rejectWithdrawal(
  withdrawalId: string,
  note: string,
): Promise<AdminWithdrawalResponse> {
  return api.post<AdminWithdrawalResponse>(`/api/v1/admin/withdrawals/${withdrawalId}/reject`, {
    note,
  })
}

// ============================================================================
// Engagement metrics (E9). Absolute values only — period-over-period deltas
// need E7 (not delivered), so the views leave the delta fields blank.
// ============================================================================

export function getCheckinMetric(): Promise<CheckinMetricResponse> {
  return api.get<CheckinMetricResponse>('/api/v1/admin/metrics/check-in')
}

export function getFeedbackMetric(): Promise<FeedbackMetricResponse> {
  return api.get<FeedbackMetricResponse>('/api/v1/admin/metrics/feedback')
}

export function getReturnMetric(): Promise<ReturnMetricResponse> {
  return api.get<ReturnMetricResponse>('/api/v1/admin/metrics/return')
}

// ============================================================================
// Oversight: practices (list + detail/roster) + revenue (E9)
// ============================================================================

/** Scope filter for the global practices list (backend: ?scope=). */
export type AdminPracticeScope = 'all' | 'upcoming' | 'past'

export function getAdminPractices(
  scope: AdminPracticeScope = 'all',
  limit = 20,
  offset = 0,
): Promise<PaginatedAdminPracticesResponse> {
  const query = buildQuery({ scope, limit, offset })
  return api.get<PaginatedAdminPracticesResponse>(`/api/v1/admin/practices${query}`)
}

export function getAdminPracticeDetail(id: string): Promise<AdminPracticeDetailResponse> {
  return api.get<AdminPracticeDetailResponse>(`/api/v1/admin/practices/${id}`)
}

/** Platform revenue/commission/payout + per-master breakdown for the period. */
export function getAdminRevenue(period: 'week' | 'month' = 'week'): Promise<AdminRevenueResponse> {
  const query = buildQuery({ period })
  return api.get<AdminRevenueResponse>(`/api/v1/admin/revenue${query}`)
}
