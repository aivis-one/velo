<!--
  VELO Frontend -- AnalyticsView (Phase F9.2)

  Master analytics hub. Route: /master/analytics (inside MasterShell).

  Two tabs (mockup M10):
    1. Отзывы   -- aggregated stats grid + rating progress bars
                   + past practices list with expandable insights
    2. Платежи  -- redirect card to MasterFinanceView

  Insights per practice are lazy-loaded when the user expands a row.
  They are cached locally (Map<practiceId, PracticeInsightsResponse>)
  to avoid repeated requests within the session.

  Aggregate stats grid at the top is computed from all cached insights.
  On mount we load insights for the first completed practice automatically
  so the grid is not empty on first open.

  Practices list comes from masterStore (already loaded by shell).
  Only 'completed' status practices are shown.
-->

<template>
  <div class="analytics">
    <!-- Header -->
    <header class="analytics__header">
      <h1 class="analytics__header-title">📈 Аналитика</h1>
    </header>

    <!-- Tabs -->
    <div class="analytics__tabs">
      <button
        class="analytics__tab"
        :class="{ 'analytics__tab--active': activeTab === 'reviews' }"
        @click="activeTab = 'reviews'"
      >
        Отзывы
      </button>
      <button
        class="analytics__tab"
        :class="{ 'analytics__tab--active': activeTab === 'payments' }"
        @click="activeTab = 'payments'"
      >
        Платежи
      </button>
    </div>

    <!-- ================================================================
         TAB: ОТЗЫВЫ
         ================================================================ -->
    <div v-show="activeTab === 'reviews'" class="analytics__body">

      <!-- Stats grid (aggregate from all cached insights) -->
      <div class="analytics__stats-grid">
        <div class="analytics__stat-card">
          <div class="analytics__stat-value">{{ aggregateCheckinPct }}</div>
          <div class="analytics__stat-label">Check-in</div>
        </div>
        <div class="analytics__stat-card">
          <div class="analytics__stat-value">{{ aggregateFeedbackPct }}</div>
          <div class="analytics__stat-label">Feedback</div>
        </div>
        <div class="analytics__stat-card">
          <div class="analytics__stat-value">{{ aggregateTotalFeedbacks }}</div>
          <div class="analytics__stat-label">отзывов</div>
        </div>
      </div>

      <div class="analytics__divider" />

      <!-- Overall rating distribution (from all cached insights) -->
      <div
        v-if="aggregateTotalFeedbacks > 0"
        class="analytics__section"
      >
        <div class="analytics__section-title">💬 Общая статистика</div>
        <div class="analytics__rating-bars">
          <div
            v-for="bar in ratingBars"
            :key="bar.key"
            class="analytics__rating-row"
          >
            <span class="analytics__rating-label">{{ bar.emoji }} {{ bar.label }}</span>
            <div class="analytics__rating-track">
              <div
                class="analytics__rating-fill"
                :style="{ width: `${bar.pct}%`, background: bar.color }"
              />
            </div>
            <span class="analytics__rating-meta">{{ bar.pct }}% ({{ bar.count }})</span>
          </div>
        </div>
      </div>

      <div class="analytics__divider" />

      <!-- Past practices list -->
      <div class="analytics__section">
        <div class="analytics__section-title">📅 Прошедшие практики</div>

        <!-- Practices loading -->
        <div v-if="masterStore.practicesLoading && pastPractices.length === 0" class="analytics__loader">
          <VLoader />
        </div>

        <!-- Empty -->
        <VEmptyState
          v-else-if="!masterStore.practicesLoading && pastPractices.length === 0"
          icon="📋"
          title="Нет завершённых практик"
          description="Здесь появятся данные после первой практики"
        />

        <!-- Practice rows -->
        <div v-else class="analytics__practice-list">
          <div
            v-for="practice in pastPractices"
            :key="practice.id"
            class="analytics__practice-card"
          >
            <!-- Row header (always visible) -->
            <div
              class="analytics__practice-row"
              @click="togglePractice(practice.id)"
            >
              <div class="analytics__practice-left">
                <span class="analytics__practice-emoji">{{ typeEmoji(practice.practice_type) }}</span>
                <div class="analytics__practice-info">
                  <div class="analytics__practice-title">{{ practice.title }}</div>
                  <div class="analytics__practice-meta">
                    {{ formatShortDate(practice.scheduled_at) }}
                    · {{ practice.current_participants }} участников
                  </div>
                </div>
              </div>

              <!-- Mini rating badges (shown if cached) -->
              <div v-if="insightsCache.has(practice.id)" class="analytics__practice-badges">
                <span>🔥 {{ ratingPct(practice.id, 'fire') }}%</span>
                <span>👍 {{ ratingPct(practice.id, 'good') }}%</span>
                <span>❓ {{ ratingPct(practice.id, 'confused') }}%</span>
              </div>

              <!-- Expand chevron -->
              <span
                class="analytics__practice-chevron"
                :class="{ 'analytics__practice-chevron--open': expandedId === practice.id }"
              >›</span>
            </div>

            <!-- Expanded insights panel -->
            <Transition name="expand">
              <div
                v-if="expandedId === practice.id"
                class="analytics__insights"
              >
                <!-- Loading insights -->
                <div v-if="loadingInsights.has(practice.id)" class="analytics__insights-loader">
                  <VLoader size="sm" />
                </div>

                <!-- Error -->
                <div v-else-if="insightsError.has(practice.id)" class="analytics__insights-error">
                  ⚠️ {{ insightsError.get(practice.id) }}
                  <button class="analytics__retry-btn" @click="loadInsights(practice.id)">
                    Повторить
                  </button>
                </div>

                <!-- Insights data -->
                <template v-else-if="insightsCache.has(practice.id)">
                  <div class="analytics__insights-stats">
                    <div class="analytics__insights-stat">
                      <span class="analytics__insights-stat-val">{{ insightsCache.get(practice.id)!.participants }}</span>
                      <span class="analytics__insights-stat-lbl">участников</span>
                    </div>
                    <div class="analytics__insights-stat">
                      <span class="analytics__insights-stat-val">{{ totalCheckins(practice.id) }}</span>
                      <span class="analytics__insights-stat-lbl">check-ins</span>
                    </div>
                    <div class="analytics__insights-stat">
                      <span class="analytics__insights-stat-val">{{ totalFeedbacks(practice.id) }}</span>
                      <span class="analytics__insights-stat-lbl">отзывов</span>
                    </div>
                  </div>

                  <!-- Feedback bars for this practice -->
                  <div
                    v-if="totalFeedbacks(practice.id) > 0"
                    class="analytics__insights-bars"
                  >
                    <div
                      v-for="bar in insightRatingBars(practice.id)"
                      :key="bar.key"
                      class="analytics__rating-row analytics__rating-row--compact"
                    >
                      <span class="analytics__rating-label">{{ bar.emoji }}</span>
                      <div class="analytics__rating-track">
                        <div
                          class="analytics__rating-fill"
                          :style="{ width: `${bar.pct}%`, background: bar.color }"
                        />
                      </div>
                      <span class="analytics__rating-meta">{{ bar.pct }}%</span>
                    </div>
                  </div>

                  <div v-else class="analytics__insights-empty">
                    Отзывов пока нет
                  </div>

                  <div v-if="insightsCache.get(practice.id)!.comments_count > 0" class="analytics__insights-comments">
                    💬 {{ insightsCache.get(practice.id)!.comments_count }} {{ pluralComments(insightsCache.get(practice.id)!.comments_count) }}
                  </div>
                </template>
              </div>
            </Transition>
          </div>

          <!-- Load more past practices -->
          <div v-if="masterStore.practicesHasMore" class="analytics__load-more">
            <VButton
              variant="ghost"
              block
              :loading="masterStore.practicesLoading"
              @click="masterStore.loadMorePractices()"
            >
              Показать ещё
            </VButton>
          </div>
        </div>
      </div>
    </div>

    <!-- ================================================================
         TAB: ПЛАТЕЖИ
         ================================================================ -->
    <div v-show="activeTab === 'payments'" class="analytics__body">
      <div class="analytics__section">
        <div class="analytics__section-title">💰 Финансы и выплаты</div>
        <p class="analytics__payments-hint">
          История транзакций, заработок и запрос на вывод средств доступны
          в разделе Финансы.
        </p>
        <VButton
          variant="primary"
          block
          size="lg"
          @click="router.push({ name: 'master-finance' })"
        >
          Перейти в Финансы →
        </VButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMasterStore } from '@/stores/master'
