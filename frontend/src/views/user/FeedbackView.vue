<!--
  VELO Frontend -- FeedbackView (Phase F9.1, updated back-button, WARNING-9)

  Full-screen post-practice feedback form.
  Uses FormShell for shared layout/CSS. Only rating-specific logic stays here.

  Route: /user/feedback/:practiceId
  Param: practiceId (practice UUID)
-->

<template>
  <FormShell
    back-label="Feedback"
    :practice="practice"
    :practice-loading="practiceLoading"
    question-title="Как прошла практика?"
    question-subtitle="Оцените своё состояние после"
    v-model:comment="comment"
    :submitting="diaryStore.feedbackSubmitting"
    :submit-disabled="!selectedRating"
    submit-label="Отправить feedback"
    :submitted="submitted"
    success-title="Спасибо за feedback!"
    success-text="Ваш отзыв поможет нам улучшить практики"
    @back="onBack"
    @submit="onSubmit"
  >
    <!-- Practice meta line -->
    <template #practice-meta>
      с {{ practice?.master_name ?? 'Мастером' }} · Завершена
    </template>

    <!-- Rating buttons -->
    <template #selection>
      <div class="feedback__rating-buttons">
        <button
          v-for="opt in RATING_OPTIONS"
          :key="opt.value"
          class="feedback__rating-btn"
          :class="[
            `feedback__rating-btn--${opt.value}`,
            { 'feedback__rating-btn--selected': selectedRating === opt.value },
          ]"
          @click="selectRating(opt.value)"
        >
          <span class="feedback__rating-icon" :style="{ color: RATING_ICON_COLOR[opt.value] }">
            <component :is="RATING_ICON[opt.value]" :size="40" />
          </span>
          <span class="feedback__rating-label">{{ opt.label }}</span>
        </button>
      </div>
    </template>

    <!-- Success icon: teal heart (Figma 541:2354) -->
    <template #success-icon>
      <span class="feedback__success-heart">
        <IconHeart :size="56" />
      </span>
    </template>

    <!-- Success actions -->
    <template #success-actions>
      <VButton variant="primary" size="lg" block @click="goToDiary">
        В дневник
      </VButton>
      <VButton variant="ghost" block @click="goToDashboard">
        На главную
      </VButton>
    </template>
  </FormShell>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePracticesStore } from '@/stores/practices'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { platform } from '@/platform'
import { VButton } from '@/components/ui'
import {
  IconRatingConfused,
  IconRatingGood,
  IconRatingFire,
  IconHeart,
} from '@/components/icons'
import FormShell from '@/components/shared/FormShell.vue'
import { RATING_OPTIONS, RATING_ICON_COLOR } from '@/utils/displayHelpers'
import type { FeedbackRating } from '@/api/types'

// Map rating value -> icon component (kept here, not in displayHelpers, to
// avoid mixing the utils layer with .vue components -- same as MOOD_ICON in
// CheckinView). Colors come from RATING_ICON_COLOR (--velo-rating-* tokens).
const RATING_ICON = {
  confused: IconRatingConfused,
  good:     IconRatingGood,
  fire:     IconRatingFire,
} as const

const route = useRoute()
const router = useRouter()
const practicesStore = usePracticesStore()
const diaryStore = useDiaryStore()
const toast = useToast()

const practiceId = route.params.practiceId as string

const practice = computed(() => practicesStore.selected)
const practiceLoading = computed(() => practicesStore.selectedLoading)

const selectedRating = ref<FeedbackRating | null>(null)
const comment = ref('')
const submitted = ref(false)

function selectRating(rating: FeedbackRating): void {
  selectedRating.value = rating
  try { platform.hapticFeedback('light') } catch { /* silent fallback */ }
}

async function onSubmit(): Promise<void> {
  if (!selectedRating.value || diaryStore.feedbackSubmitting) return

  const result = await diaryStore.submitFeedback(practiceId, {
    rating: selectedRating.value,
    comment: comment.value.trim() || null,
  })

  if (result.ok) {
    try { platform.hapticFeedback('medium') } catch { /* silent fallback */ }
    submitted.value = true
  } else {
    toast.error(result.error)
  }
}

function onBack(): void {
  router.push({ name: 'user-bookings' })
}

function goToDiary(): void {
  router.push({ name: 'user-diary' })
}

function goToDashboard(): void {
  router.push({ name: 'user-dashboard' })
}

onMounted(() => {
  if (practicesStore.selected?.id !== practiceId) {
    practicesStore.fetchPractice(practiceId)
  }
})
</script>

<style scoped>
/* Rating buttons -- unique to FeedbackView */
.feedback__rating-buttons {
  display: flex;
  justify-content: center;
  gap: var(--space-4);
}

.feedback__rating-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: var(--size-option-btn-min);
  font-family: var(--font-body);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.feedback__rating-btn:hover {
  opacity: 0.8;
}

.feedback__rating-btn--selected.feedback__rating-btn--confused {
  border-color: var(--velo-peach-300);
  background: var(--velo-glass-peach-40);
  box-shadow: var(--velo-shadow-glow);
}

.feedback__rating-btn--selected.feedback__rating-btn--good {
  border-color: var(--velo-teal-400);
  background: var(--velo-glass-teal-30);
  box-shadow: var(--velo-shadow-glow);
}

.feedback__rating-btn--selected.feedback__rating-btn--fire {
  border-color: var(--velo-pink-300);
  background: var(--velo-glass-peach-40);
  box-shadow: var(--velo-shadow-glow);
}

.feedback__rating-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.feedback__success-heart {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--velo-teal-400);
}

.feedback__rating-label {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
}
</style>
