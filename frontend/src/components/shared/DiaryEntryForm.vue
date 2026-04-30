<!--
  VELO Frontend -- DiaryEntryForm (NEW-3)

  Shared form for creating and editing diary entries.
  Extracted from DiaryView.vue.

  Props:
    mode            — 'new' | 'edit'
    initialTitle    — pre-filled title (edit mode)
    initialContent  — pre-filled content (edit mode)
    submitting      — loading state
    confirmVisible  — show delete confirmation bar (edit mode)

  Emits:
    back            — back / cancel clicked
    submit          — form submitted with { title, content }
    delete          — delete icon clicked (edit mode)
    delete-confirm  — confirm delete clicked
    delete-cancel   — cancel delete clicked
-->

<template>
  <div class="entry-form">
    <!-- Header -->
    <header class="entry-form__header">
      <button
        class="entry-form__back"
        aria-label="Назад"
        @click="emit('back')"
      >
        ←
      </button>
      <h1 class="entry-form__title">
        {{ mode === 'new' ? 'Новая запись' : 'Редактировать' }}
      </h1>
      <button
        v-if="mode === 'edit'"
        class="entry-form__delete"
        aria-label="Удалить"
        :disabled="submitting"
        @click="emit('delete')"
      >
        🗑️
      </button>
      <span
        v-else
        class="entry-form__spacer"
      />
    </header>

    <!-- Delete confirmation bar (edit mode) -->
    <div
      v-if="confirmVisible"
      class="entry-form__confirm-bar"
    >
      <span class="entry-form__confirm-text">Удалить запись навсегда?</span>
      <div class="entry-form__confirm-actions">
        <VButton
          size="sm"
          variant="danger"
          :loading="submitting"
          @click="emit('delete-confirm')"
        >
          Удалить
        </VButton>
        <VButton
          size="sm"
          variant="ghost"
          @click="emit('delete-cancel')"
        >
          Отмена
        </VButton>
      </div>
    </div>

    <!-- Form fields -->
    <div class="entry-form__body">
      <div class="entry-form__group">
        <label class="entry-form__label">Заголовок</label>
        <input
          v-model="title"
          class="entry-form__input"
          type="text"
          placeholder="О чём хотите написать?"
          maxlength="200"
        >
      </div>
      <div class="entry-form__group entry-form__group--grow">
        <label class="entry-form__label">Текст</label>
        <textarea
          v-model="content"
          class="entry-form__textarea"
          :placeholder="mode === 'new' ? 'Напишите свои мысли...' : ''"
          maxlength="10000"
        />
      </div>
    </div>

    <!-- Submit button -->
    <div class="entry-form__actions">
      <VButton
        variant="primary"
        size="lg"
        block
        :disabled="!content.trim()"
        :loading="submitting"
        @click="onSubmit"
      >
        Сохранить
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { VButton } from '@/components/ui'

const props = defineProps<{
  mode: 'new' | 'edit'
  initialTitle?: string
  initialContent?: string
  submitting: boolean
  confirmVisible?: boolean
}>()

const emit = defineEmits<{
  back: []
  submit: [payload: { title: string; content: string }]
  delete: []
  'delete-confirm': []
  'delete-cancel': []
}>()

const title   = ref(props.initialTitle   ?? '')
const content = ref(props.initialContent ?? '')

function onSubmit(): void {
  if (!content.value.trim() || props.submitting) return
  emit('submit', { title: title.value, content: content.value })
}
</script>

<style scoped>
.entry-form {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.entry-form__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
}

.entry-form__back {
  width: 36px;
  height: 36px;
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  background: var(--surface-steel-alpha-15);
  font-size: var(--text-lg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity var(--transition-fast);
  flex-shrink: 0;
}

.entry-form__back:hover { opacity: 0.8; }

.entry-form__title {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.entry-form__spacer { width: 36px; }

.entry-form__delete {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  transition: opacity var(--transition-fast);
}

.entry-form__delete:hover { opacity: 0.7; }
.entry-form__delete:disabled { opacity: 0.4; cursor: not-allowed; }

.entry-form__confirm-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--surface-warm-alpha-40);
  border-bottom: 1px solid var(--pink-primary);
}

.entry-form__confirm-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--warm-deep);
}

.entry-form__confirm-actions {
  display: flex;
  gap: var(--space-2);
}

.entry-form__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-4);
  gap: var(--space-4);
  overflow-y: auto;
}

.entry-form__group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.entry-form__group--grow { flex: 1; }

.entry-form__label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-secondary);
}

.entry-form__input {
  width: 100%;
  padding: var(--space-3);
  border: 2px solid transparent;
  border-radius: 5px;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--text-primary);
  background: var(--surface-steel-alpha-15);
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
}

.entry-form__input::placeholder { color: var(--text-muted); }
.entry-form__input:focus { outline: none; border-color: var(--steel-muted); }

.entry-form__textarea {
  flex: 1;
  min-height: 240px;
  width: 100%;
  padding: var(--space-3);
  border: 2px solid transparent;
  border-radius: 5px;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--text-primary);
  line-height: 1.6;
  resize: vertical;
  background: var(--surface-steel-alpha-15);
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
}

.entry-form__textarea::placeholder { color: var(--text-muted); }
.entry-form__textarea:focus { outline: none; border-color: var(--steel-muted); }

.entry-form__actions {
  padding: var(--space-4);
}
</style>
