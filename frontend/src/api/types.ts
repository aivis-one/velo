// =============================================================================
// VELO Frontend -- API Types (Phase F1.2 + F3.1)
// =============================================================================
//
// TypeScript interfaces matching backend Pydantic schemas.
// Manual typing (not auto-generated from OpenAPI).
//
// F3.1: PaginatedResponse fixed to limit/offset (matches backend).
//        Practice types added for catalog feature.
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
