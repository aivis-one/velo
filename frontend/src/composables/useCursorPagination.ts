// =============================================================================
// VELO Frontend -- useCursorPagination Composable (Diary feed)
// =============================================================================
//
// Cursor-based "load more" pagination, mirror of usePagination but for APIs
// that return { items, next_cursor } instead of { items, total, offset }.
//
// The diary feed (GET /api/v1/diary/feed) is an append-only timeline read
// newest-first; offset pagination is unsafe there (rows shift as new events
// are projected), so it uses an opaque cursor: the next page is requested
// with the previous response's next_cursor, and next_cursor === null marks
// the end of the feed.
//
// Usage:
//   const feed = useCursorPagination<DiaryFeedItem>(
//     (cursor, limit) => listDiaryFeed({ ...filters, cursor, limit }),
//   )
//   await feed.refresh()             // first page (reset + load)
//   if (feed.hasMore.value) feed.loadMore()
//   feed.reset()                     // clear, keep no cursor
// =============================================================================

import { ref, type Ref } from 'vue'

export interface CursorResult<T> {
  items: T[]
  next_cursor: string | null
}

// fetchFn receives the current cursor (null on the first page) and the page
// size, and returns one page plus the cursor for the following page.
type CursorFetchFn<T> = (cursor: string | null, limit: number) => Promise<CursorResult<T>>

export function useCursorPagination<T>(fetchFn: CursorFetchFn<T>, pageSize = 20) {
  const items = ref<T[]>([]) as Ref<T[]>
  const cursor = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  // Becomes false once the backend returns next_cursor === null. Starts true
  // so the very first loadMore() is allowed.
  const hasMore = ref(true)

  /**
   * Load the next page and append it. Returns false if a load is already in
   * flight or the feed is exhausted.
   */
  async function loadMore(): Promise<boolean> {
    if (loading.value) return false
    if (!hasMore.value) return false

    loading.value = true
    error.value = null

    try {
      const result = await fetchFn(cursor.value, pageSize)
      items.value = [...items.value, ...result.items]
      cursor.value = result.next_cursor
      hasMore.value = result.next_cursor !== null
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear all loaded items and the cursor. Does NOT auto-fetch. hasMore is
   * reset to true so the next loadMore() / refresh() starts a fresh feed.
   */
  function reset(): void {
    items.value = []
    cursor.value = null
    error.value = null
    hasMore.value = true
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
    cursor,
    loading,
    error,
    hasMore,
    loadMore,
    reset,
    refresh,
  }
}
