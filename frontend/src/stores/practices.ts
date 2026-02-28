// =============================================================================
// VELO Frontend -- Practices Store (Phase F3.1)
// =============================================================================
//
// Pinia store for the practice catalog (public feed) and single
// practice detail. Uses api/practices.ts for typed API calls and
// usePagination composable for load-more logic.
//
// Two independent data flows:
//   1. Catalog (list):  filters + paginated list for Dashboard/Calendar
//   2. Detail (single): selected practice for PracticeDetailView
//
// Catalog uses usePagination internally. Views call fetchPractices()
// on mount and loadMore() on scroll/button. Filter changes trigger
// refresh (reset + fetch).
// =============================================================================

import { defineStore } from 'pinia'
import { ref, reactive, watch } from 'vue'
import { getPractices, getPractice } from '@/api/practices'
import { usePagination } from '@/composables/usePagination'
import type {
  PracticeResponse,
  PracticeFilters,
} from '@/api/types'

export const usePracticesStore = defineStore('practices', () => {
  // -- Filters --
  const filters = reactive<PracticeFilters>({
    sort_by: 'scheduled_at',
    sort_order: 'asc',
  })

  // -- Paginated catalog --
  const pagination = usePagination<PracticeResponse>(
    (limit, offset) => getPractices(filters, limit, offset),
  )

  /**
   * Initial load. Called once from view onMounted.
   * Skips if already loaded (e.g. navigating back).
   */
  async function fetchPractices(): Promise<void> {
    if (pagination.items.value.length > 0) return
    await pagination.refresh()
  }

  /**
   * Apply new filters and reload from scratch.
   */
  function applyFilters(newFilters: Partial<PracticeFilters>): void {
    Object.assign(filters, newFilters)
  }

  // Auto-refresh when filters change
  watch(filters, () => {
    pagination.refresh()
  })

  // -- Single practice detail --
  const selected = ref<PracticeResponse | null>(null)
  const selectedLoading = ref(false)
  const selectedError = ref<string | null>(null)

  /**
   * Fetch a single practice by ID for the detail view.
   * Tries to find it in the already-loaded catalog first (avoids
   * extra API call when navigating from list → detail).
   */
  async function fetchPractice(id: string): Promise<void> {
    // Check catalog cache first
    const cached = pagination.items.value.find((p) => p.id === id)
    if (cached) {
      selected.value = cached
      return
    }

    selectedLoading.value = true
    selectedError.value = null
    try {
      selected.value = await getPractice(id)
    } catch (e) {
      selectedError.value = e instanceof Error ? e.message : 'Unknown error'
      selected.value = null
    } finally {
      selectedLoading.value = false
    }
  }

  function clearSelected(): void {
    selected.value = null
    selectedError.value = null
  }

  return {
    // Catalog
    practices: pagination.items,
    total: pagination.total,
    loading: pagination.loading,
    error: pagination.error,
    hasMore: pagination.hasMore,
    filters,
    fetchPractices,
    loadMore: pagination.loadMore,
    applyFilters,
    refreshPractices: pagination.refresh,

    // Detail
    selected,
    selectedLoading,
    selectedError,
    fetchPractice,
    clearSelected,
  }
})
