// =============================================================================
// VELO Frontend -- API Types (Phase F1.2 + F3.1 + F4.1 + F6 + F7)
// =============================================================================
//
// TypeScript interfaces matching backend Pydantic schemas.
// Manual typing (not auto-generated from OpenAPI).
//
// F3.1: PaginatedResponse fixed to limit/offset (matches backend).
//        Practice types added for catalog feature.
// F4.1: Booking, Purchase, and Preview types added for booking flow.
// F5 review: W-28 -- PurchaseStatus union type (was string).
// F6: Master profile, apply flow, attendance, practice CRUD types.
// F7: PayoutDetails, WithdrawalStatus, WithdrawalResponse,
//     PaginatedWithdrawalsResponse. MasterProfileResponse + payout field.
// =============================================================================

// -- Auth --

export interface TelegramAuthRequest {
  init_data: string
}

export interface AuthResponse {
  user: UserResponse
  session_token: string
}

// -- Users --

export type UserRole = 'user' | 'master' | 'admin'

export interface UserResponse {
  id: string
  telegram_id: number | null
  role: UserRole
  first_name: string | null
  last_name: string | null
  avatar_url: string | null
  timezone: string
  language: string
  is_active: boolean
  balance_cents: number
  created_at: string
  last_login_at: string | null
}

export interface UserUpdate {
  first_name?: string | null
  last_name?: string | null
  timezone?: string
  language?: string
}

// -- Pagination --

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

// -- Practices --

export type PracticeType = 'live' | 'series' | 'one_on_one' | 'replay'

export type PracticeStatus =
  | 'draft'
  | 'scheduled'
  | 'live'
  | 'completed'
  | 'cancelled'
  | 'deleted'

export interface PracticeResponse {
  id: string
  master_id: string
  master_name: string | null
  practice_type: PracticeType
  status: PracticeStatus
  title: string
  description: string | null
  scheduled_at: string
  duration_minutes: number
  timezone: string
  max_participants: number | null
  current_participants: number
  zoom_link: string | null
  parent_practice_id: string | null
  is_free: boolean
  price_cents: number
  currency: string
  created_at: string
  updated_at: string | null
}

export type PaginatedPracticesResponse = PaginatedResponse<PracticeResponse>

// -- Practice filters (used by store and API module) --

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
  scheduled_at: string            // ISO 8601, must be in the future
  duration_minutes: number
  timezone: string                // IANA timezone, e.g. "Europe/Berlin"
  max_participants?: number | null
  zoom_link?: string | null
  parent_practice_id?: string | null
  is_free?: boolean
  price_cents?: number
  currency?: 'EUR'
}

// Only statuses reachable via state machine (backend _VALID_TRANSITIONS).
// "cancelled" is NOT here -- use cancelPractice() instead.
export type PracticeStatusTransition = 'scheduled' | 'live' | 'completed' | 'deleted'

export interface UpdatePracticeRequest {
  title?: string | null
  description?: string | null
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

// -- Bookings (Phase F4.1) --

export type BookingStatus = 'pending' | 'confirmed' | 'attended' | 'no_show' | 'cancelled'

/**
 * Compact practice representation embedded in booking/purchase responses.
 * Matches backend PracticeSummary schema.
 */
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

// -- Purchases (Phase F4.1, W-28 fix) --

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

// -- Masters (Phase F6.1, updated F7) --

export type MasterStatus = 'pending' | 'verified' | 'rejected'

/**
 * Payout configuration stored in MasterProfile.data.payout.
 * method determines which keys are expected in details:
 *   bank_transfer -> { iban, account_holder?, swift? }
 *   paypal        -> { email }
 *   revolut       -> { tag? } or { phone? }
 */
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
  /** F7: payout details. null until master configures via PATCH /me/payout. */
  payout: PayoutDetails | null
  created_at: string
  updated_at: string | null
}

// Step 1 of the 3-step apply form
export interface MasterApplyProfile {
  display_name: string
  email?: string | null
  phone?: string | null
}

// Step 2 of the 3-step apply form
export interface MasterApplyExperience {
  methods: string[]
  experience_years: number
  bio?: string | null
  certifications?: string[]
}

// Combined request sent as one POST to /api/v1/masters/apply
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

// -- Attendance (Phase F6.3) --

// Subset of BookingStatus relevant to attendance tracking
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

// -- Withdrawals (Phase F7) --

export type WithdrawalStatus = 'pending' | 'approved' | 'rejected'

export interface WithdrawalResponse {
  id: string
  user_id: string
  amount_cents: number
  /** Platform fee deducted from amount_cents on approval. */
  fee_cents: number
  currency: string
  status: WithdrawalStatus
  /** Snapshot of payout details at withdrawal creation time. */
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

// -- Errors --

// Backend returns string detail on most errors (400, 401, 403, 404, 409)
// and an array of validation objects on 422.
// client.ts normalises the array to a joined string before throwing.
export interface ApiError {
  detail:
    | string
    | Array<{
        loc: (string | number)[]
        msg: string
        type: string
      }>
}
