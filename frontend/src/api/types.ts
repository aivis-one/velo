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
  DiaryFeedItem,
  DiaryFeedResponse,
  DismissReportRequest,
  ExistingReportResponse,
  FeedbackRequest,
  FeedbackResponse,
  MasterApplyExperience,
  MasterApplyProfile,
  MasterApplyRequest,
  MasterApplyResponse,
  MasterProfileResponse,
  MasterPublicResponse,
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
  PayoutDetails,
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

// -- Calendar taxonomy facets (match backend data.taxonomy values) --
// Mirror of settings.practice_allowed_directions in backend/app/core/config.py.
// Keep in sync when the backend list is extended.
//
// FRONT-FIRST (2026-05-28): the 10 keys below reflect the final taxonomy
// agreed with the operator. The backend currently accepts the OLD 8 keys
// (meditation/yoga/breathwork/somatic/tantra/womens_circle/mens_circle/
// kundalini); see handoff §9 task B-2 for the matching backend rollout
// (extend practice_allowed_directions, migrate womens_circle/mens_circle
// → circles + style, migrate kundalini → yoga + style=kundalini). The
// frontend commit MUST wait for the backend deploy.
export type PracticeDirection =
  | 'meditation'
  | 'yoga'
  | 'breathwork'
  | 'somatic'
  | 'tantra'
  | 'circles'
  | 'sound_healing'
  | 'art'
  | 'narrative'
  | 'movement'
export type PracticeDifficulty = 'beginner' | 'medium' | 'high'
// -- Calendar feed buckets (match backend filter literals) --
export type DurationBucket = 'short' | 'long'
export type TimeOfDay = 'night' | 'morning' | 'day' | 'evening'
export type BookingStatus = 'pending' | 'confirmed' | 'attended' | 'no_show' | 'cancelled'
export type PurchaseStatus = 'pending' | 'completed' | 'refunded' | 'failed'
export type MasterStatus = 'pending' | 'verified' | 'rejected'
export type AttendanceBookingStatus = 'pending' | 'confirmed' | 'attended' | 'no_show'
export type WithdrawalStatus = 'pending' | 'approved' | 'rejected'
export type WaitlistStatus = 'waiting' | 'notified' | 'confirmed' | 'left' | 'expired' | 'declined'
export type Mood = 'low' | 'mid' | 'high'
export type FeedbackRating = 'fire' | 'good' | 'confused'

// -- Diary feed (unified timeline) --
// Event kinds are a closed vocabulary on the backend (DiaryEventKind). We
// narrow the generated `DiaryFeedItem.kind: string` to this union at the
// rendering layer for exhaustive card mapping. Keep in sync with the backend
// enum -- regenerating types does NOT produce this (snapshot/kind stay open).
export type DiaryEventKind =
  | 'booking_confirmed'
  | 'booking_cancelled_by_user'
  | 'practice_rescheduled'
  | 'practice_cancelled_by_master'
  | 'practice_outcome'
  | 'checkin'
  | 'feedback'
  | 'note'
  | 'dream'

// Filter chips on the feed. Map 1:1 onto backend `category` query values
// (settings.diary_feed_categories). Omitting category = "Все".
export type DiaryFeedCategory =
  | 'entries'
  | 'dreams'
  | 'feedbacks'
  | 'checkins'
  | 'practices'

// Query params for GET /api/v1/diary/feed (cursor pagination).
export interface DiaryFeedFilters {
  // Filter chips -> repeated `category` params. Empty/undefined = all.
  categories?: DiaryFeedCategory[]
  date_from?: string
  date_to?: string
  search?: string
}

// -- Query / filter types (used by stores and API modules) -------------------

export interface PracticeFilters {
  // Multi-select: OR within the facet, sent as repeated query params.
  practice_type?: PracticeType[]
  // Calendar facets (all optional). Multi-select facets are arrays.
  direction?: PracticeDirection[]
  difficulty?: PracticeDifficulty[]
  style?: string
  duration_bucket?: DurationBucket
  time_of_day?: TimeOfDay
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
