<!--
  VELO Frontend -- AnalyticsView (Phase-3 Master DS rebuild)

  Master analytics hub. Route: /master/analytics (inside MasterShell).

  Two tabs (operator design 2026-06-11), each under a shared period toggle:
    1. Отзывы  -- aggregate stats (Check-in / Feedback / Отзывов) + overall
                  rating distribution bars + "Требуют внимания" + past-practice
                  cards with inline rating badges.
    2. Платежи -- period income + transactions list + link to full Finance.

  Controls are the track+thumb pattern (single glass track, active fill pill) --
  the same shape as the master-dashboard period toggle, NOT the two-pill VSegment
  (operator design; VSegment<->track+thumb unification is a SHELL task).

  Data reality (decisions locked with operator 2026-06-11):
    REAL: past completed practices (masterStore) + per-practice insights
          (GET /practices/{id}/insights -> anonymous rating/mood distributions).
          Insights are eager-loaded for the visible page so the inline badges and
          the aggregate are populated without a tap.
    STUB (no backend yet -> master-ds-zod-roadmap.md):
      - Период «Неделя/Месяц»: no period-scoped API -> toggle is visual-only.
      - «Требуют внимания»: insights are anonymous (no names / comment texts), so
        the de-anonymised attention feed has no source. Section is scaffolded and
        renders its empty state until Zod adds a NON-anonymous endpoint.
      - «Платежи»: no income-by-period and no transactions/ledger endpoints. Income
        shows "—", transactions show the empty state. Currency canon stays EUR
        (₽ vs € is a cross-screen SHELL decision). Full finance (balance, payout,
        withdrawals) lives on /master/finance -> "Открыть Финансы" link.
-->

