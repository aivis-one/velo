// =============================================================================
// VELO Frontend -- Admin store (Admin DS rebuild 2026-06-14)
// =============================================================================
//
// Shared admin state for the admin shell + screens. Holds the dashboard stats
// and the live "pending" counts that drive the tab-bar badges (masters awaiting
// verification + reports awaiting moderation), so the shell and the dashboard
// view fetch once and read the same source.
//
// /admin/stats is the cumulative-counter source for the tab/alert badges
// (pending verifications / method-changes, + a moderation count from getReports).
// The 3 dashboard stat cards + their percent deltas come from the period-scoped
// /admin/stats/overview (E7), fetched separately with a period + offset.
// =============================================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getAdminStats, getAdminStatsOverview, getReports } from '@/api/admin'
import type { AdminStatsResponse, AdminStatsOverviewResponse } from '@/api/admin'

export const useAdminStore = defineStore('admin', () => {
  const stats = ref<AdminStatsResponse | null>(null)
  const pendingReports = ref(0)
  const loading = ref(false)
  const loaded = ref(false)

  // Period-scoped overview (E7) for the 3 stat cards + percent deltas. Refetched
  // on period/offset change; always refetches (cheap, and the window shifts).
  const overview = ref<AdminStatsOverviewResponse | null>(null)
  const overviewLoading = ref(false)

  const pendingVerifications = computed((): number => stats.value?.pending_verifications ?? 0)
  const pendingModeration = computed((): number => pendingReports.value)
  // A2: pending master method-change requests -> red badge on the dashboard row.
  const pendingMethodChanges = computed((): number => stats.value?.pending_method_changes ?? 0)

  // Load the dashboard data set (stats + pending-reports count) once. Idempotent:
  // skips while in flight and after a successful load unless `force` is passed.
  async function fetchDashboard(force = false): Promise<void> {
    if (loading.value) return
    if (loaded.value && !force) return
    loading.value = true
    try {
      const [s, reports] = await Promise.all([
        getAdminStats(),
        getReports('pending', undefined, 1, 0),
      ])
      stats.value = s
      pendingReports.value = reports.total
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  // Load the period-scoped overview for the stat cards + deltas (D1/D6).
  async function fetchOverview(
    period: 'week' | 'month',
    offset = 0,
  ): Promise<void> {
    overviewLoading.value = true
    try {
      overview.value = await getAdminStatsOverview(period, offset)
    } finally {
      overviewLoading.value = false
    }
  }

  return {
    stats,
    pendingReports,
    loading,
    loaded,
    pendingVerifications,
    pendingModeration,
    pendingMethodChanges,
    fetchDashboard,
    overview,
    overviewLoading,
    fetchOverview,
  }
})
