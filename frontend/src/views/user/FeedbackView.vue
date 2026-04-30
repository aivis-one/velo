<!--
  VELO Frontend -- FeedbackView (S2 P08 C32 — refresh per skin 29)

  3-button feedback rating + comment + submit. Reuses
  useDiaryStore.submitFeedback. On success routes to FeedbackSuccessView.

  Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="fv">
    <VHeader
      title="Практика"
      show-back
      @back="$router.back()"
    />

    <div
      v-if="loadingPractice"
      class="fv__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="!practice"
      class="fv__error"
    >
      Практика не найдена
    </div>
    <div
      v-else
      class="fv__body"
    >
      <section class="fv__head">
        <h2>{{ practice.title }}</h2>
        <p>с {{ practice.master_name ?? 'Мастером' }} · Завершена</p>
      </section>

      <section class="fv__q">
        <h3>Как прошла практика?</h3>
        <p>Оцените своё состояние после</p>
      </section>

      <div class="fv__ratings">
        <button
          v-for="opt in RATING_OPTS"
          :key="opt.value"
          type="button"
          class="fv__rating"
          :class="{ 'fv__rating--active': rating === opt.value }"
          @click="rating = opt.value"
        >
          <component
            :is="opt.icon"
            class="fv__rating-icon"
            :size="32"
          />
          <span>{{ opt.label }}</span>
        </button>
      </div>

      <textarea
        v-model="comment"
        class="fv__textarea"
        placeholder="Добавьте комментарий (необязательно)..."
        rows="3"
        maxlength="1000"
      />

      <VButton
        variant="primary"
        size="md"
        block
        :loading="submitting"
        :disabled="!rating"
        @click="onSubmit"
      >
        Отправить feedback
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VButton } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { IconHeart, IconWarning, IconBrain } from '@/components/icons'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { getPractice } from '@/api/practices'
import { extractApiError } from '@/composables/useApiError'
import type { FeedbackRating, PracticeResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const diary = useDiaryStore()
const toast = useToast()

const RATING_OPTS: Array<{ value: FeedbackRating; label: string; icon: Component }> = [
  { value: 'confused', label: 'Есть вопросы', icon: IconWarning },
  { value: 'good', label: 'Хорошо', icon: IconHeart },
  { value: 'fire', label: 'Огонь!', icon: IconBrain },
]

const practice = ref<PracticeResponse | null>(null)
const loadingPractice = ref(false)
const rating = ref<FeedbackRating | null>(null)
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
  if (!practice.value || !rating.value || submitting.value) return
  submitting.value = true
  const result = await diary.submitFeedback(practice.value.id, {
    rating: rating.value,
    comment: comment.value.trim() || null,
  })
  submitting.value = false
  if (result.ok) {
    router.push(`/user/practices/${practice.value.id}/feedback/success`)
  } else {
    toast.error(result.error)
  }
}

onMounted(load)
</script>

<style scoped>
.fv {
  display: flex;
  flex-direction: column;
}

.fv__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.fv__loader,
.fv__error {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.fv__head {
  text-align: center;
}

.fv__head h2 {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  margin: 0 0 var(--space-1);
  font-weight: 400;
  color: var(--text-primary);
}

.fv__head p {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.fv__q {
  text-align: center;
}

.fv__q h3 {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0 0 var(--space-1);
  font-weight: 400;
  color: var(--text-primary);
}

.fv__q p {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.fv__ratings {
  display: flex;
  gap: var(--space-2);
}

.fv__rating {
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

.fv__rating--active {
  border-color: var(--steel-button);
}

.fv__rating-icon {
  color: var(--text-primary);
}

.fv__textarea {
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
</style>
