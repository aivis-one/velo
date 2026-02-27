// =============================================================================
// VELO Frontend -- API Types (Phase F1.2, username fix)
// =============================================================================
//
// TypeScript interfaces matching backend Pydantic schemas.
// Manual typing (not auto-generated from OpenAPI).
//
// USERNAME FIX: backend UserResponse has no `username` field.
// telegram_username is stored in credentials JSONB, not exposed.
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
  page: number
  per_page: number
  pages: number
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
