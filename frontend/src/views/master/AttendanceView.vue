<!--
  VELO Frontend -- AttendanceView (Phase F6.3)

  Attendance list and aggregates for a specific practice.
  Protected by masterStatusGuard. Rendered inside MasterShell.

  Data: GET /api/v1/practices/:id/attendance
  Returns: { total, attended, no_show, pending, items[] }

  Layout (matching mockup screen-attendance):
    - Practice title + date (from masterStore cache or fetched)
    - Aggregate stats: присутствовало / не пришли / ожидают
    - Sections: ✅ Присутствовали / ❌ Не пришли / ⏳ Ожидают
    - Each row: initials avatar, user_id (short), status icon, time
    - "Финализировать" button if practice status is live or scheduled

  Note on names: AttendanceItemResponse contains only user_id (UUID),
  not user display names. MVP shows first 8 chars of UUID as identifier.
  Full names require an additional endpoint (not in scope for F6).
-->

<template>
  <div class="attendance">
    <VHeader
      title="Посещаемость"
      show-back
      @back="router.push({ name: 'master-practice-edit', params: { id: practiceId } })"
    />

    <!-- Loading -->
    <div v-if="loading" class="attendance__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="attendance__content">
      <VEmptyState icon="⚠️" title="Не удалось загрузить посещаемость" :description="error">
        <VButton size="sm" variant="outline" @click="load">Повторить</VButton>
      </VEmptyState>
    </div>

    <template v-else-if="attendance">
      <div class="attendance__content">

        <!-- Practice subtitle -->
        <p v-if="practiceSubtitle" class="attendance__subtitle">
          {{ practiceSubtitle }}
        </p>

        <!-- ================================================================
             AGGREGATE STATS
             ================================================================ -->
        <div class="attendance__stats">
          <div class="attendance__stat attendance__stat--present">
            <div class="attendance__stat-value">{{ attendance.attended }}</div>
            <div class="attendance__stat-label">присутствовало</div>
          </div>
          <div class="attendance__stat attendance__stat--absent">
            <div class="attendance__stat-value">{{ attendance.no_show }}</div>
            <div class="attendance__stat-label">не пришли</div>
          </div>
          <div class="attendance__stat">
            <div class="attendance__stat-value">{{ attendance.pending }}</div>
            <div class="attendance__stat-label">ожидают</div>
          </div>
        </div>

        <div class="attendance__divider" />

        <!-- ================================================================
             FINALIZE BUTTON (live / scheduled -> completed)
             ================================================================ -->
        <VButton
          v-if="canFinalize"
          variant="primary"
          block
          :loading="finalizing"
          @click="confirmFinalize"
        >
          ✅ Финализировать практику
        </VButton>

        <!-- ================================================================
             ✅ ATTENDED
             ================================================================ -->
        <template v-if="attendedItems.length > 0">
          <div class="attendance__section-title attendance__section-title--present">
            ✅ Присутствовали ({{ attendedItems.length }})
          </div>
          <div
            v-for="item in attendedItems"
            :key="item.booking_id"
            class="attendance__row"
          >
            <div class="attendance__avatar">{{ initials(item.user_id) }}</div>
            <div class="attendance__row-info">
              <div class="attendance__row-name">{{ shortId(item.user_id) }}</div>
              <div v-if="item.joined_at" class="attendance__row-meta">
                Зашёл: {{ formatTime(item.joined_at) }}
              </div>
            </div>
            <span class="attendance__row-badge attendance__row-badge--present">✓</span>
          </div>
        </template>

        <!-- ================================================================
             ❌ NO_SHOW
             ================================================================ -->
        <template v-if="noShowItems.length > 0">
          <div class="attendance__section-title attendance__section-title--absent">
            ❌ Не пришли ({{ noShowItems.length }})
          </div>
          <div
            v-for="item in noShowItems"
            :key="item.booking_id"
            class="attendance__row"
          >
            <div class="attendance__avatar attendance__avatar--absent">{{ initials(item.user_id) }}</div>
            <div class="attendance__row-info">
              <div class="attendance__row-name">{{ shortId(item.user_id) }}</div>
              <div class="attendance__row-meta">Не отметился</div>
            </div>
            <span class="attendance__row-badge attendance__row-badge--absent">✗</span>
          </div>
        </template>

        <!-- ================================================================
             ⏳ PENDING (confirmed but not yet resolved)
             ================================================================ -->
        <template v-if="pendingItems.length > 0">
          <div class="attendance__section-title">
            ⏳ Ожидают ({{ pendingItems.length }})
          </div>
          <div
            v-for="item in pendingItems"
            :key="item.booking_id"
            class="attendance__row"
          >
            <div class="attendance__avatar attendance__avatar--pending">{{ initials(item.user_id) }}</div>
            <div class="attendance__row-info">
              <div class="attendance__row-name">{{ shortId(item.user_id) }}</div>
              <div class="attendance__row-meta">Ожидает отметки</div>
            </div>
            <span class="attendance__row-badge attendance__row-badge--pending">⏳</span>
          </div>
        </template>

        <!-- Empty state -->
        <VEmptyState
          v-if="attendance.total === 0"
          icon="👥"
          title="Нет записавшихся"
          description="На эту практику ещё никто не записался"
        />
      </div>

      <!-- Confirm dialog -->
      <Teleport to="body">
        <div v-if="confirmVisible" class="attendance__overlay" @click.self="confirmVisible = false">
          <div class="attendance__dialog">
            <p class="attendance__dialog-text">
              Финализировать практику? Посещаемость будет зафиксирована, замороженные средства разморожены.
            </p>
            <div class="attendance__dialog-actions">
              <VButton variant="ghost" @click="confirmVisible = false">Отмена</VButton>
              <VButton variant="primary" :loading="finalizing" @click="finalize">
                Финализировать
              </VButton>
            </div>
          </div>
        </div>
      </Teleport>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VHeader, VButton, VLoader, VEmptyState } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useMasterStore } from '@/stores/master'
