// =============================================================================
// VELO Frontend -- Promos API (E10 -- wire the delivered backend)
// =============================================================================
//
// Master promo codes. Backend delivered (promos/router.py):
//   GET   /api/v1/masters/me/promos               -- list my promos (newest first)
//   PATCH /api/v1/masters/me/promos/{id}/deactivate -- soft-deactivate (is_active=false)
// (POST create exists too and is used by the create form, not here.)
// =============================================================================

import { api } from '@/api/client'
import { buildQuery } from '@/api/utils'
import type { PaginatedPromosResponse, PromoResponse } from '@/api/types'

/** List the current master's promo codes (newest first). */
export function getMyPromos(limit = 50, offset = 0): Promise<PaginatedPromosResponse> {
  const query = buildQuery({ limit, offset })
  return api.get<PaginatedPromosResponse>(`/api/v1/masters/me/promos${query}`)
}

/** Deactivate a promo code (soft -- sets is_active=false; no hard delete). */
export function deactivatePromo(promoId: string): Promise<PromoResponse> {
  return api.patch<PromoResponse>(`/api/v1/masters/me/promos/${promoId}/deactivate`)
}
