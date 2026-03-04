// =============================================================================
// VELO Frontend -- API Utilities (Phase F4.1)
// =============================================================================
//
// Shared helpers used across API modules (practices.ts, bookings.ts, etc.).
// =============================================================================

/**
 * Build query string from an object, skipping undefined/null values.
 *
 * Example:
 *   buildQuery({ limit: 20, offset: 0, status: undefined })
 *   => "?limit=20&offset=0"
 */
export function buildQuery(params: Record<string, string | number | undefined | null>): string {
  const entries = Object.entries(params).filter(
    (entry): entry is [string, string | number] =>
      entry[1] !== undefined && entry[1] !== null,
  )
  if (entries.length === 0) return ''
  const qs = new URLSearchParams(
    entries.map(([k, v]) => [k, String(v)]),
  )
  return `?${qs.toString()}`
}
