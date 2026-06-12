<!--
  VELO Frontend -- MasterPracticeDetailView (Phase-3 Master DS)

  Master's detail screen for a PAST practice. Route: /master/practices/:id/detail
  (masterStatusGuard; rendered inside MasterShell, no tab bar — detail route).
  Reached by tapping a past practice card in MasterPracticesView.

  Decision Р1=А (operator 2026-06-12): ONE detail route practices/:id/detail,
  branched by status. THIS commit builds the PAST branch (completed/cancelled);
  the UPCOMING branch is WI-B (on deck) — until then a non-past practice arriving
  here is redirected to the edit screen (its current entry point). PracticeReviewsView
  (analytics/practice/:id) is NOT touched; its dedup with this screen is a SHELL pass.

  Sections (operator SVG "5 Practice (past) 1/2"):
    - VHeader (back + "Прошедшая практика").
    - Hero card: direction icon + title + date·time / duration + rating-distribution
      badges (45/40/15 %).
    - 2 VStatCard: Присутствовало (teal) / Не пришли (rose).
    - «Отзывы участников»: individual reviews list.
    - «Финансы»: Записалось / Присутствовало / Доход.
    - CTAs: Check-ins (→ AttendanceView) + Посещаемость (→ AttendanceRosterView).

  Data reality:
    REAL: practice header (getPractice) · Присутствовало/Не пришли + Записалось
          (getAttendance.attended/no_show/total) · rating badges (getPracticeInsights,
          anonymous, reused from the diary cache).
    STUB → Zod: «Отзывы участников» (name + comment — insights are anonymous, needs the
          same non-anonymous endpoint as the dashboard «Требуют внимания»; empty until
          then). «Доход» — no income/ledger API → «—» (currency canon ₽ vs € deferred).
-->

<template>
  <div class="practice-detail">
    <VHeader title="Прошедшая практика" show-back @back="router.back()" />

    <!-- Loading -->
    <div v-if="loading" class="practice-detail__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="practice-detail__content">
      <VEmptyState icon="warning" title="Не удалось загрузить практику" :description="error">
        <VButton size="sm" variant="outline" @click="load">Повторить</VButton>
      </VEmptyState>
    </div>

    <template v-else-if="practice">
      <div class="practice-detail__content">
        <!-- Hero -->
        <div class="practice-detail__head">
          <span class="practice-detail__head-icon">
            <component :is="practiceIconFor(practice)" :size="48" />
          </span>
          <div class="practice-detail__head-title">{{ practice.title }}</div>
          <div class="practice-detail__head-meta">
            <span><IconCalendar :size="16" />{{ whenLabel }}</span>
            <span><IconClock :size="16" />{{ durationLabel }}</span>
          </div>
          <div v-if="hasRating" class="practice-detail__rbadges">
            <span class="practice-detail__rbadge practice-detail__rbadge--fire">
              <IconRatingFire :size="16" /> {{ ratingPct('fire') }}%
            </span>
            <span class="practice-detail__rbadge practice-detail__rbadge--good">
              <IconRatingGood :size="16" /> {{ ratingPct('good') }}%
            </span>
            <span class="practice-detail__rbadge practice-detail__rbadge--conf">
              <IconRatingConfused :size="16" /> {{ ratingPct('confused') }}%
            </span>
          </div>
        </div>

        <!-- Stats -->
        <div class="practice-detail__stats">
          <VStatCard :value="attendedValue" label="Присутствовало" value-tone="teal" />
          <VStatCard :value="noShowValue" label="Не пришли" value-tone="rose" />
        </div>

        <!-- Отзывы участников (stub: empty until a non-anonymous endpoint lands) -->
        <section class="practice-detail__section">
          <h2 class="practice-detail__section-title">Отзывы участников</h2>
          <template v-if="reviews.length > 0">
            <div v-for="(r, i) in reviews" :key="i" class="practice-detail__review">
              <div class="practice-detail__review-top">
                <component :is="RATING_ICON[r.rating]" :size="22" :style="{ color: RATING_ICON_COLOR[r.rating] }" />
                <span class="practice-detail__review-name">{{ r.name }}</span>
              </div>
              <div class="practice-detail__review-quote">«{{ r.comment }}»</div>
            </div>
          </template>
          <div v-else class="practice-detail__empty">Отзывов пока нет</div>
        </section>

        <!-- Финансы -->
        <section class="practice-detail__section">
          <h2 class="practice-detail__section-title">Финансы</h2>
          <div class="practice-detail__finance">
            <div class="practice-detail__finrow">
              <span>Записалось</span><span>{{ enrolledLabel }}</span>
            </div>
            <div class="practice-detail__finrow">
              <span>Присутствовало</span><span>{{ attendedPeopleLabel }}</span>
            </div>
            <div class="practice-detail__finrow practice-detail__finrow--income">
              <span>Доход</span><span>{{ incomeLabel }}</span>
            </div>
          </div>
        </section>

        <!-- CTAs -->
        <div class="practice-detail__actions">
          <VButton variant="primary" block @click="goCheckins">Check-ins</VButton>
          <VButton variant="outline" block @click="goRoster">Посещаемость</VButton>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDiaryStore } from '@/stores/diary'
import { useMasterStore } from '@/stores/master'
import { getPractice, getAttendance } from '@/api/practices'
import { ApiResponseError } from '@/api/client'
import { VStatCard, VButton, VLoader, VEmptyState } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { IconCalendar, IconClock, IconRatingFire, IconRatingGood, IconRatingConfused } from '@/components/icons'
import { practiceIconFor, RATING_ICON_COLOR } from '@/utils/displayHelpers'
import { formatDateShort, formatTime } from '@/utils/format'
import type { PracticeResponse, AttendanceResponse, FeedbackRating } from '@/api/types'

