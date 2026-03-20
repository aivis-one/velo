<!--
  VELO Frontend -- DiaryView (Phase F9.2, NEW-3 refactor)

  Thin orchestrator. Manages navigation state and lifecycle only.
  All UI is delegated to extracted components:

    DiaryList           — tabs + card list + FAB
    DiaryCheckinDetail  — read-only checkin
    DiaryFeedbackDetail — read-only feedback
    DiaryEntryDetail    — entry with edit button
    DiaryEntryForm      — new + edit form

  Route: /user/diary (name: user-diary)
-->

<template>
  <div class="diary">
    <DiaryList
      v-if="currentView === 'list'"
      :checkins="diaryStore.checkins"
      :feedbacks="diaryStore.feedbacks"
      :entries="diaryStore.entries"
      :checkins-loading="diaryStore.checkinsLoading"
      :feedbacks-loading="diaryStore.feedbacksLoading"
      :entries-loading="diaryStore.entriesLoading"
      :checkins-has-more="diaryStore.checkinsHasMore"
      :feedbacks-has-more="diaryStore.feedbacksHasMore"
      :entries-has-more="diaryStore.entriesHasMore"
      :checkins-error="diaryStore.checkinsError"
      :feedbacks-error="diaryStore.feedbacksError"
      :entries-error="diaryStore.entriesError"
      @open-checkin="openCheckinDetail"
      @open-feedback="openFeedbackDetail"
      @open-entry="openEntryDetail"
      @open-new="openNew"
      @load-more="onLoadMore"
      @retry="onRetry"
    />

    <DiaryCheckinDetail
      v-else-if="currentView === 'detail-checkin' && selectedCheckin"
      :item="selectedCheckin"
      @back="backToList"
    />

    <DiaryFeedbackDetail
      v-else-if="currentView === 'detail-feedback' && selectedFeedback"
      :item="selectedFeedback"
      @back="backToList"
    />

    <DiaryEntryDetail
      v-else-if="currentView === 'detail-entry' && selectedEntry"
      :item="selectedEntry"
      @back="backToList"
      @edit="openEdit"
    />

    <DiaryEntryForm
      v-else-if="currentView === 'new'"
      mode="new"
      :submitting="formSubmitting"
      @back="backToList"
      @submit="onCreateEntry"
    />

    <DiaryEntryForm
      v-else-if="currentView === 'edit' && selectedEntry"
      mode="edit"
      :initial-title="selectedEntry.title ?? ''"
      :initial-content="selectedEntry.content"
      :submitting="formSubmitting"
      :confirm-visible="confirmDeleteVisible"
      @back="cancelEdit"
      @submit="onUpdateEntry"
      @delete="confirmDeleteVisible = true"
      @delete-confirm="onConfirmDelete"
      @delete-cancel="confirmDeleteVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { platform } from '@/platform'
import DiaryList from '@/components/shared/DiaryList.vue'
import DiaryCheckinDetail from '@/components/shared/DiaryCheckinDetail.vue'
import DiaryFeedbackDetail from '@/components/shared/DiaryFeedbackDetail.vue'
import DiaryEntryDetail from '@/components/shared/DiaryEntryDetail.vue'
import DiaryEntryForm from '@/components/shared/DiaryEntryForm.vue'
import type { CheckinResponse, FeedbackResponse, DiaryEntryResponse } from '@/api/types'

const diaryStore = useDiaryStore()
const toast = useToast()

// -- Navigation --

type DiaryViewState = 'list' | 'detail-checkin' | 'detail-feedback' | 'detail-entry' | 'new' | 'edit'

const currentView      = ref<DiaryViewState>('list')
const selectedCheckin  = ref<CheckinResponse  | null>(null)
const selectedFeedback = ref<FeedbackResponse | null>(null)
const selectedEntry    = computed(() => diaryStore.selectedEntry)

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

function openEdit(): void {
  confirmDeleteVisible.value = false
  currentView.value = 'edit'
}

function cancelEdit(): void {
  confirmDeleteVisible.value = false
  currentView.value = 'detail-entry'
}

function openNew(): void {
  currentView.value = 'new'
}

function backToList(): void {
  currentView.value = 'list'
  selectedCheckin.value = null
  selectedFeedback.value = null
  confirmDeleteVisible.value = false
}

// -- Form state --

const formSubmitting       = ref(false)
const confirmDeleteVisible = ref(false)

async function onCreateEntry(payload: { title: string; content: string }): Promise<void> {
  if (formSubmitting.value) return
  formSubmitting.value = true
  const result = await diaryStore.createEntry({
    content: payload.content.trim(),
    title:   payload.title.trim() || null,
  })
  formSubmitting.value = false
  if (result.ok) {
    try { platform.hapticFeedback('medium') } catch { /* silent */ }
    toast.success('Запись сохранена')
    backToList()
  } else {
    toast.error(result.error)
  }
}

async function onUpdateEntry(payload: { title: string; content: string }): Promise<void> {
  if (!selectedEntry.value || formSubmitting.value) return
  formSubmitting.value = true
  const trimmedTitle = payload.title.trim()
  const result = await diaryStore.updateEntry(selectedEntry.value.id, {
    content:     payload.content.trim(),
    title:       trimmedTitle || null,
    clear_title: !trimmedTitle && !!selectedEntry.value.title,
  })
  formSubmitting.value = false
  if (result.ok) {
    try { platform.hapticFeedback('medium') } catch { /* silent */ }
    toast.success('Запись обновлена')
    await diaryStore.fetchEntry(selectedEntry.value.id)
    currentView.value = 'detail-entry'
  } else {
    toast.error(result.error)
  }
}

async function onConfirmDelete(): Promise<void> {
  if (!selectedEntry.value || formSubmitting.value) return
  formSubmitting.value = true
  const result = await diaryStore.deleteEntry(selectedEntry.value.id)
  formSubmitting.value = false
  if (result.ok) {
    try { platform.hapticFeedback('medium') } catch { /* silent */ }
    toast.success('Запись удалена')
    backToList()
  } else {
    toast.error(result.error)
  }
}

// -- Load more + retry --

async function onLoadMore(): Promise<void> {
  try {
    await Promise.all([
      diaryStore.entriesHasMore   ? diaryStore.loadMoreEntries()   : Promise.resolve(),
      diaryStore.checkinsHasMore  ? diaryStore.loadMoreCheckins()  : Promise.resolve(),
      diaryStore.feedbacksHasMore ? diaryStore.loadMoreFeedbacks() : Promise.resolve(),
    ])
  } catch {
    toast.error('Не удалось загрузить записи')
  }
}

async function onRetry(): Promise<void> {
  await diaryStore.refreshEntries()
}

// -- Lifecycle --

onMounted(async () => {
  try {
    await Promise.all([
      diaryStore.fetchEntries(),
      diaryStore.fetchCheckins(),
      diaryStore.fetchFeedbacks(),
    ])
  } catch {
    toast.error('Не удалось загрузить дневник')
  }
})
</script>

<style scoped>
.diary {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
</style>
