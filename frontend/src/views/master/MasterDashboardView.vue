<!--
  VELO Frontend -- MasterDashboardView (Phase F6.2)

  Master dashboard. Rendered inside MasterShell (with tab bar).

  Real data (from stores):
    - display_name, status (masterStore.profile)
    - available_cents balance (masterStore.profile.available_cents)
    - nearest upcoming practice (derived from masterStore.practices)

  Placeholder data (no API in F6, future F7/F9):
    - Stats grid (practices count, participants, income) -- shows "—"
    - AI summary card -- static placeholder text
    - Period toggle (Неделя / Месяц) -- visual only, no data change

  On mount:
    - fetchMyProfile (lazy, skips if loaded by masterStatusGuard)
    - fetchMyPractices (lazy, skips if already loaded)

  Quick actions:
    - "Создать практику" -> /master/practices/new
    - "Мои практики"    -> /master/practices
    - "Аналитика"       -> /master/analytics
    - "Финансы"         -> /master/finance
-->

<template>
  <div class="master-dashboard">
    <!-- Loading skeleton -->
    <template v-if="masterStore.profileLoading && !masterStore.profile">
      <div class="master-dashboard__skeleton">
        <VLoader size="lg" />
      </div>
    </template>

    <template v-else>
      <!-- ================================================================
           GREETING + STATUS
           ================================================================ -->
      <div class="master-dashboard__greeting">
        <div>
          <h2 class="master-dashboard__greeting-name">
            Привет, {{ displayName }}! 👋
          </h2>
          <VBadge variant="success">✓ Верифицирован</VBadge>
        </div>
        <VAvatar :name="displayName" size="md" />
      </div>

      <!-- ================================================================
           BALANCE CARD
           ================================================================ -->
      <div class="master-dashboard__balance-card" @click="router.push({ name: 'master-finance' })">
        <div class="master-dashboard__balance-label">Доступно к выводу</div>
        <div class="master-dashboard__balance-value">{{ formattedAvailable }}</div>
        <div v-if="frozenCents > 0" class="master-dashboard__balance-frozen">
          Заморожено: {{ formattedFrozen }}
        </div>
        <span class="master-dashboard__balance-arrow">→</span>
      </div>

      <!-- ================================================================
           STATS GRID (with period toggle)
           F7/F9: real data. For now shows "—" placeholders.
           ================================================================ -->
      <div class="master-dashboard__section-header">
        <span class="master-dashboard__section-title">📊 Моя статистика</span>
        <button class="master-dashboard__period-toggle" aria-label="Переключить период" @click="togglePeriod">
          {{ period === 'week' ? 'Неделя ▼' : 'Месяц ▼' }}
        </button>
      </div>

      <div class="master-dashboard__stats-grid">
        <div class="master-dashboard__stat-card">
          <div class="master-dashboard__stat-value">—</div>
          <div class="master-dashboard__stat-label">практик</div>
        </div>
        <div class="master-dashboard__stat-card">
          <div class="master-dashboard__stat-value">—</div>
          <div class="master-dashboard__stat-label">участников</div>
        </div>
        <div class="master-dashboard__stat-card">
          <div class="master-dashboard__stat-value">—</div>
          <div class="master-dashboard__stat-label">доход</div>
        </div>
      </div>

      <div class="master-dashboard__divider" />

      <!-- ================================================================
           AI SUMMARY (placeholder — F9)
           ================================================================ -->
      <div class="master-dashboard__ai-card">
        <div class="master-dashboard__ai-header">🧠 Саммари недели</div>
        <div class="master-dashboard__ai-content">
          Аналитика по итогам практик появится здесь после проведения
          первых занятий.
        </div>
      </div>

      <div class="master-dashboard__divider" />

      <!-- ================================================================
           NEAREST PRACTICE
           ================================================================ -->
      <div class="master-dashboard__section-title">📅 Ближайшая практика</div>

      <template v-if="masterStore.practicesLoading">
        <div class="master-dashboard__loading-row">
          <VLoader size="sm" />
        </div>
      </template>

      <template v-else-if="nearestPractice">
        <div
          class="master-dashboard__practice-card"
          @click="router.push({ name: 'master-practice-edit', params: { id: nearestPractice.id } })"
        >
          <div class="master-dashboard__practice-header">
            <span class="master-dashboard__practice-icon">{{ typeEmoji(nearestPractice.practice_type) }}</span>
            <div class="master-dashboard__practice-info">
              <div class="master-dashboard__practice-title">{{ nearestPractice.title }}</div>
              <div class="master-dashboard__practice-meta">
                {{ formatDate(nearestPractice.scheduled_at, nearestPractice.timezone) }}
                · {{ formatDuration(nearestPractice.duration_minutes) }}
              </div>
            </div>
            <VBadge :variant="statusVariant(nearestPractice.status)">
              {{ statusLabel(nearestPractice.status) }}
            </VBadge>
          </div>
          <div class="master-dashboard__practice-participants">
            {{ formatParticipants(nearestPractice.current_participants, nearestPractice.max_participants) }}
            · {{ formatMoney(nearestPractice.price_cents, nearestPractice.currency) }}
          </div>
        </div>
      </template>

      <template v-else>
        <VEmptyState
          icon="📅"
          title="Нет предстоящих практик"
          description="Создайте первую практику"
        >
          <VButton size="sm" variant="outline" @click="router.push({ name: 'master-practice-new' })">
            Создать
          </VButton>
        </VEmptyState>
      </template>

      <div class="master-dashboard__divider" />

      <!-- ================================================================
           QUICK ACTIONS
           ================================================================ -->
      <div class="master-dashboard__section-title">⚡ Быстрые действия</div>
      <div class="master-dashboard__actions-grid">
        <button
          class="master-dashboard__action-btn"
          @click="router.push({ name: 'master-practice-new' })"
        >
          <span class="master-dashboard__action-icon">➕</span>
          <span class="master-dashboard__action-label">Создать практику</span>
        </button>
        <button
          class="master-dashboard__action-btn"
          @click="router.push({ name: 'master-practices' })"
        >
          <span class="master-dashboard__action-icon">📋</span>
          <span class="master-dashboard__action-label">Мои практики</span>
        </button>
        <button
          class="master-dashboard__action-btn"
          @click="router.push({ name: 'master-analytics' })"
        >
          <span class="master-dashboard__action-icon">📈</span>
          <span class="master-dashboard__action-label">Аналитика</span>
        </button>
        <button
          class="master-dashboard__action-btn"
          @click="router.push({ name: 'master-finance' })"
        >
          <span class="master-dashboard__action-icon">💰</span>
          <span class="master-dashboard__action-label">Финансы</span>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VBadge, VAvatar, VButton, VLoader, VEmptyState } from '@/components/ui'
