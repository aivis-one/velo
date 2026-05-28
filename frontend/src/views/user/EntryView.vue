<!--
  VELO Frontend -- EntryView (Diary redesign, Variant B; screens 56-59)

  Full-screen view / edit / delete for a single diary entry (note / dream),
  opened by tapping an editable card in the diary feed
  (DiaryFeedView.onTap -> route user-diary-entry with the entry id).

  Data flow:
    - the entry itself (title, content, mood, practice_id) comes from
      diaryStore.fetchEntry(id) -> GET /diary/{id};
    - the optional practice header (screen 56) is built from a separate
      GET /practices/{practice_id} when the entry is linked to one; entries
      with no practice link render without the header (screen 57). The
      verified badge is intentionally omitted here -- it lives on the feed's
      own practice cards (snapshot-sourced), and PracticeResponse carries no
      verified flag.

  Modes:
    view  -- header "← Запись ⋯", optional practice header, date, title,
             full content.
    menu  -- the "⋯" popover: pencil (edit) + trash (delete).
    edit  -- editable title + autogrow textarea + "Сохранить".
    delete-> soft-delete, navigate back to the feed; the feed shows an
             "Запись удалена / Отменить" undo bar (handled in DiaryFeedView
             via the ?deleted query param).

  Relationships ("Найдена взаимосвязь", screens 53-55) is an AI feature
  outside the MVP and is deliberately NOT rendered here.
-->

<template>
  <div class="entry">
    <!-- Header -->
    <header class="entry__header">
      <button
        type="button"
        class="entry__icon-btn entry__back"
        aria-label="Назад"
        @click="goBack"
      >
        <IconArrowRight :size="20" class="entry__back-glyph" />
      </button>
      <h1 class="entry__title-bar">Запись</h1>

      <!-- "..." menu (view mode only): edit + delete as round icon buttons.
           Delete fires directly -- the diary feed shows an undo bar. -->
      <VMenu v-if="mode === 'view'">
        <template #default="{ close }">
          <VMenuItem
            :icon="IconPen"
            ariaLabel="Редактировать"
            @click="startEdit(); close()"
          />
          <VMenuItem
            :icon="IconTrash"
            ariaLabel="Удалить"
            @click="onDelete(); close()"
          />
        </template>
      </VMenu>
      <!-- Spacer to keep the title centered in edit mode (no menu button). -->
      <span v-else class="entry__icon-btn entry__icon-spacer" aria-hidden="true" />
    </header>

    <!-- Body -->
    <div class="entry__body">
      <!-- Loading -->
      <div v-if="loading" class="entry__state">
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

      <template v-else-if="entry">
        <!-- Optional practice header (screen 56). Omitted when the entry has
             no practice link (screen 57). -->
        <div v-if="practice" class="entry__practice">
          <component
            :is="practiceIcon"
            :size="40"
            class="entry__practice-icon"
          />
          <p class="entry__practice-title">{{ practice.title }}</p>
          <div class="entry__practice-master">
            <span class="entry__avatar" aria-hidden="true">
              <img
                v-if="practice.master_avatar_url"
                :src="practice.master_avatar_url"
                alt=""
                class="entry__avatar-img"
              />
            </span>
            <span class="entry__master-name">{{ practice.master_name }}</span>
          </div>
          <div class="entry__practice-meta">
            <IconCalendar :size="14" class="entry__meta-icon" />
            <span>{{ practiceDate }}</span>
            <IconClock :size="14" class="entry__meta-icon" />
            <span>{{ practiceDuration }}</span>
          </div>
        </div>

        <!-- The entry card -->
        <div class="entry__card">
          <p class="entry__date">{{ entryDate }}</p>

          <!-- View mode -->
          <template v-if="mode === 'view'">
            <h2 v-if="entry.title" class="entry__heading">{{ entry.title }}</h2>
            <p class="entry__content">{{ entry.content }}</p>
          </template>

          <!-- Edit mode -->
          <template v-else>
            <input
              v-model="editTitle"
              class="entry__edit-title"
              type="text"
              placeholder="Заголовок (необязательно)"
              :maxlength="MAX_TITLE_LEN"
              :disabled="saving"
            />
            <textarea
              ref="editEl"
              v-model="editContent"
              class="entry__edit-content"
              rows="3"
              :maxlength="MAX_CONTENT_LEN"
              :disabled="saving"
              @input="autogrow"
            />
          </template>
        </div>
      </template>
    </div>

    <!-- Save bar (edit mode) -->
    <div v-if="mode === 'edit'" class="entry__save-bar">
      <VButton
        variant="primary"
        size="lg"
        block
        :disabled="!canSave || saving"
        :loading="saving"
        @click="onSave"
      >
        Сохранить
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { VLoader, VEmptyState, VButton, VMenu, VMenuItem } from '@/components/ui'
import {
  IconArrowRight,
  IconDots,
  IconPen,
  IconCalendar,
  IconClock,
  IconMeditation,
  IconYoga,
  IconBreathwork,
} from '@/components/icons'
// IconTrash is not re-exported from the icons barrel; import the component
// file directly (same pattern as other ad-hoc icon imports in the project).
import IconTrash from '@/components/icons/IconTrash.vue'
import { useDiaryStore } from '@/stores/diary'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { getPractice } from '@/api/practices'
import { formatFeedDateTime, formatDate, formatDuration } from '@/utils/format'
import type { PracticeResponse } from '@/api/types'

