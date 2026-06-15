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
            <div class="pd-menu">
              <button class="pd-menu__row" @click="() => { goEdit(); close() }">Изменить</button>
              <button
                class="pd-menu__row pd-menu__row--danger"
                @click="() => { openDestructive(); close() }"
              >
                {{ destructiveLabel }}
              </button>
            </div>
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

        <!-- Записалось / Мест / Цена -->
        <div class="practice-detail__stats practice-detail__stats--3">
          <VStatCard :value="enrolledStat" label="Записалось" />
          <VStatCard :value="capacityStat" label="Мест" />
          <VStatCard :value="priceStat" label="Цена" />
        </div>

        <!-- Записались (roster; each row removable — FORK1) -->
        <section v-if="rosterItems.length > 0" class="practice-detail__section">
          <h2 class="practice-detail__section-title">Записались</h2>
          <div v-for="item in rosterItems" :key="item.booking_id" class="pd-prow">
            <span class="pd-prow__ava">
              <img v-if="item.user_avatar_url" :src="item.user_avatar_url" alt="" class="pd-prow__ava-img" />
              <template v-else>{{ initials(item) }}</template>
            </span>
            <span class="pd-prow__name">{{ displayName(item) }}</span>
            <button class="pd-prow__x" aria-label="Отменить запись" @click="openCancelRes(item)">
              <IconClose :size="16" />
            </button>
          </div>
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

        <!-- CTAs -->
        <div class="practice-detail__actions">
          <VButton
            v-if="canStart"
            variant="primary"
            block
            :loading="starting"
            @click="startPractice"
          >
            Начать практику
          </VButton>
          <VButton variant="outline" block @click="goCheckins">Check-ins</VButton>
        </div>
      </div>

      <!-- ===================== PAST detail (read-only) ===================== -->
      <div v-else class="practice-detail__content">
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
    <VModal :open="showCancelRes" :show-close="false" :close-on-overlay="true" @close="showCancelRes = false">
      <div class="pd-cres">
        <h2 class="pd-cres__title">Отменить запись?</h2>
        <div class="pd-cres__pcard">
          <span class="pd-cres__ava">{{ resInitials }}</span>
          <span class="pd-cres__name">{{ resName }}</span>
        </div>
        <Banner
          variant="warning"
          body="Участнику вернётся оплата и придёт уведомление об отмене."
        >
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
import { getPractice, getAttendance, updatePractice, deletePractice, cancelPractice } from '@/api/practices'
import { ApiResponseError } from '@/api/client'
import { VStatCard, VButton, VLoader, VEmptyState, VModal, VConfirmDialog, VAccordion, VMenu } from '@/components/ui'
import { VHeader } from '@/components/layout'
import PracticeHeroCard from '@/components/shared/PracticeHeroCard.vue'
import CancelPracticeDialog from '@/components/shared/CancelPracticeDialog.vue'
import Banner from '@/components/shared/Banner.vue'
import { IconCalendar, IconClock, IconClose, IconWarning, IconRatingFire, IconRatingGood, IconRatingConfused } from '@/components/icons'
import { practiceIconFor, RATING_ICON_COLOR, DIFFICULTY_DOTS, DIFFICULTY_LABEL } from '@/utils/displayHelpers'
import { formatDateShort, formatTime, formatMoney } from '@/utils/format'
import { useToast } from '@/composables/useToast'
import type { PracticeResponse, AttendanceResponse, AttendanceItemResponse, FeedbackRating, PracticeDifficulty } from '@/api/types'

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
// «Начать практику» publishes draft/scheduled → live. A live practice is already
// started, so the CTA is hidden then (FORK3: no «Опубликовать» here regardless).
const canStart = computed(
  (): boolean => practice.value?.status === 'draft' || practice.value?.status === 'scheduled',
)
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
const enrolledStat = computed((): string | number => (attendance.value ? attendance.value.total : '—'))
const capacityStat = computed((): string | number => {
  const cap = practice.value?.max_participants
  return cap != null ? cap : '∞'
})
const priceStat = computed((): string => {
  if (!practice.value) return '—'
  return practice.value.is_free
    ? 'Бесплатно'
    : formatMoney(practice.value.price_cents, (practice.value.currency || 'eur').toUpperCase())
})

// -- Roster (Записались) --
const rosterItems = computed((): AttendanceItemResponse[] => attendance.value?.items ?? [])

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
const attendedValue = computed((): string | number => (attendance.value ? attendance.value.attended : '—'))
const noShowValue = computed((): string | number => (attendance.value ? attendance.value.no_show : '—'))
const enrolledLabel = computed((): string => (attendance.value ? `${attendance.value.total} чел.` : '—'))
const attendedPeopleLabel = computed((): string => (attendance.value ? `${attendance.value.attended} чел.` : '—'))
// STUB → Zod: no income/ledger API yet (currency canon ₽ vs € also deferred).
const incomeLabel = '—'

// -- Past: Отзывы участников scaffold (no backend source — insights are anonymous) --
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
function goEdit(): void {
  router.push({ name: 'master-practice-edit', params: { id: practiceId } })
}

// -- «Начать практику» (scheduled/draft → live) --
const starting = ref(false)
async function startPractice(): Promise<void> {
  if (starting.value || !practice.value) return
  starting.value = true
  try {
    practice.value = await updatePractice(practiceId, { status: 'live' })
    toast.success('Практика началась')
    await masterStore.refreshMyPractices()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось начать практику')
  } finally {
    starting.value = false
  }
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

/* ===== Hero card (PAST bespoke) ===== */
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

/* Rating-distribution badges (sand/pink/blue-100 tints; confused = blue-400). */
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

/* ===== Stats ===== */
.practice-detail__stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.practice-detail__stats--3 {
  grid-template-columns: repeat(3, 1fr);
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

/* ===== «…» menu rows (text popover in the VMenu slot) ===== */
.pd-menu {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  box-shadow: var(--velo-shadow-glow);
  overflow: hidden;
  min-width: 200px;
}

.pd-menu__row {
  display: block;
  width: 100%;
  padding: 13px var(--space-4);
  border: none;
  background: none;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  text-align: left;
  transition: background-color var(--transition-fast);
}

.pd-menu__row:hover {
  background: var(--velo-glass-blue-15);
}

.pd-menu__row + .pd-menu__row {
  border-top: 1px solid var(--velo-border-light);
}

.pd-menu__row--danger {
  color: var(--velo-danger-text);
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
  padding: 13px 16px;
}

.pd-cres__ava {
  width: 44px;
  height: 44px;
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
