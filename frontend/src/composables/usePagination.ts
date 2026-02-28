// =============================================================================
// VELO Frontend -- usePagination Composable (Phase F3.1)
// =============================================================================
//
// Reusable composable for limit/offset pagination with "load more"
// pattern. Works with any API that returns { items, total, limit, offset }.
//
// Usage:
//   const { items, loading, hasMore, loadMore, reset } = usePagination(
//     (limit, offset) => getPractices(filters, limit, offset),
//   )
//   await loadMore()              // first page
//   if (hasMore.value) loadMore() // next page
//   reset()                       // clear and start over
// =============================================================================

import { ref, computed, type Ref } from 'vue'

export interface PaginatedResult<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

type FetchFn<T> = (limit: number, offset: number) => Promise<PaginatedResult<T>>

export function usePagination<T>(
  fetchFn: FetchFn<T>,
  pageSize = 20,
) {
  const items = ref<T[]>([]) as Ref<T[]>
  const total = ref(0)
  const offset = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const hasMore = computed(() => offset.value < total.value)

  /**
   * Load the next page of results. Appends to existing items.
   * Returns false if already loading or no more items.
   */
  async function loadMore(): Promise<boolean> {
    if (loading.value) return false
    if (items.value.length > 0 && !hasMore.value) return false

    loading.value = true
    error.value = null

    try {
      const result = await fetchFn(pageSize, offset.value)
      items.value = [...items.value, ...result.items]
      total.value = result.total
      offset.value = offset.value + result.items.length
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear all loaded items and reset offset. Does NOT auto-fetch.
   */
  function reset(): void {
    items.value = []
    total.value = 0
    offset.value = 0
    error.value = null
  }

  /**
   * Reset and immediately load the first page.
   */
  async function refresh(): Promise<void> {
    reset()
    await loadMore()
  }

  return {
    items,
    total,
    loading,
    error,
    hasMore,
    loadMore,
    reset,
    refresh,
  }
}
