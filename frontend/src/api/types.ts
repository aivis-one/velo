// =============================================================================
// VELO Frontend -- API Types
// =============================================================================
//
// Single import point for all API types. Combines:
//   1. Auto-generated types from backend OpenAPI (generated.ts)
//   2. Frontend-only types (filters, UI unions, error shapes)
//
// CONSUMERS: always import from '@/api/types', never from '@/api/generated'.
// BACKEND TYPES: do NOT add manually — they come from generated.ts.
// Run `make gen-types` after changing any Pydantic schema.
// =============================================================================

// -- Re-export everything from generated backend types -----------------------

export type {
  AISummaryResponse,
  AdminMasterActionResponse,
  AdminMasterListItem,
  AdminStatsResponse,
  AdminWithdrawalResponse,
  ApproveWithdrawalRequest,
  AttendanceItemResponse,
  AttendanceResponse,
  AuthResponse,
  BookingDetailResponse,
  BookingResponse,
  BookingWithPracticeResponse,
  CancelBookingRequest,
  CheckinRequest,
  CheckinResponse,
  ConsistencyResponse,
  CreateBookingRequest,
  CreateCompanyPromoRequest,
  CreateDiaryEntryRequest,
  CreateMasterPromoRequest,
  CreatePracticeRequest,
  CreateReportRequest,
  CreateWithdrawalRequest,
  DiaryEntryResponse,
  DismissReportRequest,
  ExistingReportResponse,
  FeedbackRequest,
  FeedbackResponse,
  MasterApplyExperience,
  MasterApplyProfile,
  MasterApplyRequest,
  MasterApplyResponse,
  MasterProfileResponse,
  MoodDistribution,
  PaginatedAdminWithdrawalsResponse,
  PaginatedBookingsResponse,
  PaginatedCheckinsResponse,
  PaginatedDiaryEntriesResponse,
  PaginatedFeedbacksResponse,
  PaginatedMastersResponse,
  PaginatedPracticesResponse,
  PaginatedPromosResponse,
  PaginatedPurchasesResponse,
  PaginatedReportsResponse,
  PaginatedUserReportsResponse,
  PaginatedUsersResponse,
  PaginatedWaitlistResponse,
  PaginatedWithdrawalsResponse,
  PayoutDetailsResponse,
  PayoutDetailsUpdate,
  PracticeInsightsResponse,
  PracticeResponse,
  PracticeSummary,
  PreviewPurchaseRequest,
  PreviewPurchaseResponse,
  PromoResponse,
  PurchaseRequest,
  PurchaseResponse,
  PurchaseWithPracticeResponse,
  RatingDistribution,
  RejectMasterRequest,
  RejectWithdrawalRequest,
  ReportResponse,
  ResolveReportRequest,
  SemaphoreResult,
  TelegramAuthRequest,
  TopupRequest,
  TopupResponse,
  UpdateDiaryEntryRequest,
  UpdatePracticeRequest,
  UpdateReportRequest,
  UserResponse,
  UserRole,
  UserUpdate,
  VerifyMasterRequest,
  WaitlistConfirmResponse,
  WaitlistEntryResponse,
  WaitlistWithPracticeResponse,
  WithdrawalResponse,
} from './generated'

// =============================================================================
// Frontend-only types (no backend counterpart)
// =============================================================================

// -- API error shape (matches VeloError + Pydantic 422 formats) --------------

export interface ApiError {
  /** Machine-readable error code ("bad_request", "not_found", etc.) */
  error?: string
  /** Human-readable message (VeloError format). */
  message?: string
  /** Pydantic validation error details (422 only). */
  detail?:
    | string
    | Array<{
        loc: (string | number)[]
        msg: string
        type: string
      }>
}

// -- UI union types (narrower than backend str for type safety) --------------

export type PracticeType = 'live' | 'series' | 'one_on_one' | 'replay'
export type PracticeStatus = 'draft' | 'scheduled' | 'live' | 'completed' | 'cancelled' | 'deleted'
export type PracticeStatusTransition = 'scheduled' | 'live' | 'completed' | 'deleted'
export type BookingStatus = 'pending' | 'confirmed' | 'attended' | 'no_show' | 'cancelled'
export type PurchaseStatus = 'pending' | 'completed' | 'refunded' | 'failed'
export type MasterStatus = 'pending' | 'verified' | 'rejected'
export type AttendanceBookingStatus = 'pending' | 'confirmed' | 'attended' | 'no_show'
export type WithdrawalStatus = 'pending' | 'approved' | 'rejected'
export type WaitlistStatus = 'waiting' | 'notified' | 'confirmed' | 'left' | 'expired' | 'declined'
export type Mood = 'low' | 'mid' | 'high'
export type FeedbackRating = 'fire' | 'good' | 'confused'

// -- Query / filter types (used by stores and API modules) -------------------

export interface PracticeFilters {
  practice_type?: PracticeType
  status?: 'scheduled' | 'live'
  master_id?: string
  date_from?: string
  date_to?: string
  sort_by?: 'scheduled_at' | 'price_cents'
  sort_order?: 'asc' | 'desc'
}

export type ReportStatusFilter = 'pending' | 'resolved' | 'dismissed'
export type ReportTargetTypeFilter = 'user' | 'master' | 'practice'

// -- Convenience re-export for generic paginated response -------------------

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

// -- Promo request (unified for master and admin UI) ------------------------

export interface CreatePromoRequest {
  code: string
  discount_percent: number
  max_uses?: number | null
  practice_id?: string | null
  valid_from?: string | null
  valid_until?: string | null
  first_purchase_only?: boolean
}
