<!--
  VELO Frontend -- DetailView (Diary redesign, Batch 1b; screen 52)

  Read-only detail for a check-in or a feedback, opened by tapping the
  corresponding card in the diary feed (DiaryFeedView.onTap -> route
  user-diary-detail with :type = checkin|feedback and :id = the row id).

  The :type segment is constrained to checkin|feedback in the route regex,
  so an invalid type never reaches this component (it 404s at the router).

  Data flow (mirrors EntryView):
    - the row itself (mood/rating, full comment, created_at, practice_id)
      comes from getCheckin(id) / getFeedback(id);
    - the optional practice header is built from GET /practices/{practice_id}
      when the row is linked to a practice. The verified badge is omitted
      (PracticeResponse carries no verified flag -- same call as EntryView).

  No store: this is a one-shot read with no caching or mutations, loaded
  directly via the api wrappers (like getPractice).

  Relationships ("Найдена взаимосвязь", screens 53-55) is an AI feature
  outside the MVP and is deliberately NOT rendered here.
-->

<template>
  <div class="detail">
    <!-- Header -->
    <header class="detail__header">
      <button
        type="button"
        class="detail__icon-btn detail__back"
        aria-label="Назад"
        @click="goBack"
      >
        <IconArrowRight :size="20" class="detail__back-glyph" />
      </button>
      <h1 class="detail__title-bar">Запись</h1>
      <span class="detail__icon-btn detail__icon-spacer" aria-hidden="true" />
    </header>

    <!-- Body -->
    <div class="detail__body">
      <!-- Loading -->
      <div v-if="loading" class="detail__state">
        <VLoader size="lg" />
      </div>

      <!-- Error -->
      <VEmptyState
        v-else-if="loadError"
        icon="⚠️"
        title="Не удалось загрузить запись"
        :description="loadError"
      >
        <template #action>
          <VButton variant="primary" @click="reload">Повторить</VButton>
        </template>
      </VEmptyState>

      <template v-else-if="loaded">
        <!-- Optional practice header (same layout as EntryView). -->
        <div v-if="practice" class="detail__practice">
          <component
            :is="practiceIcon"
            :size="40"
            class="detail__practice-icon"
          />
          <p class="detail__practice-title">{{ practice.title }}</p>
          <div class="detail__practice-master">
            <span class="detail__avatar" aria-hidden="true">
              <img
                v-if="practice.master_avatar_url"
                :src="practice.master_avatar_url"
                alt=""
                class="detail__avatar-img"
              />
            </span>
            <span class="detail__master-name">{{ practice.master_name }}</span>
          </div>
          <div class="detail__practice-meta">
            <IconCalendar :size="14" class="detail__meta-icon" />
            <span>{{ practiceDate }}</span>
            <IconClock :size="14" class="detail__meta-icon" />
            <span>{{ practiceDuration }}</span>
          </div>
        </div>

        <!-- The check-in / feedback pill -->
        <div class="detail__pill">
          <span class="detail__pill-icon">
            <component :is="leadIcon" :size="32" />
          </span>
          <span class="detail__pill-title">{{ pillTitle }}</span>
        </div>

        <!-- The detail card -->
        <div class="detail__card">
          <p class="detail__date">{{ dateLine }}</p>
          <p v-if="comment" class="detail__content">{{ comment }}</p>
          <p v-else class="detail__empty">Без комментария</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import {
  IconArrowRight,
  IconCalendar,
  IconClock,
  IconMoodLow,
  IconMoodMid,
  IconMoodHigh,
  IconRatingFire,
  IconRatingGood,
  IconRatingConfused,
} from '@/components/icons'
import { useAuthStore } from '@/stores/auth'
import { extractApiError } from '@/composables/useApiError'
import { getCheckin, getFeedback } from '@/api/diary'
import { getPractice } from '@/api/practices'
import { formatFeedDateTime, formatDate, formatDuration } from '@/utils/format'
import { MOOD_LABEL, RATING_LABEL, practiceIconFor } from '@/utils/displayHelpers'
import type {
  CheckinResponse,
  FeedbackResponse,
  PracticeResponse,
} from '@/api/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const tz = computed(() => authStore.user?.timezone ?? 'UTC')
const detailType = computed<'checkin' | 'feedback'>(
  () => (route.params.type === 'feedback' ? 'feedback' : 'checkin'),
)
const detailId = computed(() => String(route.params.id))

// -- loaded row + practice header --------------------------------------------

const checkin = ref<CheckinResponse | null>(null)
const feedback = ref<FeedbackResponse | null>(null)
const practice = ref<PracticeResponse | null>(null)

const loading = ref(false)
const loadError = ref<string | null>(null)
const loaded = computed(
  () => checkin.value !== null || feedback.value !== null,
)

// -- icon / label maps (kind|mood|rating -> component; .vue can't live in
//    displayHelpers, mirrors DiaryFeedCard) ----------------------------------