import { getPracticeInsights } from '@/api/diary'
import { useToast } from '@/composables/useToast'
import { ApiResponseError } from '@/api/client'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import { formatDate } from '@/utils/format'
import type { PracticeInsightsResponse, PracticeType } from '@/api/types'

const router = useRouter()
const masterStore = useMasterStore()
const toast = useToast()

// =========================================================================
// Tabs
// =========================================================================

const activeTab = ref<'reviews' | 'payments'>('reviews')

// =========================================================================
// Past practices (completed, sorted desc)
// =========================================================================

const pastPractices = computed(() =>
  masterStore.practices
    .filter((p) => p.status === 'completed')
    .sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime()),
)

// =========================================================================
// Insights cache (local, within this session)
// =========================================================================

// Using reactive Maps so Vue can track additions.
const insightsCache = reactive(new Map<string, PracticeInsightsResponse>())
const loadingInsights = reactive(new Set<string>())
const insightsError = reactive(new Map<string, string>())

const expandedId = ref<string | null>(null)

async function loadInsights(practiceId: string): Promise<void> {
  if (loadingInsights.has(practiceId)) return

  // Clear previous error for retry.
  insightsError.delete(practiceId)
  loadingInsights.add(practiceId)

  try {
    const data = await getPracticeInsights(practiceId)
    insightsCache.set(practiceId, data)
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки'
    insightsError.set(practiceId, msg)
  } finally {
    loadingInsights.delete(practiceId)
  }
}