<template>
  <div class="analytics">
    <!-- Header -->
    <header class="analytics__header">
      <h1 class="analytics__title">Аналитика</h1>
    </header>

    <!-- Tab segment (track+thumb) -->
    <div class="analytics__seg" role="tablist">
      <button
        v-for="tab in TAB_OPTIONS"
        :key="tab.value"
        type="button"
        role="tab"
        :aria-selected="activeTab === tab.value"
        class="analytics__seg-btn"
        :class="{ 'analytics__seg-btn--active': activeTab === tab.value }"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Period toggle -- visual-only until a period-scoped analytics API exists. -->
    <div class="analytics__period-row">
      <div class="analytics__period" role="tablist" aria-label="Период статистики">
        <button
          type="button"
          class="analytics__period-btn"
          :class="{ 'analytics__period-btn--active': period === 'week' }"
          @click="period = 'week'"
        >
          Неделя
        </button>
        <button
          type="button"
          class="analytics__period-btn"
          :class="{ 'analytics__period-btn--active': period === 'month' }"
          @click="period = 'month'"
        >
          Месяц
        </button>
      </div>
    </div>

    <!-- ================================================================
         TAB: ОТЗЫВЫ
         ================================================================ -->
    <div v-show="activeTab === 'reviews'" class="analytics__body">
      <!-- Aggregate stats (over loaded insights; period scoping has no API). -->
      <div class="analytics__stats">
        <VStatCard :value="aggregateCheckinPct" label="Check-in" />
        <VStatCard :value="aggregateFeedbackPct" label="Feedback" />
        <VStatCard :value="aggregateTotalFeedbacks" label="Отзывов" />
      </div>

      <!-- Общая статистика -->
      <section class="analytics__section">
        <h2 class="analytics__section-title">Общая статистика</h2>
        <VCard class="analytics__rating">
          <div v-for="bar in ratingBars" :key="bar.key" class="analytics__rrow">
            <span class="analytics__rrow-head">
              <component :is="bar.icon" :size="22" :style="{ color: bar.iconColor }" />
              {{ bar.label }}
            </span>
            <div class="analytics__rtrack">
              <div
                class="analytics__rfill"
                :style="{ width: `${bar.pct}%`, background: bar.barColor }"
              />
            </div>
            <span class="analytics__rmeta">{{ bar.pct }}% ({{ bar.count }})</span>
          </div>
        </VCard>
      </section>

      <!-- Требуют внимания (scaffold: empty until a non-anonymous endpoint lands). -->
      <section class="analytics__section">
        <h2 class="analytics__section-title">Требуют внимания</h2>
        <template v-if="attentionItems.length > 0">
          <VCard v-for="(item, i) in attentionItems" :key="i" class="analytics__attention">
            <span class="analytics__attention-av"><IconProfile :size="26" /></span>
            <div class="analytics__attention-body">
              <div class="analytics__attention-name">{{ item.name }}</div>
              <div class="analytics__attention-rate">
                <IconRatingConfused :size="16" :style="{ color: 'var(--velo-rating-confused)' }" />
                {{ item.rating }}
                <span class="analytics__attention-pr">• {{ item.practice }}</span>
              </div>
              <div class="analytics__attention-quote">«{{ item.comment }}»</div>
            </div>
          </VCard>
        </template>
        <div v-else class="analytics__empty">Данных пока нет — создайте первую практику</div>
      </section>

      <!-- Прошедшие практики -->
      <section class="analytics__section">
        <h2 class="analytics__section-title">Прошедшие практики</h2>

        <div
          v-if="masterStore.practicesLoading && pastPractices.length === 0"
          class="analytics__loader"
        >
          <VLoader />
        </div>

        <div v-else-if="pastPractices.length === 0" class="analytics__empty">
          Данных пока нет — создайте первую практику
        </div>

        <template v-else>
          <button
            v-for="p in pastPractices"
            :key="p.id"
            type="button"
            class="analytics__pcard"
            @click="openReviews(p.id)"
          >
            <div class="analytics__pcard-top">
              <span class="analytics__pcard-icon">
                <component :is="practiceIconFor(p)" :size="46" />
              </span>
              <div class="analytics__pcard-info">
                <div class="analytics__pcard-title">{{ p.title }}</div>
                <div class="analytics__pcard-meta">
                  {{ formatShortDate(p.scheduled_at) }} · {{ p.current_participants }} участников
                </div>
              </div>
            </div>

            <!-- Inline rating badges (insights eager-loaded for the page). -->
            <div
              v-if="insightsCache.has(p.id) && totalFeedbacks(p.id) > 0"
              class="analytics__pcard-badges"
            >
              <span class="analytics__rbadge analytics__rbadge--fire">
                <IconRatingFire :size="14" />{{ ratingPct(p.id, 'fire') }}%
              </span>
              <span class="analytics__rbadge analytics__rbadge--good">
                <IconRatingGood :size="14" />{{ ratingPct(p.id, 'good') }}%
              </span>
              <span class="analytics__rbadge analytics__rbadge--confused">
                <IconRatingConfused :size="14" />{{ ratingPct(p.id, 'confused') }}%
              </span>
            </div>
          </button>

          <div v-if="masterStore.practicesHasMore" class="analytics__more">
            <VButton variant="ghost" :loading="masterStore.practicesLoading" @click="onLoadMore">
              Показать ещё
            </VButton>
          </div>
        </template>
      </section>
    </div>

    <!-- ================================================================
         TAB: ПЛАТЕЖИ
         ================================================================ -->
    <div v-show="activeTab === 'payments'" class="analytics__body">
      <!-- Income — no income-by-period API yet -> "—" (roadmap Zod). -->
      <div class="analytics__income">
        <div class="analytics__income-value">{{ income }}</div>
        <div class="analytics__income-label">Доход за период</div>
      </div>

      <!-- Транзакции — no ledger-list API yet -> empty (roadmap Zod). -->
      <section class="analytics__section">
        <h2 class="analytics__section-title">Транзакции</h2>
        <div v-if="transactions.length > 0" class="analytics__txns">
          <div v-for="(t, i) in transactions" :key="i" class="analytics__txn">
            <div class="analytics__txn-info">
              <div class="analytics__txn-title">{{ t.title }}</div>
              <div class="analytics__txn-meta">{{ t.date }} · {{ t.counterparty }}</div>
            </div>
            <div
              class="analytics__txn-amt"
              :class="t.amountCents >= 0 ? 'analytics__txn-amt--in' : 'analytics__txn-amt--out'"
            >
              {{ formatTxnAmount(t.amountCents) }}
            </div>
          </div>
        </div>
        <div v-else class="analytics__empty">Данных пока нет</div>
      </section>

      <!-- Full finance (balance / payout / withdrawals) lives on /master/finance. -->
      <button
        type="button"
        class="analytics__finance-link"
        @click="router.push({ name: 'master-finance' })"
      >
        Открыть Финансы<IconArrowRight :size="16" class="analytics__finance-arrow" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { useMasterStore } from '@/stores/master'
