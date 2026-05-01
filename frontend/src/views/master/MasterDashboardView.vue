<!--
  VELO Frontend -- MasterDashboardView (Phase F6.2; refreshed S4 P14 C57)

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

  Path Y MEDIUM (#047). No emojis (#048): icons + Velo DS components.
  PRACTICE_TYPE_ICON migration: replaced legacy emoji map per #048.
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
      <!-- Greeting + status -->
      <header class="master-dashboard__greeting">
        <div>
          <p class="master-dashboard__greeting-time">
            {{ greetingPrefix }}
          </p>
          <h1 class="master-dashboard__greeting-name">
            {{ displayName }}
          </h1>
          <VBadge variant="success">
            <IconCheck :size="14" />
            <span>Верифицирован</span>
          </VBadge>
        </div>
        <VAvatar
          :name="displayName"
          size="md"
        />
      </header>

      <!-- Balance card -->
      <button
        type="button"
        class="master-dashboard__balance-card"
        @click="router.push({ name: 'master-finance' })"
      >
        <div class="master-dashboard__balance-label">
          Доступно к выводу
        </div>
        <div class="master-dashboard__balance-value">
          {{ formattedAvailable }}
        </div>
        <div
          v-if="frozenCents > 0"
          class="master-dashboard__balance-frozen"
        >
          Заморожено: {{ formattedFrozen }}
        </div>
        <span class="master-dashboard__balance-arrow">
          <IconArrowForward :size="20" />
        </span>
      </button>

      <!-- Stats grid (with period toggle); F7/F9 — real data; placeholders for now -->
      <div class="master-dashboard__section-header">
        <h3 class="master-dashboard__section-title">
          Моя статистика
        </h3>
        <button
          type="button"
          class="master-dashboard__period-toggle"
          aria-label="Переключить период"
          @click="togglePeriod"
        >
          {{ period === 'week' ? 'Неделя' : 'Месяц' }}
          <IconChevronDown :size="14" />
        </button>
      </div>

      <div class="master-dashboard__stats-grid">
        <StatCard
          value="—"
          label="практик"
        />
        <StatCard
          value="—"
          label="участников"
        />
        <StatCard
          value="—"
          label="доход"
        />
      </div>

      <!-- AI summary placeholder (BEC § A.8 mock-until-ready) -->
      <AICommentaryCard
        title="Саммари недели"
        body="Аналитика по итогам практик появится здесь после проведения первых занятий."
        :is-placeholder="true"
      />

      <!-- Nearest practice -->
      <h3 class="master-dashboard__section-title">
        Ближайшая практика
      </h3>

      <template v-if="masterStore.practicesLoading">
        <div class="master-dashboard__loading-row">
          <VLoader size="sm" />
        </div>
      </template>

      <template v-else-if="nearestPractice">
        <button
          type="button"
          class="master-dashboard__practice-card"
          @click="router.push({ name: 'master-practice-edit', params: { id: nearestPractice.id } })"
        >
          <div class="master-dashboard__practice-header">
            <span class="master-dashboard__practice-icon">
              <component
                :is="practiceIconFor(nearestPractice.practice_type)"
                :size="28"
              />
            </span>
            <div class="master-dashboard__practice-info">
              <div class="master-dashboard__practice-title">
                {{ nearestPractice.title }}
              </div>
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
        </button>
      </template>

      <template v-else>
        <VEmptyState
          title="Нет предстоящих практик"
          description="Создайте первую практику"
        >
          <VButton
            size="sm"
            variant="outline"
            @click="router.push({ name: 'master-practice-new' })"
          >
            Создать
          </VButton>
        </VEmptyState>
      </template>

      <!-- Quick actions -->
      <h3 class="master-dashboard__section-title">
        Быстрые действия
      </h3>
      <div class="master-dashboard__actions-grid">
        <button
          type="button"
          class="master-dashboard__action-btn"
          @click="router.push({ name: 'master-practice-new' })"
        >
          <span class="master-dashboard__action-icon">
            <IconEdit :size="22" />
          </span>
          <span class="master-dashboard__action-label">Создать практику</span>
        </button>
        <button
          type="button"
          class="master-dashboard__action-btn"
          @click="router.push({ name: 'master-practices' })"
        >
          <span class="master-dashboard__action-icon">
            <IconCalendar :size="22" />
          </span>
          <span class="master-dashboard__action-label">Мои практики</span>
        </button>
        <button
          type="button"
          class="master-dashboard__action-btn"
          @click="router.push({ name: 'master-analytics' })"
        >
          <span class="master-dashboard__action-icon">
            <IconBrain :size="22" />
          </span>
          <span class="master-dashboard__action-label">Аналитика</span>
        </button>
        <button
          type="button"
          class="master-dashboard__action-btn"
          @click="router.push({ name: 'master-finance' })"
        >
          <span class="master-dashboard__action-icon">
            <IconBookFeather :size="22" />
          </span>
          <span class="master-dashboard__action-label">Финансы</span>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { VBadge, VAvatar, VButton, VLoader, VEmptyState } from '@/components/ui'
import {
  IconCheck,
  IconArrowForward,
  IconChevronDown,
  IconCalendar,
  IconEdit,
  IconBrain,
  IconBookFeather,
  IconMeditation,
} from '@/components/icons'
import StatCard from '@/components/shared/StatCard.vue'
import AICommentaryCard from '@/components/shared/AICommentaryCard.vue'
import { useMasterStore } from '@/stores/master'
import { formatDate, formatDuration, formatMoney, formatParticipants } from '@/utils/format'
import { PRACTICE_TYPE_ICON } from '@/utils/displayHelpers'

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

const greetingPrefix = computed((): string => {
  const h = new Date().getHours()
  if (h < 5) return 'Доброй ночи,'
  if (h < 12) return 'Доброе утро,'
  if (h < 18) return 'Добрый день,'
  return 'Добрый вечер,'
})

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

// -- Practice type icon (PRACTICE_TYPE_ICON Component-map; #048 migration) --
function practiceIconFor(t: string): Component {
  return PRACTICE_TYPE_ICON[t] ?? IconMeditation
}

// -- Practice status badge helpers --
const STATUS_LABEL: Partial<Record<string, string>> = {
  draft: 'Черновик',
  scheduled: 'Запланирована',
  live: 'В эфире',
  completed: 'Завершена',
  cancelled: 'Отменена',
}
function statusLabel(s: string): string {
  return STATUS_LABEL[s] ?? s
}

function statusVariant(s: string): 'success' | 'warning' | 'error' | 'info' {
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

.master-dashboard__greeting-time {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.master-dashboard__greeting-name {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-2);
}

/* -- Balance card -- */
.master-dashboard__balance-card {
  position: relative;
  background: var(--steel-button);
  color: white;
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  cursor: pointer;
  text-align: left;
  transition: opacity var(--transition-fast);
  font-family: var(--font-body);
}

.master-dashboard__balance-card:active {
  opacity: 0.9;
}

.master-dashboard__balance-label {
  font-size: var(--text-sm);
  opacity: 0.85;
  margin-bottom: var(--space-1);
}

.master-dashboard__balance-value {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 400;
  letter-spacing: 0.02em;
}

.master-dashboard__balance-frozen {
  font-size: var(--text-xs);
  opacity: 0.75;
  margin-top: var(--space-1);
}

.master-dashboard__balance-arrow {
  position: absolute;
  top: 50%;
  right: var(--space-5);
  transform: translateY(-50%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* -- Section header with period toggle -- */
.master-dashboard__section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.master-dashboard__section-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--text-primary);
  margin: 0;
}

.master-dashboard__period-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-primary);
  padding: var(--space-1) var(--space-3);
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  background: var(--surface-steel-alpha-15);
  cursor: pointer;
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
  text-align: left;
  width: 100%;
  font-family: var(--font-body);
  transition: opacity var(--transition-fast);
}

.master-dashboard__practice-card:active {
  opacity: 0.85;
}

.master-dashboard__practice-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.master-dashboard__practice-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
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
  color: var(--text-secondary);
  margin-top: 2px;
}

.master-dashboard__practice-participants {
  font-family: var(--font-body);
  font-size: var(--text-sm);
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
  font-family: var(--font-body);
}

.master-dashboard__action-btn:hover {
  opacity: 0.9;
}

.master-dashboard__action-btn:active {
  opacity: 0.8;
}

.master-dashboard__action-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
}

.master-dashboard__action-label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-align: center;
}
</style>
