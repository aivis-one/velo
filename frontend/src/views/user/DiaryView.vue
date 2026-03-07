<!--
  VELO Frontend -- DiaryView (Phase F9.2)

  Personal diary hub. Manages all sub-views via internal state
  (no separate routes) matching the mockup navigation graph:

    list           ← main hub: tabs + card list + FAB
    detail-checkin ← read-only checkin view
    detail-feedback← read-only feedback view
    detail-entry   ← diary entry detail with edit/delete actions
    new            ← new entry form
    edit           ← edit existing entry form

  Tabs: Всё / Check-ins / Feedbacks / Записи

  "Всё" merges all three data types, sorted by created_at desc.
  Check-ins and Feedbacks are read-only (submitted through
  CheckinView / FeedbackView respectively).
  Diary entries are fully CRUD: create, read, update, delete.

  Route: /user/diary (name: user-diary)
-->

<template>
  <div class="diary">

    <!-- ================================================================
         LIST VIEW
         ================================================================ -->
    <template v-if="currentView === 'list'">
      <header class="diary__header">
        <h1 class="diary__header-title">Дневник</h1>
      </header>

      <!-- Tabs -->
      <div class="diary__tabs">
        <button
          v-for="tab in TABS"
          :key="tab.value"
          class="diary__tab"
          :class="{ 'diary__tab--active': activeTab === tab.value }"
          @click="setTab(tab.value)"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Loading (initial) -->
      <div v-if="listLoading && visibleItems.length === 0" class="diary__loader">
        <VLoader size="lg" />
      </div>

      <!-- Error -->
      <VEmptyState
        v-else-if="listError && visibleItems.length === 0"
        icon="⚠️"
        title="Ошибка загрузки"
        :description="listError"
      >
        <VButton size="sm" @click="onRetry">Попробовать снова</VButton>
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
          @click="openNew"
        >
          Написать запись
        </VButton>
      </VEmptyState>

      <!-- Card list -->
      <div v-else class="diary__list">
        <template v-for="item in visibleItems" :key="item.id">
          <!-- Checkin card -->
          <div
            v-if="item._type === 'checkin'"
            class="diary-card"
            @click="openCheckinDetail(item)"
          >
            <div class="diary-card__header">
              <span class="diary-card__date">{{ formatShortDate(item.created_at) }}</span>
              <span class="diary-card__emoji">{{ MOOD_EMOJI[item.mood] }}</span>
            </div>
            <div class="diary-card__title">Check-in: {{ MOOD_LABEL[item.mood] }}</div>
            <div class="diary-card__preview">{{ item.comment || '—' }}</div>
          </div>

          <!-- Feedback card -->
          <div
            v-else-if="item._type === 'feedback'"
            class="diary-card"
            @click="openFeedbackDetail(item)"
          >
            <div class="diary-card__header">
              <span class="diary-card__date">{{ formatShortDate(item.created_at) }}</span>
              <span class="diary-card__emoji">{{ RATING_EMOJI[item.rating] }}</span>
            </div>
            <div class="diary-card__title">Feedback: {{ RATING_LABEL[item.rating] }}</div>
            <div class="diary-card__preview">{{ item.comment || '—' }}</div>
          </div>

          <!-- Diary entry card -->
          <div
            v-else-if="item._type === 'entry'"
            class="diary-card diary-card--entry"
            @click="openEntryDetail(item)"
          >
            <div class="diary-card__header">
              <span class="diary-card__date">{{ formatShortDate(item.created_at) }}</span>
              <span v-if="item.mood" class="diary-card__emoji">{{ MOOD_EMOJI[item.mood] }}</span>
            </div>
            <div class="diary-card__title">{{ item.title || 'Без названия' }}</div>
            <div class="diary-card__preview">{{ truncate(item.content, 80) }}</div>
          </div>
        </template>

        <!-- Load more -->
        <div v-if="listHasMore" class="diary__load-more">
          <VButton
            variant="ghost"
            block
            :loading="listLoading"
            @click="onLoadMore"
          >
            Показать ещё
          </VButton>
        </div>
      </div>

      <!-- FAB: new diary entry -->
      <button class="diary__fab" @click="openNew">+</button>
    </template>

    <!-- ================================================================
         DETAIL: CHECKIN (read-only)
         ================================================================ -->
    <template v-else-if="currentView === 'detail-checkin' && selectedCheckin">
      <header class="diary__header diary__header--nav">
        <button class="diary__back" @click="backToList">←</button>
        <h1 class="diary__header-title">Check-in</h1>
        <span class="diary__header-spacer" />
      </header>

      <div class="diary__detail-body">
        <div class="diary__detail-date">{{ formatFullDate(selectedCheckin.created_at) }}</div>
        <h2 class="diary__detail-title">
          {{ MOOD_EMOJI[selectedCheckin.mood] }} Check-in: {{ MOOD_LABEL[selectedCheckin.mood] }}
        </h2>
        <div v-if="selectedCheckin.comment" class="diary__detail-content">
          {{ selectedCheckin.comment }}
        </div>
        <div class="diary__detail-context">
          📌 Перед практикой
        </div>
      </div>
    </template>

    <!-- ================================================================
         DETAIL: FEEDBACK (read-only)
         ================================================================ -->
    <template v-else-if="currentView === 'detail-feedback' && selectedFeedback">
      <header class="diary__header diary__header--nav">
        <button class="diary__back" @click="backToList">←</button>
        <h1 class="diary__header-title">Feedback</h1>
        <span class="diary__header-spacer" />
      </header>

      <div class="diary__detail-body">
        <div class="diary__detail-date">{{ formatFullDate(selectedFeedback.created_at) }}</div>
        <h2 class="diary__detail-title">
          {{ RATING_EMOJI[selectedFeedback.rating] }} Feedback: {{ RATING_LABEL[selectedFeedback.rating] }}
        </h2>
        <div v-if="selectedFeedback.comment" class="diary__detail-content">
          {{ selectedFeedback.comment }}
        </div>
        <div class="diary__detail-context">
          📌 После практики
        </div>
      </div>
    </template>

    <!-- ================================================================
         DETAIL: ENTRY (with edit button)
         ================================================================ -->
    <template v-else-if="currentView === 'detail-entry' && selectedEntry">
      <header class="diary__header diary__header--nav">
        <button class="diary__back" @click="backToList">←</button>
        <h1 class="diary__header-title">Запись</h1>
        <button class="diary__header-action" @click="openEdit">✏️</button>
      </header>

      <div class="diary__detail-body">
        <div class="diary__detail-date">{{ formatFullDate(selectedEntry.created_at) }}</div>
        <h2 class="diary__detail-title">{{ selectedEntry.title || 'Без названия' }}</h2>
        <div class="diary__detail-content">{{ selectedEntry.content }}</div>
      </div>
    </template>

    <!-- ================================================================
         NEW ENTRY FORM
         ================================================================ -->
    <template v-else-if="currentView === 'new'">
      <header class="diary__header diary__header--nav">
        <button class="diary__back" @click="backToList">←</button>
        <h1 class="diary__header-title">Новая запись</h1>
        <span class="diary__header-spacer" />
      </header>

      <div class="diary__form">
        <div class="diary__form-group">
          <label class="diary__form-label">Заголовок</label>
          <input
            v-model="formTitle"
            class="diary__input"
            type="text"
            placeholder="О чём хотите написать?"
            maxlength="200"
          />
        </div>
        <div class="diary__form-group diary__form-group--grow">
          <label class="diary__form-label">Текст</label>
          <textarea
            v-model="formContent"
            class="diary__textarea"
            placeholder="Напишите свои мысли..."
            maxlength="10000"
          />
        </div>
      </div>

      <div class="diary__form-actions">
        <VButton
          variant="primary"
          size="lg"
          block
          :disabled="!formContent.trim()"
          :loading="formSubmitting"
          @click="onCreateEntry"
        >
          Сохранить
        </VButton>
      </div>
    </template>

    <!-- ================================================================
         EDIT ENTRY FORM
         ================================================================ -->
    <template v-else-if="currentView === 'edit' && selectedEntry">
      <header class="diary__header diary__header--nav">
        <button class="diary__back" @click="cancelEdit">←</button>
        <h1 class="diary__header-title">Редактировать</h1>
        <button
          class="diary__header-action diary__header-action--danger"
          :disabled="formSubmitting"
          @click="onDeleteEntry"
        >
          🗑️
        </button>
      </header>

      <!-- Delete confirmation bar -->
      <div v-if="confirmDeleteVisible" class="diary__confirm-bar">
        <span class="diary__confirm-text">Удалить запись навсегда?</span>
        <div class="diary__confirm-actions">
          <VButton size="sm" variant="danger" :loading="formSubmitting" @click="onConfirmDelete">
            Удалить
          </VButton>
          <VButton size="sm" variant="ghost" @click="confirmDeleteVisible = false">
            Отмена
          </VButton>
        </div>
      </div>

      <div class="diary__form">
        <div class="diary__form-group">
          <label class="diary__form-label">Заголовок</label>
          <input
            v-model="formTitle"
            class="diary__input"
            type="text"
            placeholder="О чём хотите написать?"
            maxlength="200"
          />
        </div>
        <div class="diary__form-group diary__form-group--grow">
          <label class="diary__form-label">Текст</label>
          <textarea
            v-model="formContent"
            class="diary__textarea"
            maxlength="10000"
          />
        </div>
      </div>

      <div class="diary__form-actions">
        <VButton
          variant="primary"
          size="lg"
          block
          :disabled="!formContent.trim()"
          :loading="formSubmitting"
          @click="onUpdateEntry"
        >
          Сохранить
        </VButton>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { platform } from '@/platform'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import type { CheckinResponse, FeedbackResponse, DiaryEntryResponse, Mood, FeedbackRating } from '@/api/types'

