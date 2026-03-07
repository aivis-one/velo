// =============================================================================
// VELO Frontend -- Master Store (Phase F6, fixed W-4)
// =============================================================================
//
// W-4: fetchMyPractices() now uses a dedicated practicesLoaded flag instead
// of checking items.length > 0. The old guard incorrectly re-fetched every
// time a master with zero practices visited the list view.
// =============================================================================

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMyMasterProfile, getMyPractices } from '@/api/masters'
import { usePagination } from '@/composables/usePagination'
import { ApiResponseError } from '@/api/client'
import type { MasterProfileResponse, PracticeResponse } from '@/api/types'

export const useMasterStore = defineStore('master', () => {
  // =========================================================================
  // Profile
  // =========================================================================

  const profile = ref<MasterProfileResponse | null>(null)
  const profileLoading = ref(false)
  const profileError = ref<string | null>(null)

  // Tracks whether at least one successful fetch has completed.
  // Used by masterStatusGuard to skip redundant network calls.
  const profileLoaded = ref(false)

  /**
   * Fetch master profile from API.
   *
   * @param force - If true, always fetches even if already loaded.
   *                Default false: skips if profileLoaded is true.
   *
   * Called by:
   *   - masterStatusGuard (lazy, force=false)
   *   - MasterPendingView (polling / manual recheck, force=true)
   *   - MasterDashboardView (on mount, force=false)
   */
  async function fetchMyProfile(force = false): Promise<void> {
    if (!force && profileLoaded.value) return
    profileLoading.value = true
    profileError.value = null
    try {
      profile.value = await getMyMasterProfile()
      profileLoaded.value = true
    } catch (e) {
      profileError.value =
        e instanceof ApiResponseError ? e.detail : 'Не удалось загрузить профиль мастера'
    } finally {
      profileLoading.value = false
    }
  }

  // =========================================================================
  // Practices (paginated)
  // =========================================================================

  const pagination = usePagination<PracticeResponse>(
    (limit, offset) => getMyPractices(limit, offset),
  )

  // W-4: separate flag instead of items.length > 0 check.
  // Prevents re-fetching when master legitimately has zero practices.
  const practicesLoaded = ref(false)

  /**
   * Initial load of master's practices.
   * Skips if already loaded (navigating back to list).
   */
  async function fetchMyPractices(): Promise<void> {
    if (practicesLoaded.value) return
    await pagination.refresh()
    practicesLoaded.value = true
  }

  /**
   * Force-reload practices list.
   * Called after create / edit / delete / cancel operations.
   */
  async function refreshMyPractices(): Promise<void> {
    await pagination.refresh()
    practicesLoaded.value = true
  }

  // =========================================================================
  // Reset (on logout -- W-1)
  // =========================================================================

  function $reset(): void {
    profile.value = null
    profileLoading.value = false
    profileError.value = null
    profileLoaded.value = false
    pagination.items.value = []
    pagination.total.value = 0
    practicesLoaded.value = false
  }

  return {
    // Profile
    profile,
    profileLoading,
    profileError,
    profileLoaded,
    fetchMyProfile,

    // Practices list
    practices: pagination.items,
    practicesTotal: pagination.total,
    practicesLoading: pagination.loading,
    practicesError: pagination.error,
    practicesHasMore: pagination.hasMore,
    fetchMyPractices,
    refreshMyPractices,
    loadMorePractices: pagination.loadMore,

    // Reset
    $reset,
  }
})