import { useDiaryStore } from '@/stores/diary'
import { VLoader, VButton, VStatCard, VCard } from '@/components/ui'
import {
  IconArrowRight,
  IconRatingFire,
  IconRatingGood,
  IconRatingConfused,
  IconProfile,
} from '@/components/icons'
import { practiceIconFor, RATING_COLOR, RATING_ICON_COLOR } from '@/utils/displayHelpers'
import { formatMoney } from '@/utils/format'

const router = useRouter()
const masterStore = useMasterStore()
const diaryStore = useDiaryStore()

// Reactive Map<practiceId, insights> -- computeds below track additions.
const insightsCache = diaryStore.insightsCache

// =========================================================================
// Tabs (track+thumb segment) + period toggle (visual-only)
// =========================================================================

const activeTab = ref<'reviews' | 'payments'>('reviews')
const TAB_OPTIONS: Array<{ value: 'reviews' | 'payments'; label: string }> = [
  { value: 'reviews', label: 'Отзывы' },
  { value: 'payments', label: 'Платежи' },
]

// Period scoping has no backend yet -> the toggle only moves the active pill
// (mirrors the master-dashboard pattern). Roadmap: period-scoped summary API.
const period = ref<'week' | 'month'>('week')

// =========================================================================
// Past practices (completed, newest first)
// =========================================================================

const pastPractices = computed(() =>
  masterStore.practices
    .filter((p) => p.status === 'completed')
    .sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime()),
)

// =========================================================================
// Aggregate stats (over all loaded insights)
// =========================================================================

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
  insightsCache.forEach((ins) => {
    total += ins.participants
  })
  return total
})

/** Check-in rate over loaded insights. "—" when there is no data yet. */
const aggregateCheckinPct = computed((): string => {
  if (aggregateTotalParticipants.value === 0) return '—'
  return `${Math.round((aggregateTotalCheckins.value / aggregateTotalParticipants.value) * 100)}%`
})

/** Feedback rate over loaded insights. "—" when there is no data yet. */
const aggregateFeedbackPct = computed((): string => {
  if (aggregateTotalParticipants.value === 0) return '—'
  return `${Math.round((aggregateTotalFeedbacks.value / aggregateTotalParticipants.value) * 100)}%`
})

// =========================================================================
// Overall rating distribution bars (Общая статистика)
// =========================================================================

interface RatingBar {
  key: 'fire' | 'good' | 'confused'
  icon: Component
  label: string
  count: number
  pct: number
  iconColor: string
  barColor: string
}

// Bar fill = RATING_COLOR (peach-300 / pink-300 / blue-400); icon accent =
// RATING_ICON_COLOR (--velo-rating-*). Two palettes on purpose (see displayHelpers).
const RATING_BARS_CONFIG: Array<{
  key: 'fire' | 'good' | 'confused'
  icon: Component
  label: string
}> = [
  { key: 'fire', icon: IconRatingFire, label: 'Огонь!' },
  { key: 'good', icon: IconRatingGood, label: 'Хорошо' },
  { key: 'confused', icon: IconRatingConfused, label: 'Есть вопросы' },
]