const MOOD_ICON: Record<string, Component> = {
  low: IconMoodLow,
  mid: IconMoodMid,
  high: IconMoodHigh,
}
const RATING_ICON: Record<string, Component> = {
  fire: IconRatingFire,
  good: IconRatingGood,
  confused: IconRatingConfused,
}
const leadIcon = computed<Component>(() => {
  if (detailType.value === 'checkin') {
    return MOOD_ICON[checkin.value?.mood ?? 'mid'] ?? IconMoodMid
  }
  return RATING_ICON[feedback.value?.rating ?? 'good'] ?? IconRatingGood
})

const pillTitle = computed(() => {
  if (detailType.value === 'checkin') {
    const mood = checkin.value?.mood
    const label = mood ? MOOD_LABEL[mood] ?? '' : ''
    return label ? `Check-in: ${label}` : 'Check-in'
  }
  const rating = feedback.value?.rating
  const label = rating ? RATING_LABEL[rating] ?? '' : ''
  return label ? `Feedback: ${label}` : 'Feedback'
})

const comment = computed(
  () => checkin.value?.comment ?? feedback.value?.comment ?? null,
)

const createdAt = computed(
  () => checkin.value?.created_at ?? feedback.value?.created_at ?? null,
)
const dateLine = computed(() =>
  createdAt.value ? formatFeedDateTime(createdAt.value, tz.value) : '',
)

// -- practice header ---------------------------------------------------------

const practiceIcon = computed<Component>(() =>
  practiceIconFor({
    direction: practice.value?.direction,
    title: practice.value?.title,
  }),
)
const practiceDate = computed(() =>
  practice.value ? formatDate(practice.value.scheduled_at, tz.value) : '',
)
const practiceDuration = computed(() =>
  practice.value ? formatDuration(practice.value.duration_minutes) : '',
)

// -- load --------------------------------------------------------------------

async function reload(): Promise<void> {
  loading.value = true
  loadError.value = null
  checkin.value = null
  feedback.value = null
  practice.value = null
  try {
    let practiceId: string | null = null
    if (detailType.value === 'checkin') {
      const row = await getCheckin(detailId.value)
      checkin.value = row
      practiceId = row.practice_id
    } else {
      const row = await getFeedback(detailId.value)
      feedback.value = row
      practiceId = row.practice_id
    }
    if (practiceId) {
      try {
        practice.value = await getPractice(practiceId)
      } catch {
        // Practice header is best-effort; degrade to no header.
        practice.value = null
      }
    }
  } catch (e) {
    loadError.value = extractApiError(e, 'Запись не найдена')
  } finally {
    loading.value = false
  }
}

onMounted(reload)

// -- navigation --------------------------------------------------------------

function goBack(): void {
  void router.push({ name: 'user-diary' })
}
</script>

<style scoped>
/* Read-only variant of EntryView's layout: fixed header + scrolling body,
   no menu / no save bar. Tokens only (variables.css). */
.detail {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* -- Header -- */
.detail__header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-8) var(--space-3);
}

.detail__title-bar {
  flex: 1;
  text-align: center;
  font-family: var(--font-heading);
  font-size: var(--text-base);
  letter-spacing: 0.36px;
  color: var(--velo-text-primary);
}

.detail__icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.detail__icon-spacer {
  cursor: default;
  background: transparent;
}

.detail__back {
  background: var(--velo-bg-card-solid);
  color: var(--velo-text-primary);
}

/* The only "back" glyph available is a right arrow -- mirror it. */
.detail__back-glyph {
  transform: scaleX(-1);
}

.detail__icon-btn:hover {
  opacity: 0.85;
}

/* -- Body (scrolls) -- */
.detail__body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: 0 var(--space-8) var(--space-4);
}

.detail__state {
  display: flex;
  justify-content: center;
  padding: var(--space-10) 0;
}

/* -- Practice header (mirrors EntryView / feed-card--practice) -- */
.detail__practice {
  position: relative;
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.detail__practice-icon {
  position: absolute;
  top: var(--space-3);
  left: var(--space-4);
  /* Цвет — text-primary (Figma DS): иконка сама несёт circle-обводку. */
  color: var(--velo-text-primary);
}

.detail__practice-title {
  font-size: 16px;
  text-align: center;
  letter-spacing: 0.32px;
  color: var(--velo-text-primary);
}

.detail__practice-master {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
}

.detail__avatar {
  width: 14px;
  height: 14px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-40);
  overflow: hidden;
  flex-shrink: 0;
}

.detail__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail__master-name {
  font-size: 12px;
  color: var(--velo-text-secondary);
}

.detail__practice-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  font-size: 12px;
  color: var(--velo-text-secondary);
}

.detail__meta-icon {
  color: var(--velo-text-secondary);
}

/* -- Check-in / feedback pill (lead icon + title) -- */
.detail__pill {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
}

.detail__pill-icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
}

.detail__pill-title {
  font-size: 16px;
  letter-spacing: 0.32px;
  color: var(--velo-text-primary);
}

/* -- Detail card (date + full comment) -- */
.detail__card {
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.detail__date {
  font-size: 12.375px;
  letter-spacing: 0.2475px;
  opacity: 0.6;
  color: var(--velo-text-primary);
}

.detail__content {
  font-size: var(--text-sm);
  line-height: 1.5;
  color: var(--velo-text-primary);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.detail__empty {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  opacity: 0.7;
}
</style>
