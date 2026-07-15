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

export function usePagination<T>(fetchFn: FetchFn<T>, pageSize = 20) {
  const items = ref<T[]>([]) as Ref<T[]>
  const total = ref(0)
  const offset = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const hasMore = computed(() => offset.value < total.value)

  // W17 fix (ПРОМТ №409): reset()/refresh() calling loadMore() while an
  // EARLIER loadMore() is still in flight used to corrupt state -- the
  // earlier call's `loading` guard blocked the new refresh's own loadMore
  // from running at all, then the earlier (stale-offset, stale-filter)
  // response landed on top of the just-cleared list once it resolved.
  // requestId tags each fetch; reset() bumps it so any in-flight loadMore
  // recognises itself as stale when it resolves and discards its result
  // instead of applying it.
  let requestId = 0

  /**
   * Load the next page of results. Appends to existing items.
   * Returns false if already loading or no more items.
   */
  async function loadMore(): Promise<boolean> {
    if (loading.value) return false
    if (items.value.length > 0 && !hasMore.value) return false

    loading.value = true
    error.value = null
    const myRequestId = ++requestId
    const requestOffset = offset.value

    try {
      const result = await fetchFn(pageSize, requestOffset)
      if (myRequestId !== requestId) return false // superseded by a reset/refresh
      items.value = [...items.value, ...result.items]
      total.value = result.total
      offset.value = requestOffset + result.items.length
      return true
    } catch (e) {
      if (myRequestId !== requestId) return false
      error.value = e instanceof Error ? e.message : 'Unknown error'
      return false
    } finally {
      if (myRequestId === requestId) loading.value = false
    }
  }

  /**
   * Clear all loaded items and reset offset. Does NOT auto-fetch. Invalidates
   * any in-flight loadMore() so its stale response can't land on top of the
   * cleared state (W17).
   */
  function reset(): void {
    requestId += 1
    items.value = []
    total.value = 0
    offset.value = 0
    error.value = null
    loading.value = false
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
