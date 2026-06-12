<!--
  VELO Frontend -- LanguageTimezoneView (Profile redesign Screen F)

  Settings screen for interface language + timezone. Matches Figma node
  4715:3763 (75_Language-Timezone), adapted to existing infrastructure:

  LANGUAGE (stub): the app has no i18n yet, so the language section is a
  single, already-selected "Русский" row. It is rendered from LANGUAGE_OPTIONS
  via v-for so adding real languages later is one array entry + dropping the
  stub flag -- no structural rewrite. Tapping the row does nothing (it is the
  only, already-active option). We deliberately do NOT persist language: with
  one option there is nothing to change, so no PATCH is sent.

  TIMEZONE: reuses the onboarding timezone picker -- VSelect over the curated
  TIMEZONE_OPTIONS (IANA value, "City UTC+X" label). The mockup's separate
  "Изменить город" free-text field and the Москва/Лондон radio rows are NOT
  implemented for MVP; the single select covers the same need (choose a zone)
  with the infrastructure we already have. An exotic profile zone outside the
  curated list is injected via makeTimezoneOption so it stays visible/selectable
  (same approach as OnboardingView).

  Timezone is auto-saved on selection (no explicit Save button -- the mockup
  has none on this screen) via authStore.updateProfile({ timezone }), with a
  short success/error toast.

  Route: /user/profile/language-timezone (name: 'user-language-timezone')
-->

<template>
  <div class="lang-tz">
    <VHeader
      title="Язык/Часовой пояс"
      show-back
      @back="router.back()"
    />

    <div class="lang-tz__content">
      <!-- Language (stub: single active option) -->
      <section class="lang-tz__section">
        <h2 class="lang-tz__section-title">Язык интерфейса</h2>
        <div class="lang-tz__list">
          <button
            v-for="opt in LANGUAGE_OPTIONS"
            :key="opt.value"
            type="button"
            class="lang-tz__row"
            :class="{
              'lang-tz__row--active': opt.value === selectedLanguage,
              'lang-tz__row--static': isLanguageStatic,
            }"
            :disabled="isLanguageStatic"
            @click="onSelectLanguage(opt.value)"
          >
            <span class="lang-tz__row-label">{{ opt.label }}</span>
            <span
              v-if="opt.value === selectedLanguage"
              class="lang-tz__row-check"
              aria-hidden="true"
            >
              <IconCheck :size="18" />
            </span>
          </button>
        </div>
      </section>

      <!-- Timezone (reuses onboarding picker) -->
      <section class="lang-tz__section">
        <h2 class="lang-tz__section-title">Часовой пояс</h2>
        <TimezoneCityPicker
          v-model="selectedTimezone"
          @update:modelValue="onTimezoneChange"
        />
        <p class="lang-tz__hint">
          Часовой пояс используется, чтобы правильно показывать время практик.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { IconCheck } from '@/components/icons'
import TimezoneCityPicker from '@/components/shared/TimezoneCityPicker.vue'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { ApiResponseError } from '@/api/client'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

// -- Language (stub) --------------------------------------------------------
// Extensible by design: add entries here (and remove the single-option
// assumption) once i18n lands. For now only Russian, always selected.
interface LanguageOption {
  value: string
  label: string
}
const LANGUAGE_OPTIONS: LanguageOption[] = [
  { value: 'ru', label: 'Русский' },
]

// While there is only one language, the row is non-interactive (it is already
// selected and there is nothing to switch to). When real languages are added
// this flips to false automatically and the row becomes tappable again.
const isLanguageStatic = LANGUAGE_OPTIONS.length <= 1

// Current language: the user's stored value if it is one we offer, else the
// only available option. With one option this is always 'ru'.
const selectedLanguage = ref(
  LANGUAGE_OPTIONS.some((o) => o.value === authStore.user?.language)
    ? (authStore.user?.language as string)
    : (LANGUAGE_OPTIONS[0]?.value ?? 'ru'),
)

function onSelectLanguage(value: string): void {
  // No-op while only one language exists (button is disabled too). Kept as a
  // handler so wiring real languages later is a one-line change.
  if (isLanguageStatic) return
  selectedLanguage.value = value
}

// -- Timezone ---------------------------------------------------------------
const FALLBACK_TIMEZONE = 'UTC'

/** Whether an IANA id is a real, resolvable zone (Intl throws otherwise). */
function isValidIana(zone: string): boolean {
  try {
    Intl.DateTimeFormat(undefined, { timeZone: zone })
    return true
  } catch {
    return false
  }
}

// Initial timezone: the user's profile zone (kept as-is when valid, even if
// it is outside the curated list), else fallback.
const profileTz = authStore.user?.timezone
const initialTimezone =
  profileTz && isValidIana(profileTz) ? profileTz : FALLBACK_TIMEZONE
const selectedTimezone = ref(initialTimezone)

const saving = ref(false)

async function onTimezoneChange(value: string): Promise<void> {
  if (saving.value) return
  const previous = selectedTimezone.value
  selectedTimezone.value = value
  saving.value = true
  try {
    await authStore.updateProfile({ timezone: value })
    toast.info('Часовой пояс сохранён')
  } catch (error) {
    // Revert the selection so the UI matches the server on failure.
    selectedTimezone.value = previous
    const message =
      error instanceof ApiResponseError
        ? error.detail || 'Не удалось сохранить часовой пояс'
        : 'Не удалось сохранить часовой пояс'
    toast.error(message)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.lang-tz {
  display: flex;
  flex-direction: column;
  margin: calc(-1 * var(--space-4));
}

.lang-tz__content {
  padding: 0 var(--space-4) var(--space-4);
}

.lang-tz__section {
  margin-bottom: var(--space-5);
}

.lang-tz__section-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-3);
}

.lang-tz__list {
  background: var(--velo-glass-blue-15);
  border: 1px solid var(--velo-glass-border);
  border-radius: var(--radius-md);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  overflow: hidden;
}

.lang-tz__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  text-align: left;
}

.lang-tz__row + .lang-tz__row {
  border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.lang-tz__row--static {
  cursor: default;
}

.lang-tz__row--active {
  color: var(--velo-primary);
}

.lang-tz__row-check {
  display: inline-flex;
  align-items: center;
  color: var(--velo-primary);
}

.lang-tz__hint {
  margin: var(--space-2) 0 0;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
}
</style>
