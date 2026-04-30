<!--
  VELO Frontend -- CheckinView (S2 P08 C30 — refresh per skin 12)

  3-icon mood picker (NOT slider per A.13) + comment textarea + submit.
  Reuses useDiaryStore.submitCheckin upsert pattern. On success routes to
  CheckinSuccessView.

  Path Y MEDIUM. No emojis (#048) — uses mood SVG assets from S1 P01 batch.
-->

<template>
  <div class="ci">
    <VHeader
      title="Check-in"
      show-back
      @back="$router.back()"
    />

    <div
      v-if="loadingPractice"
      class="ci__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="!practice"
      class="ci__error"
    >
      Практика не найдена
    </div>
    <div
      v-else
      class="ci__body"
    >
      <section class="ci__head">
        <h2>{{ practice.title }}</h2>
        <p>с {{ practice.master_name ?? 'Мастером' }}</p>
        <p>{{ formatDateShort(practice.scheduled_at, practice.timezone) }}</p>
      </section>

      <section class="ci__q">
        <h3>Как вы себя чувствуете?</h3>
        <p>Оцените своё состояние перед практикой</p>
      </section>

      <div class="ci__moods">
        <button
          v-for="opt in MOOD_OPTS"
          :key="opt.value"
          type="button"
          class="ci__mood"
          :class="{ 'ci__mood--active': mood === opt.value }"
          @click="mood = opt.value"
        >
          <img
            :src="opt.svg"
            alt=""
            aria-hidden="true"
            class="ci__mood-img"
          >
          <span>{{ opt.label }}</span>
        </button>
      </div>

      <textarea
        v-model="comment"
        class="ci__textarea"
        placeholder="Добавьте комментарий (необязательно)..."
        rows="3"
        maxlength="1000"
      />

      <VButton
        variant="primary"
        size="md"
        block
        :loading="submitting"
        :disabled="!mood"
        @click="onSubmit"
      >
        Check-in перед практикой
      </VButton>

      <button
        type="button"
        class="ci__skip"
        @click="$router.back()"
      >
        Пропустить
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VButton } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { formatDateShort } from '@/utils/format'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { getPractice } from '@/api/practices'
import { extractApiError } from '@/composables/useApiError'
import moodSadSvg from '@/assets/mood/mood-sad.svg'
import moodNeutralSvg from '@/assets/mood/mood-neutral.svg'
import moodCalmSvg from '@/assets/mood/mood-calm.svg'
import type { Mood, PracticeResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const diary = useDiaryStore()
const toast = useToast()

const MOOD_OPTS: Array<{ value: Mood; label: string; svg: string }> = [
  { value: 'low', label: 'Не очень', svg: moodSadSvg },
  { value: 'mid', label: 'Нормально', svg: moodNeutralSvg },
  { value: 'high', label: 'Хорошо', svg: moodCalmSvg },
]

const practice = ref<PracticeResponse | null>(null)
const loadingPractice = ref(false)
const mood = ref<Mood | null>('mid')
const comment = ref('')
const submitting = ref(false)

async function load(): Promise<void> {
  const id = route.params.practiceId as string
  loadingPractice.value = true
  try {
    practice.value = await getPractice(id)
  } catch (e) {
    toast.error(extractApiError(e, 'Не удалось загрузить практику'))
  } finally {
    loadingPractice.value = false
  }
}

async function onSubmit(): Promise<void> {
  if (!practice.value || !mood.value || submitting.value) return
  submitting.value = true
  const result = await diary.submitCheckin(practice.value.id, {
    mood: mood.value,
    comment: comment.value.trim() || null,
  })
  submitting.value = false
  if (result.ok) {
    router.push(`/user/practices/${practice.value.id}/checkin/success`)
  } else {
    toast.error(result.error)
  }
}

onMounted(load)
</script>

<style scoped>
.ci {
  display: flex;
  flex-direction: column;
}

.ci__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.ci__loader,
.ci__error {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.ci__head {
  text-align: center;
}

.ci__head h2 {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  margin: 0 0 var(--space-1);
  font-weight: 400;
  color: var(--text-primary);
}

.ci__head p {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.ci__q {
  text-align: center;
}

.ci__q h3 {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0 0 var(--space-1);
  font-weight: 400;
  color: var(--text-primary);
}

.ci__q p {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.ci__moods {
  display: flex;
  gap: var(--space-2);
}

.ci__mood {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: var(--surface-steel-alpha-15);
  border: 2px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.ci__mood--active {
  border-color: var(--steel-button);
}

.ci__mood-img {
  width: 48px;
  height: 48px;
}

.ci__textarea {
  width: 100%;
  padding: var(--space-3);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  resize: none;
  box-sizing: border-box;
}

.ci__skip {
  background: transparent;
  border: none;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-decoration: underline;
  cursor: pointer;
  margin: 0 auto;
}
</style>
