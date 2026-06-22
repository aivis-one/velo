<!--
  VELO Frontend -- MasterPracticeDetailView (Phase-3 Master DS)

  Master's practice detail at /master/practices/:id/detail (masterStatusGuard;
  rendered inside MasterShell, no tab bar). Reached by tapping a practice card in
  MasterPracticesView (both tabs). Р1=А: ONE route, status-branched.

    - PAST branch (completed / cancelled): read-only review — hero + attendance
      stats + participant reviews + finance + Check-ins / Посещаемость CTAs.
    - UPCOMING branch (draft / scheduled / live) = WI-B hub: PracticeHeroCard +
      Записалось/Мест/Цена stat cards + «Записались» roster (each row removable) +
      description/contraindications accordions + «Начать практику» + Check-ins,
      with a «…» menu (Изменить / отменить|удалить). Replaces the former redirect
      to the edit screen. EditPracticeView is untouched (reached via «…» → Изменить).

  Decisions (operator, WI-B, all Г=А):
    FORK1 — the per-participant X opens a "Cancel a reservation" modal; confirm
            raises a «недоступно» toast: there is NO master-removes-participant
            endpoint (cancelBooking is self-only) → backend ask in
            master-ds-zod-roadmap (E11). FORK2 — the recurrence-days hero line is
            HIDDEN (no recurrence model). FORK3 — NO «Опубликовать» on the hub
            (draft→scheduled stays in EditPracticeView). FORK4 — the hub hero
            reuses the shared PracticeHeroCard.

  Data reality:
    REAL: header (getPractice) · Записалось/Мест/Цена + roster (getAttendance) ·
          «Начать практику» (updatePractice status='live') · отменить
          (cancelPractice) · удалить draft (deletePractice). PAST rating badges +
          stats as before (getAttendance + anonymous insights).
    STUB → Zod: remove-one-participant (no endpoint) → toast; «Доход» (no
          income/ledger API) → «—»; «Отзывы участников» (insights are anonymous).
-->

