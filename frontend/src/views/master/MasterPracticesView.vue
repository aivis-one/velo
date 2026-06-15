<!--
  VELO Frontend -- MasterPracticesView (Phase-3 Master DS)

  Master's own practice list. masterStatusGuard; rendered inside MasterShell.

  Tabs (VSegment):
    - "Предстоящие" -- draft + scheduled + live  (asc by scheduled_at)
    - "Прошедшие"   -- completed + cancelled     (desc by scheduled_at)

  Card (operator SVG 2026-06-11):
    - direction icon + title + "когда, время • N мин"
    - meta row: участники / check-ins / «Регулярная» (series)
    - upcoming: «Изменить» + «Check-ins» buttons BELOW the card
    - past: ✓/✗ attendance + rating-distribution badges INSIDE the card

  Data reality (Q4=А):
    REAL  -- participants, date/time/duration, practice icon; check-in count
             (insights.checkins / max) + rating distribution (insights.feedbacks,
             reused from diaryStore cache like AnalyticsView).
    STUB  -- attended/no-show counts (no aggregate field) → «—»; recurrence days
             («Регулярная» shown for series, exact days TBD); «осталось N из M»
             omitted (no series-session field). All recorded in
             master-ds-zod-roadmap.md.
-->

<template>
  <div class="master-practices">
    <!-- Header -->
    <VHeader title="Практики">
      <template #action>
        <button
          class="master-practices__add-btn"
          aria-label="Создать практику"
          @click="goNew"
        >
          <IconPlus :size="22" />
        </button>
      </template>
    </VHeader>

    <!-- Tabs -->
    <div class="master-practices__tabs">
      <VSegment
        :model-value="activeTab"
        :options="tabOptions"
        @update:model-value="activeTab = $event as 'upcoming' | 'past'"
      />
    </div>

    <!-- Loading -->
    <div v-if="masterStore.practicesLoading && masterStore.practices.length === 0" class="master-practices__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error -->
    <div v-else-if="masterStore.practicesError" class="master-practices__content">
      <VEmptyState
        icon="warning"
        title="Не удалось загрузить практики"
        :description="masterStore.practicesError"
      >
        <VButton size="sm" variant="outline" @click="masterStore.refreshMyPractices()">
          Повторить
        </VButton>
      </VEmptyState>
    </div>

    <!-- List -->
    <div v-else class="master-practices__content">
      <!-- ===================== Upcoming ===================== -->
      <template v-if="activeTab === 'upcoming'">
        <template v-if="upcomingPractices.length > 0">
          <article
            v-for="p in upcomingPractices"
            :key="p.id"
            class="mp-card mp-card--clickable"
            role="button"
            :tabindex="0"
            @click="goDetail(p.id)"
            @keydown.enter.space.prevent="goDetail(p.id)"
          >
            <div class="mp-card__head">
              <span class="mp-card__icon"><component :is="practiceIconFor(p)" :size="46" /></span>
              <div class="mp-card__titles">
                <div class="mp-card__title">{{ p.title }}</div>
                <div class="mp-card__sub">{{ whenLabel(p) }}, {{ formatTime(p.scheduled_at, p.timezone) }} • {{ p.duration_minutes }} мин</div>
              </div>
            </div>
            <div class="mp-card__meta">
              <span class="mp-stat"><IconGroup :size="16" /> {{ participantsLabel(p) }}</span>
              <span class="mp-stat"><IconCheckin :size="16" /> {{ checkinLabel(p) }}</span>
              <span v-if="p.practice_type === 'series'" class="mp-stat"><IconRepeat :size="16" /> Регулярная</span>
            </div>
          </article>
        </template>
        <VEmptyState
          v-else
          icon="calendar"
          title="Нет предстоящих практик"
          description="Создайте первую практику"
        >
          <VButton size="sm" variant="outline" @click="goNew">Создать</VButton>
        </VEmptyState>
      </template>

      <!-- ===================== Past ===================== -->
      <template v-else>
        <template v-if="pastPractices.length > 0">
          <article
            v-for="p in pastPractices"
            :key="p.id"
            class="mp-card mp-card--clickable"
            role="button"
            :tabindex="0"
            @click="goDetail(p.id)"
            @keydown.enter.space.prevent="goDetail(p.id)"
          >
            <div class="mp-card__head">
              <span class="mp-card__icon"><component :is="practiceIconFor(p)" :size="46" /></span>
              <div class="mp-card__titles">
                <div class="mp-card__title">{{ p.title }}</div>
                <div class="mp-card__sub">{{ whenLabel(p) }}, {{ formatTime(p.scheduled_at, p.timezone) }} • {{ p.duration_minutes }} мин</div>
              </div>
            </div>
            <div class="mp-card__meta">
              <span class="mp-stat"><IconGroup :size="16" /> {{ p.current_participants }}</span>
              <!-- attended / no-show: no aggregate field yet (→ Zod), shown as «—». -->
              <span class="mp-stat mp-stat--ok"><IconCheck :size="16" /> —</span>
              <span class="mp-stat mp-stat--no"><IconClose :size="16" /> —</span>
            </div>
            <!-- Rating distribution (REAL, anonymous insights — eager-loaded). -->
            <div v-if="hasRating(p.id)" class="mp-card__rbadges">
              <span class="mp-rbadge mp-rbadge--fire"><IconRatingFire :size="14" /> {{ ratingPct(p.id, 'fire') }}%</span>
              <span class="mp-rbadge mp-rbadge--good"><IconRatingGood :size="14" /> {{ ratingPct(p.id, 'good') }}%</span>
              <span class="mp-rbadge mp-rbadge--conf"><IconRatingConfused :size="14" /> {{ ratingPct(p.id, 'confused') }}%</span>
            </div>
          </article>
        </template>
        <VEmptyState
          v-else
          icon="list"
          title="Нет прошедших практик"
          description="Здесь появятся завершённые и отменённые практики"
        />
      </template>

      <!-- Load more -->
      <div v-if="masterStore.practicesHasMore" class="master-practices__load-more">
        <VButton
          variant="ghost"
          block
          :loading="masterStore.practicesLoading"
          @click="onLoadMore"
        >
          Показать ещё
        </VButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton, VLoader, VEmptyState, VSegment } from '@/components/ui'