const MAX_TITLE_LEN = 200
const MAX_CONTENT_LEN = 10000

const route = useRoute()
const router = useRouter()
const diaryStore = useDiaryStore()
const authStore = useAuthStore()
const toast = useToast()

const { selectedEntry, selectedEntryLoading, selectedEntryError } =
  storeToRefs(diaryStore)

const entry = computed(() => selectedEntry.value)
const loading = computed(() => selectedEntryLoading.value)
const loadError = computed(() => selectedEntryError.value)
const tz = computed(() => authStore.user?.timezone ?? 'UTC')

const entryId = computed(() => String(route.params.id))

// -- mode (view / edit) ------------------------------------------------------

const mode = ref<'view' | 'edit'>('view')

// -- practice header (optional) ---------------------------------------------

const practice = ref<PracticeResponse | null>(null)

const DIRECTION_ICON_LOCAL: Record<string, Component> = {
  meditation: IconMeditation,
  yoga: IconYoga,
  breathwork: IconBreathwork,
}

const practiceIcon = computed<Component>(() => {
  const dir = practice.value?.direction ?? ''
  // Neutral placeholder (IconDots) for directions without a dedicated icon,
  // matching DiaryFeedCard.
  return DIRECTION_ICON_LOCAL[dir] ?? IconDots
})

const practiceDate = computed(() =>
  practice.value ? formatDate(practice.value.scheduled_at, tz.value) : '',
)
const practiceDuration = computed(() =>
  practice.value ? formatDuration(practice.value.duration_minutes) : '',
)

// -- entry date line ---------------------------------------------------------

const entryDate = computed(() =>
  entry.value ? formatFeedDateTime(entry.value.created_at, tz.value) : '',
)

// -- load --------------------------------------------------------------------

async function reload(): Promise<void> {
  await diaryStore.fetchEntry(entryId.value)
  practice.value = null
  const linked = entry.value?.practice_id
  if (linked) {
    try {
      practice.value = await getPractice(linked)
    } catch {
      // Practice header is best-effort; a missing/forbidden practice just
      // degrades to the no-header layout (screen 57).
      practice.value = null
    }
  }
}

onMounted(reload)

// -- edit --------------------------------------------------------------------

const editTitle = ref('')
const editContent = ref('')
const saving = ref(false)
const editEl = ref<HTMLTextAreaElement | null>(null)

const canSave = computed(() => editContent.value.trim().length > 0)