const route = useRoute()
const router = useRouter()
const diaryStore = useDiaryStore()
const masterStore = useMasterStore()

const practiceId = route.params.id as string

// -- Data --
const practice = ref<PracticeResponse | null>(null)
const attendance = ref<AttendanceResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// Reactive insights cache (shared with Analytics / Practices — often warm).
const insightsCache = diaryStore.insightsCache
const insights = computed(() => insightsCache.get(practiceId) ?? null)

// -- Hero meta --
const whenLabel = computed((): string => {
  if (!practice.value) return ''
  const day = formatDateShort(practice.value.scheduled_at, practice.value.timezone)
  const time = formatTime(practice.value.scheduled_at, practice.value.timezone)
  return `${day}, ${time}`
})

const durationLabel = computed((): string =>
  practice.value ? `${practice.value.duration_minutes} мин` : '',
)

// -- Rating distribution badges (REAL, anonymous insights) --
const totalFeedbacks = computed((): number => {
  const f = insights.value?.feedbacks
  return f ? f.fire + f.good + f.confused : 0
})

const hasRating = computed((): boolean => insights.value != null && totalFeedbacks.value > 0)

function ratingPct(key: 'fire' | 'good' | 'confused'): number {
  const f = insights.value?.feedbacks
  if (!f) return 0
  const total = totalFeedbacks.value
  return total > 0 ? Math.round((f[key] / total) * 100) : 0
}

// -- Stats + finance (REAL via getAttendance; "—" until loaded) --
const attendedValue = computed((): string | number => (attendance.value ? attendance.value.attended : '—'))
const noShowValue = computed((): string | number => (attendance.value ? attendance.value.no_show : '—'))
const enrolledLabel = computed((): string => (attendance.value ? `${attendance.value.total} чел.` : '—'))
const attendedPeopleLabel = computed((): string => (attendance.value ? `${attendance.value.attended} чел.` : '—'))
// STUB → Zod: no income/ledger API yet (currency canon ₽ vs € also deferred).
const incomeLabel = '—'

// -- Отзывы участников: scaffold (no backend source — insights are anonymous) --
interface Review {
  name: string
  rating: FeedbackRating
  comment: string
}
const reviews = ref<Review[]>([])

const RATING_ICON: Record<FeedbackRating, Component> = {
  fire: IconRatingFire,
  good: IconRatingGood,
  confused: IconRatingConfused,
}

// -- Navigation --
function goCheckins(): void {
  router.push({ name: 'master-attendance', params: { id: practiceId } })
}
function goRoster(): void {
  router.push({ name: 'master-attendance-roster', params: { id: practiceId } })
}

// -- Load --
async function load(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const cached = masterStore.practices.find((p) => p.id === practiceId)
    practice.value = cached ?? (await getPractice(practiceId))

    // Р1=А: only the PAST branch exists here; the upcoming hub is WI-B. Until
    // then, a non-past practice arriving at :id/detail falls back to its edit screen.
    const s = practice.value.status
    if (s !== 'completed' && s !== 'cancelled') {
      router.replace({ name: 'master-practice-edit', params: { id: practiceId } })
      return
    }

    const [attendanceData] = await Promise.all([
      getAttendance(practiceId),
      diaryStore.loadInsights(practiceId),
    ])
    attendance.value = attendanceData
  } catch (e) {
    error.value = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.practice-detail {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.practice-detail__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-10) 0;
}

.practice-detail__content {
  flex: 1;
  /* F-5 rail sync: ride MobileLayout's 24px rail (no local h-padding). */
  padding: var(--space-4) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* ===== Hero card ===== */
.practice-detail__head {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-4) var(--space-3);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.practice-detail__head-icon {
  color: var(--velo-text-primary);
  display: flex;
}

.practice-detail__head-title {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.3px;
  text-align: center;
}

.practice-detail__head-meta {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.practice-detail__head-meta > span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.practice-detail__head-meta :deep(svg) {
  opacity: 0.85;
}

/* Rating-distribution badges (sand/pink/blue-100 tints; confused = blue-400,
   unified with the practices-list rating badges). */
.practice-detail__rbadges {
  display: flex;
  gap: var(--space-2);
  margin-top: 4px;
}

.practice-detail__rbadge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 12px;
  border-radius: var(--velo-radius-badge);
  font-size: var(--text-xs);
}

.practice-detail__rbadge--fire {
  background: var(--velo-sand-100);
  color: var(--velo-rating-fire);
}

.practice-detail__rbadge--good {
  background: var(--velo-pink-100);
  color: var(--velo-rating-good);
}

.practice-detail__rbadge--conf {
  background: var(--velo-blue-100);
  color: var(--velo-blue-400);
}

/* ===== Stats (2-col, coloured values) ===== */
.practice-detail__stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

/* ===== Section ===== */
.practice-detail__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.practice-detail__section-title {
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

/* ===== Review card ===== */
.practice-detail__review {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--velo-card-padding-y) var(--velo-card-padding-x);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.practice-detail__review-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.practice-detail__review-name {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.practice-detail__review-quote {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  line-height: 1.45;
  padding-left: 32px;
}

/* ===== Empty ===== */
.practice-detail__empty {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  line-height: 1.5;
}

/* ===== Finance card ===== */
.practice-detail__finance {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.practice-detail__finrow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--velo-text-primary);
}

.practice-detail__finrow--income {
  color: var(--velo-teal-600);
}

/* ===== CTAs ===== */
.practice-detail__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-top: var(--space-1);
}
</style>
