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
    success-text="Спасибо! Ваше состояние записано. Хорошей практики!"
    @back="onBack"
    @submit="onSubmit"
    @skip="onSkip"
  >
    <!-- Practice meta line -->
    <template #practice-meta>
      с {{ practice?.master_name ?? 'Мастером' }}
      <IconCalendar :size="14" /> {{ formattedDate }}
    </template>

    <!-- Mood selector: selected face grows to center, others shrink/dim.
         The track + dot below is a decorative indicator of the discrete
         choice (low/mid/high) -- not a real range slider. -->
    <template #selection>
      <div class="checkin__mood">
        <div class="checkin__mood-row">
          <button
            v-for="opt in MOOD_OPTIONS"
            :key="opt.value"
            type="button"
            class="checkin__mood-btn"
            :class="{ 'checkin__mood-btn--selected': selectedMood === opt.value }"
            @click="selectMood(opt.value)"
          >
            <component
              :is="MOOD_ICON[opt.value]"
              :size="selectedMood === opt.value ? 63 : 40"
            />
            <span class="checkin__mood-label">{{ opt.label }}</span>
          </button>
        </div>
        <!-- Decorative track + dot under the selected position -->
        <div class="checkin__mood-track">
          <span
            class="checkin__mood-dot"
            :class="`checkin__mood-dot--${selectedMood ?? 'mid'}`"
          />
        </div>
      </div>
    </template>

    <!-- Success icon: reused IconCheck in a teal circle (Figma 13) -->
    <template #success-icon>
      <span class="checkin__success-check">
        <IconCheck :size="48" />
      </span>
    </template>

    <!-- Success actions -->
    <template #success-actions>
      <VButton variant="primary" size="lg" block @click="goToPracticeLive">
        Начать практику
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
import FormShell from '@/components/shared/FormShell.vue'
import {
  IconCalendar,
  IconCheck,
  IconMoodLow,
  IconMoodMid,
  IconMoodHigh,
} from '@/components/icons'
import { MOOD_OPTIONS } from '@/utils/displayHelpers'
import { formatDate } from '@/utils/format'
import type { Mood } from '@/api/types'

// Map discrete mood value -> face icon component (kept here, not in
// displayHelpers, to avoid mixing the utils layer with .vue components).
const MOOD_ICON = {
  low: IconMoodLow,
  mid: IconMoodMid,
  high: IconMoodHigh,
} as const

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

  // selectedMood stays a discrete Mood for the UI (icons / track); the
  // backend now takes a 1..10 score, so map the chosen option to its score.
  const moodScore =
    MOOD_OPTIONS.find((o) => o.value === selectedMood.value)?.score ?? 6

  const result = await diaryStore.submitCheckin(practiceId, {
    mood: moodScore,
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
  // Return to wherever the user came from (practice detail, dashboard, etc.)
  // instead of always pushing practice-detail, which created a 12<->15 loop.
  router.back()
}

function goToDashboard(): void {
  router.push({ name: 'user-dashboard' })
}

// Navigate to the live practice screen (route exists, see router/index.ts).
function goToPracticeLive(): void {
  router.push({ name: 'practice-live', params: { practiceId } })
}

onMounted(() => {
  if (practicesStore.selected?.id !== practiceId) {
    practicesStore.fetchPractice(practiceId)
  }
})
</script>

<style scoped>
/* Mood selector -- unique to CheckinView */
.checkin__mood {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  width: 100%;
}

.checkin__mood-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
}

.checkin__mood-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  /* Unselected: small dim card. Selected: large bright card. */
  width: 82px;
  height: 84px;
  padding: var(--space-2);
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: 9.5px;
  cursor: pointer;
  opacity: 0.8;
  transition: all var(--transition-base);
  font-family: var(--font-body);
}

.checkin__mood-btn--selected {
  width: 129px;
  height: 132px;
  border-radius: var(--radius-md);
  opacity: 1;
  box-shadow: var(--velo-shadow-glow);
}

.checkin__mood-label {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-primary);
}

/* Decorative track + dot (reflects the discrete choice position) */
.checkin__mood-track {
  position: relative;
  width: 253px;
  height: 2px;
  border-radius: var(--radius-full);
  background: var(--velo-text-primary);
  opacity: 0.5;
}

.checkin__mood-dot {
  position: absolute;
  top: 50%;
  width: 21.5px;
  height: 21.5px;
  border-radius: var(--radius-full);
  background: var(--velo-primary);
  border: 2px solid #ffffff;
  transform: translate(-50%, -50%);
  transition: left var(--transition-base);
}

.checkin__mood-dot--low {
  left: 0;
}
.checkin__mood-dot--mid {
  left: 50%;
}
.checkin__mood-dot--high {
  left: 100%;
}

/* Success check icon in a teal circle (reused IconCheck, Figma 13) */
.checkin__success-check {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 93px;
  height: 93px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}
</style>
