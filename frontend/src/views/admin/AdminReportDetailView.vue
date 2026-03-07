<!--
  VELO Frontend -- AdminReportDetailView (Phase F8.3, updated F8-fix)

  Full report detail with resolve / dismiss actions.

  Data source: router state (history.state.report) from AdminReportsView.
  Fallback (W-2 fix): GET /api/v1/admin/reports/{id} -- single resource fetch,
  used when navigating directly by URL (refresh, deep link).

  Backend rules:
    resolve: resolution_note required (min 1)
    dismiss: resolution_note optional
-->

<template>
  <div class="report-detail">
    <VHeader title="Жалоба" :show-back="true" @back="router.back()" />

    <div class="report-detail__content">
      <!-- Loading -->
      <div v-if="loading" class="report-detail__loader">
        <VLoader size="lg" />
      </div>

      <template v-else-if="report">
        <!-- Status + type header -->
        <div class="report-detail__header">
          <VBadge :variant="statusVariant(currentStatus)">
            {{ statusLabel(currentStatus) }}
          </VBadge>
          <span class="report-detail__type">{{ targetLabel(report.target_type) }}</span>
        </div>

        <!-- Report content -->
        <div class="report-detail__section">
          <div class="report-detail__section-title">Текст жалобы</div>
          <div class="report-detail__reason">{{ report.reason }}</div>
        </div>

        <!-- Meta -->
        <div class="report-detail__section">
          <div class="report-detail__section-title">Детали</div>
          <div class="report-detail__meta-list">
            <div class="report-detail__meta-row">
              <span class="report-detail__meta-key">Тип цели</span>
              <span class="report-detail__meta-val">{{ report.target_type }}</span>
            </div>
            <div class="report-detail__meta-row">
              <span class="report-detail__meta-key">ID цели</span>
              <span class="report-detail__meta-val report-detail__meta-val--mono">
                {{ report.target_id.slice(0, 8) }}…
              </span>
            </div>
            <div class="report-detail__meta-row">
              <span class="report-detail__meta-key">Создана</span>
              <span class="report-detail__meta-val">{{ formatDate(report.created_at) }}</span>
            </div>
            <template v-if="report.resolved_at">
              <div class="report-detail__meta-row">
                <span class="report-detail__meta-key">Обработана</span>
                <span class="report-detail__meta-val">{{ formatDate(report.resolved_at) }}</span>
              </div>
            </template>
            <template v-if="report.resolution_note">
              <div class="report-detail__meta-row report-detail__meta-row--column">
                <span class="report-detail__meta-key">Примечание</span>
                <span class="report-detail__meta-note">{{ report.resolution_note }}</span>
              </div>
            </template>
          </div>
        </div>

        <!-- Actions: only for pending -->
        <template v-if="currentStatus === 'pending'">
          <!-- Resolve form -->
          <div class="report-detail__section">
            <div class="report-detail__section-title">Решить жалобу</div>
            <div class="report-detail__action-form">
              <VTextarea
                v-model="resolveNote"
                label="Примечание к решению *"
                placeholder="Опишите, какие меры приняты"
                :rows="3"
                :error="resolveError"
              />
              <VButton
                variant="primary"
                block
                :loading="resolving"
                :disabled="anyLoading"
                @click="onResolve"
              >
                ✅ Решить
              </VButton>
            </div>
          </div>

          <!-- Dismiss form -->
          <div class="report-detail__section">
            <div class="report-detail__section-title">Отклонить жалобу</div>
            <div class="report-detail__action-form">
              <VTextarea
                v-model="dismissNote"
                label="Примечание (необязательно)"
                placeholder="Причина отклонения"
                :rows="2"
              />
              <VButton
                variant="outline"
                block
                :loading="dismissing"
                :disabled="anyLoading"
                @click="onDismiss"
              >
                ❌ Отклонить
              </VButton>
            </div>
          </div>
        </template>

        <!-- Already processed -->
        <div v-else class="report-detail__processed">
          Жалоба уже обработана — статус: <strong>{{ statusLabel(currentStatus) }}</strong>
        </div>
      </template>

      <!-- Not found -->
      <div v-else class="report-detail__not-found">
        <VEmptyState
          icon="❓"
          title="Жалоба не найдена"
          description="Вернитесь к списку жалоб"
        />
        <VButton variant="outline" block @click="router.back()">Назад</VButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VBadge, VButton, VTextarea, VEmptyState, VLoader } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { getReportById, resolveReport, dismissReport } from '@/api/admin'