import {
  IconPlus,
  IconGroup,
  IconCheckin,
  IconRepeat,
  IconCheck,
  IconClose,
  IconRatingFire,
  IconRatingGood,
  IconRatingConfused,
} from '@/components/icons'
import { useMasterStore } from '@/stores/master'
import { useDiaryStore } from '@/stores/diary'
import { practiceIconFor } from '@/utils/displayHelpers'
import { formatDateShort, formatShortDate, formatTime } from '@/utils/format'
import type { PracticeResponse } from '@/api/types'

const router = useRouter()
const masterStore = useMasterStore()
const diaryStore = useDiaryStore()

// Reactive insights cache (shared with Analytics / PracticeReviews — often warm).
const insightsCache = diaryStore.insightsCache

const activeTab = ref<'upcoming' | 'past'>('upcoming')

// -- Upcoming: draft + scheduled + live, ascending --
const upcomingPractices = computed((): PracticeResponse[] =>
  masterStore.practices
    .filter((p) => p.status === 'draft' || p.status === 'scheduled' || p.status === 'live')
    .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime()),
)

// -- Past: completed + cancelled, descending (newest first) --
const pastPractices = computed((): PracticeResponse[] =>
  masterStore.practices
    .filter((p) => p.status === 'completed' || p.status === 'cancelled')
    .sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime()),
)

const tabOptions = computed(() => [
  { value: 'upcoming', label: 'Предстоящие', badge: upcomingPractices.value.length || undefined },
  { value: 'past', label: 'Прошедшие', badge: pastPractices.value.length || undefined },
])

// -- Card subtitle helpers --------------------------------------------------

/** Relative "Сегодня"/"Завтра", else compact "25 янв." (timezone-safe). */
function whenLabel(p: PracticeResponse): string {
  const rel = formatDateShort(p.scheduled_at, p.timezone)
  return rel === 'Сегодня' || rel === 'Завтра'
    ? rel
    : formatShortDate(p.scheduled_at, p.timezone)
}

function participantsLabel(p: PracticeResponse): string {
  return p.max_participants != null
    ? `${p.current_participants}/${p.max_participants}`
    : `${p.current_participants}`
}

// -- Insights-derived (REAL) ------------------------------------------------

function totalCheckins(id: string): number {
  const i = insightsCache.get(id)
  return i ? i.checkins.high + i.checkins.mid + i.checkins.low : 0
}