const diaryStore = useDiaryStore()
const toast = useToast()

// =========================================================================
// Types for the merged "all" feed
// =========================================================================

type TaggedCheckin  = CheckinResponse  & { _type: 'checkin' }
type TaggedFeedback = FeedbackResponse & { _type: 'feedback' }
type TaggedEntry    = DiaryEntryResponse & { _type: 'entry' }
type FeedItem = TaggedCheckin | TaggedFeedback | TaggedEntry

// =========================================================================
// Navigation state
// =========================================================================

type DiaryView = 'list' | 'detail-checkin' | 'detail-feedback' | 'detail-entry' | 'new' | 'edit'

const currentView = ref<DiaryView>('list')

// =========================================================================
// Tabs
// =========================================================================

type TabValue = 'all' | 'checkins' | 'feedbacks' | 'entries'

const TABS: Array<{ value: TabValue; label: string }> = [
  { value: 'all',       label: 'Всё' },
  { value: 'checkins',  label: 'Check-ins' },
  { value: 'feedbacks', label: 'Feedbacks' },
  { value: 'entries',   label: 'Записи' },
]

const activeTab = ref<TabValue>('all')

function setTab(tab: TabValue): void {
  activeTab.value = tab
}

// =========================================================================
// Mood / Rating display maps
// =========================================================================

