// =============================================================================
// VELO Frontend -- API Client (Phase F1.2, fixed 10.2)
// =============================================================================
//
// FIX 10.2: 401 handler clears token via setAuthToken + sessionStorage
// only. Auth store reactivity handles the rest (App.vue shows stub).
// No window.location.href redirect -- Vue reactivity does it.
// =============================================================================

import type { ApiError } from './types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

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

  // 401 Unauthorized -- just throw, let auth store handle cleanup.
  // FIX 10.2: no direct token/sessionStorage mutation here.
  if (response.status === 401) {
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

  const errorData = data as ApiError
  const detail = errorData?.detail || `Request failed (${response.status})`
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