<template>
  <div class="practice-detail">
    <VHeader :title="headerTitle" show-back @back="router.back()">
      <template v-if="isUpcoming" #action>
        <VMenu aria-label="Меню">
          <template #default="{ close }">
            <!-- Карандаш → редактирование, корзина → удаление/отмена (Q1=А,
                 openDestructive контекстный: черновик удаляет, запланированную
                 отменяет, с подтверждением). -->
            <VMenuItem
              :icon="IconEdit"
              ariaLabel="Редактировать"
              @click="
                () => {
                  goEdit()
                  close()
                }
              "
            />
            <VMenuItem
              :icon="IconTrash"
              danger
              :ariaLabel="destructiveLabel"
              @click="
                () => {
                  openDestructive()
                  close()
                }
              "
            />
          </template>
        </VMenu>
      </template>
    </VHeader>

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
      <!-- ===================== UPCOMING hub (WI-B) ===================== -->
      <div v-if="isUpcoming" class="practice-detail__content">
        <!-- Hero (shared PracticeHeroCard — FORK4). Recurrence-days line is
             intentionally NOT shown (FORK2: no recurrence model). -->
        <PracticeHeroCard
          :title="practice.title"
          :date="whenLabel"
          :duration="durationLabel"
          :participants="participantsLabel"
          :direction="practice.direction"
          :difficulty-dots="difficultyDots"
          :difficulty-label="difficultyLabel"
        />

        <!-- Записалось / Мест (карточка «Цена» убрана — operator 2026-06-18) -->
        <div class="practice-detail__stats">
          <VStatCard :value="enrolledStat" label="Записалось" />
          <VStatCard :value="capacityStat" label="Мест" />
        </div>

        <!-- Записались (roster; первые 5 + раскрытие — operator 2026-06-18) -->
        <section v-if="rosterItems.length > 0" class="practice-detail__section">
          <h2 class="velo-section-title">Записались</h2>
          <div v-for="item in visibleRoster" :key="item.booking_id" class="pd-prow">
            <span class="pd-prow__ava">
              <img
                v-if="item.user_avatar_url"
                :src="item.user_avatar_url"
                alt=""
                class="pd-prow__ava-img"
              />
              <template v-else>{{ initials(item) }}</template>
            </span>
            <span class="pd-prow__name">{{ displayName(item) }}</span>
            <button class="pd-prow__x" aria-label="Отменить запись" @click="openCancelRes(item)">
              <IconClose :size="16" />
            </button>
          </div>
          <VShowMore
            v-if="!rosterExpanded && hiddenRosterCount > 0"
            :count="hiddenRosterCount"
            noun="участников"
            @click="rosterExpanded = true"
          />
        </section>

        <!-- Описание / Противопоказания -->
        <section
          v-if="practice.description || practice.contraindications"
          class="practice-detail__section practice-detail__accordions"
        >
          <VAccordion v-if="practice.description" title="Описание" :default-open="true">
            {{ practice.description }}
          </VAccordion>
          <VAccordion v-if="practice.contraindications" title="Противопоказания">
            {{ practice.contraindications }}
          </VAccordion>
        </section>

        <!-- Нижние кнопки убраны (operator 2026-06-18): запуск — авто по
             расписанию (Зод), check-in живёт на дашборде ≤24ч. -->
      </div>

      <!-- ===================== PAST detail (read-only) ===================== -->
      <div v-else class="practice-detail__content">
        <!-- Hero (shared PracticeHeroCard; titleSize base canon, icon-46;
             rating-distribution badges via the additive #extra slot) -->
        <PracticeHeroCard
          :title="practice.title"
          title-size="base"
          :date="whenLabel"
          :duration="durationLabel"
          :direction="practice.direction"
        >
          <template v-if="hasRating" #extra>
            <VRatingBadges
              size="lg"
              :fire="ratingPct('fire')"
              :good="ratingPct('good')"
              :confused="ratingPct('confused')"
            />
          </template>
        </PracticeHeroCard>

        <!-- Stats -->
        <div class="practice-detail__stats">
          <VStatCard :value="attendedValue" label="Присутствовало" value-tone="teal" />
          <VStatCard :value="noShowValue" label="Не пришли" value-tone="rose" />
        </div>

        <!-- Отзывы участников (E1 named reviews — getPracticeReviews) -->
        <section class="practice-detail__section">
          <h2 class="velo-section-title">Отзывы участников</h2>
          <div v-if="reviewsLoading && reviews.length === 0" class="practice-detail__rloader">
            <VLoader />
          </div>
          <template v-else-if="reviews.length > 0">
            <div v-for="(r, i) in visibleReviews" :key="i" class="practice-detail__review">
              <div class="practice-detail__review-top">
                <VAvatar :name="r.reviewer_name" :url="r.avatar_url ?? ''" size="sm" />
                <div class="practice-detail__review-id">
                  <span class="practice-detail__review-name">{{ r.reviewer_name }}</span>
                  <span class="practice-detail__review-date">{{
                    formatDateShort(r.created_at)
                  }}</span>
                </div>
                <span class="practice-detail__review-rating">
                  <component
                    :is="RATING_ICON[r.rating]"
                    :size="22"
                    :style="{ color: RATING_ICON_COLOR[r.rating] }"
                  />
                  {{ RATING_LABEL[r.rating] }}
                </span>
              </div>
              <div v-if="r.comment" class="practice-detail__review-quote">«{{ r.comment }}»</div>
            </div>
            <!-- Первые 5 + раскрытие «+ ещё N отзывов» (operator 2026-06-18). -->
            <VShowMore
              v-if="!reviewsExpanded && hiddenReviewsCount > 0"
              :count="hiddenReviewsCount"
              noun="отзывов"
              @click="expandReviews"
            />
            <div v-else-if="reviewsExpanded && hasMoreReviews" class="practice-detail__more">
              <VButton variant="ghost" @click="loadMoreReviews">Показать ещё</VButton>
            </div>
          </template>
          <VEmptyState v-else variant="note" title="Отзывов пока нет" />
        </section>

        <!-- Финансы -->
        <section class="practice-detail__section">
          <h2 class="velo-section-title">Финансы</h2>
          <div class="practice-detail__finance">
            <div class="practice-detail__finrow">
              <span>Записалось</span><span>{{ enrolledLabel }}</span>
            </div>
            <div class="practice-detail__finrow">
              <span>Присутствовало</span><span>{{ attendedPeopleLabel }}</span>
            </div>
            <!-- «Доход» убран до появления ledger-API (operator 2026-06-18). -->
          </div>
        </section>

        <!-- CTAs -->
        <div class="practice-detail__actions">
          <VButton variant="primary" block @click="goCheckins">Check-ins</VButton>
          <VButton variant="outline" block @click="goRoster">Посещаемость</VButton>
        </div>
      </div>
    </template>

    <!-- Cancel the whole practice (scheduled/live) — reuses CancelPracticeDialog. -->
    <CancelPracticeDialog
      :open="showCancel"
      :practice="practice"
      :loading="cancelling"
      @confirm="doCancel"
      @cancel="showCancel = false"
    />

    <!-- Delete a draft practice. -->
    <VConfirmDialog
      :open="showDelete"
      message="Удалить черновик практики? Это действие необратимо."
      confirm-label="Удалить"
      :loading="deleting"
      @confirm="doDelete"
      @cancel="showDelete = false"
    />

    <!-- Cancel a reservation (per participant) — FORK1: stub, no endpoint → toast. -->
    <VModal
      :open="showCancelRes"
      :show-close="false"
      :close-on-overlay="true"
      @close="showCancelRes = false"
    >
      <div class="pd-cres">
        <h2 class="pd-cres__title">Отменить запись?</h2>
        <div class="pd-cres__pcard">
          <span class="pd-cres__ava">{{ resInitials }}</span>
          <span class="pd-cres__name">{{ resName }}</span>
        </div>
        <Banner variant="warning" body="Участнику вернётся оплата и придёт уведомление об отмене.">
          <template #icon><IconWarning :size="28" /></template>
        </Banner>
        <div class="pd-cres__actions">
          <VButton variant="primary" @click="showCancelRes = false">Не отменять</VButton>
          <VButton variant="danger" @click="confirmCancelRes">Отменить запись</VButton>
        </div>
      </div>
    </VModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDiaryStore } from '@/stores/diary'