import type { ReportResponse } from '@/api/admin'
import { ApiResponseError } from '@/api/client'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const reportId = route.params.id as string

const report = ref<ReportResponse | null>(null)
const loading = ref(false)

// Local status -- updated after action to prevent double-submit UI.
const currentStatus = ref<string>('pending')

const resolveNote = ref('')
const resolveError = ref('')
const dismissNote = ref('')

const resolving = ref(false)
const dismissing = ref(false)
const anyLoading = computed(() => resolving.value || dismissing.value)

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
  return new Date(iso).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Load report: from router state (standard flow) or single fetch (fallback).
async function loadReport(): Promise<void> {
  // Standard flow: data passed from AdminReportsView via router state.
  const stateData = (history.state as { report?: ReportResponse }).report
  if (stateData && stateData.id === reportId) {
    report.value = stateData
    currentStatus.value = stateData.status
    return
  }

  // W-2 fix: fallback -- single resource fetch instead of showing empty state.
  loading.value = true
  try {
    const fetched = await getReportById(reportId)
    report.value = fetched
    currentStatus.value = fetched.status
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки жалобы'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

async function onResolve(): Promise<void> {
  resolveError.value = ''
  if (!resolveNote.value.trim()) {
    resolveError.value = 'Введите примечание к решению'
    return
  }
  if (resolving.value) return
  resolving.value = true
  try {
    const updated = await resolveReport(reportId, resolveNote.value.trim())
    currentStatus.value = updated.status
    toast.success('Жалоба решена')
    router.back()
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка при обработке'
    toast.error(msg)
  } finally {
    resolving.value = false
  }
}

async function onDismiss(): Promise<void> {
  if (dismissing.value) return
  dismissing.value = true
  try {
    const updated = await dismissReport(
      reportId,
      dismissNote.value.trim() || undefined,
    )
    currentStatus.value = updated.status
    toast.success('Жалоба отклонена')
    router.back()
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка при обработке'
    toast.error(msg)
  } finally {
    dismissing.value = false
  }
}

onMounted(loadReport)
</script>

<style scoped>
.report-detail {
  min-height: 100dvh;
}

.report-detail__content {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.report-detail__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

/* -- Header -- */
.report-detail__header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.report-detail__type {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  margin-left: auto;
}

/* -- Section -- */
.report-detail__section-title {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--velo-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-2);
}

.report-detail__reason {
  background: var(--velo-bg-card);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  line-height: 1.6;
}

/* -- Meta -- */
.report-detail__meta-list {
  background: var(--velo-bg-card);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.report-detail__meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--velo-border);
  gap: var(--space-2);
}

.report-detail__meta-row--column {
  flex-direction: column;
  align-items: flex-start;
}

.report-detail__meta-row:last-child {
  border-bottom: none;
}

.report-detail__meta-key {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  flex-shrink: 0;
}

.report-detail__meta-val {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-text-primary);
  text-align: right;
}

.report-detail__meta-val--mono {
  font-family: monospace;
  font-size: var(--text-xs);
}

.report-detail__meta-note {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.5;
  margin-top: var(--space-1);
}

/* -- Action forms -- */
.report-detail__action-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* -- Processed -- */
.report-detail__processed {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  padding: var(--space-4);
  background: var(--velo-bg-subtle);
  border-radius: var(--radius-lg);
}

.report-detail__not-found {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
</style>
