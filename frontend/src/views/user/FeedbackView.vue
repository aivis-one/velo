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
    :submit-disabled="false"
    submit-label="Отправить feedback"
    :submitted="submitted"
    success-icon=""
    success-title="Спасибо за feedback!"
    success-text="Ваш отзыв поможет нам улучшить практики"
    @back="onBack"
    @submit="onSubmit"
  >
    <!-- Practice meta line -->
    <template #practice-meta>
      с {{ practice?.master_name ?? 'Мастером' }} · Завершена
    </template>

    <!-- Rating slider -->
    <template #selection>
      <div class="feedback__rating">
        <MoodSlider
          v-model="ratingScore"
          :zones="RATING_ZONES"
          aria-label="Оценка практики от 1 до 10"
        />
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
import MoodSlider from '@/components/shared/MoodSlider.vue'
import { RATING_ICON_COLOR } from '@/utils/displayHelpers'

// Three slider zones (low -> high), passed to MoodSlider. Icons are .vue
// components so they stay in the view. Per-zone color keeps the Figma tint
// (confused = brand blue, good = rose, fire = peach) via --velo-rating-*.
const RATING_ZONES = [
  { icon: IconRatingConfused, label: 'Есть вопросы', color: RATING_ICON_COLOR.confused },
  { icon: IconRatingGood,     label: 'Хорошо',       color: RATING_ICON_COLOR.good },
  { icon: IconRatingFire,     label: 'Огонь!',       color: RATING_ICON_COLOR.fire },
]

const route = useRoute()
const router = useRouter()
const practicesStore = usePracticesStore()
const diaryStore = useDiaryStore()
const toast = useToast()

const practiceId = route.params.practiceId as string

const practice = computed(() => practicesStore.selected)
const practiceLoading = computed(() => practicesStore.selectedLoading)

const ratingScore = ref<number>(6)
const comment = ref('')
const submitted = ref(false)

async function onSubmit(): Promise<void> {
  if (diaryStore.feedbackSubmitting) return

  const result = await diaryStore.submitFeedback(practiceId, {
    rating: ratingScore.value,
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
/* Rating slider wrapper -- the slider carries its own styles. */
.feedback__rating {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  width: 100%;
}

.feedback__success-heart {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--velo-teal-400);
}
</style>
