// =============================================================================
// VELO Frontend -- Admin store (Admin DS rebuild 2026-06-14)
// =============================================================================
//
// Shared admin state for the admin shell + screens. Holds the dashboard stats
// and the live "pending" counts that drive the tab-bar badges (masters awaiting
// verification + reports awaiting moderation), so the shell and the dashboard
// view fetch once and read the same source.
//
// Backend gaps (build-full-design -> Zod): /admin/stats returns only 4 counters
// (users/masters/practices/pending_verifications). Revenue, engagement rates,
// stat deltas, period scoping and a pending-reports counter are NOT exposed yet
// -> the dashboard stubs them. Moderation count is derived from a second call
// (getReports 'pending' .total) until /admin/stats carries it directly.
// =============================================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getAdminStats, getReports } from '@/api/admin'
import type { AdminStatsResponse } from '@/api/admin'

export const useAdminStore = defineStore('admin', () => {
  const stats = ref<AdminStatsResponse | null>(null)
  const pendingReports = ref(0)
  const loading = ref(false)
  const loaded = ref(false)

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

  return {
    stats,
    pendingReports,
    loading,
    loaded,
    pendingVerifications,
    pendingModeration,
    pendingMethodChanges,
    fetchDashboard,
  }
})