const MOOD_EMOJI: Record<Mood | string, string> = {
  low: '😔', mid: '😐', high: '😊',
}
const MOOD_LABEL: Record<Mood | string, string> = {
  low: 'Не очень', mid: 'Нормально', high: 'Хорошо',
}
const RATING_EMOJI: Record<FeedbackRating | string, string> = {
  fire: '🔥', good: '👍', confused: '❓',
}
const RATING_LABEL: Record<FeedbackRating | string, string> = {
  fire: 'Огонь!', good: 'Хорошо', confused: 'Есть вопросы',
}

// =========================================================================
// Merged "all" feed (computed from store data)
// =========================================================================

const allItems = computed((): FeedItem[] => {
  const checkins: TaggedCheckin[]  = diaryStore.checkins.map((c) => ({ ...c, _type: 'checkin'  as const }))
  const feedbacks: TaggedFeedback[] = diaryStore.feedbacks.map((f) => ({ ...f, _type: 'feedback' as const }))
  const entries: TaggedEntry[]      = diaryStore.entries.map((e)  => ({ ...e, _type: 'entry'    as const }))

  return [...checkins, ...feedbacks, ...entries].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )
})

// =========================================================================
// Filtered list + loading/hasMore per tab
// =========================================================================

const visibleItems = computed((): FeedItem[] => {
  switch (activeTab.value) {
    case 'checkins':  return diaryStore.checkins.map((c) => ({ ...c, _type: 'checkin'  as const }))
    case 'feedbacks': return diaryStore.feedbacks.map((f) => ({ ...f, _type: 'feedback' as const }))
    case 'entries':   return diaryStore.entries.map((e)  => ({ ...e, _type: 'entry'    as const }))
    default:          return allItems.value
  }
})

const listLoading = computed((): boolean => {
  switch (activeTab.value) {
    case 'checkins':  return diaryStore.checkinsLoading
    case 'feedbacks': return diaryStore.feedbacksLoading
    case 'entries':   return diaryStore.entriesLoading
    default:          return diaryStore.checkinsLoading || diaryStore.feedbacksLoading || diaryStore.entriesLoading
  }
})

const listHasMore = computed((): boolean => {
  switch (activeTab.value) {
    case 'checkins':  return diaryStore.checkinsHasMore
    case 'feedbacks': return diaryStore.feedbacksHasMore
    case 'entries':   return diaryStore.entriesHasMore
    // For "all", offer load more if any of the three has more.
    default:          return diaryStore.checkinsHasMore || diaryStore.feedbacksHasMore || diaryStore.entriesHasMore
  }
})

