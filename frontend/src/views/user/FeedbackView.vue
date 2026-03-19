<!--
  VELO Frontend -- FeedbackView (Phase F9.1, updated back-button)

  Full-screen post-practice feedback form.
  Matches mockup screen-feedback layout:
    - Header with back button (VHeader with pill back button)
    - Practice info (emoji + name + "Завершена")
    - "Как прошла практика?" question
    - Three rating buttons: confused / good / fire
    - Optional comment textarea
    - Submit button (disabled until rating selected)
    - Success screen (inline, no route change)

  Route: /user/feedback/:practiceId
  Param: practiceId (practice UUID)

  On success: offers navigation to diary or dashboard.
  Note: no "Skip" button -- feedback is voluntary but if opened, user intent
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
    <VHeader show-back back-label="Feedback" @back="onBack" />

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
import { VHeader } from '@/components/layout'
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

const typeEmoji = computed(() =>
  practice.value
    ? (PRACTICE_TYPE_EMOJI[practice.value.practice_type] ?? '🧘')
    : '🧘',
)

// -- Actions --
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

// -- Lifecycle --
onMounted(() => {
  if (practicesStore.selected?.id !== practiceId) {
    practicesStore.fetchPractice(practiceId)
  }
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
  background: var(--velo-glass-teal-30);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.feedback-success__icon {
  font-size: 80px;
  margin-bottom: var(--space-6);
}

.feedback-success__title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-success-text);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-3);
}

.feedback-success__text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
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
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-2);
}

.feedback__practice-meta {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
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
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-1);
}

.feedback__question p {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
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
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: 90px;
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

.feedback__rating-emoji {
  font-size: 36px;
}

.feedback__rating-label {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

/* Comment */
.feedback__textarea {
  width: 100%;
  padding: var(--space-3);
  border: 2px solid transparent;
  border-radius: 5px;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-primary);
  resize: none;
  background: var(--velo-glass-blue-15);
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
}

.feedback__textarea::placeholder {
  color: var(--velo-text-muted);
}

.feedback__textarea:focus {
  outline: none;
  border-color: var(--velo-border-input-focus);
}

/* Actions */
.feedback__actions {
  margin-top: auto;
}
</style>
