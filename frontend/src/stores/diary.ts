// =============================================================================
// VELO Frontend -- Diary Store (Phase F9)
// =============================================================================
//
// Manages state for all diary-related data:
//
//   submit:
//     submitCheckin()  -- upsert check-in, used by CheckinView
//     submitFeedback() -- upsert feedback, used by FeedbackView
//
//   diary entries (DiaryView tab "Записи"):
//     fetchEntries() / loadMoreEntries() -- paginated list
//     createEntry() / updateEntry() / deleteEntry()
//     selectedEntry + fetchEntry() -- single entry view/edit
//
//   checkins (DiaryView tab "Check-ins"):
//     fetchCheckins() / loadMoreCheckins() -- paginated list
//
//   feedbacks (DiaryView tab "Feedbacks"):
//     fetchFeedbacks() / loadMoreFeedbacks() -- paginated list
//
//   insights (AnalyticsView):
//     fetchInsights(practiceId) -- aggregated data for master
//
// Each list uses usePagination internally for consistent load-more behaviour.
// =============================================================================

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { ApiResponseError } from '@/api/client'
import { extractApiError } from '@/composables/useApiError'
import { usePagination } from '@/composables/usePagination'
import {
  upsertCheckin,
  upsertFeedback,
  listMyCheckins,
  listMyFeedbacks,
  createDiaryEntry,
  listDiaryEntries,
  getDiaryEntry,
  updateDiaryEntry,
  deleteDiaryEntry,
  getPracticeInsights,
} from '@/api/diary'
import type {
  CheckinRequest,
  CheckinResponse,
  FeedbackRequest,
  FeedbackResponse,
  CreateDiaryEntryRequest,
  UpdateDiaryEntryRequest,
  DiaryEntryResponse,
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
      return { ok: true, error: '' }
    } catch (e) {
      const message =
        extractApiError(e, 'Не удалось отправить check-in')
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
      return { ok: true, error: '' }
    } catch (e) {
      const message =
        extractApiError(e, 'Не удалось отправить feedback')
      return { ok: false, error: message }
    } finally {
      feedbackSubmitting.value = false
    }
  }

  // ===========================================================================
  // Diary entries list (DiaryView tab "Записи")
  // ===========================================================================

  const entriesPagination = usePagination<DiaryEntryResponse>(
    (limit, offset) => listDiaryEntries({ limit, offset }),
  )

  /**
   * Initial load of diary entries.
   * Skips if already loaded (navigating back).
   */
  async function fetchEntries(): Promise<void> {
    if (entriesPagination.items.value.length > 0) return
    await entriesPagination.refresh()
  }

  /**
   * Force-reload entries list (after create/update/delete).
   */
  async function refreshEntries(): Promise<void> {
    await entriesPagination.refresh()
  }

  // ===========================================================================
  // Single diary entry (view / edit)
  // ===========================================================================

  const selectedEntry = ref<DiaryEntryResponse | null>(null)
  const selectedEntryLoading = ref(false)
  const selectedEntryError = ref<string | null>(null)

  /**
   * Fetch a single diary entry by ID.
   * Tries the already-loaded list first to avoid a network call.
   */
  async function fetchEntry(id: string): Promise<void> {
    const cached = entriesPagination.items.value.find((e) => e.id === id)
    if (cached) {
      selectedEntry.value = cached
      return
    }
    selectedEntryLoading.value = true
    selectedEntryError.value = null
    try {
      selectedEntry.value = await getDiaryEntry(id)
    } catch (e) {
      selectedEntryError.value =
        extractApiError(e, 'Запись не найдена')
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
  // ===========================================================================

  /**
   * Create a new diary entry, then refresh the list.
   */
  async function createEntry(
    body: CreateDiaryEntryRequest,
  ): Promise<SubmitResult & { entry: DiaryEntryResponse | null }> {
    try {
      const entry = await createDiaryEntry(body)
      await refreshEntries()
      return { ok: true, error: '', entry }
    } catch (e) {
      const message =
        extractApiError(e, 'Не удалось создать запись')
      return { ok: false, error: message, entry: null }
    }
  }

  /**
   * Update an existing diary entry, then refresh the list.
   */
  async function updateEntry(
    id: string,
    body: UpdateDiaryEntryRequest,
  ): Promise<SubmitResult & { entry: DiaryEntryResponse | null }> {
    try {
      const entry = await updateDiaryEntry(id, body)
      await refreshEntries()
      // Update selected entry in-place if it's the one being edited.
      if (selectedEntry.value?.id === id) {
        selectedEntry.value = entry
      }
      return { ok: true, error: '', entry }
    } catch (e) {
      const message =
        extractApiError(e, 'Не удалось обновить запись')
      return { ok: false, error: message, entry: null }
    }
  }

  /**
   * Hard-delete a diary entry, then refresh the list.
   */
  async function deleteEntry(id: string): Promise<SubmitResult> {
    try {
      await deleteDiaryEntry(id)
      await refreshEntries()
      if (selectedEntry.value?.id === id) {
        selectedEntry.value = null
      }
      return { ok: true, error: '' }
    } catch (e) {
      const message =
        extractApiError(e, 'Не удалось удалить запись')
      return { ok: false, error: message }
    }
  }

  // ===========================================================================
  // Checkins list (DiaryView tab "Check-ins")
  // ===========================================================================

  const checkinsPagination = usePagination<CheckinResponse>(
    (limit, offset) => listMyCheckins({ limit, offset }),
  )

  /**
   * Initial load of check-ins for the diary tab.
   */
  async function fetchCheckins(): Promise<void> {
    if (checkinsPagination.items.value.length > 0) return
    await checkinsPagination.refresh()
  }

  // ===========================================================================
  // Feedbacks list (DiaryView tab "Feedbacks")
  // ===========================================================================

  const feedbacksPagination = usePagination<FeedbackResponse>(
    (limit, offset) => listMyFeedbacks({ limit, offset }),
  )

  /**
   * Initial load of feedbacks for the diary tab.
   */
  async function fetchFeedbacks(): Promise<void> {
    if (feedbacksPagination.items.value.length > 0) return
    await feedbacksPagination.refresh()
  }

  // ===========================================================================
  // Practice insights cache (AnalyticsView, master-facing)
  //
  // Using reactive Maps so Vue tracks additions and AnalyticsView computeds
  // update automatically as new insights arrive.
  // Cache persists for the session -- AnalyticsView does not re-fetch on
  // re-visit unless $reset() is called (logout).
  // ===========================================================================

  const insightsCache     = reactive(new Map<string, PracticeInsightsResponse>())
  const insightsLoadingSet = reactive(new Set<string>())
  const insightsErrorMap  = reactive(new Map<string, string>())

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
    entriesPagination.items.value = []
    entriesPagination.total.value = 0
    checkinsPagination.items.value = []
    checkinsPagination.total.value = 0
    feedbacksPagination.items.value = []
    feedbacksPagination.total.value = 0
    selectedEntry.value = null
    selectedEntryError.value = null
    insightsCache.clear()
    insightsLoadingSet.clear()
    insightsErrorMap.clear()
  }

  return {
    // Check-in submit
    checkinSubmitting,
    submitCheckin,

    // Feedback submit
    feedbackSubmitting,
    submitFeedback,

    // Diary entries list
    entries: entriesPagination.items,
    entriesTotal: entriesPagination.total,
    entriesLoading: entriesPagination.loading,
    entriesError: entriesPagination.error,
    entriesHasMore: entriesPagination.hasMore,
    fetchEntries,
    loadMoreEntries: entriesPagination.loadMore,
    refreshEntries,

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

    // Checkins list
    checkins: checkinsPagination.items,
    checkinsTotal: checkinsPagination.total,
    checkinsLoading: checkinsPagination.loading,
    checkinsError: checkinsPagination.error,
    checkinsHasMore: checkinsPagination.hasMore,
    fetchCheckins,
    loadMoreCheckins: checkinsPagination.loadMore,

    // Feedbacks list
    feedbacks: feedbacksPagination.items,
    feedbacksTotal: feedbacksPagination.total,
    feedbacksLoading: feedbacksPagination.loading,
    feedbacksError: feedbacksPagination.error,
    feedbacksHasMore: feedbacksPagination.hasMore,
    fetchFeedbacks,
    loadMoreFeedbacks: feedbacksPagination.loadMore,

    // Insights cache
    insightsCache,
    insightsLoadingSet,
    insightsErrorMap,
    loadInsights,

    // Reset
    $reset,
  }
})