const listError = computed((): string | null => {
  return diaryStore.entriesError
})

// =========================================================================
// Empty state copy per tab
// =========================================================================

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

// =========================================================================
// Detail selection
// =========================================================================

const selectedCheckin  = ref<CheckinResponse  | null>(null)
const selectedFeedback = ref<FeedbackResponse | null>(null)

// diary entries use the store's selectedEntry
const selectedEntry = computed(() => diaryStore.selectedEntry)

function openCheckinDetail(item: CheckinResponse): void {
  selectedCheckin.value = item
  currentView.value = 'detail-checkin'
}

function openFeedbackDetail(item: FeedbackResponse): void {
  selectedFeedback.value = item
  currentView.value = 'detail-feedback'
}

async function openEntryDetail(item: DiaryEntryResponse): Promise<void> {
  await diaryStore.fetchEntry(item.id)
  currentView.value = 'detail-entry'
}

function backToList(): void {
  currentView.value = 'list'
  selectedCheckin.value = null
  selectedFeedback.value = null
  confirmDeleteVisible.value = false
}

// =========================================================================
// New entry form
// =========================================================================

const formTitle    = ref('')
const formContent  = ref('')
const formSubmitting = ref(false)

function openNew(): void {
  formTitle.value   = ''
  formContent.value = ''
  currentView.value = 'new'
}

async function onCreateEntry(): Promise<void> {
  if (!formContent.value.trim() || formSubmitting.value) return

  formSubmitting.value = true
  const result = await diaryStore.createEntry({
    content: formContent.value.trim(),
    title:   formTitle.value.trim() || null,
  })
  formSubmitting.value = false

  if (result.ok) {
    platform.hapticFeedback('medium')
    toast.success('Запись сохранена')
    backToList()
  } else {
    toast.error(result.error)
  }
}

// =========================================================================
// Edit entry form
// =========================================================================

const confirmDeleteVisible = ref(false)

function openEdit(): void {
  if (!selectedEntry.value) return
  formTitle.value   = selectedEntry.value.title ?? ''
  formContent.value = selectedEntry.value.content
  confirmDeleteVisible.value = false
  currentView.value = 'edit'
}

function cancelEdit(): void {
  confirmDeleteVisible.value = false
  currentView.value = 'detail-entry'
}

async function onUpdateEntry(): Promise<void> {
  if (!selectedEntry.value || !formContent.value.trim() || formSubmitting.value) return

  formSubmitting.value = true
  const trimmedTitle = formTitle.value.trim()
  const result = await diaryStore.updateEntry(selectedEntry.value.id, {
    content: formContent.value.trim(),
    // If user cleared the title field, send clear_title sentinel.
    title:       trimmedTitle || null,
    clear_title: !trimmedTitle && !!selectedEntry.value.title,
  })
  formSubmitting.value = false

  if (result.ok) {
    platform.hapticFeedback('medium')
    toast.success('Запись обновлена')
    // Re-fetch entry to show updated state.
    await diaryStore.fetchEntry(selectedEntry.value.id)
    currentView.value = 'detail-entry'
  } else {
    toast.error(result.error)
  }
}

function onDeleteEntry(): void {
  confirmDeleteVisible.value = true
}

async function onConfirmDelete(): Promise<void> {
  if (!selectedEntry.value || formSubmitting.value) return

  formSubmitting.value = true
  const result = await diaryStore.deleteEntry(selectedEntry.value.id)
  formSubmitting.value = false

  if (result.ok) {
    platform.hapticFeedback('medium')
    toast.success('Запись удалена')
    backToList()
  } else {
    toast.error(result.error)
  }
}

// =========================================================================
// Load more
// =========================================================================

async function onLoadMore(): Promise<void> {
  switch (activeTab.value) {
    case 'checkins':
      await diaryStore.loadMoreCheckins()
      break
    case 'feedbacks':
      await diaryStore.loadMoreFeedbacks()
      break
    case 'entries':
      await diaryStore.loadMoreEntries()
      break
    default:
      // For "all" tab load more from whichever has more, prioritise entries.
      if (diaryStore.entriesHasMore)  await diaryStore.loadMoreEntries()
      if (diaryStore.checkinsHasMore) await diaryStore.loadMoreCheckins()
      if (diaryStore.feedbacksHasMore) await diaryStore.loadMoreFeedbacks()
  }
}

async function onRetry(): Promise<void> {
  await diaryStore.refreshEntries()
}

// =========================================================================
// Date formatting helpers
// =========================================================================

/**
 * Short: "22 января"  (day + month name)
 */
function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

/**
 * Full: "22 января, 20:15"
 */
function formatFullDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit',
  })
}

/**
 * Truncate text to max length, appending "…" if needed.
 */
function truncate(text: string, max: number): string {
  if (text.length <= max) return text
  return text.slice(0, max).trimEnd() + '…'
}

// =========================================================================
// Lifecycle
// =========================================================================

onMounted(() => {
  // Load all three feeds in parallel. Each skips if already loaded.
  Promise.all([
    diaryStore.fetchEntries(),
    diaryStore.fetchCheckins(),
    diaryStore.fetchFeedbacks(),
  ])
})
</script>

<style scoped>
.diary {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  position: relative;
  padding-bottom: var(--space-20, 80px); /* room for FAB */
}

/* ===== Header ===== */
.diary__header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--velo-border);
}

.diary__header-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0;
}

.diary__header--nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.diary__back {
  width: 36px;
  height: 36px;
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-full);
  background: transparent;
  font-size: var(--text-lg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--transition-fast);
  flex-shrink: 0;
}

.diary__back:hover {
  background: var(--velo-bg-subtle);
}

.diary__header-spacer {
  width: 36px;
}

.diary__header-action {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.diary__header-action:hover {
  background: var(--velo-bg-subtle);
}

.diary__header-action--danger:hover {
  background: rgba(220, 38, 38, 0.08);
}

/* ===== Tabs ===== */
.diary__tabs {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  overflow-x: auto;
  border-bottom: 1px solid var(--velo-border);
  scrollbar-width: none;
}

.diary__tabs::-webkit-scrollbar {
  display: none;
}

.diary__tab {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  border: 1px solid var(--velo-border);
  background: white;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-text-secondary);
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast);
  font-family: var(--font-body);
}

.diary__tab:hover {
  border-color: var(--velo-primary-light);
  color: var(--velo-primary);
}

.diary__tab--active {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: white;
}

/* ===== List ===== */
.diary__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-10) 0;
}

.diary__list {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.diary__load-more {
  padding-top: var(--space-2);
}

/* ===== Diary card (checkin / feedback / entry) ===== */
.diary-card {
  background: white;
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.diary-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(51, 77, 110, 0.1);
}

.diary-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-1);
}

.diary-card__date {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.diary-card__emoji {
  font-size: 20px;
}

.diary-card__title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-1);
}

.diary-card__preview {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* Entry card: left accent border */
.diary-card--entry {
  border-left: 3px solid var(--velo-primary);
}

/* ===== FAB ===== */
.diary__fab {
  position: fixed;
  bottom: calc(var(--space-16, 64px) + var(--space-4));
  right: var(--space-4);
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  background: var(--velo-primary);
  color: white;
  font-size: 28px;
  font-weight: 300;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(51, 77, 110, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  z-index: 20;
}

.diary__fab:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(51, 77, 110, 0.35);
}

.diary__fab:active {
  transform: scale(0.97);
}

/* ===== Detail view ===== */
.diary__detail-body {
  padding: var(--space-6) var(--space-4);
}

.diary__detail-date {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-2);
}

.diary__detail-title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-4);
  line-height: 1.3;
}

.diary__detail-content {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  line-height: 1.7;
  white-space: pre-wrap;
  margin-bottom: var(--space-4);
}

.diary__detail-context {
  font-size: var(--text-sm);
  color: var(--velo-text-muted, var(--velo-text-secondary));
  padding-top: var(--space-4);
  border-top: 1px solid var(--velo-border);
}

/* ===== Form ===== */
.diary__form {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-4);
  gap: var(--space-4);
  overflow-y: auto;
}

.diary__form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.diary__form-group--grow {
  flex: 1;
}

.diary__form-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-text-secondary);
}

.diary__input {
  width: 100%;
  padding: var(--space-3);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  background: white;
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
}

.diary__input:focus {
  outline: none;
  border-color: var(--velo-primary);
}

.diary__textarea {
  flex: 1;
  min-height: 240px;
  width: 100%;
  padding: var(--space-3);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  line-height: 1.6;
  resize: vertical;
  background: white;
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
}

.diary__textarea:focus {
  outline: none;
  border-color: var(--velo-primary);
}

.diary__form-actions {
  padding: var(--space-4);
  border-top: 1px solid var(--velo-border);
  background: white;
}

/* ===== Delete confirm bar ===== */
.diary__confirm-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: #FEF2F2;
  border-bottom: 1px solid #FECACA;
}

.diary__confirm-text {
  font-size: var(--text-sm);
  font-weight: 500;
  color: #991B1B;
}

.diary__confirm-actions {
  display: flex;
  gap: var(--space-2);
}
</style>
