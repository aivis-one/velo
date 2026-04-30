<!--
  VELO Frontend — DiaryEntryView (S2-S3 SPEEDRUN MEGA-2 §C42 + §C43 + §C44)

  Single-entry view. Two render modes:
    - read (skin 52 with practice context, OR skin 56 standalone)
    - edit (in-place, skin 59) — same layout, content card becomes form
  Plus action menu (••• → edit / trash) and undo snackbar after delete.

  "Найдена взаимосвязь" CTA links to /user/diary/entry/:id/relationships.
  At v1 the CTA always shows (degraded — backend signal pending).
-->

<template>
  <div class="entry">
    <header class="entry__header">
      <button
        type="button"
        class="entry__back"
        aria-label="Назад"
        @click="onBack"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="entry__title">
        Запись
      </h1>
    </header>

    <div
      v-if="loading"
      class="entry__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="!entry || pendingDelete"
      class="entry__empty"
    >
      Запись не найдена или была удалена.
    </div>
    <div
      v-else
      class="entry__body"
    >
      <article
        v-if="entry.practice_id"
        class="entry__practice"
      >
        <p class="entry__practice-label">
          Привязана к практике
        </p>
        <p class="entry__practice-id">
          {{ entry.practice_id }}
        </p>
      </article>

      <article
        v-if="entry.mood && !isEditing"
        class="entry__mood"
      >
        <span>Check-in: {{ entry.mood }}</span>
      </article>

      <article
        v-if="!isEditing"
        class="entry__card"
      >
        <p class="entry__date">
          {{ humanDate(entry.created_at) }}
        </p>
        <h2
          v-if="entry.title"
          class="entry__heading"
        >
          {{ entry.title }}
        </h2>
        <p class="entry__text">
          {{ entry.content }}
        </p>
      </article>

      <article
        v-else
        class="entry__form"
      >
        <input
          v-model="editTitle"
          type="text"
          class="entry__input"
          placeholder="Заголовок (необязательно)"
        >
        <textarea
          v-model="editContent"
          class="entry__textarea"
          rows="10"
        />
        <button
          type="button"
          class="entry__save"
          :disabled="!canSave || saving"
          @click="onSave"
        >
          {{ saving ? 'Сохранение…' : 'Сохранить' }}
        </button>
      </article>

      <RouterLink
        v-if="!isEditing"
        :to="`/user/diary/entry/${entry.id}/relationships`"
        class="entry__link-cta"
      >
        <IconLink :size="22" />
        <span class="entry__link-cta-text">
          <strong>Найдена взаимосвязь</strong>
          <small>Нажмите, чтобы посмотреть</small>
        </span>
      </RouterLink>
    </div>

    <EntryActionMenu
      v-if="entry && !isEditing && !pendingDelete"
      @edit="enterEdit"
      @delete="onDeleteRequest"
    />

    <UndoSnackbar
      v-if="pendingDelete"
      message="Запись удалена"
      action-label="Отменить"
      :timeout="3000"
      @action="onUndo"
      @timeout="onConfirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { IconArrowBack, IconLink } from '@/components/icons'
import EntryActionMenu from '@/components/shared/EntryActionMenu.vue'
import UndoSnackbar from '@/components/shared/UndoSnackbar.vue'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import type { DiaryEntryResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const diary = useDiaryStore()
const toast = useToast()

const loading = ref(false)
const isEditing = ref(false)
const pendingDelete = ref(false)
const editTitle = ref('')
const editContent = ref('')
const saving = ref(false)

const entry = computed<DiaryEntryResponse | null>(
  () => diary.selectedEntry,
)

const canSave = computed(() => editContent.value.trim().length > 0)

watch(
  () => route.params.id,
  async (id) => {
    if (typeof id === 'string') await load(id)
  },
)

async function load(id: string): Promise<void> {
  loading.value = true
  isEditing.value = false
  pendingDelete.value = false
  try {
    await diary.fetchEntry(id)
  } catch {
    toast.error('Не удалось открыть запись')
  } finally {
    loading.value = false
  }
}

function onBack(): void {
  if (isEditing.value) {
    isEditing.value = false
    return
  }
  router.back()
}

function enterEdit(): void {
  if (!entry.value) return
  editTitle.value = entry.value.title ?? ''
  editContent.value = entry.value.content
  isEditing.value = true
}

async function onSave(): Promise<void> {
  if (!entry.value || !canSave.value || saving.value) return
  saving.value = true
  const trimmedTitle = editTitle.value.trim()
  const result = await diary.updateEntry(entry.value.id, {
    content: editContent.value.trim(),
    title: trimmedTitle || null,
    clear_title: !trimmedTitle && !!entry.value.title,
  })
  saving.value = false
  if (result.ok) {
    toast.success('Запись обновлена')
    isEditing.value = false
    await diary.fetchEntry(entry.value.id)
  } else {
    toast.error(result.error)
  }
}

function onDeleteRequest(): void {
  pendingDelete.value = true
}

function onUndo(): void {
  pendingDelete.value = false
  toast.info('Удаление отменено')
}

async function onConfirmDelete(): Promise<void> {
  if (!entry.value) return
  const result = await diary.deleteEntry(entry.value.id)
  if (result.ok) {
    toast.success('Запись удалена')
    router.push('/user/diary')
  } else {
    pendingDelete.value = false
    toast.error(result.error)
  }
}

function humanDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    })
  } catch {
    return iso
  }
}

onMounted(async () => {
  const id = route.params.id
  if (typeof id === 'string') await load(id)
})
</script>

<style scoped>
.entry {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  min-height: 100%;
}

.entry__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.entry__back {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.entry__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.entry__loader,
.entry__empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.entry__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.entry__practice,
.entry__mood,
.entry__card,
.entry__form {
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.entry__practice-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin: 0;
}

.entry__practice-id {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-primary);
  margin: 0;
  word-break: break-all;
}

.entry__mood {
  background: var(--surface-steel-alpha-15);
}

.entry__date {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin: 0;
}

.entry__heading {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.entry__text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  margin: 0;
  white-space: pre-wrap;
}

.entry__input,
.entry__textarea {
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  color: var(--text-primary);
  font-size: var(--text-base);
}

.entry__textarea {
  resize: vertical;
}

.entry__save {
  padding: var(--space-3);
  background: var(--steel-button);
  color: white;
  border: 0;
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 500;
  cursor: pointer;
}

.entry__save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.entry__link-cta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--mint-primary, var(--text-primary));
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  text-decoration: none;
}

.entry__link-cta-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.entry__link-cta-text strong {
  font-family: var(--font-body);
  font-weight: 500;
}

.entry__link-cta-text small {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}
</style>
