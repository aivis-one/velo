<!--
  VELO Frontend — DiaryComposerExpanded (S2-S3 SPEEDRUN MEGA-2 §C40)

  Full-screen slide-up modal for new diary entry. Path Y MEDIUM — analogy
  to EditProfile + Check-in form patterns since designer skin not delivered.

  Mood + practice picker fields are local-only at v1; mood maps to
  CreateDiaryEntryRequest.mood; practice_id wired from upcomingBookings.
-->

<template>
  <Teleport to="body">
    <div
      class="ce"
      role="dialog"
      aria-modal="true"
    >
      <div
        class="ce__backdrop"
        @click="$emit('close')"
      />
      <div class="ce__panel">
        <header class="ce__head">
          <button
            type="button"
            class="ce__back"
            aria-label="Назад"
            @click="$emit('close')"
          >
            <IconArrowBack :size="20" />
          </button>
          <h2 class="ce__title">
            Новая запись
          </h2>
        </header>

        <input
          v-model="title"
          type="text"
          class="ce__input"
          placeholder="Заголовок (необязательно)"
        >
        <textarea
          v-model="content"
          class="ce__textarea"
          placeholder="О чём вы хотите написать?"
          rows="8"
        />

        <div class="ce__moods">
          <button
            v-for="opt in MOOD_OPTIONS"
            :key="opt.value"
            type="button"
            class="ce__mood"
            :class="{ 'ce__mood--active': mood === opt.value }"
            @click="mood = mood === opt.value ? null : opt.value"
          >
            <img
              :src="opt.src"
              :alt="opt.label"
              class="ce__mood-img"
            >
          </button>
        </div>

        <select
          v-model="practiceId"
          class="ce__select"
        >
          <option :value="null">
            Без практики
          </option>
          <option
            v-for="b in linkable"
            :key="b.id"
            :value="b.practice_id"
          >
            {{ b.practice.title }}
          </option>
        </select>

        <button
          type="button"
          class="ce__submit"
          :disabled="!canSave || saving"
          @click="onSave"
        >
          {{ saving ? 'Сохранение…' : 'Сохранить' }}
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { IconArrowBack } from '@/components/icons'
import { useDiaryStore } from '@/stores/diary'
import { useBookingsStore } from '@/stores/bookings'
import { useToast } from '@/composables/useToast'
import moodSadSvg from '@/assets/mood/mood-sad.svg'
import moodNeutralSvg from '@/assets/mood/mood-neutral.svg'
import moodCalmSvg from '@/assets/mood/mood-calm.svg'

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const diary = useDiaryStore()
const bookings = useBookingsStore()
const toast = useToast()

const MOOD_OPTIONS = [
  { value: 'sad', label: 'Грусть', src: moodSadSvg },
  { value: 'neutral', label: 'Нейтрально', src: moodNeutralSvg },
  { value: 'calm', label: 'Спокойно', src: moodCalmSvg },
] as const

const title = ref('')
const content = ref('')
const mood = ref<string | null>(null)
const practiceId = ref<string | null>(null)
const saving = ref(false)

const linkable = computed(() => {
  const all = bookings.upcomingBookings ?? []
  return all.slice(0, 10)
})

const canSave = computed(() => content.value.trim().length > 0)

async function onSave(): Promise<void> {
  if (!canSave.value || saving.value) return
  saving.value = true
  const result = await diary.createEntry({
    content: content.value.trim(),
    title: title.value.trim() || null,
    mood: mood.value,
    practice_id: practiceId.value,
  })
  saving.value = false
  if (result.ok) {
    emit('saved')
  } else {
    toast.error(result.error)
  }
}
</script>

<style scoped>
.ce {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
}

.ce__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
}

.ce__panel {
  position: relative;
  background: var(--surface-default);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  width: 100%;
  overflow-y: auto;
}

.ce__head {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.ce__back {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ce__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.ce__input,
.ce__textarea,
.ce__select {
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: var(--text-base);
  width: 100%;
}

.ce__textarea {
  resize: vertical;
  min-height: 160px;
}

.ce__moods {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
}

.ce__mood {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ce__mood--active {
  background: var(--steel-button);
  border-color: var(--steel-button);
}

.ce__mood-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.ce__submit {
  width: 100%;
  padding: var(--space-3);
  background: var(--steel-button);
  color: white;
  border: 0;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 500;
  margin-top: auto;
}

.ce__submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
