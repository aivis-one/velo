<!--
  VELO Frontend -- AdminReportsView (Phase F8.3, updated F8-fix W-3 + W-5)

  List of reports with status + target_type filters and pagination.
  W-3: generation counter prevents stale responses from racing filter changes.
  W-5: statusVariant / statusLabel / targetLabel replaced with adminHelpers.

  Data: GET /api/v1/admin/reports
-->

<template>
  <div class="admin-reports">
    <VHeader title="Жалобы" />

    <div class="admin-reports__content">
      <!-- Filters -->
      <div class="admin-reports__filters">
        <VSelect
          v-model="filterStatus"
          label="Статус"
          :options="statusOptions"
          @update:model-value="onFilterChange"
        />
        <VSelect
          v-model="filterTargetType"
          label="Тип цели"
          :options="targetTypeOptions"
          @update:model-value="onFilterChange"
        />
      </div>

      <!-- Loading: initial -->
      <div v-if="loading && items.length === 0" class="admin-reports__loader">
        <VLoader size="lg" />
      </div>

      <!-- Empty state -->
      <VEmptyState
        v-else-if="!loading && items.length === 0"
        icon="success"
        title="Жалоб нет"
        description="По выбранным фильтрам ничего не найдено"
      />

      <template v-else>
        <!-- Count -->
        <div class="admin-reports__count">
          Найдено: <strong>{{ total }}</strong>
        </div>

        <!-- List -->
        <div class="admin-reports__list">
          <VCard
            v-for="item in items"
            :key="item.id"
            class="admin-reports__card"
            clickable
            padding="none"
            @click="openDetail(item)"
          >
            <div class="admin-reports__card-header">
              <VBadge :variant="reportStatusVariant(item.status)">
                {{ reportStatusLabel(item.status) }}
              </VBadge>
              <span class="admin-reports__card-type">
                {{ reportTargetLabel(item.target_type) }}
              </span>
            </div>
            <div class="admin-reports__card-reason">{{ item.reason }}</div>
            <div class="admin-reports__card-date">
              {{ formatShortDate(item.created_at) }}
            </div>
          </VCard>
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
import { VBadge, VButton, VLoader, VEmptyState, VSelect, VCard } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { getReports } from '@/api/admin'
import type { ReportResponse, ReportStatusFilter, ReportTargetTypeFilter } from '@/api/admin'
import { ApiResponseError } from '@/api/client'
import {
  reportStatusVariant,
  reportStatusLabel,
  reportTargetLabel,
  formatShortDate,
} from '@/utils/adminHelpers'

const LIMIT = 20

const router = useRouter()
const toast = useToast()

const items = ref<ReportResponse[]>([])
const total = ref(0)
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(false)

const filterStatus = ref<ReportStatusFilter | ''>('')
const filterTargetType = ref<ReportTargetTypeFilter | ''>('')

// W-3: generation counter to discard stale responses from rapid filter changes.
// Each loadInitial() call captures the generation at call time.
// If the counter has advanced by the time the response arrives, the result is dropped.
let generation = 0

const statusOptions = [
  { value: '', label: 'Все статусы' },
  { value: 'pending', label: 'Ожидает' },
  { value: 'resolved', label: 'Решена' },
  { value: 'dismissed', label: 'Отклонена' },
]

const targetTypeOptions = [
  { value: '', label: 'Все типы' },
  { value: 'user', label: '👤 Юзер' },
  { value: 'master', label: '🧘 Мастер' },
  { value: 'practice', label: '📅 Практика' },
]

async function loadInitial(): Promise<void> {
  // Capture generation before await -- any newer call will have incremented it.
  generation += 1
  const myGeneration = generation

  loading.value = true
  items.value = []
  total.value = 0
  hasMore.value = false

  try {
    const res = await getReports(
      filterStatus.value || undefined,
      filterTargetType.value || undefined,
      LIMIT,
      0,
    )

    // W-3: discard if a newer request has started since we awaited.
    if (myGeneration !== generation) return

    items.value = res.items
    total.value = res.total
    hasMore.value = res.items.length < res.total
  } catch (e) {
    if (myGeneration !== generation) return
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки жалоб'
    toast.error(msg)
  } finally {
    if (myGeneration === generation) {
      loading.value = false
    }
  }
}

async function loadMore(): Promise<void> {
  loadingMore.value = true
  try {
    const res = await getReports(
      filterStatus.value || undefined,
      filterTargetType.value || undefined,
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

function onFilterChange(): void {
  loadInitial()
}

function openDetail(item: ReportResponse): void {
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
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2);
}

/* -- Loader -- */
.admin-reports__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

/* -- Count -- */
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
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: opacity var(--transition-fast);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.admin-reports__card:active {
  opacity: 0.8;
}

.admin-reports__card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.admin-reports__card-type {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
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
}

/* -- Load more -- */
.admin-reports__load-more {
  padding-top: var(--space-2);
}
</style>
