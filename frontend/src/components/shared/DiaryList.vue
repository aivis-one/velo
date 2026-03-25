<!--
  VELO Frontend -- DiaryList (NEW-3)

  List view of the diary hub: tabs, card list, FAB, load more.
  Extracted from DiaryView.vue.

  Emits:
    open-checkin(item)   — checkin card clicked
    open-feedback(item)  — feedback card clicked
    open-entry(item)     — entry card clicked
    open-new             — FAB or empty state CTA clicked
    load-more            — "Показать ещё" clicked
    retry                — error state retry clicked
-->

<template>
  <div class="diary-list">
    <!-- Header -->
    <header class="diary-list__header">
      <h1 class="diary-list__header-title">Дневник</h1>
    </header>

    <!-- Tabs -->
    <div class="diary-list__tabs">
      <button
        v-for="tab in TABS"
        :key="tab.value"
        class="diary-list__tab"
        :class="{ 'diary-list__tab--active': activeTab === tab.value }"
        @click="setTab(tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading (initial) -->
    <div v-if="listLoading && visibleItems.length === 0" class="diary-list__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error -->
    <VEmptyState
      v-else-if="listError && visibleItems.length === 0"
      icon="⚠️"
      title="Ошибка загрузки"
      :description="listError"
    >
      <VButton size="sm" @click="emit('retry')">Попробовать снова</VButton>
    </VEmptyState>

    <!-- Empty state -->
    <VEmptyState
      v-else-if="!listLoading && visibleItems.length === 0"
      :icon="emptyIcon"
      :title="emptyTitle"
      :description="emptyDescription"
    >
      <VButton
        v-if="activeTab === 'entries' || activeTab === 'all'"
        size="sm"
        variant="outline"
        @click="emit('open-new')"
      >
        Написать запись
      </VButton>
    </VEmptyState>

    <!-- Card list -->
    <div v-else class="diary-list__cards">
      <template v-for="item in visibleItems" :key="item.id">
        <!-- Checkin card -->
        <div
          v-if="item._type === 'checkin'"
          class="diary-card"
          @click="emit('open-checkin', item)"
        >
          <div class="diary-card__header">
            <span class="diary-card__date">{{ formatLongDate(item.created_at) }}</span>
            <span class="diary-card__emoji">{{ MOOD_EMOJI[item.mood] }}</span>
          </div>
          <div class="diary-card__title">Check-in: {{ MOOD_LABEL[item.mood] }}</div>
          <div class="diary-card__preview">{{ item.comment || '—' }}</div>
        </div>

        <!-- Feedback card -->
        <div
          v-else-if="item._type === 'feedback'"
          class="diary-card"
          @click="emit('open-feedback', item)"
        >
          <div class="diary-card__header">
            <span class="diary-card__date">{{ formatLongDate(item.created_at) }}</span>
            <span class="diary-card__emoji">{{ RATING_EMOJI[item.rating] }}</span>
          </div>
          <div class="diary-card__title">Feedback: {{ RATING_LABEL[item.rating] }}</div>
          <div class="diary-card__preview">{{ item.comment || '—' }}</div>
        </div>

        <!-- Entry card -->
        <div
          v-else-if="item._type === 'entry'"
          class="diary-card diary-card--entry"
          @click="emit('open-entry', item)"
        >
          <div class="diary-card__header">
            <span class="diary-card__date">{{ formatLongDate(item.created_at) }}</span>
            <span v-if="item.mood" class="diary-card__emoji">{{ MOOD_EMOJI[item.mood] }}</span>
          </div>
          <div class="diary-card__title">{{ item.title || 'Без названия' }}</div>
          <div class="diary-card__preview">{{ truncate(item.content, 80) }}</div>
        </div>
      </template>

      <!-- Load more -->
      <div v-if="listHasMore" class="diary-list__load-more">
        <VButton
          variant="ghost"
          block
          :loading="listLoading"
          @click="emit('load-more')"
        >
          Показать ещё
        </VButton>
      </div>
    </div>

    <!-- FAB -->
    <button class="diary-list__fab" aria-label="Новая запись" @click="emit('open-new')">+</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import {
  MOOD_EMOJI,
  MOOD_LABEL,
  RATING_EMOJI,
  RATING_LABEL,
} from '@/utils/displayHelpers'
import type { CheckinResponse, FeedbackResponse, DiaryEntryResponse } from '@/api/types'

// -- Types --
type TaggedCheckin  = CheckinResponse  & { _type: 'checkin' }
type TaggedFeedback = FeedbackResponse & { _type: 'feedback' }
type TaggedEntry    = DiaryEntryResponse & { _type: 'entry' }
export type FeedItem = TaggedCheckin | TaggedFeedback | TaggedEntry

type TabValue = 'all' | 'checkins' | 'feedbacks' | 'entries'

const TABS: Array<{ value: TabValue; label: string }> = [
  { value: 'all',       label: 'Всё' },
  { value: 'checkins',  label: 'Check-ins' },
  { value: 'feedbacks', label: 'Feedbacks' },
  { value: 'entries',   label: 'Записи' },
]

