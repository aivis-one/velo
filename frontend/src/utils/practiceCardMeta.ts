// =============================================================================
// VELO Frontend -- Practice card meta helpers (shared)
// =============================================================================
// Inline meta rendered under a practice card's title: check-in count, series
// recurrence, remaining sessions. Extracted from MasterPracticesView so the
// master dashboard's «Ближайшие практики» card renders identical meta (DB-2,
// 2026-06-30) WITHOUT duplicating the formatting logic. The data source (the
// anonymous-insights cache) is the shared diaryStore.insightsCache, passed in.
//
// NB: check-in COUNTS are the E12 path — the per-id figure equals whatever the
// insights endpoint returns today; data-correctness is a separate Zod thread.
// =============================================================================

import { recurrenceDaysLabel } from './displayHelpers'
import type { PracticeResponse, PracticeInsightsResponse } from '@/api/types'

type InsightsCache = Map<string, PracticeInsightsResponse>

/** Total submitted check-ins for a practice from its insights; 0 when uncached. */
function totalCheckins(id: string, cache: InsightsCache): number {
  const i = cache.get(id)
  return i ? i.checkins.high + i.checkins.mid + i.checkins.low : 0
}

/** Check-in count "10/20" (submitted check-ins / capacity). Always a fraction —
 * "0/N" before anyone has checked in (operator: never a bare «—»). */
export function checkinLabel(p: PracticeResponse, cache: InsightsCache): string {
  const denom = p.max_participants ?? p.current_participants
  return `${totalCheckins(p.id, cache)}/${denom}`
}

/** Series recurrence: weekday list / «Ежедневно» from recurrence_days, falling
 * back to «Регулярная» for a series with no day list. null when not a series. */
export function recurrenceLabel(p: PracticeResponse): string | null {
  if (p.practice_type !== 'series') return null
  return recurrenceDaysLabel(p.recurrence_days) ?? 'Регулярная'
}

/** «Осталось N из M занятий» for a series with a known session count; null otherwise. */
export function remainingSessionsLabel(p: PracticeResponse): string | null {
  const total = p.total_sessions
  if (total == null) return null
  const left = Math.max(0, total - (p.completed_sessions ?? 0))
  return `Осталось ${left} из ${total} занятий`
}
