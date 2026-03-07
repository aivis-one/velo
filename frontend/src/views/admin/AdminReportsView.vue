<!--
  VELO Frontend -- AdminReportsView (Phase F8.3)

  List of reports with filters by status and target_type.
  Click on a report -> AdminReportDetailView with report data in router state.

  Data: GET /api/v1/admin/reports (paginated, load-more)
-->

<template>
  <div class="admin-reports">
    <VHeader title="Жалобы" />

    <div class="admin-reports__content">
      <!-- Filters -->
      <div class="admin-reports__filters">
        <div class="admin-reports__filter-row">
          <button
            v-for="s in STATUS_OPTIONS"
            :key="String(s.value)"
            class="admin-reports__filter-chip"
            :class="{ 'admin-reports__filter-chip--active': statusFilter === s.value }"
            @click="setStatusFilter(s.value)"
          >
            {{ s.label }}
          </button>
        </div>
        <div class="admin-reports__filter-row">
          <button
            v-for="t in TARGET_OPTIONS"
            :key="String(t.value)"
            class="admin-reports__filter-chip"
            :class="{ 'admin-reports__filter-chip--active': targetFilter === t.value }"
            @click="setTargetFilter(t.value)"
          >
            {{ t.label }}
          </button>
        </div>
      </div>

      <!-- Loading: initial -->
      <div v-if="loading && items.length === 0" class="admin-reports__loader">
        <VLoader size="lg" />
      </div>

      <!-- Empty state -->
      <VEmptyState
        v-else-if="!loading && items.length === 0"
        icon="✅"
        title="Жалоб нет"
        description="По выбранным фильтрам ничего не найдено"
      />

      <template v-else>
        <!-- Count -->
        <div class="admin-reports__count">Всего: {{ total }}</div>

        <!-- List -->
        <div class="admin-reports__list">
          <div
            v-for="item in items"
            :key="item.id"
            class="admin-reports__card"
            @click="openDetail(item)"
          >
            <div class="admin-reports__card-top">
              <VBadge :variant="statusVariant(item.status)">
                {{ statusLabel(item.status) }}
              </VBadge>
              <span class="admin-reports__card-type">{{ targetLabel(item.target_type) }}</span>
            </div>
            <div class="admin-reports__card-reason">{{ item.reason }}</div>
            <div class="admin-reports__card-date">
              {{ formatDate(item.created_at) }}
            </div>
          </div>
        </div>

        <!-- Load more -->
        <div v-if="hasMore" class="admin-reports__load-more">
          <VButton
            variant="outline"
            block
            :loading="loadingMore"
            @click="loadMore"
          >
            Показать ещё
          </VButton>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VBadge, VButton, VLoader, VEmptyState } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { getReports } from '@/api/admin'
import type { ReportResponse, ReportStatusFilter, ReportTargetTypeFilter } from '@/api/admin'
import { ApiResponseError } from '@/api/client'

const LIMIT = 20

const STATUS_OPTIONS: Array<{ value: ReportStatusFilter | undefined; label: string }> = [
  { value: undefined, label: 'Все' },
  { value: 'pending', label: 'Ожидают' },
  { value: 'resolved', label: 'Решены' },
  { value: 'dismissed', label: 'Отклонены' },
]

const TARGET_OPTIONS: Array<{ value: ReportTargetTypeFilter | undefined; label: string }> = [
  { value: undefined, label: 'Все типы' },
  { value: 'user', label: 'Юзер' },
  { value: 'master', label: 'Мастер' },
  { value: 'practice', label: 'Практика' },
]

const router = useRouter()
const toast = useToast()

const items = ref<ReportResponse[]>([])
const total = ref(0)
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(false)

const statusFilter = ref<ReportStatusFilter | undefined>('pending')
const targetFilter = ref<ReportTargetTypeFilter | undefined>(undefined)

function statusVariant(status: string): 'warning' | 'success' | 'error' | 'info' {
  if (status === 'pending') return 'warning'
  if (status === 'resolved') return 'success'
  if (status === 'dismissed') return 'info'
  return 'info'
}

function statusLabel(status: string): string {
  if (status === 'pending') return 'Ожидает'
  if (status === 'resolved') return 'Решена'
  if (status === 'dismissed') return 'Отклонена'
  return status
}

function targetLabel(type: string): string {
  if (type === 'user') return '👤 Юзер'
  if (type === 'master') return '🧘 Мастер'
  if (type === 'practice') return '📅 Практика'
  return type
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

async function loadInitial(): Promise<void> {
  loading.value = true
  items.value = []
  try {
    const res = await getReports(statusFilter.value, targetFilter.value, LIMIT, 0)
    items.value = res.items
    total.value = res.total
    hasMore.value = res.items.length < res.total
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки жалоб'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

async function loadMore(): Promise<void> {
  loadingMore.value = true
  try {
    const res = await getReports(
      statusFilter.value,
      targetFilter.value,
      LIMIT,
      items.value.length,
    )
    items.value.push(...res.items)
    hasMore.value = items.value.length < res.total
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки'
    toast.error(msg)
  } finally {
    loadingMore.value = false
  }
}

function setStatusFilter(value: ReportStatusFilter | undefined): void {
  statusFilter.value = value
  loadInitial()
}

function setTargetFilter(value: ReportTargetTypeFilter | undefined): void {
  targetFilter.value = value
  loadInitial()
}

function openDetail(item: ReportResponse): void {
  // Serialize to plain object: vue-router HistoryState requires index signature
  // for 'number' which TypeScript interfaces don't satisfy directly.
  router.push({
    name: 'admin-report-detail',
    params: { id: item.id },
    state: { report: JSON.parse(JSON.stringify(item)) },
  })
}

onMounted(loadInitial)
</script>

<style scoped>
.admin-reports {
  min-height: 100dvh;
}

.admin-reports__content {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* -- Filters -- */
.admin-reports__filters {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.admin-reports__filter-row {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.admin-reports__filter-chip {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-full);
  background: var(--velo-bg-card);
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.admin-reports__filter-chip--active {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: #fff;
}

/* -- Loader -- */
.admin-reports__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

.admin-reports__count {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
}

/* -- List -- */
.admin-reports__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.admin-reports__card {
  background: var(--velo-bg-card);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: all var(--transition-base);
}

.admin-reports__card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.admin-reports__card-top {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.admin-reports__card-type {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  margin-left: auto;
}

.admin-reports__card-reason {
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.admin-reports__card-date {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  margin-top: var(--space-2);
}

.admin-reports__load-more {
  padding-top: var(--space-2);
}
</style>
