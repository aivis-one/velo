// =============================================================================
// VELO Frontend -- API Types (Phase F1.2 + F3.1 + F4.1)
// =============================================================================
//
// TypeScript interfaces matching backend Pydantic schemas.
// Manual typing (not auto-generated from OpenAPI).
//
// F3.1: PaginatedResponse fixed to limit/offset (matches backend).
//        Practice types added for catalog feature.
// F4.1: Booking, Purchase, and Preview types added for booking flow.
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

export type PracticeStatus = 'draft' | 'scheduled' | 'live' | 'completed' | 'cancelled' | 'deleted'

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

// -- Purchases (Phase F4.1) --

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
  status: string
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

// -- Errors --

// Backend returns string detail on most errors (400, 401, 403, 404, 409)
// and an array of validation objects on 422.
// client.ts normalises the array to a joined string before throwing.
export interface ApiError {
  detail: string | Array<{
    loc: (string | number)[]
    msg: string
    type: string
  }>
}