import { useMasterStore } from '@/stores/master'
import { formatDate, formatDuration, formatMoney, formatParticipants } from '@/utils/format'
import { PRACTICE_TYPE_EMOJI } from '@/utils/displayHelpers'
import type { PracticeType, PracticeStatus } from '@/api/types'

const router = useRouter()
const masterStore = useMasterStore()

// -- Period toggle (visual only -- no real data until F9) --
const period = ref<'week' | 'month'>('week')
function togglePeriod(): void {
  period.value = period.value === 'week' ? 'month' : 'week'
}

// -- Display name fallback --
const displayName = computed((): string =>
  masterStore.profile?.display_name ?? 'Мастер',
)

// -- Balance values --
const frozenCents = computed(() => masterStore.profile?.frozen_cents ?? 0)

const formattedAvailable = computed(() =>
  formatMoney(masterStore.profile?.available_cents ?? 0, 'EUR', 'ru', true),
)

const formattedFrozen = computed(() =>
  formatMoney(frozenCents.value, 'EUR', 'ru', true),
)

// -- Nearest upcoming / live practice --
// Sorted ascending by scheduled_at; picks first scheduled or live.
const nearestPractice = computed(() => {
  const upcoming = masterStore.practices
    .filter((p) => p.status === 'scheduled' || p.status === 'live')
    .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())
  return upcoming[0] ?? null
})

// -- Practice type emoji -- imported from displayHelpers
function typeEmoji(t: PracticeType): string {
  return PRACTICE_TYPE_EMOJI[t] ?? '🧘'
}

