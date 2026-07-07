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
  AdminMasterDetail,
  AdminMasterListItem,
  EditMasterMethodsRequest,
  AdminPracticeDetailResponse,
  AdminPracticeListItem,
  AdminRevenuePerMaster,
  AdminRevenueResponse,
  AdminRosterEntry,
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
  CheckinMetricResponse,
  CheckinRequest,
  CheckinResponse,
  ClaimMasterInviteRequest,
  ClaimMasterInviteResponse,
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
  FeedbackMetricResponse,
  FeedbackRatingDistribution,
  FeedbackRequest,
  FeedbackResponse,
  IncomeResponse,
  InviteMasterResponse,
  LowCheckinPractice,
  MasterApplyExperience,
  MasterApplyProfile,
  MasterApplyRequest,
  MasterApplyResponse,
  MasterProfileResponse,
  MasterPublicResponse,
  MasterReviewItem,
  MasterStatsResponse,
  MasterTransactionItem,
  MethodChangeActionResponse,
  MethodChangeRequest,
  MethodChangeRequestSubmit,
  MoodDistribution,
  PaginatedAdminPracticesResponse,
  PaginatedAdminWithdrawalsResponse,
  PaginatedBookingsResponse,
  PaginatedCheckinsResponse,
  PaginatedDiaryEntriesResponse,
  PaginatedFeedbacksResponse,
  PaginatedMasterReviewsResponse,
  PaginatedMastersResponse,
  PaginatedMethodChangeRequestsResponse,
  AdminMethodChangeItem,
  PaginatedPracticesResponse,
  PaginatedPromosResponse,
  PaginatedPurchasesResponse,
  PaginatedReportsResponse,
  PaginatedReviewsResponse,
  PaginatedStudentsResponse,
  PaginatedTransactionsResponse,
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
  RecurrenceSpec,
  RejectMasterRequest,
  RejectMethodChangeRequest,
  RejectWithdrawalRequest,
  ReportResponse,
  ResolveReportRequest,
  ReturnMetricResponse,
  ReviewItem,
  SeriesPoint,
  StudentCheckinItem,
  StudentDetailResponse,
  StudentFeedbackItem,
  StudentListItem,
  TelegramAuthRequest,
  TopUser,
  TopupRequest,
  TopupResponse,
  UpdateDiaryEntryRequest,
  UpdatePracticeRequest,
  UpdateReportRequest,
  MasterApplicationInfo,
  UserResponse,
  UserRole,
  UserStatsResponse,
  UserUpdate,
  VerifyMasterRequest,
  WaitlistConfirmResponse,
  WaitlistEntryResponse,
  WaitlistStatus,
  WaitlistWithPracticeResponse,
  WithdrawalResponse,
} from './generated'

// =============================================================================
// Frontend-only types (no backend counterpart)
// =============================================================================

// -- Role switch (capability-derived, №256) -----------------------------------
// Mirrors the backend UserResponse.role_switch block: null when there is
// nothing to switch to, otherwise the derived set (verified master ->
// user/master; admin -> all three). Kept here (not relying on generated.ts)
// because the frontend must typecheck locally BEFORE the server regenerates
// generated.ts on the next `velo update`. After regen the generated field is
// read structurally — no conflict, since this is a separate named type.
import type { UserRole } from './generated'

export interface RoleSwitchInfo {
  /** Roles this account may switch itself into. */
  allowed_roles: UserRole[]
}

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
// -> circles + style, migrate kundalini -> yoga + style=kundalini). The
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
// WaitlistStatus is re-exported from generated.ts (the backend is the source
// of truth: 'waiting' | 'notified' | 'converted' | 'left' | 'declined' |
// 'expired'). A stale hand-written copy used to live here with 'confirmed'
// instead of 'converted' -- removed to avoid shadowing the generated type.
//
// Mood / FeedbackRating are UI BUCKETS, not the raw backend value. On the
// backend a check-in mood and a feedback rating are each a 1..10 score; the
// frontend groups that score into three labelled buckets for the faces / glyphs
// (see MOOD_OPTIONS / RATING_OPTIONS in displayHelpers.ts, where each bucket
// carries its numeric `score`). These are intentionally frontend-only.
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

// Filter chips on the feed. Map 1:1 onto backend \`category\` query values
// (settings.diary_feed_categories). Omitting category = "Все".
export type DiaryFeedCategory = 'entries' | 'dreams' | 'feedbacks' | 'checkins' | 'practices'

// Query params for GET /api/v1/diary/feed (cursor pagination).
export interface DiaryFeedFilters {
  // Filter chips -> repeated \`category\` params. Empty/undefined = all.
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
  // F-8 (2026-05-29): style теперь multi-select chips, отправляется как массив
  // (как direction/difficulty). Backend B-4 принимает list[str] и фильтрует
  // через .in_().
  style?: string[]
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
