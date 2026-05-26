// =============================================================================
// VELO Frontend -- Diary Store (Diary redesign: unified feed)
// =============================================================================
//
// Manages state for all diary-related data:
//
//   submit (unchanged -- used by CheckinView / FeedbackView):
//     submitCheckin()  -- upsert check-in
//     submitFeedback() -- upsert feedback
//
//   feed (DiaryFeedView -- the unified timeline, replaces the old tabs):
//     fetchFeed() / loadMoreFeed() -- cursor-paginated DiaryEvent list
//     setFeedFilters() / clearFeedFilters() / runFeedSearch()
//
//   diary entry CRUD (composer + future inline editor):
//     createEntry() / updateEntry() / deleteEntry()
//     selectedEntry + fetchEntry() -- single entry view/edit
//
//   insights (AnalyticsView, master-facing -- unchanged):
//     loadInsights(practiceId) -- aggregated data for master
//
// The feed uses useCursorPagination (cursor, not offset) because the
// DiaryEvent journal is append-only and read newest-first. Entry CRUD
// refreshes the feed (a created/edited/deleted note is a feed event).
// =============================================================================

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { extractApiError } from '@/composables/useApiError'
import { useCursorPagination } from '@/composables/useCursorPagination'
import { useBookingsStore } from '@/stores/bookings'
import {
  upsertCheckin,
  upsertFeedback,
  createDiaryEntry,
  getDiaryEntry,
  updateDiaryEntry,
  deleteDiaryEntry,
  listDiaryFeed,
  getPracticeInsights,
} from '@/api/diary'
import type {
  CheckinRequest,
  FeedbackRequest,
  CreateDiaryEntryRequest,
  UpdateDiaryEntryRequest,
  DiaryEntryResponse,
  DiaryFeedItem,
  DiaryFeedFilters,
  PracticeInsightsResponse,
} from '@/api/types'

export interface SubmitResult {
  ok: boolean
  error: string
}

