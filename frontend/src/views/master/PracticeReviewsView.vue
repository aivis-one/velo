<!--
  VELO Frontend -- PracticeReviewsView (Phase-3 Master DS)

  Per-practice reviews detail. Route: /master/analytics/practice/:id
  (nested under analytics so the Аналитика tab stays active; masterStatusGuard).
  Reached by tapping a practice card in AnalyticsView → «Прошедшие практики».

  Sections (operator design 2026-06-11, "Отзывы о практике"):
    - VHeader (back + title).
    - Practice header card: direction icon + title + date · participants.
    - 3 VStatCard: Check-in % / Feedback % / Отзывов (count).
    - «Распределение»: rating bars (fill = RATING_COLOR, icon = RATING_ICON_COLOR).
    - «Отзывы»: individual reviews list.

  Data reality (E1 wired, 2026-06-16):
    REAL: practice header (getPractice) + stats/distribution (getPracticeInsights,
          reused from diaryStore cache — eager-loaded by AnalyticsView).
    REAL: the «Отзывы» list — getPracticeReviews (E1 named reviews, paginated).
          `rating` arrives pre-bucketed ('fire'|'good'|'confused') from the backend.
-->

<template>
  <div class="practice-reviews">
    <VHeader title="Отзывы о практике" show-back solid @back="router.back()" />

    <!-- Practice header card -->
    <div v-if="practice" class="practice-reviews__head">
      <span class="practice-reviews__head-icon">
        <component :is="practiceIconFor(practice)" :size="52" />
      </span>
      <div class="practice-reviews__head-title">{{ practice.title }}</div>
      <div class="practice-reviews__head-meta">
        <span><IconCalendar :size="16" />{{ practiceDate }}</span>
        <span><IconGroup :size="16" />{{ participantsLabel }}</span>
      </div>
    </div>

    <!-- Stats -->
    <div class="practice-reviews__stats">
      <VStatCard :value="checkinPct" label="Check-in" />
      <VStatCard :value="feedbackPct" label="Feedback" />
      <VStatCard :value="feedbacksLabel" label="Отзывов" />
    </div>

    <!-- Распределение -->
    <section class="practice-reviews__section">
      <h2 class="velo-section-title">Распределение</h2>
      <VCard class="practice-reviews__rating">
        <div v-for="bar in ratingBars" :key="bar.key" class="practice-reviews__rrow">
          <span class="practice-reviews__rrow-head">
            <component :is="bar.icon" :size="22" :style="{ color: bar.iconColor }" />
            {{ bar.label }}
          </span>
          <div class="practice-reviews__rtrack">
            <div
              class="practice-reviews__rfill"
              :style="{ width: `${bar.pct}%`, background: bar.barColor }"
            />
          </div>
          <span class="practice-reviews__rmeta">{{ bar.pct }}% ({{ bar.count }})</span>
        </div>
      </VCard>
    </section>

    <!-- Отзывы (E1 named reviews) -->
    <section class="practice-reviews__section">
      <h2 class="velo-section-title">Отзывы</h2>
      <div v-if="reviewsLoading && reviews.length === 0" class="practice-reviews__rloader">
        <VLoader size="lg" />
      </div>
      <VEmptyState v-else-if="reviewsError" icon="warning" title="Не удалось загрузить отзывы">
        <VButton size="sm" variant="outline" @click="loadReviews">Повторить</VButton>
      </VEmptyState>
      <template v-else-if="reviews.length > 0">
        <VCard v-for="(r, i) in reviews" :key="i" class="practice-reviews__review">
          <div class="practice-reviews__review-top">
            <VAvatar :name="r.reviewer_name" :url="r.avatar_url ?? ''" size="sm" />
            <div class="practice-reviews__review-id">
              <span class="practice-reviews__review-name">{{ r.reviewer_name }}</span>
              <span class="practice-reviews__review-date">{{ formatShortDate(r.created_at) }}</span>
            </div>
            <span class="practice-reviews__review-rating">
              <component
                :is="RATING_ICON[r.rating]"
                :size="22"
                :style="{ color: RATING_ICON_COLOR[r.rating] }"
              />
              {{ RATING_LABEL[r.rating] }}
            </span>
          </div>
          <div v-if="r.comment" class="practice-reviews__review-quote">«{{ r.comment }}»</div>
        </VCard>
        <div v-if="hasMoreReviews" class="practice-reviews__more">
          <VButton variant="ghost" @click="loadMoreReviews">Показать ещё</VButton>
        </div>
      </template>
      <div v-else class="practice-reviews__empty">Отзывов пока нет</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDiaryStore } from '@/stores/diary'