import { getAttendance, finalizePractice, getPractice } from '@/api/practices'
import { formatTime } from '@/utils/format'
import { ApiResponseError } from '@/api/client'
import type { AttendanceResponse, AttendanceItemResponse, PracticeResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const masterStore = useMasterStore()

const practiceId = route.params.id as string

// -- Data --
const attendance = ref<AttendanceResponse | null>(null)
const practice = ref<PracticeResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// -- Action state --
const finalizing = ref(false)
const confirmVisible = ref(false)

// -- Practice subtitle (title + date) from cache or fetched --
const practiceSubtitle = computed((): string => {
  if (!practice.value) return ''
  const dt = new Date(practice.value.scheduled_at)
  const dateStr = dt.toLocaleDateString('ru', {
    day: 'numeric',
    month: 'short',
    timeZone: practice.value.timezone,
  })
  return `${practice.value.title} · ${dateStr}`
})

// -- Can finalize (practice is live or scheduled and not yet completed) --
const canFinalize = computed((): boolean => {
  const s = practice.value?.status
  return s === 'live' || s === 'scheduled'
})

// -- Filtered item lists --
const attendedItems = computed((): AttendanceItemResponse[] =>
  attendance.value?.items.filter((i) => i.status === 'attended') ?? [],
)

const noShowItems = computed((): AttendanceItemResponse[] =>
  attendance.value?.items.filter((i) => i.status === 'no_show') ?? [],
)

const pendingItems = computed((): AttendanceItemResponse[] =>
  attendance.value?.items.filter(
    (i) => i.status === 'pending' || i.status === 'confirmed',
  ) ?? [],
)

// -- Display helpers --
// UUID first 2 chars as initials (no real names in AttendanceItemResponse)
function initials(userId: string): string {
  return userId.slice(0, 2).toUpperCase()
}

// Short UUID prefix for display
function shortId(userId: string): string {
  return `#${userId.slice(0, 8)}`
}

// -- Load attendance + practice --
async function load(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    // Load in parallel: attendance data + practice info for subtitle/canFinalize
    const [attendanceData] = await Promise.all([
      getAttendance(practiceId),
      loadPractice(),
    ])
    attendance.value = attendanceData
  } catch (e) {
    error.value = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

async function loadPractice(): Promise<void> {
  // Try store cache first
  const cached = masterStore.practices.find((p) => p.id === practiceId)
  if (cached) {
    practice.value = cached
    return
  }
  try {
    practice.value = await getPractice(practiceId)
  } catch {
    // Non-critical: subtitle and finalize button just won't show
  }
}

onMounted(load)

// -- Confirm finalize --
function confirmFinalize(): void {
  confirmVisible.value = true
}

// -- Finalize --
async function finalize(): Promise<void> {
  if (finalizing.value) return
  finalizing.value = true
  try {
    const updated = await finalizePractice(practiceId)
    practice.value = updated
    confirmVisible.value = false
    toast.success('Практика завершена!')
    await masterStore.refreshMyPractices()
    // Reload attendance to reflect resolved statuses
    const fresh = await getAttendance(practiceId)
    attendance.value = fresh
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось финализировать')
  } finally {
    finalizing.value = false
  }
}
</script>

<style scoped>
.attendance {
  min-height: 100%;
  background: linear-gradient(135deg, var(--velo-bg-start) 0%, var(--velo-bg-end) 100%);
  display: flex;
  flex-direction: column;
}

.attendance__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-12) 0;
}