function togglePractice(practiceId: string): void {
  if (expandedId.value === practiceId) {
    expandedId.value = null
    return
  }
  expandedId.value = practiceId
  // Lazy-load if not already cached.
  if (!insightsCache.has(practiceId)) {
    loadInsights(practiceId)
  }
}

// =========================================================================
// Aggregate stats (over all cached insights)
// =========================================================================

/** Sum of all feedback counts across cached insights. */
const aggregateTotalFeedbacks = computed((): number => {
  let total = 0
  insightsCache.forEach((ins) => {
    total += ins.feedbacks.fire + ins.feedbacks.good + ins.feedbacks.confused
  })
  return total
})

const aggregateTotalCheckins = computed((): number => {
  let total = 0
  insightsCache.forEach((ins) => {
    total += ins.checkins.high + ins.checkins.mid + ins.checkins.low
  })
  return total
})

const aggregateTotalParticipants = computed((): number => {
  let total = 0
  insightsCache.forEach((ins) => { total += ins.participants })
  return total
})

/** Check-in rate: checkins / participants across all cached. */
const aggregateCheckinPct = computed((): string => {
  if (aggregateTotalParticipants.value === 0) return '—'
  const pct = Math.round((aggregateTotalCheckins.value / aggregateTotalParticipants.value) * 100)
  return `${pct}%`
})

/** Feedback rate: feedbacks / participants across all cached. */
const aggregateFeedbackPct = computed((): string => {
  if (aggregateTotalParticipants.value === 0) return '—'
  const pct = Math.round((aggregateTotalFeedbacks.value / aggregateTotalParticipants.value) * 100)
  return `${pct}%`
})

// =========================================================================
// Aggregate rating progress bars
// =========================================================================

interface RatingBar {
  key: string
  emoji: string
  label: string
  count: number
  pct: number
  color: string
}

const RATING_BARS_CONFIG = [
  { key: 'fire',     emoji: '🔥', label: 'Огонь!',       color: '#DC2626' },
  { key: 'good',     emoji: '👍', label: 'Хорошо',       color: '#22C55E' },
  { key: 'confused', emoji: '❓', label: 'Есть вопросы', color: '#F59E0B' },
] as const

const ratingBars = computed((): RatingBar[] => {
  const totals = { fire: 0, good: 0, confused: 0 }
  insightsCache.forEach((ins) => {
    totals.fire     += ins.feedbacks.fire
    totals.good     += ins.feedbacks.good
    totals.confused += ins.feedbacks.confused
  })
  const total = totals.fire + totals.good + totals.confused

  return RATING_BARS_CONFIG.map((cfg) => ({
    ...cfg,
    count: totals[cfg.key],
    pct:   total > 0 ? Math.round((totals[cfg.key] / total) * 100) : 0,
  }))
})

// =========================================================================
// Per-practice helpers
// =========================================================================

function totalCheckins(practiceId: string): number {
  const ins = insightsCache.get(practiceId)
  if (!ins) return 0
  return ins.checkins.high + ins.checkins.mid + ins.checkins.low
}

function totalFeedbacks(practiceId: string): number {
  const ins = insightsCache.get(practiceId)
  if (!ins) return 0
  return ins.feedbacks.fire + ins.feedbacks.good + ins.feedbacks.confused
}

/** Percentage of a specific rating for a practice. */
function ratingPct(practiceId: string, rating: 'fire' | 'good' | 'confused'): number {
  const total = totalFeedbacks(practiceId)
  if (total === 0) return 0
  const ins = insightsCache.get(practiceId)!
  return Math.round((ins.feedbacks[rating] / total) * 100)
}

function insightRatingBars(practiceId: string): RatingBar[] {
  const total = totalFeedbacks(practiceId)
  return RATING_BARS_CONFIG.map((cfg) => {
    const count = insightsCache.get(practiceId)?.feedbacks[cfg.key] ?? 0
    return {
      ...cfg,
      count,
      pct: total > 0 ? Math.round((count / total) * 100) : 0,
    }
  })
}

