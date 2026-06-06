<!--
  VELO Frontend -- AdminConsistencyView (Phase F8.3, updated F8-fix S-3)

  Data consistency semaphores: 21 checks grouped by category.
  S-3: separate `rerunning` ref for the re-run button -- initial load uses
  `loading` (shows full skeleton), re-run uses `rerunning` (inline spinner
  on button only, existing results stay visible).
-->

<template>
  <div class="consistency">
    <VHeader title="Семафоры" />

    <div class="consistency__content">
      <!-- Initial loading -->
      <div v-if="loading" class="consistency__loader">
        <VLoader size="lg" />
      </div>

      <template v-else-if="data">
        <!-- Summary bar -->
        <div
          class="consistency__summary"
          :class="data.alert_count > 0
            ? 'consistency__summary--alert'
            : 'consistency__summary--ok'"
        >
          <div class="consistency__summary-left">
            <span class="consistency__summary-icon">
              {{ data.alert_count > 0 ? '🔴' : '✅' }}
            </span>
            <div>
              <div class="consistency__summary-title">
                {{ data.alert_count > 0
                  ? `${data.alert_count} проблем обнаружено`
                  : 'Все проверки пройдены' }}
              </div>
              <div class="consistency__summary-sub">
                {{ data.ok_count }} / {{ data.total }} OK
              </div>
            </div>
          </div>
          <!-- S-3: rerunning ref -- only button spins, results stay visible. -->
          <VButton variant="outline" size="sm" :loading="rerunning" @click="rerun">
            ↺
          </VButton>
        </div>

        <!-- Run timestamp -->
        <div class="consistency__run-at">
          Проверено: {{ formatDateTime(data.run_at) }}
        </div>

        <!-- Groups -->
        <div
          v-for="[category, group] in groupedItems"
          :key="category"
          class="consistency__group"
        >
          <div class="consistency__group-title">{{ category }}</div>
          <div class="consistency__group-list">
            <div
              v-for="item in group"
              :key="item.name"
              class="consistency__item"
              :class="item.status === 'ALERT'
                ? 'consistency__item--alert'
                : 'consistency__item--ok'"
            >
              <div class="consistency__item-header">
                <span class="consistency__item-icon">
                  {{ item.status === 'ALERT' ? '🔴' : '✅' }}
                </span>
                <span class="consistency__item-name">{{ item.name }}</span>
                <VBadge
                  :variant="criticalityVariant(item.criticality)"
                  class="consistency__item-crit"
                >
                  {{ item.criticality }}
                </VBadge>
              </div>
              <div v-if="item.status === 'ALERT'" class="consistency__item-detail">
                <span class="consistency__item-expected">
                  ожидалось: {{ item.expected }}
                </span>
                <span class="consistency__item-actual">
                  фактически: {{ item.actual }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Error -->
      <VEmptyState
        v-else
        icon="⚠️"
        title="Не удалось загрузить данные"
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
import { formatDateTime } from '@/utils/adminHelpers'

const toast = useToast()

const data = ref<ConsistencyResponse | null>(null)
// S-3: two separate loading states.
// `loading` -- initial fetch (shows full skeleton).
// `rerunning` -- re-run button (inline spinner, existing results stay visible).
const loading = ref(false)
const rerunning = ref(false)

const groupedItems = computed((): [string, SemaphoreResult[]][] => {
  if (!data.value) return []
  const map = new Map<string, SemaphoreResult[]>()
  for (const item of data.value.items) {
    const list = map.get(item.category) ?? []
    list.push(item)
    map.set(item.category, list)
  }
  return Array.from(map.entries())
})

function criticalityVariant(c: string): 'error' | 'warning' | 'info' {
  if (c === 'critical') return 'error'
  if (c === 'warning') return 'warning'
  return 'info'
}

async function loadData(): Promise<void> {
  loading.value = true
  try {
    data.value = await getConsistency()
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки семафоров'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

// S-3: re-run triggered by button -- keeps existing data visible, only
// spins the button. Replaces data silently on success.
async function rerun(): Promise<void> {
  if (rerunning.value) return
  rerunning.value = true
  try {
    data.value = await getConsistency()
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка повторного запуска'
    toast.error(msg)
  } finally {
    rerunning.value = false
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
  justify-content: space-between;
  gap: var(--space-3);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  border: 1px solid;
}

.consistency__summary--ok {
  background: var(--velo-success-bg);
  border-color: var(--velo-success);
}

.consistency__summary--alert {
  background: var(--velo-error-bg);
  border-color: var(--velo-error-border);
}

.consistency__summary-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.consistency__summary-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.consistency__summary-title {
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-primary);
}

.consistency__summary-sub {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  margin-top: 2px;
}

/* -- Run at -- */
.consistency__run-at {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  text-align: right;
}

/* -- Group -- */
.consistency__group-title {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-2);
}

.consistency__group-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* -- Item -- */
.consistency__item {
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  border: 1px solid;
}

.consistency__item--ok {
  background: var(--velo-bg-card-solid);
  border-color: var(--velo-border-card);
}

.consistency__item--alert {
  background: var(--velo-error-bg-subtle);
  border-color: var(--velo-error-border);
}

.consistency__item-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.consistency__item-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.consistency__item-name {
  flex: 1;
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-primary);
}

.consistency__item-crit {
  flex-shrink: 0;
}

.consistency__item-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px solid var(--velo-error-border);
}

.consistency__item-expected {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

.consistency__item-actual {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-error-text);
}
</style>
