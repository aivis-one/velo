<!--
  VELO Frontend -- CheckinView (Phase F9.1)

  Full-screen pre-practice check-in form.
  Matches mockup screen-checkin layout:
    - Header with back button
    - Practice info (emoji + name + time)
    - "Как вы себя чувствуете?" question
    - Three mood buttons: low / mid / high
    - Optional comment textarea
    - Submit button (disabled until mood selected)
    - "Пропустить" ghost button
    - Success screen (inline, no route change)

  Route: /user/checkin/:practiceId
  Param: practiceId (practice UUID)

  On success: navigates to dashboard or back to practice detail.
  On skip: navigates back without submitting.
-->

<template>
  <!-- ===== SUCCESS SCREEN ===== -->
  <div v-if="submitted" class="checkin-success">
    <div class="checkin-success__icon">✅</div>
    <h1 class="checkin-success__title">Check-in отправлен!</h1>
    <p class="checkin-success__text">Спасибо! Ваше состояние записано. Хорошей практики! 🙏</p>
    <div class="checkin-success__actions">
      <VButton variant="primary" size="lg" block @click="goToDashboard">
        На главную
      </VButton>
      <VButton variant="ghost" block @click="goToDiary">
        В дневник
      </VButton>
    </div>
  </div>

  <!-- ===== FORM SCREEN ===== -->
  <div v-else class="checkin">
    <!-- Header -->
    <header class="checkin__header">
      <button class="checkin__back" @click="onBack">←</button>
      <h1 class="checkin__header-title">Check-in</h1>
      <!-- Spacer keeps title centered -->
      <span class="checkin__header-spacer" />
    </header>

    <div class="checkin__body">
      <!-- Practice info -->
      <div v-if="practice" class="checkin__practice">
        <div class="checkin__practice-emoji">{{ typeEmoji }}</div>
        <h2 class="checkin__practice-name">{{ practice.title }}</h2>
        <p class="checkin__practice-meta">
          с {{ practice.master_name ?? 'Мастером' }} · {{ formattedDate }}
        </p>
      </div>
      <div v-else-if="practiceLoading" class="checkin__loader">
        <VLoader />
      </div>

      <!-- Question -->
      <div class="checkin__question">
        <h3>Как вы себя чувствуете?</h3>
        <p>Оцените своё состояние перед практикой</p>
      </div>

      <!-- Mood buttons -->
      <div class="checkin__mood-buttons">
        <button
          v-for="opt in MOOD_OPTIONS"
          :key="opt.value"
          class="checkin__mood-btn"
          :class="[
            `checkin__mood-btn--${opt.value}`,
            { 'checkin__mood-btn--selected': selectedMood === opt.value },
          ]"
          @click="selectMood(opt.value)"
        >
          <span class="checkin__mood-emoji">{{ opt.emoji }}</span>
          <span class="checkin__mood-label">{{ opt.label }}</span>
        </button>
      </div>

      <!-- Comment -->
      <div class="checkin__comment">
        <textarea
          v-model="comment"
          class="checkin__textarea"
          placeholder="Добавьте комментарий (необязательно)..."
          maxlength="1000"
          rows="3"
        />
      </div>

      <!-- Actions -->
      <div class="checkin__actions">
        <VButton
          variant="primary"
          size="lg"
          block
          :disabled="!selectedMood"
          :loading="diaryStore.checkinSubmitting"
          @click="onSubmit"
        >
          Отправить check-in
        </VButton>
        <VButton
          variant="ghost"
          block
          :disabled="diaryStore.checkinSubmitting"
          @click="onSkip"
        >
          Пропустить
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
import { formatDate } from '@/utils/format'
import { MOOD_OPTIONS, PRACTICE_TYPE_EMOJI } from '@/utils/displayHelpers'
import type { Mood } from '@/api/types'

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
const selectedMood = ref<Mood | null>(null)
const comment = ref('')
const submitted = ref(false)

