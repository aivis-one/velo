<!--
  VELO Frontend -- Onboarding View (onboarding 05-08)

  Four-step welcome carousel, shown once to new users (those whose
  onboarding_completed flag is false) right after they tap "Войти" on
  WelcomeView. App.vue mounts this only for new users.

  Steps:
    0  "Найдите свою практику"      (intro)
    1  "Ведите дневник"             (intro)
    2  "Карта себя"                 (intro)
    3  "Часовой пояс" -- VSelect of IANA zones, default from auto-detect

  Navigation:
    - "Далее" advances; on the last intro step it goes to the timezone step.
    - "Пропустить" jumps straight to the timezone step (step 3) -- the zone
      still has to be confirmed, so we never skip it entirely.
    - "Готово" on step 3 persists { timezone, onboarding_completed: true }
      via authStore.updateProfile, then emits `done`.

  Single outward event: `done`. App.vue switches to the dashboard on it.
  Persistence happens here so App.vue stays a simple state machine.

  Illustrations live in public/onboarding/ (provided separately):
    /onboarding/onboarding-practice.svg
    /onboarding/onboarding-diary.svg
    /onboarding/onboarding-masters.svg
-->

<template>
  <div class="onboarding">
    <!-- Skip: visible on intro steps only (not on the timezone step). -->
    <div class="onboarding__skip-row">
      <button
        v-if="!isTimezoneStep"
        type="button"
        class="onboarding__skip"
        @click="goToTimezoneStep"
      >
        Пропустить
      </button>
    </div>

    <!-- ================= INTRO STEPS (0-2) ================= -->
    <div v-if="!isTimezoneStep" class="onboarding__body">
      <img
        :src="currentSlide.image"
        :alt="currentSlide.title"
        class="onboarding__illustration"
      />
      <h2 class="onboarding__title">{{ currentSlide.title }}</h2>
      <p class="onboarding__text">{{ currentSlide.text }}</p>
    </div>

    <!-- ================= TIMEZONE STEP (3) ================= -->
    <div v-else class="onboarding__body onboarding__body--form">
      <h2 class="onboarding__title">Часовой пояс</h2>
      <p class="onboarding__text">
        Укажите ваш часовой пояс, чтобы мы правильно показывали время практик
      </p>
      <div class="onboarding__field">
        <VSelect
          v-model="selectedTimezone"
          label="Часовой пояс"
          :options="TIMEZONE_OPTIONS"
        />
      </div>
    </div>

    <!-- ================= FOOTER: dots + action ================= -->
    <div class="onboarding__footer">
      <div class="onboarding__dots" aria-hidden="true">
        <span
          v-for="(_, i) in TOTAL_STEPS"
          :key="i"
          class="onboarding__dot"
          :class="{ 'onboarding__dot--active': i === step }"
        />
      </div>

      <button
        type="button"
        class="onboarding__button"
        :disabled="submitting"
        @click="onPrimaryAction"
      >
        {{ isTimezoneStep ? 'Готово' : 'Далее' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { VSelect } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { ApiResponseError } from '@/api/client'
import { TIMEZONE_OPTIONS } from '@/utils/practiceOptions'

const emit = defineEmits<{
  /** Onboarding finished (completed or skipped); flag is already persisted. */
  done: []
}>()

const authStore = useAuthStore()
const toast = useToast()

// Total steps: 3 intro + 1 timezone. Last index (3) is the timezone step.
const TOTAL_STEPS = 4
const TIMEZONE_STEP_INDEX = TOTAL_STEPS - 1

const step = ref(0)
const submitting = ref(false)
// Guards against a fast multi-click slipping past the timezone screen.
//
// The naive "step += 1" lets click 1 land on the timezone index (isTimezoneStep
// turns true synchronously) and click 2 immediately hit finish() -- the user
// never sees the timezone picker and it saves with the default zone.
//
// Two flags fix it deterministically:
//   advancing   -- blocks re-entrant intro->intro/->timezone advances.
//   finishArmed -- finish() only fires once the timezone step has been
//                  ENTERED and settled (armed on the next microtask). A click
//                  that races the transition into the timezone step finds
//                  finishArmed=false and is ignored; a deliberate later tap
//                  finds it true and proceeds.
const advancing = ref(false)
const finishArmed = ref(false)

const isTimezoneStep = computed(() => step.value === TIMEZONE_STEP_INDEX)

// -- Intro slides (0-2). Illustrations served from public/onboarding/. --
const SLIDES = [
  {
    image: '/onboarding/onboarding-practice.svg',
    title: 'Найдите свою практику',
    text: 'Выбирайте из медитаций, breathwork и других практик с лучшими мастерами',
  },
  {
    image: '/onboarding/onboarding-diary.svg',
    title: 'Ведите дневник',
    text: 'Отслеживайте свое состояние до и после практик, получайте AI-инсайты',
  },
  {
    image: '/onboarding/onboarding-masters.svg',
    title: 'Карта себя',
    text: 'Живая карта, которая меняется вместе с вами, оставаясь актуальной по мере того, как вы продолжаете исследовать себя',
  },
] as const

// Only read on intro steps (v-if="!isTimezoneStep" -> step in 0..2), and
// step is capped at TIMEZONE_STEP_INDEX, so SLIDES[step] is always defined
// here. The ?? SLIDES[0] is a defensive fallback for an impossible state,
// not normal flow.
const currentSlide = computed(() => SLIDES[step.value] ?? SLIDES[0])

// -- Timezone default: auto-detect, fall back to Moscow if not in our list. --
// We only offer the curated TIMEZONE_OPTIONS set, so an auto-detected zone
// outside it (e.g. Asia/Novosibirsk) falls back rather than being injected.
const FALLBACK_TIMEZONE = 'Europe/Moscow'

function detectDefaultTimezone(): string {
  let detected = ''
  try {
    detected = Intl.DateTimeFormat().resolvedOptions().timeZone || ''
  } catch {
    detected = ''
  }
  const isKnownZone = (zone: string): boolean =>
    TIMEZONE_OPTIONS.some((opt: { label: string; value: string }) => opt.value === zone)

  // Prefer the user's existing profile zone if it is a known option,
  // otherwise the detected zone, otherwise the fallback.
  const profileTz = authStore.user?.timezone
  if (profileTz && isKnownZone(profileTz)) {
    return profileTz
  }
  return isKnownZone(detected) ? detected : FALLBACK_TIMEZONE
}

const selectedTimezone = ref(detectDefaultTimezone())

// -- Navigation --------------------------------------------------------------

/**
 * Enter the timezone step and arm finish() only after the change settles.
 * Arming on the next microtask is what prevents a click that raced the
 * transition from immediately triggering finish().
 */
async function enterTimezoneStep(): Promise<void> {
  step.value = TIMEZONE_STEP_INDEX
  finishArmed.value = false
  await Promise.resolve()
  finishArmed.value = true
}

function goToTimezoneStep(): void {
  // "Пропустить" -- same destination, also armed after settle.
  void enterTimezoneStep()
}

async function onPrimaryAction(): Promise<void> {
  if (isTimezoneStep.value) {
    // Ignore clicks that raced the transition into the timezone step.
    if (!finishArmed.value) return
    await finish()
    return
  }
  // Intro steps: block re-entrant advances; cap at the timezone index.
  if (advancing.value) return
  advancing.value = true
  // try/finally so advancing is always released. Nothing here throws today
  // (assignments + a microtask await), but the finally guards against a
  // future change introducing a throw and leaving the button permanently
  // locked (every click would hit the `if (advancing.value) return` above).
  try {
    const next = Math.min(step.value + 1, TIMEZONE_STEP_INDEX)
    if (next === TIMEZONE_STEP_INDEX) {
      await enterTimezoneStep()
    } else {
      step.value = next
    }
  } finally {
    advancing.value = false
  }
}

// -- Finish: persist timezone + onboarding flag, then emit done. -------------

async function finish(): Promise<void> {
  if (submitting.value) return
  submitting.value = true
  try {
    await authStore.updateProfile({
      timezone: selectedTimezone.value,
      onboarding_completed: true,
    })
    emit('done')
  } catch (error) {
    const message =
      error instanceof ApiResponseError
        ? error.detail
        : 'Не удалось сохранить. Попробуйте ещё раз.'
    toast.error(message)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.onboarding {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--space-6);
  background: transparent;
}

.onboarding__skip-row {
  display: flex;
  justify-content: flex-end;
  /* Reserve height even when Skip is hidden so layout doesn't jump. */
  min-height: 24px;
}

.onboarding__skip {
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  padding: var(--space-1) var(--space-2);
}

.onboarding__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: var(--space-4);
}

.onboarding__body--form {
  justify-content: center;
  gap: var(--space-5);
}

.onboarding__illustration {
  width: 180px;
  height: 180px;
  object-fit: contain;
}

.onboarding__title {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.onboarding__text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin: 0;
  max-width: 300px;
  line-height: 1.5;
}

.onboarding__field {
  width: 100%;
  max-width: var(--velo-content-width);
  text-align: left;
}

.onboarding__footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-5);
  padding-top: var(--space-4);
}

.onboarding__dots {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.onboarding__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(76, 101, 137, 0.6);
  transition: width var(--transition-fast), background var(--transition-fast);
}

.onboarding__dot--active {
  width: 13px;
  border-radius: var(--radius-full);
  background: var(--velo-text-primary);
}

.onboarding__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: var(--velo-content-width);
  height: 50px;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  cursor: pointer;
  border-radius: var(--radius-full);
  border: 1px solid #ffffff;
  background: var(--velo-primary);
  color: white;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  box-shadow: var(--velo-shadow-glow);
  transition: opacity var(--transition-fast);
}

.onboarding__button:hover {
  opacity: 0.9;
}

.onboarding__button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.onboarding__button:focus-visible {
  outline: 2px solid var(--velo-primary);
  outline-offset: 2px;
}
</style>
