<!--
  VELO Frontend -- AdminReportDetailView (Phase F8.3, updated F8-fix S-1/S-2)

  Full report detail with resolve / dismiss actions.

  S-1/S-2: after resolve/dismiss use router.push({ name: 'admin-reports' })
  instead of router.back(). Guarantees a fresh mount of AdminReportsView
  and a fresh loadInitial() -- no stale reports shown.
-->

<template>
  <div class="report-detail">
    <VHeader
      title="Жалоба"
      :show-back="true"
      @back="router.back()"
    />

    <div class="report-detail__content">
      <!-- Loading -->
      <div
        v-if="loading"
        class="report-detail__loader"
      >
        <VLoader size="lg" />
      </div>

      <template v-else-if="report">
        <!-- Status + type header -->
        <div class="report-detail__header">
          <VBadge :variant="reportStatusVariant(currentStatus)">
            {{ reportStatusLabel(currentStatus) }}
          </VBadge>
          <span class="report-detail__type">
            {{ reportTargetLabel(report.target_type) }}
          </span>
        </div>

        <!-- Report content -->
        <div class="report-detail__section">
          <div class="report-detail__section-title">
            Текст жалобы
          </div>
          <div class="report-detail__reason">
            {{ report.reason }}
          </div>
        </div>

        <!-- Meta -->
        <div class="report-detail__section">
          <div class="report-detail__section-title">
            Детали
          </div>
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
              <span class="report-detail__meta-val">
                {{ formatDateTime(report.created_at) }}
              </span>
            </div>
            <template v-if="report.resolved_at">
              <div class="report-detail__meta-row">
                <span class="report-detail__meta-key">Обработана</span>
                <span class="report-detail__meta-val">
                  {{ formatDateTime(report.resolved_at) }}
                </span>
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
          <div class="report-detail__section">
            <div class="report-detail__section-title">
              Решить жалобу
            </div>
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
                @click="askResolveConfirm"
              >
                Решить
              </VButton>
            </div>
          </div>

          <div class="report-detail__section">
            <div class="report-detail__section-title">
              Отклонить жалобу
            </div>
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
                @click="askDismissConfirm"
              >
                Отклонить
              </VButton>
            </div>
          </div>
        </template>

        <!-- Already processed -->
        <div
          v-else
          class="report-detail__processed"
        >
          Жалоба уже обработана — статус:
          <strong>{{ reportStatusLabel(currentStatus) }}</strong>
        </div>
      </template>

      <!-- Not found -->
      <div
        v-else
        class="report-detail__not-found"
      >
        <VEmptyState
          title="Жалоба не найдена"
          description="Вернитесь к списку жалоб"
        />
        <VButton
          variant="outline"
          block
          @click="router.back()"
        >
          Назад
        </VButton>
      </div>
    </div>

    <!-- Resolve confirm modal -->
    <ConfirmModal
      v-model:visible="confirmResolve"
      :loading="resolving"
      title="Закрыть жалобу"
      message="Подтвердите решение. Жалоба будет помечена resolved."
      confirm-label="Решить"
      @confirm="onResolve"
      @cancel="confirmResolve = false"
    />

    <!-- Dismiss confirm modal -->
    <ConfirmModal
      v-model:visible="confirmDismiss"
      :loading="dismissing"
      :danger="true"
      title="Отклонить жалобу"
      message="Жалоба будет помечена dismissed. Действие фиксируется в audit log."
      confirm-label="Отклонить"
      @confirm="onDismiss"
      @cancel="confirmDismiss = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VBadge, VButton, VTextarea, VEmptyState, VLoader } from '@/components/ui'
import ConfirmModal from '@/components/shared/ConfirmModal.vue'
import { useToast } from '@/composables/useToast'
import { getReportById, resolveReport, dismissReport } from '@/api/admin'
import type { ReportResponse } from '@/api/admin'
import { ApiResponseError } from '@/api/client'
import {
  reportStatusVariant,
  reportStatusLabel,
  reportTargetLabel,
  formatDateTime,
} from '@/utils/adminHelpers'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const reportId = route.params.id as string

const report = ref<ReportResponse | null>(null)
const loading = ref(false)
const currentStatus = ref<string>('pending')

const resolveNote = ref('')
const resolveError = ref('')
const dismissNote = ref('')

const resolving = ref(false)
const dismissing = ref(false)
const anyLoading = computed(() => resolving.value || dismissing.value)

const confirmResolve = ref(false)
const confirmDismiss = ref(false)

function askResolveConfirm(): void {
  resolveError.value = ''
  if (!resolveNote.value.trim()) {
    resolveError.value = 'Введите примечание к решению'
    return
  }
  confirmResolve.value = true
}

function askDismissConfirm(): void {
  confirmDismiss.value = true
}

async function loadReport(): Promise<void> {
  const stateData = (history.state as { report?: ReportResponse }).report
  if (stateData && stateData.id === reportId) {
    report.value = stateData
    currentStatus.value = stateData.status
    return
  }
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
  if (resolving.value) return
  resolving.value = true
  try {
    await resolveReport(reportId, resolveNote.value.trim())
    toast.success('Жалоба решена')
    confirmResolve.value = false
    // S-1/S-2: push to list instead of back() -- guarantees fresh loadInitial().
    router.push({ name: 'admin-reports' })
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
    await dismissReport(reportId, dismissNote.value.trim() || undefined)
    toast.success('Жалоба отклонена')
    confirmDismiss.value = false
    // S-1/S-2: push to list instead of back() -- guarantees fresh loadInitial().
    router.push({ name: 'admin-reports' })
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

.report-detail__header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.report-detail__type {
  font-size: var(--text-sm);
  color: var(--text-muted);
  margin-left: auto;
}

.report-detail__section-title {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-2);
}

.report-detail__reason {
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-primary);
  line-height: 1.6;
}

.report-detail__meta-list {
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.report-detail__meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
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
  color: var(--text-muted);
  flex-shrink: 0;
}

.report-detail__meta-val {
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-primary);
  text-align: right;
}

.report-detail__meta-val--mono {
  font-family: monospace;
  font-size: var(--text-xs);
}

.report-detail__meta-note {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  margin-top: var(--space-1);
}

.report-detail__action-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.report-detail__processed {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--text-muted);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border-radius: var(--radius-lg);
}

.report-detail__not-found {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
</style>