const ratingBars = computed((): RatingBar[] => {
  const totals = { fire: 0, good: 0, confused: 0 }
  insightsCache.forEach((ins) => {
    totals.fire += ins.feedbacks.fire
    totals.good += ins.feedbacks.good
    totals.confused += ins.feedbacks.confused
  })
  const total = totals.fire + totals.good + totals.confused
  return RATING_BARS_CONFIG.map((cfg) => ({
    ...cfg,
    iconColor: RATING_ICON_COLOR[cfg.key],
    barColor: RATING_COLOR[cfg.key],
    count: totals[cfg.key],
    pct: total > 0 ? Math.round((totals[cfg.key] / total) * 100) : 0,
  }))
})

// =========================================================================
// Per-practice rating (inline badges)
// =========================================================================

function totalFeedbacks(practiceId: string): number {
  const ins = insightsCache.get(practiceId)
  if (!ins) return 0
  return ins.feedbacks.fire + ins.feedbacks.good + ins.feedbacks.confused
}

function ratingPct(practiceId: string, rating: 'fire' | 'good' | 'confused'): number {
  const total = totalFeedbacks(practiceId)
  if (total === 0) return 0
  return Math.round((insightsCache.get(practiceId)!.feedbacks[rating] / total) * 100)
}

// =========================================================================
// Требуют внимания -- scaffold (no backend source: insights are anonymous)
// =========================================================================

// Needs a NON-anonymous endpoint (negative/«есть вопросы» feedback with the
// participant name + comment text + practice). Until Zod adds it the array stays
// empty and the section shows its empty state; the v-for is wiring-ready.
interface AttentionItem {
  name: string
  rating: string
  practice: string
  comment: string
}
const attentionItems = ref<AttentionItem[]>([])

// =========================================================================
// Платежи -- scaffold (no income-by-period / transactions endpoints yet)
// =========================================================================

// Income: "—" until an income-by-period API exists. Currency canon = EUR.
const income = '—'

interface Transaction {
  title: string
  date: string
  counterparty: string
  amountCents: number
}
const transactions = ref<Transaction[]>([])

function formatTxnAmount(cents: number): string {
  const sign = cents >= 0 ? '+' : '−'
  return `${sign}${formatMoney(Math.abs(cents), 'EUR', 'ru', true)}`
}

// =========================================================================
// Helpers
// =========================================================================

function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

// Eager-load insights for the visible page -- feeds both the aggregate stats and
// the inline practice-card badges. loadInsights() skips already-cached ids, so
// this is idempotent across re-runs and load-more.
function loadVisibleInsights(): Promise<void[]> {
  return Promise.all(pastPractices.value.map((p) => diaryStore.loadInsights(p.id)))
}

async function onLoadMore(): Promise<void> {
  await masterStore.loadMorePractices()
  await loadVisibleInsights()
}

/** Open the per-practice reviews detail (Г2: closes the card-tap from Г4). */
function openReviews(practiceId: string): void {
  router.push({ name: 'master-practice-reviews', params: { id: practiceId } })
}

// =========================================================================
// Lifecycle
// =========================================================================

onMounted(async () => {
  await masterStore.fetchMyPractices()
  await loadVisibleInsights()
})
</script>