// =========================================================================
// Type emoji
// =========================================================================

const TYPE_EMOJI: Record<PracticeType, string> = {
  live: '🧘', series: '🔄', one_on_one: '👤', replay: '📹',
}
function typeEmoji(t: PracticeType): string {
  return TYPE_EMOJI[t] ?? '🧘'
}

// =========================================================================
// Date / text helpers
// =========================================================================

function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

function pluralComments(n: number): string {
  if (n % 10 === 1 && n % 100 !== 11) return 'комментарий'
  if ([2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100)) return 'комментария'
  return 'комментариев'
}

// =========================================================================
// Lifecycle
// =========================================================================

onMounted(async () => {
  // Ensure practices are loaded (they usually are via masterStatusGuard /
  // MasterPracticesView but be safe).
  await masterStore.fetchMyPractices()

  // Pre-load insights for the most recent completed practice so the
  // stats grid is not empty on first open.
  const first = pastPractices.value[0]
  if (first) {
    await loadInsights(first.id)
  }
})
</script>

<style scoped>
.analytics {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

/* ===== Header ===== */
.analytics__header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--velo-border);
}

.analytics__header-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0;
}

/* ===== Tabs ===== */
.analytics__tabs {
  display: flex;
  border-bottom: 2px solid var(--velo-border);
}

.analytics__tab {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all var(--transition-fast);
}

.analytics__tab--active {
  color: var(--velo-primary);
  border-bottom-color: var(--velo-primary);
}

/* ===== Body ===== */
.analytics__body {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* ===== Stats grid ===== */
.analytics__stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.analytics__stat-card {
  background: white;
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-3);
  text-align: center;
}

.analytics__stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--velo-primary);
  margin-bottom: var(--space-1);
}

.analytics__stat-label {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

/* ===== Divider ===== */
.analytics__divider {
  height: 1px;
  background: var(--velo-border);
}

/* ===== Section ===== */
.analytics__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.analytics__section-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--velo-text-primary);
}

/* ===== Rating bars ===== */
.analytics__rating-bars {
  background: white;
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.analytics__rating-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.analytics__rating-row--compact {
  gap: var(--space-2);
}

.analytics__rating-label {
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  min-width: 100px;
  flex-shrink: 0;
}

.analytics__rating-row--compact .analytics__rating-label {
  min-width: 24px;
}

.analytics__rating-track {
  flex: 1;
  height: 8px;
  background: var(--velo-bg-subtle);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.analytics__rating-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.4s ease;
}

.analytics__rating-meta {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  min-width: 60px;
  text-align: right;
  flex-shrink: 0;
}

/* ===== Practice list ===== */
.analytics__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-6) 0;
}

.analytics__practice-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.analytics__practice-card {
  background: white;
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.analytics__practice-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.analytics__practice-row:hover {
  background: var(--velo-bg-subtle);
}

.analytics__practice-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
  min-width: 0;
}

.analytics__practice-emoji {
  font-size: 28px;
  flex-shrink: 0;
}

.analytics__practice-info {
  min-width: 0;
}

.analytics__practice-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--velo-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.analytics__practice-meta {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.analytics__practice-badges {
  display: flex;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  flex-shrink: 0;
}

.analytics__practice-chevron {
  font-size: 20px;
  color: var(--velo-text-secondary);
  transition: transform var(--transition-fast);
  flex-shrink: 0;
}

.analytics__practice-chevron--open {
  transform: rotate(90deg);
}

/* ===== Insights panel ===== */
.analytics__insights {
  border-top: 1px solid var(--velo-border);
  padding: var(--space-4);
  background: var(--velo-bg-subtle);
}

.analytics__insights-loader {
  display: flex;
  justify-content: center;
  padding: var(--space-3) 0;
}

.analytics__insights-error {
  font-size: var(--text-sm);
  color: var(--velo-error, #DC2626);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.analytics__retry-btn {
  background: transparent;
  border: 1px solid currentColor;
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  padding: 2px var(--space-2);
  cursor: pointer;
  color: inherit;
}

.analytics__insights-stats {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.analytics__insights-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.analytics__insights-stat-val {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--velo-primary);
}

.analytics__insights-stat-lbl {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.analytics__insights-bars {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.analytics__insights-empty {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  padding: var(--space-2) 0;
}

.analytics__insights-comments {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  border-top: 1px solid var(--velo-border);
  padding-top: var(--space-3);
  margin-top: var(--space-1);
}

/* ===== Load more ===== */
.analytics__load-more {
  padding-top: var(--space-2);
}

/* ===== Payments tab ===== */
.analytics__payments-hint {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.6;
}

/* ===== Expand transition ===== */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 400px;
  opacity: 1;
}
</style>
