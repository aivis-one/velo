// =============================================================================
// VELO Frontend -- useApiError (WARNING-1)
// =============================================================================
//
// Single source of truth for API error message extraction.
// Replaces 7+ identical try/catch patterns across stores.
//
// Usage:
//   import { extractApiError } from '@/composables/useApiError'
//
//   } catch (e) {
//     return { ok: false, error: extractApiError(e, 'Не удалось выполнить действие') }
//   }
// =============================================================================

import { ApiResponseError } from '@/api/client'

/**
 * Extract a human-readable error message from a caught exception.
 *
 * - ApiResponseError: returns e.detail (message from backend)
 * - Anything else: returns the provided fallback string
 */
export function extractApiError(e: unknown, fallback: string): string {
  return e instanceof ApiResponseError ? e.detail : fallback
}
