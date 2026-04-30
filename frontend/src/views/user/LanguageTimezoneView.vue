<!--
  VELO Frontend — LanguageTimezoneView (S2-S3 SPEEDRUN MEGA-2 §C47)

  Two sections: language (ru/en) + timezone (preset rows + city search).
  PATCH /api/v1/users/me on selection. Per BACKEND § B.3 — language is
  metadata-only at v1; no i18n switch. City autocomplete reuses cities.json.
-->

<template>
  <div class="lt">
    <header class="lt__header">
      <button
        type="button"
        class="lt__back"
        aria-label="Назад"
        @click="router.back()"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="lt__title">
        Язык/Часовой пояс
      </h1>
    </header>

    <section class="lt__section">
      <h2 class="lt__sub">
        Язык интерфейса
      </h2>
      <button
        v-for="opt in LANG_OPTIONS"
        :key="opt.value"
        type="button"
        class="lt__row"
        :class="{ 'lt__row--active': language === opt.value }"
        :disabled="busy"
        @click="setLanguage(opt.value)"
      >
        <span class="lt__row-icon">
          <IconGlobe :size="18" />
        </span>
        <span class="lt__row-label">{{ opt.label }}</span>
        <span
          v-if="language === opt.value"
          class="lt__row-check"
        >
          <IconCheck :size="18" />
        </span>
      </button>
    </section>

    <section class="lt__section">
      <h2 class="lt__sub">
        Часовой пояс
      </h2>
      <button
        v-for="preset in TZ_PRESETS"
        :key="preset.iana"
        type="button"
        class="lt__row"
        :class="{ 'lt__row--active': timezone === preset.iana }"
        :disabled="busy"
        @click="setTimezone(preset.iana)"
      >
        <span class="lt__row-icon">
          <IconClock :size="18" />
        </span>
        <span class="lt__row-label">{{ preset.label }}</span>
        <span
          v-if="timezone === preset.iana"
          class="lt__row-check"
        >
          <IconCheck :size="18" />
        </span>
      </button>

      <div class="lt__city">
        <input
          v-model="cityInput"
          type="text"
          class="lt__city-input"
          placeholder="Изменить город"
        >
        <p class="lt__city-help">
          Укажите ваш фактический город проживания, чтобы мы смогли определить ваш часовой пояс.
        </p>
        <ul
          v-if="suggestions.length"
          class="lt__city-list"
        >
          <li
            v-for="c in suggestions"
            :key="c.iana"
            class="lt__city-item"
          >
            <button
              type="button"
              class="lt__city-btn"
              @click="pickCity(c)"
            >
              {{ c.name }}
            </button>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { api } from '@/api/client'
import {
  IconArrowBack,
  IconGlobe,
  IconClock,
  IconCheck,
} from '@/components/icons'
import citiesData from '@/data/cities.json'

interface CityEntry {
  name: string
  iana: string
}

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const LANG_OPTIONS = [
  { value: 'ru', label: 'Русский' },
  { value: 'en', label: 'English' },
] as const

const TZ_PRESETS = [
  { iana: 'Europe/Moscow', label: 'Москва (UTC+3)' },
  { iana: 'Europe/London', label: 'Лондон (UTC+0)' },
] as const

const cities = citiesData as CityEntry[]

const language = ref<'ru' | 'en'>('ru')
const timezone = ref<string>('Europe/Moscow')
const cityInput = ref('')
const busy = ref(false)

onMounted(() => {
  const u = auth.user as
    | (typeof auth.user & { language?: 'ru' | 'en'; timezone?: string })
    | null
  if (u?.language === 'en' || u?.language === 'ru') language.value = u.language
  if (u?.timezone) timezone.value = u.timezone
})

const suggestions = computed<CityEntry[]>(() => {
  const q = cityInput.value.trim().toLowerCase()
  if (q.length < 2) return []
  return cities
    .filter((c) => c.name.toLowerCase().includes(q))
    .slice(0, 6)
})

async function setLanguage(v: 'ru' | 'en'): Promise<void> {
  if (language.value === v || busy.value) return
  busy.value = true
  const previous = language.value
  language.value = v
  try {
    await api.patch('/api/v1/users/me', { language: v })
    toast.success('Язык обновлён')
    await auth.fetchMe()
  } catch (e) {
    console.warn('[C47] PATCH language failed', e)
    language.value = previous
    toast.error('Не удалось обновить язык')
  } finally {
    busy.value = false
  }
}

async function setTimezone(iana: string): Promise<void> {
  if (timezone.value === iana || busy.value) return
  busy.value = true
  const previous = timezone.value
  timezone.value = iana
  try {
    await api.patch('/api/v1/users/me', { timezone: iana })
    toast.success('Часовой пояс обновлён')
    await auth.fetchMe()
  } catch (e) {
    console.warn('[C47] PATCH timezone failed', e)
    timezone.value = previous
    toast.error('Не удалось обновить часовой пояс')
  } finally {
    busy.value = false
  }
}

async function pickCity(c: CityEntry): Promise<void> {
  cityInput.value = c.name
  await setTimezone(c.iana)
}
</script>

<style scoped>
.lt {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.lt__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.lt__back {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lt__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.lt__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.lt__sub {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  margin: 0 0 var(--space-1);
  color: var(--text-primary);
  font-weight: 400;
}

.lt__row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: var(--font-body);
  color: var(--text-primary);
  text-align: left;
}

.lt__row--active {
  background: var(--steel-button);
  color: white;
  border-color: var(--steel-button);
}

.lt__row-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.lt__row-label {
  flex: 1 1 auto;
  font-size: var(--text-base);
}

.lt__row-check {
  display: flex;
  align-items: center;
  justify-content: center;
}

.lt__city {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding-top: var(--space-2);
}

.lt__city-input {
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-full);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: var(--text-base);
}

.lt__city-help {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin: 0;
}

.lt__city-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.lt__city-btn {
  width: 100%;
  text-align: left;
  padding: var(--space-2) var(--space-3);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  cursor: pointer;
}
</style>