.attendance__content {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* -- Subtitle -- */
.attendance__subtitle {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
}

/* -- Aggregate stats (matches mockup .attendance-stats) -- */
.attendance__stats {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  padding: var(--space-4) 0;
}

.attendance__stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  flex: 1;
}

.attendance__stat-value {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--velo-text-primary);
}

.attendance__stat--present .attendance__stat-value {
  color: var(--velo-success);
}

.attendance__stat--absent .attendance__stat-value {
  color: var(--velo-error);
}

.attendance__stat-label {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  text-align: center;
}

/* -- Divider -- */
.attendance__divider {
  height: 1px;
  background: var(--velo-border);
}

/* -- Section titles -- */
.attendance__section-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--velo-text-secondary);
  padding: var(--space-2) 0 var(--space-1);
}

.attendance__section-title--present {
  color: var(--velo-success);
}

.attendance__section-title--absent {
  color: var(--velo-error);
}

/* -- Row (matches mockup .attendee-item / .detail-list-item) -- */
.attendance__row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--velo-border);
}

.attendance__row:last-child {
  border-bottom: none;
}

/* -- Avatar (initials) -- */
.attendance__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--velo-primary);
  color: white;
  font-size: var(--text-sm);
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.attendance__avatar--absent {
  background: var(--velo-error);
  opacity: 0.7;
}

.attendance__avatar--pending {
  background: var(--velo-text-muted);
}

/* -- Row info -- */
.attendance__row-info {
  flex: 1;
  min-width: 0;
}

.attendance__row-name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-text-primary);
  font-family: var(--font-mono, monospace);
}

.attendance__row-meta {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  margin-top: 2px;
}

/* -- Status badge -- */
.attendance__row-badge {
  font-size: var(--text-base);
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.attendance__row-badge--present {
  background: var(--velo-success);
  color: white;
  font-size: var(--text-xs);
  font-weight: 700;
}

.attendance__row-badge--absent {
  background: var(--velo-error);
  color: white;
  font-size: var(--text-xs);
  font-weight: 700;
}

.attendance__row-badge--pending {
  font-size: var(--text-sm);
}

/* -- Confirm overlay -- */
.attendance__overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  z-index: var(--z-modal, 400);
  padding: var(--space-4);
}

.attendance__dialog {
  width: 100%;
  background: var(--velo-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.attendance__dialog-text {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  text-align: center;
  line-height: 1.5;
}

.attendance__dialog-actions {
  display: flex;
  gap: var(--space-3);
}

.attendance__dialog-actions > * {
  flex: 1;
}
</style>
