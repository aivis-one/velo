// =============================================================================
// VELO Frontend -- Taxonomy API (R5 stage 3a/3b)
// =============================================================================
//
// GET /api/v1/taxonomy -- active-only direction/style catalog, any
// authenticated user (not admin-gated). Backs MethodTaxonomyPicker's DB-
// sourced options (R5 stage 3b), with the hardcoded practiceOptions.ts
// consts kept as the offline/error fallback.
//
// This is a BRAND NEW endpoint -- generated.ts has no type for it yet (not
// regenerated locally, no docker/backend here). TaxonomyListResponse below
// is hand-written to match the backend response shape byte-for-byte
// (admin/taxonomy/schemas.py TaxonomyListResponse). Swap this import to
// generated.ts once the deploy bot resyncs it -- same follow-up pattern as
// R8's RichMaster/richOf().
// =============================================================================

import { api } from '@/api/client'

export interface TaxonomyStyleItem {
  id: string
  direction_id: string
  value: string
  label: string
  display_order: number
  is_active: boolean
  source: string
}

export interface TaxonomyDirectionItem {
  id: string
  value: string
  label: string
  display_order: number
  is_active: boolean
  source: string
  styles: TaxonomyStyleItem[]
}

export interface TaxonomyListResponse {
  directions: TaxonomyDirectionItem[]
}

/** Active-only catalog (is_active=true). Throws (ApiResponseError) on
 *  failure -- callers that need an offline fallback must catch. */
export function getActiveTaxonomy(): Promise<TaxonomyListResponse> {
  return api.get<TaxonomyListResponse>('/api/v1/taxonomy')
}