// -- Props --
const props = defineProps<{
  checkins: CheckinResponse[]
  feedbacks: FeedbackResponse[]
  entries: DiaryEntryResponse[]
  checkinsLoading: boolean
  feedbacksLoading: boolean
  entriesLoading: boolean
  checkinsHasMore: boolean
  feedbacksHasMore: boolean
  entriesHasMore: boolean
  checkinsError: string | null
  feedbacksError: string | null
  entriesError: string | null
}>()

const emit = defineEmits<{
  'open-checkin': [item: CheckinResponse]
  'open-feedback': [item: FeedbackResponse]
  'open-entry': [item: DiaryEntryResponse]
  'open-new': []
  'load-more': []
  retry: []
}>()

// -- Tab state --
const activeTab = ref<TabValue>('all')

function setTab(tab: TabValue): void {
  activeTab.value = tab
}

// -- Merged feed --
const allItems = computed((): FeedItem[] => {
  const c: TaggedCheckin[]  = props.checkins.map((x) => ({ ...x, _type: 'checkin'  as const }))
  const f: TaggedFeedback[] = props.feedbacks.map((x) => ({ ...x, _type: 'feedback' as const }))
  const e: TaggedEntry[]    = props.entries.map((x)   => ({ ...x, _type: 'entry'    as const }))
  return [...c, ...f, ...e].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )
})

const visibleItems = computed((): FeedItem[] => {
  switch (activeTab.value) {
    case 'checkins':  return props.checkins.map((x) => ({ ...x, _type: 'checkin'  as const }))
    case 'feedbacks': return props.feedbacks.map((x) => ({ ...x, _type: 'feedback' as const }))
    case 'entries':   return props.entries.map((x)   => ({ ...x, _type: 'entry'    as const }))
    default:          return allItems.value
  }
})

const listLoading = computed((): boolean => {
  switch (activeTab.value) {
    case 'checkins':  return props.checkinsLoading
    case 'feedbacks': return props.feedbacksLoading
    case 'entries':   return props.entriesLoading
    default:          return props.checkinsLoading || props.feedbacksLoading || props.entriesLoading
  }
})

const listHasMore = computed((): boolean => {
  switch (activeTab.value) {
    case 'checkins':  return props.checkinsHasMore
    case 'feedbacks': return props.feedbacksHasMore
    case 'entries':   return props.entriesHasMore
    default:          return props.checkinsHasMore || props.feedbacksHasMore || props.entriesHasMore
  }
})

const listError = computed((): string | null =>
  props.entriesError ?? props.checkinsError ?? props.feedbacksError ?? null,
)

// -- Empty state copy --
const emptyIcon = computed((): string => {
  switch (activeTab.value) {
    case 'checkins':  return '✅'
    case 'feedbacks': return '💬'
    case 'entries':   return '📝'
    default:          return '📔'
  }
})

const emptyTitle = computed((): string => {
  switch (activeTab.value) {
    case 'checkins':  return 'Нет check-ins'
    case 'feedbacks': return 'Нет отзывов'
    case 'entries':   return 'Нет записей'
    default:          return 'Дневник пуст'
  }
})

const emptyDescription = computed((): string => {
  switch (activeTab.value) {
    case 'checkins':  return 'Отметьтесь перед следующей практикой'
    case 'feedbacks': return 'Оставьте отзыв после практики'
    case 'entries':   return 'Напишите свою первую заметку'
    default:          return 'Здесь появятся ваши check-ins, отзывы и записи'
  }
})

// -- Helpers --
function formatLongDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

function truncate(text: string, max: number): string {
  if (text.length <= max) return text
  return text.slice(0, max).trimEnd() + '…'
}
</script>

<style scoped>
.diary-list {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  position: relative;
  padding-bottom: var(--space-20, 80px);
}

/* Header */
.diary-list__header {
  padding: var(--space-4);
}

.diary-list__header-title {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

/* Tabs */
.diary-list__tabs {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  overflow-x: auto;
  scrollbar-width: none;
}

.diary-list__tabs::-webkit-scrollbar {
  display: none;
}

.diary-list__tab {
  padding: var(--space-2) var(--space-4);
  border-radius: 100px;
  border: 1px solid #ffffff;
  background: var(--velo-bg-card);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast);
}

.diary-list__tab:hover {
  opacity: 0.8;
}

.diary-list__tab--active {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: white;
}

/* Loader */
.diary-list__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-10) 0;
}

/* Cards */
.diary-list__cards {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.diary-list__load-more {
  padding-top: var(--space-2);
}

/* Card */
.diary-card {
  background: var(--velo-bg-card);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  cursor: pointer;
  transition: opacity var(--transition-fast);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.diary-card:hover {
  opacity: 0.9;
}

.diary-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-1);
}

.diary-card__date {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.diary-card__emoji {
  font-size: 20px;
}

.diary-card__title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-1);
}

.diary-card__preview {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.diary-card--entry {
  border-left: 3px solid var(--velo-primary);
}

/* FAB */
.diary-list__fab {
  position: fixed;
  bottom: calc(var(--space-16, 64px) + var(--space-4));
  right: var(--space-4);
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  background: var(--velo-primary);
  color: white;
  font-size: 28px;
  font-weight: 400;
  border: 1px solid #ffffff;
  cursor: pointer;
  box-shadow: var(--velo-shadow-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity var(--transition-fast);
  z-index: 20;
}

.diary-list__fab:hover {
  opacity: 0.9;
}

.diary-list__fab:active {
  opacity: 0.8;
}
</style>