// -- Mood options --
// -- Practice type emoji -- imported from displayHelpers
const typeEmoji = computed(() =>
  practice.value ? (PRACTICE_TYPE_EMOJI[practice.value.practice_type] ?? '🧘') : '🧘',
)

const formattedDate = computed(() =>
  practice.value
    ? formatDate(practice.value.scheduled_at, practice.value.timezone)
    : '',
)

// -- Actions --
function selectMood(mood: Mood): void {
  selectedMood.value = mood
  platform.hapticFeedback('light')
}

async function onSubmit(): Promise<void> {
  if (!selectedMood.value || diaryStore.checkinSubmitting) return

  const result = await diaryStore.submitCheckin(practiceId, {
    mood: selectedMood.value,
    comment: comment.value.trim() || null,
  })

  if (result.ok) {
    platform.hapticFeedback('medium')
    submitted.value = true
  } else {
    toast.error(result.error)
  }
}

function onSkip(): void {
  toast.info('Check-in пропущен')
  router.push({ name: 'user-dashboard' })
}

function onBack(): void {
  router.push({ name: 'practice-detail', params: { id: practiceId } })
}

function goToDashboard(): void {
  router.push({ name: 'user-dashboard' })
}

function goToDiary(): void {
  router.push({ name: 'user-diary' })
}

// -- Lifecycle --
onMounted(() => {
  practicesStore.fetchPractice(practiceId)
})
</script>

<style scoped>
/* ===== Success screen ===== */
.checkin-success {
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

.checkin-success__icon {
  font-size: 80px;
  margin-bottom: var(--space-6);
}

.checkin-success__title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-success-text);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-3);
}

.checkin-success__text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-success-text);
  margin-bottom: var(--space-8);
  max-width: 280px;
}

.checkin-success__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  width: 100%;
  max-width: 320px;
}

/* ===== Form screen ===== */
.checkin {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.checkin__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
}

.checkin__back {
  width: 36px;
  height: 36px;
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  font-size: var(--text-lg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity var(--transition-fast);
}

.checkin__back:hover {
  opacity: 0.8;
}

.checkin__header-title {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.checkin__header-spacer {
  width: 36px;
}

.checkin__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-6) var(--space-4);
  gap: var(--space-6);
}

/* Practice info */
.checkin__practice {
  text-align: center;
}

.checkin__practice-emoji {
  font-size: 56px;
  margin-bottom: var(--space-3);
}

.checkin__practice-name {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-2);
}

.checkin__practice-meta {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.checkin__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-4) 0;
}

/* Question */
.checkin__question {
  text-align: center;
}

.checkin__question h3 {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-1);
}

.checkin__question p {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

/* Mood buttons */
.checkin__mood-buttons {
  display: flex;
  justify-content: center;
  gap: var(--space-4);
}

.checkin__mood-btn {
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

.checkin__mood-btn:hover {
  opacity: 0.8;
}

.checkin__mood-btn--selected {
  border-color: var(--velo-primary);
  background: var(--velo-glass-blue-60);
  box-shadow: var(--velo-shadow-glow);
}

.checkin__mood-btn--selected.checkin__mood-btn--low {
  border-color: var(--velo-pink-300);
  background: var(--velo-glass-peach-40);
}

.checkin__mood-btn--selected.checkin__mood-btn--mid {
  border-color: var(--velo-peach-300);
  background: var(--velo-glass-peach-40);
}

.checkin__mood-btn--selected.checkin__mood-btn--high {
  border-color: var(--velo-teal-400);
  background: var(--velo-glass-teal-30);
}

.checkin__mood-emoji {
  font-size: 36px;
}

.checkin__mood-label {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

/* Comment */
.checkin__textarea {
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

.checkin__textarea::placeholder {
  color: var(--velo-text-muted);
}

.checkin__textarea:focus {
  outline: none;
  border-color: var(--velo-border-input-focus);
}

/* Actions */
.checkin__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-top: auto;
}
</style>