function autogrow(): void {
  const el = editEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

async function startEdit(): Promise<void> {
  if (!entry.value) return
  editTitle.value = entry.value.title ?? ''
  editContent.value = entry.value.content
  mode.value = 'edit'
  await nextTick()
  autogrow()
}

async function onSave(): Promise<void> {
  if (!entry.value || !canSave.value || saving.value) return
  saving.value = true
  const trimmedTitle = entryEditTitleTrimmed()
  const result = await diaryStore.updateEntry(entry.value.id, {
    content: editContent.value.trim(),
    title: trimmedTitle || null,
    // Clear the title server-side when emptied (was set before, now blank).
    clear_title: !trimmedTitle,
  })
  saving.value = false
  if (result.ok) {
    mode.value = 'view'
  } else {
    toast.error(result.error)
  }
}

function entryEditTitleTrimmed(): string {
  return editTitle.value.trim()
}

// -- delete (soft) + undo handoff to the feed --------------------------------

async function onDelete(): Promise<void> {
  if (!entry.value) return
  const id = entry.value.id
  const result = await diaryStore.deleteEntry(id)
  if (!result.ok) {
    toast.error(result.error)
    return
  }
  // Hand the undo affordance to the feed: it shows the "Запись удалена /
  // Отменить" bar and calls diaryStore.restoreEntry on tap.
  router.replace({ name: 'user-diary', query: { deleted: id } })
}

// -- navigation --------------------------------------------------------------

function goBack(): void {
  if (mode.value === 'edit') {
    mode.value = 'view'
    return
  }
  router.push({ name: 'user-diary' })
}
</script>

<style scoped>
/* Three-row layout mirroring DiaryFeedView: fixed header, scrolling body,
   optional fixed save bar. Tokens only (variables.css). */
.entry {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* -- Header -- */
.entry__header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-8) var(--space-3);
}

.entry__title-bar {
  flex: 1;
  text-align: center;
  font-family: var(--font-heading);
  font-size: var(--text-base);
  letter-spacing: 0.36px;
  color: var(--velo-text-primary);
}

.entry__icon-btn {
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

.entry__icon-spacer {
  cursor: default;
  background: transparent;
}

.entry__back {
  background: var(--velo-bg-card-solid);
  color: var(--velo-text-primary);
}

/* The only "back" glyph available is a right arrow -- mirror it. */
.entry__back-glyph {
  transform: scaleX(-1);
}

.entry__icon-btn:hover {
  opacity: 0.85;
}

/* -- Body (scrolls) -- */
.entry__body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: 0 var(--space-8) var(--space-4);
}

.entry__state {
  display: flex;
  justify-content: center;
  padding: var(--space-10) 0;
}

/* -- Practice header (mirrors feed-card--practice) -- */
.entry__practice {
  position: relative;
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.entry__practice-icon {
  position: absolute;
  top: var(--space-3);
  left: var(--space-4);
  /* Цвет — text-primary (Figma DS): иконка сама несёт circle-обводку. */
  color: var(--velo-text-primary);
}

.entry__practice-title {
  font-size: 16px;
  text-align: center;
  letter-spacing: 0.32px;
  color: var(--velo-text-primary);
}

.entry__practice-master {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
}

.entry__avatar {
  width: 14px;
  height: 14px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-40);
  overflow: hidden;
  flex-shrink: 0;
}

.entry__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.entry__master-name {
  font-size: 12px;
  color: var(--velo-text-secondary);
}

.entry__practice-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  font-size: 12px;
  color: var(--velo-text-secondary);
}

.entry__meta-icon {
  color: var(--velo-text-secondary);
}

/* -- Entry card -- */
.entry__card {
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.entry__date {
  font-size: 12.375px;
  letter-spacing: 0.2475px;
  opacity: 0.6;
  color: var(--velo-text-primary);
}

.entry__heading {
  font-family: var(--font-heading);
  font-size: 16px;
  letter-spacing: 0.32px;
  color: var(--velo-text-primary);
}

.entry__content {
  font-size: var(--text-sm);
  line-height: 1.5;
  color: var(--velo-text-primary);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

/* -- Edit fields -- */
.entry__edit-title {
  border: none;
  border-bottom: 1px solid var(--velo-border-light);
  background: transparent;
  padding: var(--space-1) 0;
  font-family: var(--font-heading);
  font-size: 16px;
  letter-spacing: 0.32px;
  color: var(--velo-text-primary);
  outline: none;
}

.entry__edit-title::placeholder {
  color: var(--velo-text-primary);
  opacity: 0.5;
}

.entry__edit-content {
  border: none;
  background: transparent;
  resize: none;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  line-height: 1.5;
  color: var(--velo-text-primary);
  outline: none;
  overflow-y: hidden;
}

/* -- Save bar -- */
.entry__save-bar {
  flex-shrink: 0;
  padding: var(--space-3) var(--space-8) var(--space-4);
}
</style>
