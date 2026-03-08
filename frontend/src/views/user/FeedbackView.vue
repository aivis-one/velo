<!--
  VELO Frontend -- FeedbackView (Phase F9.1)

  Full-screen post-practice feedback form.
  Matches mockup screen-feedback layout:
    - Header with back button
    - Practice info (emoji + name + "Завершена")
    - "Как прошла практика?" question
    - Three rating buttons: confused / good / fire
    - Optional comment textarea
    - Submit button (disabled until rating selected)
    - Success screen (inline, no route change)

  Route: /user/feedback/:practiceId
  Param: practiceId (practice UUID)

  On success: offers navigation to diary or dashboard.
  Note: no "Skip" button — feedback is voluntary but if opened, user intent
  is to submit. Back button serves as cancel.
-->

<template>
  <!-- ===== SUCCESS SCREEN ===== -->
  <div v-if="submitted" class="feedback-success">
    <div class="feedback-success__icon">💚</div>
    <h1 class="feedback-success__title">Спасибо за feedback!</h1>
    <p class="feedback-success__text">Ваш отзыв поможет нам улучшить практики</p>
    <div class="feedback-success__actions">
      <VButton variant="primary" size="lg" block @click="goToDiary">
        В дневник
      </VButton>
      <VButton variant="ghost" block @click="goToDashboard">
        На главную
      </VButton>
    </div>
  </div>

  <!-- ===== FORM SCREEN ===== -->
  <div v-else class="feedback">
    <!-- Header -->
    <header class="feedback__header">
      <button class="feedback__back" @click="onBack">←</button>
      <h1 class="feedback__header-title">Feedback</h1>
      <span class="feedback__header-spacer" />
    </header>

    <div class="feedback__body">
      <!-- Practice info -->
      <div v-if="practice" class="feedback__practice">
        <div class="feedback__practice-emoji">{{ typeEmoji }}</div>
        <h2 class="feedback__practice-name">{{ practice.title }}</h2>
        <p class="feedback__practice-meta">
          с {{ practice.master_name ?? 'Мастером' }} · Завершена
        </p>
      </div>
      <div v-else-if="practiceLoading" class="feedback__loader">
        <VLoader />
      </div>

      <!-- Question -->
      <div class="feedback__question">
        <h3>Как прошла практика?</h3>
        <p>Оцените своё состояние после</p>
      </div>

      <!-- Rating buttons -->
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
          <span class="feedback__rating-emoji">{{ opt.emoji }}</span>
          <span class="feedback__rating-label">{{ opt.label }}</span>
        </button>
      </div>

      <!-- Comment -->
      <div class="feedback__comment">
        <textarea
          v-model="comment"
          class="feedback__textarea"
          placeholder="Добавьте комментарий (необязательно)..."
          maxlength="1000"
          rows="3"
        />
      </div>

      <!-- Actions -->
      <div class="feedback__actions">
        <VButton
          variant="primary"
          size="lg"
          block
          :disabled="!selectedRating"
          :loading="diaryStore.feedbackSubmitting"
          @click="onSubmit"
        >
          Отправить feedback
        </VButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePracticesStore } from '@/stores/practices'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { platform } from '@/platform'
import { VButton, VLoader } from '@/components/ui'
import { RATING_OPTIONS, PRACTICE_TYPE_EMOJI } from '@/utils/displayHelpers'
import type { FeedbackRating } from '@/api/types'

const route = useRoute()
const router = useRouter()
const practicesStore = usePracticesStore()
const diaryStore = useDiaryStore()
const toast = useToast()

const practiceId = route.params.practiceId as string

// -- Practice data (for display only) --
const practice = computed(() => practicesStore.selected)
const practiceLoading = computed(() => practicesStore.selectedLoading)

// -- Form state --
const selectedRating = ref<FeedbackRating | null>(null)
const comment = ref('')
const submitted = ref(false)

// -- Rating options (order matches mockup: confused → good → fire) --
// -- Rating options and practice type emoji -- imported from displayHelpers
const typeEmoji = computed(() =>
  practice.value ? (PRACTICE_TYPE_EMOJI[practice.value.practice_type] ?? '🧘') : '🧘',
)

// -- Actions --
function selectRating(rating: FeedbackRating): void {
  selectedRating.value = rating
  platform.hapticFeedback('light')
}

async function onSubmit(): Promise<void> {
  if (!selectedRating.value || diaryStore.feedbackSubmitting) return

  const result = await diaryStore.submitFeedback(practiceId, {
    rating: selectedRating.value,
    comment: comment.value.trim() || null,
  })

  if (result.ok) {
    platform.hapticFeedback('medium')
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

// -- Lifecycle --
onMounted(() => {
  practicesStore.fetchPractice(practiceId)
})
</script>

<style scoped>
/* ===== Success screen ===== */
.feedback-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: var(--space-6);
  text-align: center;
  background: linear-gradient(135deg, var(--velo-success-bg) 0%, var(--velo-success-bg) 100%);
}

.feedback-success__icon {
  font-size: 80px;
  margin-bottom: var(--space-6);
}

.feedback-success__title {
  font-family: var(--font-heading);
  font-size: 28px;
  font-weight: 600;
  color: var(--velo-success-text);
  margin-bottom: var(--space-3);
}

.feedback-success__text {
  font-size: 15px;
  color: var(--velo-success-text);
  margin-bottom: var(--space-8);
  max-width: 280px;
}

.feedback-success__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  width: 100%;
  max-width: 320px;
}

/* ===== Form screen ===== */
.feedback {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.feedback__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--velo-border);
}

.feedback__back {
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
}

.feedback__back:hover {
  background: var(--velo-bg-subtle);
}

.feedback__header-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--velo-text-primary);
}

.feedback__header-spacer {
  width: 36px;
}

.feedback__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-6) var(--space-4);
  gap: var(--space-6);
}

/* Practice info */
.feedback__practice {
  text-align: center;
}

.feedback__practice-emoji {
  font-size: 56px;
  margin-bottom: var(--space-3);
}

.feedback__practice-name {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-2);
}

.feedback__practice-meta {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
}

.feedback__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-4) 0;
}

/* Question */
.feedback__question {
  text-align: center;
}

.feedback__question h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-1);
}

.feedback__question p {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
}

/* Rating buttons */
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
  background: white;
  border: 2px solid var(--velo-border);
  border-radius: 16px;
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: 90px;
  font-family: var(--font-body);
}

.feedback__rating-btn:hover {
  border-color: var(--velo-primary-light);
  transform: translateY(-2px);
}

/* Selected states per rating */
.feedback__rating-btn--selected.feedback__rating-btn--confused {
  border-color: var(--velo-warning);
  background: rgba(245, 158, 11, 0.1);
}

.feedback__rating-btn--selected.feedback__rating-btn--good {
  border-color: var(--velo-success);
  background: rgba(34, 197, 94, 0.1);
}

.feedback__rating-btn--selected.feedback__rating-btn--fire {
  border-color: var(--velo-error-text);
  background: rgba(220, 38, 38, 0.08);
}

.feedback__rating-emoji {
  font-size: 36px;
}

.feedback__rating-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--velo-text-secondary);
}

/* Comment */
.feedback__textarea {
  width: 100%;
  padding: var(--space-3);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  resize: none;
  background: white;
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
}

.feedback__textarea:focus {
  outline: none;
  border-color: var(--velo-primary);
}

/* Actions */
.feedback__actions {
  margin-top: auto;
}
</style>
