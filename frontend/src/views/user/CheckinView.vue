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
    :submit-disabled="false"
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
        <MoodSlider
          v-model="moodScore"
          :zones="MOOD_ZONES"
          aria-label="Оценка состояния от 1 до 10"
        />
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
import MoodSlider from '@/components/shared/MoodSlider.vue'
import {
  IconCalendar,
  IconCheck,
  IconMoodLow,
  IconMoodMid,
  IconMoodHigh,
} from '@/components/icons'
import { formatDate } from '@/utils/format'

// Three slider zones (low -> high), passed to MoodSlider. Icons are .vue
// components, so this stays in the view (not in the utils layer). Labels
// mirror the old discrete buttons (Не очень / Нормально / Хорошо).
const MOOD_ZONES = [
  { icon: IconMoodLow,  label: 'Не очень' },
  { icon: IconMoodMid,  label: 'Нормально' },
  { icon: IconMoodHigh, label: 'Хорошо' },
]

const route = useRoute()
const router = useRouter()
const practicesStore = usePracticesStore()
const diaryStore = useDiaryStore()
const toast = useToast()

const practiceId = route.params.practiceId as string

const practice = computed(() => practicesStore.selected)
const practiceLoading = computed(() => practicesStore.selectedLoading)

// Slider score 1..10. Default 6 = middle "Нормально" zone, so the slider
// opens in a neutral position (the user can still submit immediately).
const moodScore = ref<number>(6)
const comment = ref('')
const submitted = ref(false)

const formattedDate = computed(() =>
  practice.value
    ? formatDate(practice.value.scheduled_at, practice.value.timezone)
    : '',
)

async function onSubmit(): Promise<void> {
  if (diaryStore.checkinSubmitting) return

  const result = await diaryStore.submitCheckin(practiceId, {
    mood: moodScore.value,
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
/* Mood slider wrapper -- the slider itself carries its own styles. */
.checkin__mood {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  width: 100%;
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
