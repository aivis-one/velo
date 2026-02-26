// =============================================================================
// VELO Frontend -- API Types (Phase F1.2)
// =============================================================================
//
// TypeScript interfaces that mirror backend Pydantic schemas.
// Manual typings (not OpenAPI codegen) -- see Frontend Spec section 3.2.
//
// Populated incrementally as frontend phases are implemented.
// Phase F1: auth + user basics.
// =============================================================================

// -- Auth (Phase 1.2 backend) --

export interface TelegramAuthRequest {
  init_data: string
}

export interface AuthResponse {
  user: UserResponse
  session_token: string
}

// -- Users (Phase 1.4 backend) --

export interface UserResponse {
  id: string
  telegram_id: number | null
  role: 'user' | 'master' | 'admin'
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
  first_name?: string
  last_name?: string | null
  language?: string
  timezone?: string
}

// -- Generic paginated response (reused across modules) --

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

// -- API error shape (matches FastAPI/Pydantic error responses) --

export interface ApiValidationError {
  detail: Array<{
    loc: (string | number)[]
    msg: string
    type: string
  }>
}

export interface ApiError {
  detail: string
}