import { getPractice, getPracticeReviews } from '@/api/practices'
import { VStatCard, VCard, VButton, VLoader, VEmptyState, VAvatar } from '@/components/ui'
import { VHeader } from '@/components/layout'
import {
  IconCalendar,
  IconGroup,
  IconRatingFire,
  IconRatingGood,
  IconRatingConfused,
} from '@/components/icons'
import {
  practiceIconFor,
  RATING_COLOR,
  RATING_ICON_COLOR,
  RATING_LABEL,
} from '@/utils/displayHelpers'
import type { PracticeResponse, FeedbackRating, ReviewItem } from '@/api/types'

const route = useRoute()
const router = useRouter()
const diaryStore = useDiaryStore()

const practiceId = computed(() => route.params.id as string)

// Reactive insights cache (shared with AnalyticsView -- often already warm).
const insightsCache = diaryStore.insightsCache
const insights = computed(() => insightsCache.get(practiceId.value) ?? null)

// =========================================================================
// Practice header (getPractice -- robust on direct nav / refresh)
// =========================================================================

const practice = ref<PracticeResponse | null>(null)

const practiceDate = computed((): string =>
  practice.value ? formatShortDate(practice.value.scheduled_at) : '',
)

const participantsLabel = computed((): string => {
  const p = practice.value
  if (!p) return ''
  return p.max_participants != null
    ? `${p.current_participants}/${p.max_participants}`
    : String(p.current_participants)
})

// =========================================================================
// Stats (from anonymous insights). "—" until loaded.
// =========================================================================

const totalCheckins = computed((): number => {
  const i = insights.value
  return i ? i.checkins.high + i.checkins.mid + i.checkins.low : 0
})

const totalFeedbacks = computed((): number => {
  const i = insights.value
  return i ? i.feedbacks.fire + i.feedbacks.good + i.feedbacks.confused : 0
})

const checkinPct = computed((): string => {
  const i = insights.value
  if (!i || i.participants === 0) return '—'
  return `${Math.round((totalCheckins.value / i.participants) * 100)}%`
})

const feedbackPct = computed((): string => {
  const i = insights.value
  if (!i || i.participants === 0) return '—'
  return `${Math.round((totalFeedbacks.value / i.participants) * 100)}%`
})

const feedbacksLabel = computed((): string | number =>
  insights.value ? totalFeedbacks.value : '—',
)

// =========================================================================
// Distribution bars (fill = RATING_COLOR, icon = RATING_ICON_COLOR)
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
  const f = insights.value?.feedbacks ?? { fire: 0, good: 0, confused: 0 }
  const total = f.fire + f.good + f.confused
  return RATING_BARS_CONFIG.map((cfg) => ({
    ...cfg,
    iconColor: RATING_ICON_COLOR[cfg.key],
    barColor: RATING_COLOR[cfg.key],
    count: f[cfg.key],
    pct: total > 0 ? Math.round((f[cfg.key] / total) * 100) : 0,
  }))
})

// =========================================================================
// Отзывы (E1 named reviews — GET /practices/{id}/reviews, paginated)
// =========================================================================

const REVIEWS_PAGE = 20

const reviews = ref<ReviewItem[]>([])
const reviewsTotal = ref(0)
const reviewsLoading = ref(false)
const reviewsError = ref(false)
const hasMoreReviews = computed((): boolean => reviews.value.length < reviewsTotal.value)

