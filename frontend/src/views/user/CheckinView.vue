<!--
  VELO Frontend -- CheckinView (Phase F9.1, updated back-button, WARNING-9)

  Full-screen pre-practice check-in form.
  Uses FormShell for shared layout/CSS. Only mood-specific logic stays here.

  Route: /user/checkin/:practiceId
  Param: practiceId (practice UUID)
-->

<template>
  <FormShell
    back-label="Check-in"
    :practice="practice"
    :practice-loading="practiceLoading"
    question-title="Как вы себя чувствуете?"
    question-subtitle="Оцените своё состояние перед практикой"
    v-model:comment="comment"
    :submitting="diaryStore.checkinSubmitting"
    :submit-disabled="!selectedMood"
    submit-label="Check-in перед практикой"
    :show-skip="true"
    :submitted="submitted"
    success-icon="✅"
    success-title="Check-in отправлен!"
    success-text="Спасибо! Ваше состояние записано. Хорошей практики! 🙏"
    @back="onBack"
    @submit="onSubmit"
    @skip="onSkip"
  >
    <!-- Practice meta line -->
    <template #practice-meta>
      с {{ practice?.master_name ?? 'Мастером' }} · 📅 {{ formattedDate }}
    </template>

    <!-- Mood buttons -->
    <template #selection>
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
    </template>

    <!-- Success actions -->
    <template #success-actions>
      <VButton variant="primary" size="lg" block @click="goToDashboard">
        На главную
      </VButton>
      <VButton variant="ghost" block @click="goToDiary">
        В дневник
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
import FormShell from '@/components/shared/FormShell.vue'
import { MOOD_OPTIONS } from '@/utils/displayHelpers'
import { formatDate } from '@/utils/format'
import type { Mood } from '@/api/types'

const route = useRoute()
const router = useRouter()
const practicesStore = usePracticesStore()
const diaryStore = useDiaryStore()
const toast = useToast()

const practiceId = route.params.practiceId as string

const practice = computed(() => practicesStore.selected)
const practiceLoading = computed(() => practicesStore.selectedLoading)

const selectedMood = ref<Mood | null>(null)
const comment = ref('')
const submitted = ref(false)

const formattedDate = computed(() =>
  practice.value
    ? formatDate(practice.value.scheduled_at, practice.value.timezone)
    : '',
)

function selectMood(mood: Mood): void {
  selectedMood.value = mood
  try { platform.hapticFeedback('light') } catch { /* silent fallback */ }
}

async function onSubmit(): Promise<void> {
  if (!selectedMood.value || diaryStore.checkinSubmitting) return

  const result = await diaryStore.submitCheckin(practiceId, {
    mood: selectedMood.value,
    comment: comment.value.trim() || null,
  })

  if (result.ok) {
    try { platform.hapticFeedback('medium') } catch { /* silent fallback */ }
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

onMounted(() => {
  if (practicesStore.selected?.id !== practiceId) {
    practicesStore.fetchPractice(practiceId)
  }
})
</script>

<style scoped>
/* Mood buttons -- unique to CheckinView */
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
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: var(--size-option-btn-min);
  font-family: var(--font-body);
}

.checkin__mood-btn:hover {
  opacity: 0.8;
}

.checkin__mood-btn--selected {
  border-color: var(--steel-button);
  background: var(--surface-steel-alpha-60);
  box-shadow: var(--shadow-glow-white);
}

.checkin__mood-btn--selected.checkin__mood-btn--low {
  border-color: var(--pink-primary);
  background: var(--surface-warm-alpha-40);
}

.checkin__mood-btn--selected.checkin__mood-btn--mid {
  border-color: var(--warm-primary);
  background: var(--surface-warm-alpha-40);
}

.checkin__mood-btn--selected.checkin__mood-btn--high {
  border-color: var(--teal-primary);
  background: var(--surface-teal-alpha-30);
}

.checkin__mood-emoji {
  font-size: 36px;
}

.checkin__mood-label {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--text-secondary);
}
</style>
