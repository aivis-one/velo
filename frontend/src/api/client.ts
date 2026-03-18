// =============================================================================
// VELO Frontend -- API Client (Phase F1.2, fixed 10.2, fixed CRITICAL-2)
// =============================================================================
//
// FIX 10.2: 401 handler delegates cleanup to auth store via
// onUnauthorized callback. No direct token/sessionStorage mutation.
// No window.location.href redirect -- Vue reactivity does it.
//
// FIX CRITICAL-2: AbortController + 15s timeout on every request.
// Timeout throws ApiTimeoutError. Network failure throws ApiNetworkError.
// =============================================================================

import type { ApiError } from './types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const REQUEST_TIMEOUT_MS = 15_000

// -- Error classes --

export class ApiResponseError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail)
    this.name = 'ApiResponseError'
  }
}

export class ApiNetworkError extends Error {
  constructor() {
    super('Network error -- check your connection')
    this.name = 'ApiNetworkError'
  }
}

export class ApiTimeoutError extends Error {
  constructor() {
    super(`Request timed out after ${REQUEST_TIMEOUT_MS / 1000}s`)
    this.name = 'ApiTimeoutError'
  }
}

// -- Token management (separate from Pinia to avoid circular imports) --

let _token: string | null = null

/** Called by auth store to set/clear the token. */
export function setAuthToken(token: string | null): void {
  _token = token
}

/** Called by auth store to read current token. */
export function getAuthToken(): string | null {
  return _token
}

// -- 401 callback (FIX 10.2) --

let _onUnauthorized: (() => void) | null = null

/**
 * Register a callback invoked on 401 responses.
 * Auth store calls this once at init to wire up _clearSession().
 */
export function setOnUnauthorized(cb: () => void): void {
  _onUnauthorized = cb
}

// -- Core request --

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const headers: Record<string, string> = {}

  if (_token) {
    headers['Authorization'] = `Bearer ${_token}`
  }

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response: Response

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
  } catch (e) {
    if (e instanceof DOMException && e.name === 'AbortError') {
      throw new ApiTimeoutError()
    }
    throw new ApiNetworkError()
  } finally {
    clearTimeout(timeoutId)
  }

  // 204 No Content (e.g. logout).
  if (response.status === 204) {
    return undefined as T
  }

  // 401 Unauthorized -- notify auth store, then throw.
  // FIX 10.2: no direct token/sessionStorage mutation here.
  if (response.status === 401) {
    _onUnauthorized?.()
    throw new ApiResponseError(401, 'Session expired')
  }

  let data: unknown
  try {
    data = await response.json()
  } catch {
    throw new ApiResponseError(response.status, 'Invalid response from server')
  }

  if (response.ok) {
    return data as T
  }

  // Extract error detail. Backend returns either a string (most errors)
  // or an array of validation objects (422). Normalise to string so
  // ApiResponseError.detail is always a string for consumers.
  const errorData = data as ApiError
  const rawDetail = errorData?.detail
  const detail =
    typeof rawDetail === 'string'
      ? rawDetail
      : Array.isArray(rawDetail)
        ? rawDetail.map((e) => e.msg).join('; ')
        : `Request failed (${response.status})`

  throw new ApiResponseError(response.status, detail)
}

// -- Public API --

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
