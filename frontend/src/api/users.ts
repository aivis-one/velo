// =============================================================================
// VELO Frontend -- Users API
// =============================================================================
//
// Typed wrappers over api.get/patch for the current-user profile endpoints.
//
// Backend endpoints:
//   GET   /api/v1/users/me  -- current user profile
//   PATCH /api/v1/users/me  -- partial profile update
//
// UserResponse / UserUpdate are generated from the backend OpenAPI schema
// (see api/generated.ts, refreshed on `velo update` / `velo gen-types`).
// onboarding_completed is part of both: it lives in the credentials JSONB
// on the backend but is surfaced as a plain bool on UserResponse and is
// settable via UserUpdate.
// =============================================================================

import { api } from '@/api/client'
import type { UserResponse, UserUpdate } from '@/api/types'

/**
 * Fetch the authenticated user's profile.
 */
export function getMe(): Promise<UserResponse> {
  return api.get<UserResponse>('/api/v1/users/me')
}

/**
 * Partially update the authenticated user's profile.
 * Only the fields present in `body` are changed.
 *
 * Used by the profile screen and by the welcome onboarding flow
 * (which sends { timezone, onboarding_completed: true } on completion).
 */
export function updateMe(body: UserUpdate): Promise<UserResponse> {
  return api.patch<UserResponse>('/api/v1/users/me', body)
}
