<!--
  VELO Frontend -- AdminConsistencyView (Phase F8.3)

  Data consistency semaphores: 21 checks grouped by category.
  Summary counters at top. Re-run button to refresh.

  Data: GET /api/v1/admin/consistency
-->

<template>
  <div class="consistency">
    <VHeader title="Семафоры данных" />

    <div class="consistency__content">
      <!-- Loading -->
      <div v-if="loading" class="consistency__loader">
        <VLoader size="lg" />
      </div>

      <template v-else-if="data">
        <!-- Summary bar -->
        <div class="consistency__summary">
          <div class="consistency__summary-item consistency__summary-item--ok">
            <span class="consistency__summary-value">{{ data.ok_count }}</span>
            <span class="consistency__summary-label">OK</span>
          </div>
          <div class="consistency__summary-divider" />
          <div
            class="consistency__summary-item"
            :class="data.alert_count > 0 ? 'consistency__summary-item--alert' : 'consistency__summary-item--ok'"
          >
            <span class="consistency__summary-value">{{ data.alert_count }}</span>
            <span class="consistency__summary-label">ALERT</span>
          </div>
          <div class="consistency__summary-divider" />
          <div class="consistency__summary-item consistency__summary-item--total">
            <span class="consistency__summary-value">{{ data.total }}</span>
            <span class="consistency__summary-label">всего</span>
          </div>
        </div>

        <!-- Run time -->
        <div class="consistency__run-at">
          Последняя проверка: {{ formatDateTime(data.run_at) }}
        </div>

        <!-- Re-run button -->
        <VButton variant="outline" block :loading="loading" @click="loadData">
          🔄 Перезапустить проверку
        </VButton>

        <!-- Groups by category -->
        <div
          v-for="(group, category) in groupedItems"
          :key="category"
          class="consistency__group"
        >
          <div class="consistency__group-title">
            {{ categoryLabel(category) }}
            <span
              class="consistency__group-badge"
              :class="groupHasAlerts(group) ? 'consistency__group-badge--alert' : 'consistency__group-badge--ok'"
            >
              {{ group.filter((i) => i.status === 'ALERT').length }} ALERT
            </span>
          </div>

          <div class="consistency__items">
            <div
              v-for="item in group"
              :key="item.name"
              class="consistency__item"
              :class="item.status === 'ALERT' ? 'consistency__item--alert' : 'consistency__item--ok'"
            >
              <div class="consistency__item-top">
                <span class="consistency__item-indicator">
                  {{ item.status === 'OK' ? '✅' : '🚨' }}
                </span>
                <span class="consistency__item-name">{{ item.name }}</span>
                <VBadge :variant="criticalityVariant(item.criticality)">
                  {{ item.criticality }}
                </VBadge>
              </div>
              <template v-if="item.status === 'ALERT'">
                <div class="consistency__item-diff">
                  <span class="consistency__item-diff-label">Ожидалось:</span>
                  <span class="consistency__item-diff-val">{{ item.expected }}</span>
                </div>
                <div class="consistency__item-diff">
                  <span class="consistency__item-diff-label">Получено:</span>
                  <span class="consistency__item-diff-val consistency__item-diff-val--alert">
                    {{ item.actual }}
                  </span>
                </div>
              </template>
            </div>
          </div>
        </div>
      </template>

      <!-- Error state -->
      <VEmptyState
        v-else
        icon="⚠️"
        title="Не удалось запустить проверку"
        description="Проверьте соединение и попробуйте ещё раз"
      >
        <template #action>
          <VButton variant="primary" @click="loadData">Повторить</VButton>
        </template>
      </VEmptyState>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { VHeader } from '@/components/layout'
import { VBadge, VButton, VLoader, VEmptyState } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { getConsistency } from '@/api/admin'
import type { ConsistencyResponse, SemaphoreResult } from '@/api/admin'
import { ApiResponseError } from '@/api/client'

const toast = useToast()

const data = ref<ConsistencyResponse | null>(null)
const loading = ref(false)

// Group semaphore results by category, preserving insertion order.
const groupedItems = computed((): Record<string, SemaphoreResult[]> => {
  if (!data.value) return {}
  return data.value.items.reduce(
    (acc, item) => {
      if (!acc[item.category]) acc[item.category] = []
      acc[item.category].push(item)
      return acc
    },
    {} as Record<string, SemaphoreResult[]>,
  )
})

function groupHasAlerts(group: SemaphoreResult[]): boolean {
  return group.some((i) => i.status === 'ALERT')
}

function categoryLabel(category: string): string {
  const labels: Record<string, string> = {
    count_count: '1. COUNT = COUNT',
    sum_zero: '2. SUM = 0',
    computed_actual: '3. COMPUTED = ACTUAL',
    orphan_detection: '4. Orphan Detection',
    business_invariants: '5. Business Invariants',
  }
  return labels[category] ?? category
}

function criticalityVariant(criticality: string): 'error' | 'warning' | 'info' {
  if (criticality === 'critical') return 'error'
  if (criticality === 'warning') return 'warning'
  return 'info'
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

async function loadData(): Promise<void> {
  loading.value = true
  try {
    data.value = await getConsistency()
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка запуска семафоров'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.consistency {
  min-height: 100dvh;
}

.consistency__content {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.consistency__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

/* -- Summary bar -- */
.consistency__summary {
  display: flex;
  align-items: center;
  background: var(--velo-bg-card);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.consistency__summary-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-3);
}

.consistency__summary-item--ok .consistency__summary-value {
  color: #166534;
}

.consistency__summary-item--alert .consistency__summary-value {
  color: #DC2626;
}

.consistency__summary-item--total .consistency__summary-value {
  color: var(--velo-text-primary);
}

.consistency__summary-value {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 700;
  line-height: 1;
}

.consistency__summary-label {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  margin-top: var(--space-1);
}

.consistency__summary-divider {
  width: 1px;
  height: 40px;
  background: var(--velo-border);
}

/* -- Run time -- */
.consistency__run-at {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  text-align: center;
}

/* -- Group -- */
.consistency__group-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-2);
}

.consistency__group-badge {
  margin-left: auto;
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.consistency__group-badge--ok {
  background: #DCFCE7;
  color: #166534;
}

.consistency__group-badge--alert {
  background: #FEE2E2;
  color: #DC2626;
}

/* -- Items -- */
.consistency__items {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.consistency__item {
  border-radius: var(--radius-md);
  padding: var(--space-3);
  border: 1px solid var(--velo-border);
}

.consistency__item--ok {
  background: var(--velo-bg-card);
}

.consistency__item--alert {
  background: #FFF5F5;
  border-color: #FCA5A5;
}

.consistency__item-top {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.consistency__item-indicator {
  font-size: 14px;
  flex-shrink: 0;
}

.consistency__item-name {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  font-family: monospace;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.consistency__item-diff {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-2);
  font-size: var(--text-xs);
}

.consistency__item-diff-label {
  color: var(--velo-text-muted);
  flex-shrink: 0;
}

.consistency__item-diff-val {
  color: var(--velo-text-secondary);
  font-weight: 500;
}

.consistency__item-diff-val--alert {
  color: #DC2626;
  font-weight: 700;
}
</style>