// -- Practice status badge helpers --
const STATUS_LABEL: Partial<Record<PracticeStatus, string>> = {
  draft: 'Черновик',
  scheduled: 'Запланирована',
  live: 'В эфире',
  completed: 'Завершена',
  cancelled: 'Отменена',
}
function statusLabel(s: PracticeStatus): string {
  return STATUS_LABEL[s] ?? s
}

function statusVariant(s: PracticeStatus): 'success' | 'warning' | 'error' | 'info' {
  switch (s) {
    case 'live':      return 'success'
    case 'scheduled': return 'info'
    case 'draft':     return 'warning'
    default:          return 'error'
  }
}

// -- Load data on mount --
onMounted(async () => {
  // Both calls are lazy -- skip if already populated by guard / prior navigation.
  await masterStore.fetchMyProfile()
  await masterStore.fetchMyPractices()
})
</script>

<style scoped>
.master-dashboard {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* -- Skeleton / loader -- */
.master-dashboard__skeleton {
  display: flex;
  justify-content: center;
  padding: var(--space-12) 0;
}

/* -- Greeting -- */
.master-dashboard__greeting {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.master-dashboard__greeting-name {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-2);
}

/* -- Balance card -- */
.master-dashboard__balance-card {
  position: relative;
  background: var(--steel-button);
  color: white;
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.master-dashboard__balance-card:active {
  opacity: 0.9;
}

.master-dashboard__balance-label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  opacity: 0.8;
  margin-bottom: var(--space-1);
}

.master-dashboard__balance-value {
  font-family: var(--font-body);
  font-size: var(--text-3xl);
  font-weight: 400;
  letter-spacing: 0.02em;
}

.master-dashboard__balance-frozen {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  opacity: 0.7;
  margin-top: var(--space-1);
}

.master-dashboard__balance-arrow {
  position: absolute;
  top: 50%;
  right: var(--space-5);
  transform: translateY(-50%);
  font-size: var(--text-xl);
  opacity: 0.8;
}

/* -- Section header with period toggle -- */
.master-dashboard__section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.master-dashboard__section-title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.master-dashboard__period-toggle {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--steel-button);
  padding: var(--space-1) var(--space-2);
  border-radius: 100px;
  background: var(--surface-steel-alpha-15);
  transition: opacity var(--transition-fast);
}

.master-dashboard__period-toggle:hover {
  opacity: 0.9;
}

/* -- Stats grid -- */
.master-dashboard__stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.master-dashboard__stat-card {
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  text-align: center;
}

.master-dashboard__stat-value {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--text-primary);
}

.master-dashboard__stat-label {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--text-muted);
  margin-top: 2px;
}

/* -- Divider -- */
.master-dashboard__divider {
  height: 1px;
  background: var(--border-subtle);
}

/* -- AI summary card -- */
.master-dashboard__ai-card {
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.master-dashboard__ai-header {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.master-dashboard__ai-content {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-muted);
  line-height: 1.6;
}

/* -- Loading row -- */
.master-dashboard__loading-row {
  display: flex;
  justify-content: center;
  padding: var(--space-4) 0;
}

/* -- Nearest practice card -- */
.master-dashboard__practice-card {
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.master-dashboard__practice-card:active {
  opacity: 0.8;
}

.master-dashboard__practice-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.master-dashboard__practice-icon {
  font-size: 24px;
  flex-shrink: 0;
  line-height: 1;
}

.master-dashboard__practice-info {
  flex: 1;
  min-width: 0;
}

.master-dashboard__practice-title {
  font-family: var(--font-body);
  font-weight: 400;
  color: var(--text-primary);
  font-size: var(--text-base);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.master-dashboard__practice-meta {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-muted);
  margin-top: 2px;
}

.master-dashboard__practice-participants {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-secondary);
}

/* -- Quick actions grid -- */
.master-dashboard__actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.master-dashboard__action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  transition: opacity var(--transition-fast);
  cursor: pointer;
}

.master-dashboard__action-btn:hover {
  opacity: 0.9;
}

.master-dashboard__action-btn:active {
  opacity: 0.8;
}

.master-dashboard__action-icon {
  font-size: 28px;
  line-height: 1;
}

.master-dashboard__action-label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-secondary);
  text-align: center;
}
</style>