import { useMasterStore } from '@/stores/master'
import {
  getPractice,
  getAttendance,
  deletePractice,
  cancelPractice,
  getPracticeReviews,
} from '@/api/practices'
import { ApiResponseError } from '@/api/client'
import {
  VStatCard,
  VButton,
  VLoader,
  VEmptyState,
  VModal,
  VConfirmDialog,
  VAccordion,
  VMenu,
  VMenuItem,
  VAvatar,
  VRatingBadges,
} from '@/components/ui'
import { VHeader } from '@/components/layout'
import PracticeHeroCard from '@/components/shared/PracticeHeroCard.vue'
import VShowMore from '@/components/shared/VShowMore.vue'
import CancelPracticeDialog from '@/components/shared/CancelPracticeDialog.vue'
import Banner from '@/components/shared/Banner.vue'
import {
  IconClose,
  IconWarning,
  IconRatingFire,
  IconRatingGood,
  IconRatingConfused,
  IconEdit,
} from '@/components/icons'
// IconTrash is not re-exported from the icons barrel; import the component
// directly (same as EntryView).
import IconTrash from '@/components/icons/IconTrash.vue'
import {
  RATING_ICON_COLOR,
  RATING_LABEL,
  DIFFICULTY_DOTS,
  DIFFICULTY_LABEL,
} from '@/utils/displayHelpers'
import { formatDateShort, formatTime } from '@/utils/format'
import { useToast } from '@/composables/useToast'
import type {
  PracticeResponse,
  AttendanceResponse,
  AttendanceItemResponse,
  FeedbackRating,
  PracticeDifficulty,
  ReviewItem,
} from '@/api/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const diaryStore = useDiaryStore()
const masterStore = useMasterStore()

const practiceId = route.params.id as string

// -- Data --
const practice = ref<PracticeResponse | null>(null)
const attendance = ref<AttendanceResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// -- Status branch --
const isPast = computed(
  (): boolean => practice.value?.status === 'completed' || practice.value?.status === 'cancelled',
)
const isUpcoming = computed((): boolean => practice.value != null && !isPast.value)
const isDraft = computed((): boolean => practice.value?.status === 'draft')
const headerTitle = computed((): string => (isPast.value ? 'Прошедшая практика' : 'Практика'))
const destructiveLabel = computed((): string => (isDraft.value ? 'Удалить' : 'Отменить практику'))

// Reactive insights cache (shared with Analytics / Practices — often warm).
const insightsCache = diaryStore.insightsCache
const insights = computed(() => insightsCache.get(practiceId) ?? null)

// -- Hero meta (shared) --
const whenLabel = computed((): string => {
  if (!practice.value) return ''
  const day = formatDateShort(practice.value.scheduled_at, practice.value.timezone)
  const time = formatTime(practice.value.scheduled_at, practice.value.timezone)
  return `${day}, ${time}`
})

const durationLabel = computed((): string =>
  practice.value ? `${practice.value.duration_minutes} мин` : '',
)

// -- Upcoming hero extras --
const participantsLabel = computed((): string | null => {
  if (!practice.value) return null
  const enrolled = attendance.value ? attendance.value.total : practice.value.current_participants
  const cap = practice.value.max_participants
  return cap != null ? `${enrolled}/${cap}` : `${enrolled}`
})

