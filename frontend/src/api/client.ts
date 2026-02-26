// =============================================================================
// VELO Frontend -- API Client (Phase F1.2)
// =============================================================================
//
// Typed wrapper around fetch() for communicating with the FastAPI backend.
//
// FEATURES:
//   - Base URL from env (FP-01: no hardcoded URLs)
//   - Auto Bearer token injection from auth store
//   - 401 handling: clear session, redirect to login
//   - 422 handling: parse Pydantic validation errors
//   - Network error handling: throw with readable message
//   - Typed generics: api.get<UserResponse>('/users/me')
//
// USAGE:
//   import { api } from '@/api/client'
//   const user = await api.get<UserResponse>('/api/v1/users/me')
//   await api.post<AuthResponse>('/api/v1/auth/telegram', { init_data })
//   await api.patch('/api/v1/users/me', { first_name: 'New' })
//   await api.delete('/api/v1/auth/logout')
// =============================================================================

import type { ApiError } from './types'

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/**
 * Base URL for all API requests.
 * In production: '' (same origin -- Nginx routes /api/* to backend).
 * In dev: Vite proxy handles /api/* -> localhost:8000.
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// ---------------------------------------------------------------------------
// Error classes
// ---------------------------------------------------------------------------

/** API returned an error response (4xx, 5xx). */
export class ApiResponseError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail)
    this.name = 'ApiResponseError'
  }
}

/** Network error (no connection, timeout, DNS failure). */
export class ApiNetworkError extends Error {
  constructor() {
    super('Network error -- check your connection')
    this.name = 'ApiNetworkError'
  }
}

// ---------------------------------------------------------------------------
// Token management
// ---------------------------------------------------------------------------

// Token is stored here (set by auth store after login).
// Separate from Pinia to avoid circular imports (client <- store <- client).
let _token: string | null = null

/** Called by auth store to set/clear the token. */
export function setAuthToken(token: string | null): void {
  _token = token
}

/** Called by auth store to read current token. */
export function getAuthToken(): string | null {
  return _token
}

// ---------------------------------------------------------------------------
// Core request function
// ---------------------------------------------------------------------------

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const headers: Record<string, string> = {}

  // Inject Bearer token if available.
  if (_token) {
    headers['Authorization'] = `Bearer ${_token}`
  }

  // Set Content-Type for requests with body.
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }

  let response: Response

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiNetworkError()
  }

  // 204 No Content (e.g. logout).
  if (response.status === 204) {
    return undefined as T
  }

  // 401 Unauthorized -- session expired or invalid.
  if (response.status === 401) {
    _token = null
    sessionStorage.removeItem('velo_token')
    // Redirect to root (auth guard will handle the rest).
    window.location.href = '/'
    throw new ApiResponseError(401, 'Session expired')
  }

  // Parse response body.
  let data: unknown
  try {
    data = await response.json()
  } catch {
    throw new ApiResponseError(response.status, 'Invalid response from server')
  }

  // Success.
  if (response.ok) {
    return data as T
  }

  // Error response -- extract detail message.
  const errorData = data as ApiError
  const detail = errorData?.detail || `Request failed (${response.status})`
  throw new ApiResponseError(response.status, detail)
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export const api = {
  get<T>(path: string): Promise<T> {
    return request<T>('GET', path)
  },

  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>('POST', path, body)
  },

  patch<T>(path: string, body?: unknown): Promise<T> {
    return request<T>('PATCH', path, body)
  },

  delete(path: string): Promise<void> {
    return request<void>('DELETE', path)
  },
}