<style scoped>
.analytics {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

/* ===== Header (F-5 rail sync: ride MobileLayout's 24px rail) ===== */
.analytics__header {
  padding: var(--space-4) 0 var(--space-3);
}

.analytics__title {
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

/* ===== Controls: track+thumb (segment + period toggle) ===== */
.analytics__seg {
  display: flex;
  gap: 2px;
  background: var(--velo-glass-blue-15);
  border: 1px solid var(--velo-glass-border);
  border-radius: var(--radius-xl);
  padding: 3px;
}

.analytics__seg-btn {
  flex: 1;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-muted);
  background: transparent;
  border: none;
  border-radius: var(--radius-xl);
  padding: 6px 10px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.analytics__seg-btn--active {
  background: var(--velo-primary);
  color: var(--velo-white);
}

.analytics__period-row {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-3);
}

.analytics__period {
  display: flex;
  gap: 2px;
  background: var(--velo-glass-blue-15);
  border: 1px solid var(--velo-glass-border);
  border-radius: var(--radius-xl);
  padding: 2px;
}

.analytics__period-btn {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-primary);
  background: transparent;
  border: none;
  border-radius: var(--radius-xl);
  padding: var(--space-1) var(--space-3);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.analytics__period-btn--active {
  background: var(--velo-primary);
  color: var(--velo-white);
}

/* ===== Body ===== */
.analytics__body {
  flex: 1;
  padding: var(--space-4) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* ===== Stats grid ===== */
.analytics__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

/* ===== Section ===== */
.analytics__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.analytics__section-title {
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

/* ===== Rating distribution (Общая статистика) ===== */
.analytics__rating {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.analytics__rrow {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.analytics__rrow-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.analytics__rtrack {
  height: 10px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  overflow: hidden;
}

.analytics__rfill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.4s ease;
}

.analytics__rmeta {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

/* ===== Требуют внимания ===== */
.analytics__attention {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
}

.analytics__attention-av {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  color: var(--velo-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.analytics__attention-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.analytics__attention-name {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.analytics__attention-rate {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
}

.analytics__attention-pr {
  color: var(--velo-text-secondary);
}

.analytics__attention-quote {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  font-style: italic;
}

/* ===== Empty card ===== */
.analytics__empty {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  line-height: 1.5;
}

/* ===== Practice card (PracticeListCard canon padding + inline badges) ===== */
.analytics__pcard {
  width: 100%;
  text-align: left;
  font: inherit;
  cursor: pointer;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--velo-card-padding-y) var(--velo-card-padding-x);
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: opacity var(--transition-fast);
}

.analytics__pcard:active {
  opacity: 0.85;
}

.analytics__pcard-top {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.analytics__pcard-icon {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  color: var(--velo-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.analytics__pcard-info {
  flex: 1;
  min-width: 0;
}

.analytics__pcard-title {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.36px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.analytics__pcard-meta {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: 0.28px;
}

.analytics__pcard-badges {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

/* Rating badges -- analytics-local tints from DS tokens. Promote to a VBadge
   rating variant if reused elsewhere (SHELL). */
.analytics__rbadge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: var(--velo-radius-badge);
  font-size: var(--text-xs);
}

.analytics__rbadge--fire {
  background: var(--velo-sand-100);
  color: var(--velo-rating-fire);
}

.analytics__rbadge--good {
  background: var(--velo-pink-100);
  color: var(--velo-rating-good);
}

.analytics__rbadge--confused {
  background: var(--velo-blue-100);
  color: var(--velo-blue-400);
}

/* ===== Load more ===== */
.analytics__more {
  display: flex;
  justify-content: center;
  padding-top: var(--space-2);
}

.analytics__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-5) 0;
}

/* ===== Платежи ===== */
.analytics__income {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.analytics__income-value {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.5px;
}

.analytics__income-label {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
}

.analytics__txns {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: 0 var(--space-4);
}

.analytics__txn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--velo-border-light);
}

.analytics__txn:last-child {
  border-bottom: none;
}

.analytics__txn-info {
  min-width: 0;
}

.analytics__txn-title {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.analytics__txn-meta {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

.analytics__txn-amt {
  font-size: var(--text-base);
  white-space: nowrap;
}

.analytics__txn-amt--in {
  color: var(--velo-teal-600);
}

.analytics__txn-amt--out {
  color: var(--velo-pink-300);
}

.analytics__finance-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  background: transparent;
  border: none;
  padding: var(--space-2);
  cursor: pointer;
}

.analytics__finance-arrow {
  vertical-align: middle;
}
</style>