const difficultyDots = computed((): number => {
  const d = practice.value?.difficulty
  return d ? DIFFICULTY_DOTS[d as PracticeDifficulty] : 0
})
const difficultyLabel = computed((): string => {
  const d = practice.value?.difficulty
  return d ? DIFFICULTY_LABEL[d as PracticeDifficulty] : ''
})

// -- Upcoming stat cards --
const enrolledStat = computed((): string | number =>
  attendance.value ? attendance.value.total : '—',
)
const capacityStat = computed((): string | number => {
  const cap = practice.value?.max_participants
  return cap != null ? cap : '∞'
})

// -- Roster (Записались): первые 5, остальные — по «+ ещё N участников» --
const ROSTER_PREVIEW = 5
const rosterItems = computed((): AttendanceItemResponse[] => attendance.value?.items ?? [])
const rosterExpanded = ref(false)
const visibleRoster = computed((): AttendanceItemResponse[] =>
  rosterExpanded.value ? rosterItems.value : rosterItems.value.slice(0, ROSTER_PREVIEW),
)
const hiddenRosterCount = computed((): number =>
  Math.max(0, rosterItems.value.length - ROSTER_PREVIEW),
)

function displayName(item: AttendanceItemResponse): string {
  return item.user_display_name || `#${item.user_id.slice(0, 8)}`
}
function initials(item: AttendanceItemResponse): string {
  const name = (item.user_display_name || item.user_id).trim()
  return (name.charAt(0) || '?').toUpperCase()
}

// -- Past: rating distribution badges (REAL, anonymous insights) --
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

// -- Past: stats + finance (REAL via getAttendance; "—" until loaded) --
const attendedValue = computed((): string | number =>
  attendance.value ? attendance.value.attended : '—',
)
const noShowValue = computed((): string | number =>
  attendance.value ? attendance.value.no_show : '—',
)
const enrolledLabel = computed((): string =>
  attendance.value ? `${attendance.value.total} чел.` : '—',
)
const attendedPeopleLabel = computed((): string =>
  attendance.value ? `${attendance.value.attended} чел.` : '—',
)

// -- Past: Отзывы участников (E1 named reviews — getPracticeReviews, paginated) --
const REVIEWS_PAGE = 20
const REVIEWS_PREVIEW = 5
const reviews = ref<ReviewItem[]>([])
const reviewsTotal = ref(0)
const reviewsLoading = ref(false)
const hasMoreReviews = computed((): boolean => reviews.value.length < reviewsTotal.value)

// Первые 5 + раскрытие «+ ещё N отзывов» (operator 2026-06-18).
const reviewsExpanded = ref(false)
const visibleReviews = computed((): ReviewItem[] =>
  reviewsExpanded.value ? reviews.value : reviews.value.slice(0, REVIEWS_PREVIEW),
)
const hiddenReviewsCount = computed((): number => Math.max(0, reviewsTotal.value - REVIEWS_PREVIEW))
function expandReviews(): void {
  reviewsExpanded.value = true
  if (hasMoreReviews.value) loadMoreReviews()
}
const RATING_ICON: Record<FeedbackRating, Component> = {
  fire: IconRatingFire,
  good: IconRatingGood,
  confused: IconRatingConfused,
}

async function loadReviews(): Promise<void> {
  reviewsLoading.value = true
  try {
    const res = await getPracticeReviews(practiceId, REVIEWS_PAGE, 0)
    reviews.value = res.items
    reviewsTotal.value = res.total
  } catch {
    // Non-fatal: the rest of the detail view stays usable; the section shows empty.
  } finally {
    reviewsLoading.value = false
  }
}

async function loadMoreReviews(): Promise<void> {
  if (reviewsLoading.value || !hasMoreReviews.value) return
  reviewsLoading.value = true
  try {
    const res = await getPracticeReviews(practiceId, REVIEWS_PAGE, reviews.value.length)
    reviews.value = [...reviews.value, ...res.items]
    reviewsTotal.value = res.total
  } catch {
    // Keep the loaded page; the «Показать ещё» button stays for a retry.
  } finally {
    reviewsLoading.value = false
  }
}

// -- Navigation --
function goCheckins(): void {
  router.push({ name: 'master-attendance', params: { id: practiceId } })
}
function goRoster(): void {
  router.push({ name: 'master-attendance-roster', params: { id: practiceId } })
}
function goEdit(): void {
  router.push({ name: 'master-practice-edit', params: { id: practiceId } })
}

// -- «…» destructive: cancel (scheduled/live) or delete (draft) --
const showCancel = ref(false)
const showDelete = ref(false)
const cancelling = ref(false)
const deleting = ref(false)