const RATING_ICON: Record<FeedbackRating, Component> = {
  fire: IconRatingFire,
  good: IconRatingGood,
  confused: IconRatingConfused,
}

async function loadReviews(): Promise<void> {
  reviewsLoading.value = true
  reviewsError.value = false
  try {
    const res = await getPracticeReviews(practiceId.value, REVIEWS_PAGE, 0)
    reviews.value = res.items
    reviewsTotal.value = res.total
  } catch {
    reviewsError.value = true
  } finally {
    reviewsLoading.value = false
  }
}

async function loadMoreReviews(): Promise<void> {
  if (reviewsLoading.value || !hasMoreReviews.value) return
  reviewsLoading.value = true
  try {
    const res = await getPracticeReviews(practiceId.value, REVIEWS_PAGE, reviews.value.length)
    reviews.value = [...reviews.value, ...res.items]
    reviewsTotal.value = res.total
  } catch {
    // Keep the loaded page; the «Показать ещё» button stays for a retry.
  } finally {
    reviewsLoading.value = false
  }
}

// =========================================================================
// Helpers
// =========================================================================

function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

// =========================================================================
// Lifecycle
// =========================================================================

onMounted(async () => {
  // Insights are usually already cached (AnalyticsView eager-loads the page);
  // loadInsights skips a cached id, otherwise fetches.
  await diaryStore.loadInsights(practiceId.value)
  void loadReviews()
  try {
    practice.value = await getPractice(practiceId.value)
  } catch {
    // Practice not found / network -- header card hides, stats show "—".
    practice.value = null
  }
})
</script>

<style scoped>
.practice-reviews {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  /* F-5 rail sync: MobileLayout supplies the 24px horizontal rail. */
  padding: var(--space-4) 0;
}

/* ===== Practice header card ===== */
.practice-reviews__head {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-4) var(--space-3);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--velo-gap-6);
}

.practice-reviews__head-icon {
  color: var(--velo-text-primary);
  display: flex;
}

.practice-reviews__head-title {
  font-size: var(--text-lg);
  color: var(--velo-text-primary);
  letter-spacing: 0.3px;
  text-align: center;
}

.practice-reviews__head-meta {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.practice-reviews__head-meta > span {
  display: inline-flex;
  align-items: center;
  gap: var(--velo-gap-6);
}

.practice-reviews__head-meta :deep(svg) {
  opacity: 0.8;
}

/* ===== Stats ===== */
.practice-reviews__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

/* ===== Section ===== */
.practice-reviews__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* ===== Distribution ===== */
.practice-reviews__rating {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.practice-reviews__rrow {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.practice-reviews__rrow-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.practice-reviews__rtrack {
  height: 10px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  overflow: hidden;
}

.practice-reviews__rfill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.4s ease;
}

.practice-reviews__rmeta {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

/* ===== Review card ===== */
.practice-reviews__review {
  display: flex;
  flex-direction: column;
  gap: var(--velo-gap-6);
}

.practice-reviews__review-top {
  display: flex;
  align-items: center;
  gap: var(--velo-card-meta-row-gap);
}

.practice-reviews__review-id {
  display: flex;
  flex-direction: column;
  gap: var(--velo-gap-2);
  min-width: 0;
}

.practice-reviews__review-name {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.practice-reviews__review-date {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

.practice-reviews__review-rating {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: var(--velo-gap-6);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  white-space: nowrap;
}

.practice-reviews__review-quote {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  line-height: 1.45;
}

.practice-reviews__rloader {
  display: flex;
  justify-content: center;
  padding: var(--space-4) 0;
}

/* ===== Load more ===== */
.practice-reviews__more {
  display: flex;
  justify-content: center;
  padding-top: var(--space-2);
}

/* ===== Empty ===== */
.practice-reviews__empty {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  line-height: 1.5;
}
</style>
