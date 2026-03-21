// F-03: Updated ApiError to match real backend response format.
// Backend VeloErrors return: { error: string, message: string }
// Pydantic 422 returns:      { detail: string | Array<{loc, msg, type}> }
// Previously only `detail` was declared, causing all non-422 errors to produce
// "Request failed (NNN)" instead of the actual backend message.

export interface ApiError {
  /** Machine-readable error code (VeloError format: "bad_request", "not_found", etc.) */
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

// =============================================================================
// Auth
// =============================================================================

export interface AuthResponse {
  session_token: string
  user: UserResponse
}

export type UserRole = 'user' | 'master' | 'admin'

export interface UserResponse {
  id: string
  telegram_id: number | null
  first_name: string | null
  last_name: string | null
  username: string | null
  avatar_url: string | null
  role: UserRole
  is_active: boolean
  balance_cents: number
  timezone: string | null
  language_code: string | null
  created_at: string
  updated_at: string | null
}

export interface UpdateUserRequest {
  first_name?: string | null
  last_name?: string | null
  timezone?: string | null
}

// =============================================================================
// Practices
// =============================================================================

export type PracticeType = 'live' | 'series' | 'one_on_one' | 'replay'
export type PracticeStatus = 'draft' | 'scheduled' | 'live' | 'completed' | 'cancelled' | 'deleted'

export interface PracticeResponse {
  id: string
  master_id: string
  master_name: string | null
  master_methods: string[]
  practice_type: PracticeType
  title: string
  description: string | null
  what_to_prepare: string | null
  contraindications: string | null
  scheduled_at: string
  duration_minutes: number
  timezone: string
  max_participants: number | null
  current_participants: number
  zoom_link: string | null
  is_free: boolean
  price_cents: number
  currency: string
  status: PracticeStatus
  created_at: string
  updated_at: string | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export type PaginatedPracticesResponse = PaginatedResponse<PracticeResponse>

export interface PracticeFilters {
  practice_type?: PracticeType
  status?: 'scheduled' | 'live'
  master_id?: string
  date_from?: string
  date_to?: string
  sort_by?: 'scheduled_at' | 'price_cents'
  sort_order?: 'asc' | 'desc'
}

// -- Practice CRUD requests (Phase F6.2) --

export interface CreatePracticeRequest {
  practice_type: PracticeType
  title: string
  description?: string | null
  what_to_prepare?: string | null
  contraindications?: string | null
  scheduled_at: string
  duration_minutes: number
  timezone: string
  max_participants?: number | null
  zoom_link?: string | null
  parent_practice_id?: string | null
  is_free?: boolean
  price_cents?: number
  currency?: 'EUR'
}

export type PracticeStatusTransition = 'scheduled' | 'live' | 'completed' | 'deleted'

export interface UpdatePracticeRequest {
  title?: string | null
  description?: string | null
  what_to_prepare?: string | null
  contraindications?: string | null
  scheduled_at?: string | null
  duration_minutes?: number | null
  timezone?: string | null
  max_participants?: number | null
  zoom_link?: string | null
  status?: PracticeStatusTransition | null
  is_free?: boolean | null
  price_cents?: number | null
  currency?: 'EUR' | null
}

// =============================================================================
// Bookings
// =============================================================================

export type BookingStatus = 'pending' | 'confirmed' | 'attended' | 'no_show' | 'cancelled'

export interface PracticeSummary {
  id: string
  title: string
  practice_type: PracticeType
  scheduled_at: string
  duration_minutes: number
  master_id: string
  master_name: string | null
}

export interface BookingWithPracticeResponse {
  id: string
  practice_id: string
  user_id: string
  status: BookingStatus
  purchase_id: string | null
  cancelled_at: string | null
  cancellation_reason: string | null
  joined_at: string | null
  left_at: string | null
  created_at: string
  updated_at: string | null
  practice: PracticeSummary
}

export type PaginatedBookingsResponse = PaginatedResponse<BookingWithPracticeResponse>

// =============================================================================
// Purchases
// =============================================================================

export type PurchaseStatus = 'pending' | 'completed' | 'refunded' | 'failed'

export interface PurchaseResponse {
  id: string
  user_id: string
  practice_id: string
  booking_id: string
  promo_id: string | null
  amount_cents: number
  discount_cents: number
  paid_cents: number
  currency: string
  commission_cents: number
  status: PurchaseStatus
  completed_at: string | null
  created_at: string
  updated_at: string | null
}

export interface PreviewPurchaseResponse {
  practice_id: string
  amount_cents: number
  discount_cents: number
  paid_cents: number
  currency: string
  promo_code: string | null
  promo_type: string | null
  discount_percent: number | null
}

// =============================================================================
// Masters
// =============================================================================

export type MasterStatus = 'pending' | 'verified' | 'rejected'

export interface PayoutDetails {
  method: string
  details: Record<string, unknown>
}

export interface MasterProfileResponse {
  user_id: string
  status: MasterStatus
  display_name: string | null
  bio: string | null
  methods: string[]
  experience_years: number | null
  frozen_cents: number
  available_cents: number
  /** null until master configures via PATCH /me/payout. */
  payout: PayoutDetails | null
  created_at: string
  updated_at: string | null
}

export interface MasterApplyProfile {
  display_name: string
  email?: string | null
  phone?: string | null
}

export interface MasterApplyExperience {
  methods: string[]
  experience_years: number
  bio?: string | null
  certifications?: string[]
}

export interface MasterApplyRequest {
  profile: MasterApplyProfile
  experience: MasterApplyExperience
  documents?: Record<string, unknown>[]
}

export interface MasterApplyResponse {
  user_id: string
  status: MasterStatus
  created_at: string
}

// =============================================================================
// Attendance
// =============================================================================

export type AttendanceBookingStatus = 'pending' | 'confirmed' | 'attended' | 'no_show'

export interface AttendanceItemResponse {
  booking_id: string
  user_id: string
  status: AttendanceBookingStatus
  joined_at: string | null
  left_at: string | null
}

export interface AttendanceResponse {
  practice_id: string
  total: number
  attended: number
  no_show: number
  pending: number
  items: AttendanceItemResponse[]
}

// =============================================================================
// Withdrawals
// =============================================================================

export type WithdrawalStatus = 'pending' | 'approved' | 'rejected'

export interface WithdrawalResponse {
  id: string
  user_id: string
  amount_cents: number
  fee_cents: number
  currency: string
  status: WithdrawalStatus
  payout_details: PayoutDetails
  admin_id: string | null
  admin_note: string | null
  approved_at: string | null
  rejected_at: string | null
  created_at: string
  updated_at: string | null
}

export interface PaginatedWithdrawalsResponse {
  items: WithdrawalResponse[]
  total: number
  limit: number
  offset: number
}

// =============================================================================
// Admin
// =============================================================================

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

export interface AdminStatsResponse {
  users_count: number
  masters_count: number
  practices_count: number
  pending_verifications: number
}

export interface AdminMasterActionResponse {
  user_id: string
  status: string
}

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

export type ReportStatusFilter = 'pending' | 'resolved' | 'dismissed'
export type ReportTargetTypeFilter = 'user' | 'master' | 'practice'

// =============================================================================
// Diary / Check-in / Feedback / Insights (Phase F9)
// =============================================================================

export type Mood = 'low' | 'mid' | 'high'

export interface CheckinRequest {
  mood: Mood
  comment?: string | null
}

export interface CheckinResponse {
  id: string
  practice_id: string
  user_id: string
  booking_id: string
  mood: Mood
  comment: string | null
  check_type: string
  created_at: string
  updated_at: string | null
}

export interface PaginatedCheckinsResponse {
  items: CheckinResponse[]
  total: number
  limit: number
  offset: number
}

export type FeedbackRating = 'fire' | 'good' | 'confused'

export interface FeedbackRequest {
  rating: FeedbackRating
  comment?: string | null
}

export interface FeedbackResponse {
  id: string
  practice_id: string
  user_id: string
  booking_id: string
  rating: FeedbackRating
  comment: string | null
  created_at: string
  updated_at: string | null
}

export interface PaginatedFeedbacksResponse {
  items: FeedbackResponse[]
  total: number
  limit: number
  offset: number
}

export interface CreateDiaryEntryRequest {
  content: string
  title?: string | null
  mood?: Mood | null
  practice_id?: string | null
}

export interface UpdateDiaryEntryRequest {
  content?: string | null
  title?: string | null
  mood?: Mood | null
  practice_id?: string | null
  clear_mood?: boolean
  clear_title?: boolean
  clear_practice?: boolean
}

export interface DiaryEntryResponse {
  id: string
  user_id: string
  practice_id: string | null
  title: string | null
  content: string
  mood: Mood | null
  created_at: string
  updated_at: string | null
}

export interface PaginatedDiaryEntriesResponse {
  items: DiaryEntryResponse[]
  total: number
  limit: number
  offset: number
}

export interface MoodDistribution {
  high: number
  mid: number
  low: number
}

export interface RatingDistribution {
  fire: number
  good: number
  confused: number
}

export interface PracticeInsightsResponse {
  practice_id: string
  participants: number
  checkins: MoodDistribution
  feedbacks: RatingDistribution
  comments_count: number
}

// =============================================================================
// Waitlist
// =============================================================================

export type WaitlistStatus = 'waiting' | 'notified' | 'confirmed' | 'left' | 'expired' | 'declined'

export interface WaitlistEntryResponse {
  id: string
  practice_id: string
  user_id: string
  position: number
  status: WaitlistStatus
  joined_at: string
  notified_at: string | null
  expires_at: string | null
  created_at: string
  updated_at: string | null
}

export interface WaitlistWithPracticeResponse extends WaitlistEntryResponse {
  practice: PracticeSummary
}

export interface PaginatedWaitlistResponse {
  items: WaitlistWithPracticeResponse[]
  total: number
  limit: number
  offset: number
}

// =============================================================================
// Promos
// =============================================================================

export interface PromoResponse {
  id: string
  code: string
  type: 'company' | 'master'
  master_id: string | null
  practice_id: string | null
  discount_percent: number
  max_uses: number | null
  used_count: number
  is_active: boolean
  first_purchase_only: boolean
  valid_from: string | null
  valid_until: string | null
  created_at: string
  updated_at: string | null
}

export interface CreatePromoRequest {
  code: string
  discount_percent: number
  max_uses?: number | null
  practice_id?: string | null
  valid_from?: string | null
  valid_until?: string | null
  first_purchase_only?: boolean
}

export interface PaginatedPromosResponse {
  items: PromoResponse[]
  total: number
  limit: number
  offset: number
}