function openDestructive(): void {
  if (isDraft.value) showDelete.value = true
  else showCancel.value = true
}

async function doCancel(): Promise<void> {
  if (cancelling.value) return
  cancelling.value = true
  try {
    await cancelPractice(practiceId)
    toast.success('Практика отменена')
    await masterStore.refreshMyPractices()
    router.back()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось отменить практику')
  } finally {
    cancelling.value = false
    showCancel.value = false
  }
}

async function doDelete(): Promise<void> {
  if (deleting.value) return
  deleting.value = true
  try {
    await deletePractice(practiceId)
    toast.success('Черновик удалён')
    await masterStore.refreshMyPractices()
    router.back()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось удалить практику')
  } finally {
    deleting.value = false
    showDelete.value = false
  }
}

// -- Cancel a reservation (per participant) — FORK1 stub (no endpoint) --
const showCancelRes = ref(false)
const resName = ref('')
const resInitials = ref('?')
function openCancelRes(item: AttendanceItemResponse): void {
  resName.value = displayName(item)
  resInitials.value = initials(item)
  showCancelRes.value = true
}
function confirmCancelRes(): void {
  // No master-removes-participant endpoint (cancelBooking is self-only) → stub.
  // Recorded for Zod in master-ds-zod-roadmap (E11).
  showCancelRes.value = false
  toast.info('недоступно')
}

// -- Load --
async function load(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const cached = masterStore.practices.find((p) => p.id === practiceId)
    practice.value = cached ?? (await getPractice(practiceId))

    // Both branches need attendance (roster / stats). Insights (anonymous rating
    // distribution) only feed the PAST hero badges — load them lazily there.
    const [attendanceData] = await Promise.all([
      getAttendance(practiceId),
      isPast.value ? diaryStore.loadInsights(practiceId) : Promise.resolve(),
    ])
    attendance.value = attendanceData

    // Named reviews only exist for finished practices; non-fatal alongside the load.
    if (isPast.value) void loadReviews()
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

/* ===== Stats ===== */
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

/* Accordions sit on a white card plate (matches the surrounding surfaces). */
.practice-detail__accordions {
  gap: 0;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: 0 var(--space-4);
}

/* ===== Записались rows (upcoming roster) ===== */
.pd-prow {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: 10px var(--space-4);
}

.pd-prow__ava {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-60);
  color: var(--velo-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.pd-prow__ava-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pd-prow__name {
  flex: 1;
  min-width: 0;
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
}

.pd-prow__x {
  width: 30px;
  height: 30px;
  flex-shrink: 0;
  border: none;
  cursor: pointer;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  color: var(--velo-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--transition-fast);
}

.pd-prow__x:hover {
  color: var(--velo-danger-text);
}

/* ===== Review card (PAST) ===== */
.practice-detail__review {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--velo-card-padding-y) var(--velo-card-padding-x);
  display: flex;
  flex-direction: column;
  gap: var(--velo-gap-6);
}

.practice-detail__review-top {
  display: flex;
  align-items: center;
  gap: var(--velo-card-meta-row-gap);
}

.practice-detail__review-id {
  display: flex;
  flex-direction: column;
  gap: var(--velo-gap-2);
  min-width: 0;
}

.practice-detail__review-name {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.practice-detail__review-date {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

.practice-detail__review-rating {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: var(--velo-gap-6);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  white-space: nowrap;
}

.practice-detail__review-quote {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  line-height: 1.45;
}

.practice-detail__rloader {
  display: flex;
  justify-content: center;
  padding: var(--space-4) 0;
}

.practice-detail__more {
  display: flex;
  justify-content: center;
  padding-top: var(--space-2);
}

/* ===== Finance card (PAST) ===== */
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

/* ===== CTAs ===== */
.practice-detail__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-top: var(--space-1);
}

/* ===== Cancel-a-reservation modal ===== */
.pd-cres {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.pd-cres__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  text-align: center;
  letter-spacing: 0.02em;
  margin: 0;
}

.pd-cres__pcard {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  border: 1px solid var(--velo-primary);
  border-radius: var(--radius-md);
  padding: var(--velo-card-padding-y) var(--space-4);
}

.pd-cres__ava {
  width: var(--velo-size-44);
  height: var(--velo-size-44);
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-60);
  color: var(--velo-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-base);
}

.pd-cres__name {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.pd-cres__actions {
  display: flex;
  gap: var(--space-3);
}

.pd-cres__actions > * {
  flex: 1;
}
</style>