export const useDiaryStore = defineStore('diary', () => {
  // ===========================================================================
  // Check-in submit (CheckinView)
  // ===========================================================================

  const checkinSubmitting = ref(false)

  /**
   * Submit a check-in for a practice.
   * Returns { ok, error } so the view can show a toast on failure.
   */
  async function submitCheckin(
    practiceId: string,
    body: CheckinRequest,
  ): Promise<SubmitResult> {
    if (checkinSubmitting.value) return { ok: false, error: '' }
    checkinSubmitting.value = true
    try {
      await upsertCheckin(practiceId, body)
      // The check-in is now a feed event and flips the booking's has_checkin
      // flag -- refresh both so the diary feed and dashboard banner update.
      await refreshAfterDiaryMutation()
      return { ok: true, error: '' }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось отправить check-in')
      return { ok: false, error: message }
    } finally {
      checkinSubmitting.value = false
    }
  }

  // ===========================================================================
  // Feedback submit (FeedbackView)
  // ===========================================================================

  const feedbackSubmitting = ref(false)

  /**
   * Submit a feedback for a practice.
   * Returns { ok, error } so the view can show a toast on failure.
   */
  async function submitFeedback(
    practiceId: string,
    body: FeedbackRequest,
  ): Promise<SubmitResult> {
    if (feedbackSubmitting.value) return { ok: false, error: '' }
    feedbackSubmitting.value = true
    try {
      await upsertFeedback(practiceId, body)
      // The feedback is now a feed event and flips the booking's has_feedback
      // flag -- refresh both so the diary feed and dashboard banner update.
      await refreshAfterDiaryMutation()
      return { ok: true, error: '' }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось отправить feedback')
      return { ok: false, error: message }
    } finally {
      feedbackSubmitting.value = false
    }
  }

  // ===========================================================================
  // Unified feed (DiaryFeedView)
  //
  // Cursor pagination over GET /api/v1/diary/feed. Filters live alongside the
  // pagination: changing them resets and refetches from the first page so the
  // cursor stays consistent with the active filter set.
  // ===========================================================================

  const feedFilters = reactive<DiaryFeedFilters>({
    categories: [],
    date_from: undefined,
    date_to: undefined,
    search: undefined,
  })

  const feed = useCursorPagination<DiaryFeedItem>(
    (cursor, limit) =>
      listDiaryFeed({
        categories: feedFilters.categories,
        date_from: feedFilters.date_from,
        date_to: feedFilters.date_to,
        search: feedFilters.search,
        cursor: cursor ?? undefined,
        limit,
      }),
  )

  /**
   * Initial feed load. Skips if already loaded (navigating back).
   */
  async function fetchFeed(): Promise<void> {
    if (feed.items.value.length > 0) return
    await feed.refresh()
  }

  /**
   * Apply new filters (merge) and reload the feed from the first page.
   * Pass a fresh categories array / dates / search; omitted keys are kept.
   */
  async function setFeedFilters(
    patch: Partial<DiaryFeedFilters>,
  ): Promise<void> {
    Object.assign(feedFilters, patch)
    await feed.refresh()
  }

  /**
   * Clear all filters (back to "Все", no date range, no search) and reload.
   */
  async function clearFeedFilters(): Promise<void> {
    feedFilters.categories = []
    feedFilters.date_from = undefined
    feedFilters.date_to = undefined
    feedFilters.search = undefined
    await feed.refresh()
  }

  /**
   * Run a text search (empty string clears it) and reload from the first page.
   */
  async function runFeedSearch(query: string): Promise<void> {
    const trimmed = query.trim()
    feedFilters.search = trimmed.length > 0 ? trimmed : undefined
    await feed.refresh()
  }

  /**
   * Refresh the data a check-in / feedback mutation affects:
   *   - the unified feed (a new event was projected onto the timeline), and
   *   - the bookings list (the booking's has_feedback / has_checkin flag
   *     flipped, so the dashboard banners hide and can't be re-submitted).
   * Parallel + best-effort: a refresh failure must not fail the submit, and
   * fetchFeed()/fetchMyBookings() skip their own load since the store is now
   * fresh (the views read straight from it on navigation).
   */
  async function refreshAfterDiaryMutation(): Promise<void> {
    await Promise.allSettled([
      feed.refresh(),
      useBookingsStore().refreshBookings(),
    ])
  }

  // ===========================================================================
  // Single diary entry (view / edit)
  // ===========================================================================

  const selectedEntry = ref<DiaryEntryResponse | null>(null)
  const selectedEntryLoading = ref(false)
  const selectedEntryError = ref<string | null>(null)

  /**
   * Fetch a single diary entry by ID (always from the API -- the feed stores
   * DiaryEvent snapshots, not full DiaryEntry rows).
   */
  async function fetchEntry(id: string): Promise<void> {
    selectedEntryLoading.value = true
    selectedEntryError.value = null
    try {
      selectedEntry.value = await getDiaryEntry(id)
    } catch (e) {
      selectedEntryError.value = extractApiError(e, 'Запись не найдена')
      selectedEntry.value = null
    } finally {
      selectedEntryLoading.value = false
    }
  }

  function clearSelectedEntry(): void {
    selectedEntry.value = null
    selectedEntryError.value = null
  }

  // ===========================================================================
  // Diary entry CRUD
  //
  // A created / edited / deleted note is a feed event, so each mutation
  // refreshes the feed (not a separate list).
  // ===========================================================================

  /**
   * Create a new diary entry, then refresh the feed.
   */
  async function createEntry(
    body: CreateDiaryEntryRequest,
  ): Promise<SubmitResult & { entry: DiaryEntryResponse | null }> {
    try {
      const entry = await createDiaryEntry(body)
      await feed.refresh()
      return { ok: true, error: '', entry }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось создать запись')
      return { ok: false, error: message, entry: null }
    }
  }

  /**
   * Update an existing diary entry, then refresh the feed.
   */
  async function updateEntry(
    id: string,
    body: UpdateDiaryEntryRequest,
  ): Promise<SubmitResult & { entry: DiaryEntryResponse | null }> {
    try {
      const entry = await updateDiaryEntry(id, body)
      await feed.refresh()
      if (selectedEntry.value?.id === id) {
        selectedEntry.value = entry
      }
      return { ok: true, error: '', entry }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось обновить запись')
      return { ok: false, error: message, entry: null }
    }
  }

  /**
   * Soft-delete a diary entry, then refresh the feed.
   */
  async function deleteEntry(id: string): Promise<SubmitResult> {
    try {
      await deleteDiaryEntry(id)
      await feed.refresh()
      if (selectedEntry.value?.id === id) {
        selectedEntry.value = null
      }
      return { ok: true, error: '' }
    } catch (e) {
      const message = extractApiError(e, 'Не удалось удалить запись')
      return { ok: false, error: message }
    }
  }

  // ===========================================================================
  // Practice insights cache (AnalyticsView, master-facing)
  //
  // Using reactive Maps so Vue tracks additions and AnalyticsView computeds
  // update automatically as new insights arrive.
  // Cache persists for the session -- AnalyticsView does not re-fetch on
  // re-visit unless $reset() is called (logout).
  // ===========================================================================

  const insightsCache      = reactive(new Map<string, PracticeInsightsResponse>())
  const insightsLoadingSet = reactive(new Set<string>())
  const insightsErrorMap   = reactive(new Map<string, string>())

  /** NEW-6: max entries in insightsCache to prevent unbounded memory growth. */
  const MAX_INSIGHTS_CACHE = 100

  /**
   * Load insights for a single completed practice.
   * Skips if already cached or currently loading.
   */
  async function loadInsights(practiceId: string): Promise<void> {
    if (insightsLoadingSet.has(practiceId) || insightsCache.has(practiceId)) return
    insightsErrorMap.delete(practiceId)
    insightsLoadingSet.add(practiceId)
    try {
      const data = await getPracticeInsights(practiceId)
      // NEW-6: LRU eviction -- remove oldest entry when cache is full.
      if (insightsCache.size >= MAX_INSIGHTS_CACHE) {
        const oldest = insightsCache.keys().next().value
        if (oldest !== undefined) insightsCache.delete(oldest)
      }
      insightsCache.set(practiceId, data)
    } catch (e) {
      insightsErrorMap.set(
        practiceId,
        extractApiError(e, 'Не удалось загрузить аналитику'),
      )
    } finally {
      insightsLoadingSet.delete(practiceId)
    }
  }

  // ===========================================================================
  // Reset (on logout)
  // ===========================================================================

  function $reset(): void {
    checkinSubmitting.value = false
    feedbackSubmitting.value = false
    feed.reset()
    feedFilters.categories = []
    feedFilters.date_from = undefined
    feedFilters.date_to = undefined
    feedFilters.search = undefined
    selectedEntry.value = null
    selectedEntryError.value = null
    insightsCache.clear()
    insightsLoadingSet.clear()
    insightsErrorMap.clear()
  }

  return {
    // Check-in / feedback submit
    checkinSubmitting,
    submitCheckin,
    feedbackSubmitting,
    submitFeedback,

    // Unified feed
    feedItems: feed.items,
    feedLoading: feed.loading,
    feedError: feed.error,
    feedHasMore: feed.hasMore,
    feedFilters,
    fetchFeed,
    loadMoreFeed: feed.loadMore,
    refreshFeed: feed.refresh,
    setFeedFilters,
    clearFeedFilters,
    runFeedSearch,

    // Single entry
    selectedEntry,
    selectedEntryLoading,
    selectedEntryError,
    fetchEntry,
    clearSelectedEntry,

    // Entry CRUD
    createEntry,
    updateEntry,
    deleteEntry,

    // Insights cache
    insightsCache,
    insightsLoadingSet,
    insightsErrorMap,
    loadInsights,

    // Reset
    $reset,
  }
})