function totalFeedbacks(id: string): number {
  const i = insightsCache.get(id)
  return i ? i.feedbacks.fire + i.feedbacks.good + i.feedbacks.confused : 0
}

/** Check-in count "10/20" (submitted check-ins / capacity). "—" until loaded. */
function checkinLabel(p: PracticeResponse): string {
  if (!insightsCache.has(p.id)) return '—'
  const denom = p.max_participants ?? p.current_participants
  return `${totalCheckins(p.id)}/${denom}`
}

function hasRating(id: string): boolean {
  return insightsCache.has(id) && totalFeedbacks(id) > 0
}

function ratingPct(id: string, key: 'fire' | 'good' | 'confused'): number {
  const i = insightsCache.get(id)
  if (!i) return 0
  const total = totalFeedbacks(id)
  return total > 0 ? Math.round((i.feedbacks[key] / total) * 100) : 0
}

/** Eager-load insights for the visible tab (idempotent: cached ids are skipped). */
function loadTabInsights(): Promise<void[]> {
  const list = activeTab.value === 'upcoming' ? upcomingPractices.value : pastPractices.value
  return Promise.all(list.map((p) => diaryStore.loadInsights(p.id)))
}

// -- Navigation -------------------------------------------------------------

function goNew(): void {
  router.push({ name: 'master-practice-new' })
}
function goDetail(id: string): void {
  router.push({ name: 'master-practice-detail', params: { id } })
}

async function onLoadMore(): Promise<void> {
  await masterStore.loadMorePractices()
  await loadTabInsights()
}

watch(activeTab, () => {
  loadTabInsights()
})

onMounted(async () => {
  await masterStore.fetchMyPractices()
  await loadTabInsights()
})
</script>

<style scoped>
.master-practices {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

/* -- "+" add button (filled primary circle + white plus, operator SVG) -- */
.master-practices__add-btn {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--velo-white);
  background: var(--velo-primary);
  border: 1px solid var(--velo-glass-border);
  border-radius: var(--radius-full);
  box-shadow: var(--velo-shadow-glow);
  transition: background-color var(--transition-fast);
}

.master-practices__add-btn:hover {
  background: var(--velo-primary-dark);
}

/* -- Tabs (F-5 rail sync: ride MobileLayout's 24px rail, no local h-padding) -- */
.master-practices__tabs {
  padding: var(--space-3) 0;
  background: transparent;
}

/* -- Content -- */
.master-practices__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-12) 0;
}

.master-practices__content {
  flex: 1;
  padding: var(--space-3) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.master-practices__load-more {
  padding-top: var(--space-2);
}

/* ===== Practice card ===== */
.mp-card {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: 13px 15px;
  display: flex;
  flex-direction: column;
}

/* Past cards are tappable → practice detail (Р1=А). */
.mp-card--clickable {
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.mp-card--clickable:active {
  transform: scale(0.99);
}

.mp-card__head {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mp-card__icon {
  flex-shrink: 0;
  color: var(--velo-text-primary);
  display: flex;
}

.mp-card__title {
  font-size: var(--text-lg);
  color: var(--velo-text-primary);
  letter-spacing: 0.3px;
}

.mp-card__sub {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin-top: 3px;
}

.mp-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  margin-top: 13px;
  font-size: var(--text-xs);
  color: var(--velo-text-primary);
}

.mp-stat {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.mp-stat :deep(svg) {
  opacity: 0.8;
}

.mp-stat--ok {
  color: var(--velo-success);
}

.mp-stat--no {
  color: var(--velo-error);
}

/* Rating-distribution badges (sand/pink/blue-100 tints; confused = blue-400
   per operator SVG 2026-06-11). */
.mp-card__rbadges {
  display: flex;
  gap: var(--space-2);
  margin-top: 13px;
}

.mp-rbadge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 11px;
  border-radius: var(--velo-radius-badge);
  font-size: var(--text-xs);
}

.mp-rbadge--fire {
  background: var(--velo-sand-100);
  color: var(--velo-rating-fire);
}

.mp-rbadge--good {
  background: var(--velo-pink-100);
  color: var(--velo-rating-good);
}

.mp-rbadge--conf {
  background: var(--velo-blue-100);
  color: var(--velo-blue-400);
}
</style>
