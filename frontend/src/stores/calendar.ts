// =============================================================================
// VELO Frontend -- Calendar Store (Calendar iteration)
// =============================================================================
//
// Dedicated Pinia store for the Calendar screen. Kept SEPARATE from
// usePracticesStore (Dashboard/old catalog) so that week navigation and
// the Calendar facet filters never disturb that shared feed.
//
// Loading strategy (agreed): the whole visible week is fetched in ONE
// request (date_from = Monday 00:00, date_to = Sunday 23:59:59 of the
// week, in the user's local timezone). The volume per week is small, so:
//   - day dot-markers are derived on the client from the loaded set,
//   - the selected-day list is filtered on the client,
//   - no pagination is needed (avoids the "client filter breaks server
//     pagination" problem entirely).
//
// Facet filters (direction / difficulty / style / duration_bucket /
// time_of_day / practice_type) are applied SERVER-side via getPractices,
// so the loaded week already reflects them.
//
// Timezone note: the week boundaries are computed in the user's local
// timezone (the browser's). Grouping a practice into a day uses the
// PRACTICE's own timezone (calendarDateInTz), consistent with how the
// rest of the app buckets practices by local day.
// =============================================================================

import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import { getPractices } from '@/api/practices'
import { extractApiError } from '@/composables/useApiError'
import type { PracticeFilters, PracticeResponse } from '@/api/types'

// Calendar-specific facet filters (excludes pagination/sort/date-range,
// which the store manages itself). Mirrors the facet subset of
// PracticeFilters that the Calendar UI controls.
export interface CalendarFacetFilters {
  practice_type?: PracticeFilters['practice_type']
  direction?: PracticeFilters['direction']
  difficulty?: PracticeFilters['difficulty']
  style?: PracticeFilters['style']
  duration_bucket?: PracticeFilters['duration_bucket']
  time_of_day?: PracticeFilters['time_of_day']
}

// ---------------------------------------------------------------------------
// Date helpers (local, dependency-free)
// ---------------------------------------------------------------------------

/** YYYY-MM-DD for a Date in a specific IANA timezone (en-CA gives ISO order). */
function calendarDateInTz(iso: string, timeZone: string): string {
  return new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone,
  }).format(new Date(iso))
}

/** YYYY-MM-DD for a Date in the browser's local timezone. */
function localDateKey(d: Date): string {
  return new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(d)
}

/** Monday 00:00:00.000 (local) of the week containing `d`. */
function startOfWeek(d: Date): Date {
  const date = new Date(d)
  date.setHours(0, 0, 0, 0)
  // getDay(): 0=Sun..6=Sat. Shift so Monday is the first day.
  const day = date.getDay()
  const diff = (day === 0 ? -6 : 1) - day
  date.setDate(date.getDate() + diff)
  return date
}

/** The 7 day-Dates (Mon..Sun, local midnight) of the week containing `d`. */
function weekDays(anchor: Date): Date[] {
  const start = startOfWeek(anchor)
  return Array.from({ length: 7 }, (_, i) => {
    const day = new Date(start)
    day.setDate(start.getDate() + i)
    return day
  })
}

export const useCalendarStore = defineStore('calendar', () => {
  // -- State --
  // Anchor date inside the currently viewed week (local). Defaults to today.
  const weekAnchor = ref<Date>(new Date())
  // Selected day key (YYYY-MM-DD, local). Defaults to today.
  const selectedDate = ref<string>(localDateKey(new Date()))
  // Practices for the whole visible week (one request).
  const weekPractices = ref<PracticeResponse[]>([])
  // Active facet filters (server-applied on load).
  const filters = reactive<CalendarFacetFilters>({})

  const loading = ref(false)
  const error = ref<string | null>(null)

  // -- Derived: the 7 day-Dates of the current week --
  const days = computed<Date[]>(() => weekDays(weekAnchor.value))

  // -- Derived: set of local-day keys that have at least one practice --
  // Markers are computed in each practice's own timezone so a practice
  // shows under the day the master scheduled it for.
  const daysWithPractices = computed<Set<string>>(() => {
    const set = new Set<string>()
    for (const p of weekPractices.value) {
      set.add(calendarDateInTz(p.scheduled_at, p.timezone))
    }
    return set
  })

  // -- Derived: practices on the selected day (client-side slice) --
  const selectedDayPractices = computed<PracticeResponse[]>(() =>
    weekPractices.value
      .filter(
        (p) => calendarDateInTz(p.scheduled_at, p.timezone) === selectedDate.value,
      )
      .sort(
        (a, b) =>
          new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime(),
      ),
  )

  // -- Actions --

  /**
   * Load every practice in the current week in one request.
   * date_from/date_to are the local Monday 00:00 .. Sunday 23:59:59.999.
   * Facet filters are passed through to the backend.
   */
  async function loadWeek(): Promise<void> {
    loading.value = true
    error.value = null

    const week = days.value
    const from = new Date(week[0]!)
    from.setHours(0, 0, 0, 0)
    const to = new Date(week[6]!)
    to.setHours(23, 59, 59, 999)

    const query: PracticeFilters = {
      ...filters,
      date_from: from.toISOString(),
      date_to: to.toISOString(),
      sort_by: 'scheduled_at',
      sort_order: 'asc',
    }

    try {
      // A week's worth of practices is small; one generous page covers it.
      const res = await getPractices(query, 100, 0)
      weekPractices.value = res.items
    } catch (e) {
      error.value = extractApiError(e, 'Не удалось загрузить календарь')
      weekPractices.value = []
    } finally {
      loading.value = false
    }
  }

  /** Select a specific day (YYYY-MM-DD, local). Does not reload (same week). */
  function selectDay(dateKey: string): void {
    selectedDate.value = dateKey
  }

  /** Move to the previous week and reload. Keeps the same weekday selected. */
  async function prevWeek(): Promise<void> {
    const a = new Date(weekAnchor.value)
    a.setDate(a.getDate() - 7)
    weekAnchor.value = a
    await loadWeek()
  }

  /** Move to the next week and reload. Keeps the same weekday selected. */
  async function nextWeek(): Promise<void> {
    const a = new Date(weekAnchor.value)
    a.setDate(a.getDate() + 7)
    weekAnchor.value = a
    await loadWeek()
  }

  /** Replace facet filters and reload the current week. */
  async function applyFilters(next: CalendarFacetFilters): Promise<void> {
    // Reassign keys explicitly so cleared facets (undefined) are respected.
    filters.practice_type = next.practice_type
    filters.direction = next.direction
    filters.difficulty = next.difficulty
    filters.style = next.style
    filters.duration_bucket = next.duration_bucket
    filters.time_of_day = next.time_of_day
    await loadWeek()
  }

  /** First load for the screen: jump to the week of today and fetch it. */
  async function init(): Promise<void> {
    weekAnchor.value = new Date()
    selectedDate.value = localDateKey(new Date())
    await loadWeek()
  }

  return {
    // state
    weekAnchor,
    selectedDate,
    weekPractices,
    filters,
    loading,
    error,
    // derived
    days,
    daysWithPractices,
    selectedDayPractices,
    // actions
    loadWeek,
    selectDay,
    prevWeek,
    nextWeek,
    applyFilters,
    init,
    // helpers (exported for the view: local day key of a Date)
    localDateKey,
  }
})
