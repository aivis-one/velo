<!--
  VELO Frontend -- OnboardingTimezoneView (S2 P06 C21 — final onboarding step)

  City input + autocomplete -> select city -> PATCH /api/v1/users/me { timezone }
  + localStorage 'velo:onboarding_completed=true' (decision #034) + redirect
  to /user/dashboard.

  PATCH failures (e.g. 401 in PWA-no-auth context until BACKEND § A.1 lands)
  are swallowed silently per Path Y graceful degrade — localStorage flag still
  sets, navigation still happens. Cross-device parity deferred until backend
  ships User.onboarding_completed (BACKEND § B.2).

  Skin reference: docs/04_assets/velo-design-system-2026-04-30/project/uploads/08_Onboarding 4.png
  (skin 08 ambiguity resolved at OPEN §3 — confirmed timezone capture screen
  by image render: title "Часовой пояс", subtitle, input "Город", 4-dot progress).

  City -> IANA mapping: hand-curated frontend/src/data/cities.json (~100 entries).
  Native Intl.DateTimeFormat is the upstream tz library; no new dep added.
-->

<template>
  <div class="timezone">
    <header class="timezone__header">
      <button
        type="button"
        class="timezone__back"
        aria-label="Назад"
        @click="onBack"
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <div
        class="timezone__dots"
        role="tablist"
        aria-label="Шаг 4 из 4"
      >
        <span class="timezone__dot" />
        <span class="timezone__dot" />
        <span class="timezone__dot" />
        <span class="timezone__dot timezone__dot--active" />
      </div>
    </header>

    <div class="timezone__content">
      <h1 class="timezone__title">
        Часовой пояс
      </h1>
      <p class="timezone__subtitle">
        Укажите ваш фактический город проживания, чтобы мы смогли определить ваш часовой пояс
      </p>

      <div class="timezone__field">
        <VInput
          v-model="cityInput"
          type="text"
          placeholder="Город"
          label="Город"
        />
        <ul
          v-if="suggestions.length > 0"
          class="timezone__suggestions"
        >
          <li
            v-for="city in suggestions"
            :key="city.name"
            class="timezone__suggestion"
            @click="selectSuggestion(city)"
          >
            <span class="timezone__suggestion-name">{{ city.name }}</span>
            <span class="timezone__suggestion-tz">{{ city.iana }}</span>
          </li>
        </ul>
      </div>
    </div>

    <VButton
      variant="primary"
      size="md"
      block
      :disabled="!canSubmit"
      :loading="submitting"
      @click="onSubmit"
    >
      Готово
    </VButton>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VButton, VInput } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { api } from '@/api/client'
import citiesData from '@/data/cities.json'

interface CityEntry {
  name: string
  iana: string
}

const cities = citiesData as CityEntry[]
const router = useRouter()
const toast = useToast()

const cityInput = ref('')
const submitting = ref(false)

const suggestions = computed<CityEntry[]>(() => {
  const q = cityInput.value.trim().toLowerCase()
  if (q.length < 2) return []
  return cities
    .filter((c) => c.name.toLowerCase().includes(q))
    .slice(0, 8)
})

const selectedCity = computed<CityEntry | null>(() => {
  const q = cityInput.value.trim().toLowerCase()
  return cities.find((c) => c.name.toLowerCase() === q) ?? null
})

const canSubmit = computed(() => selectedCity.value !== null && !submitting.value)

function selectSuggestion(city: CityEntry): void {
  cityInput.value = city.name
}

async function onSubmit(): Promise<void> {
  if (!selectedCity.value) {
    toast.error('Выберите город из списка')
    return
  }

  const timezone = selectedCity.value.iana
  submitting.value = true

  try {
    // Real PATCH attempt — succeeds in TMA-auth context. PWA-no-auth (until
    // BACKEND § A.1 lands) returns 401; swallowed silently per Path Y graceful
    // degrade. localStorage flag below is the v1 source of truth (decision #034).
    await api.patch('/api/v1/users/me', { timezone })
  } catch (e) {
    console.warn('[C21] PATCH /users/me failed (mock/no-auth context expected):', e)
  } finally {
    submitting.value = false
  }

  // Set localStorage flag regardless of PATCH outcome (decision #034 — local v1).
  localStorage.setItem('velo:onboarding_completed', 'true')
  toast.success('Готово!')
  router.replace({ name: 'user-dashboard' })
}

function onBack(): void {
  router.back()
}
</script>

<style scoped>
.timezone {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--space-6);
  gap: var(--space-4);
  background: var(--surface-default);
}

.timezone__header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.timezone__back {
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  padding: var(--space-2);
}

.timezone__dots {
  display: flex;
  gap: var(--space-2);
  flex: 1;
  justify-content: center;
}

.timezone__dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--surface-steel-alpha-15);
}

.timezone__dot--active {
  background: var(--steel-button);
}

.timezone__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  flex: 1;
}

.timezone__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.timezone__subtitle {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.timezone__field {
  position: relative;
}

.timezone__suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 240px;
  overflow-y: auto;
  background: var(--surface-default);
  border: 1px solid var(--surface-steel-alpha-15);
  border-radius: var(--radius-lg);
  margin-top: var(--space-2);
  padding: 0;
  list-style: none;
  box-shadow: var(--shadow-md);
  z-index: 10;
}

.timezone__suggestion {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.timezone__suggestion:hover {
  background: var(--surface-steel-alpha-15);
}

.timezone__suggestion-name {
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: var(--text-base);
}

.timezone__suggestion-tz {
  color: var(--text-muted);
  font-family: var(--font-body);
  font-size: var(--text-sm);
}
</style>
