<!--
  VELO Frontend -- TimezoneCityPicker (Задача 2, 2026-06-09)

  Searchable city -> timezone picker (Google-Calendar-style), DS-built:
    - VInput search field (type a city) with an IconSearch suffix.
    - A DS glass list of matching cities; each row shows the current local time
      and the UTC offset (computed live via Intl, DST-aware) and an IconCheck on
      the selected one. Tapping a row selects its IANA zone.
    - Search AND manual browse in one (empty query = full list).
    - No match -> a plain "не найдено" hint (operator: keep it simple).

  v-model is the IANA zone id (what the backend stores). The master create/edit
  forms keep the compact VSelect (utils/practiceOptions TIMEZONE_OPTIONS); this
  richer picker is used on the profile + onboarding timezone screens.
-->

<template>
  <div class="tz-picker">
    <VInput v-model="query" :placeholder="placeholder" @focus="onFieldFocus">
      <template #suffix><IconSearch :size="18" /></template>
    </VInput>

    <div v-if="filtered.length" class="tz-picker__list">
      <button
        v-for="c in filtered"
        :key="c.iana + c.city"
        type="button"
        class="tz-picker__row"
        :class="{ 'tz-picker__row--active': c.iana === modelValue }"
        @click="select(c.iana)"
      >
        <span class="tz-picker__main">
          <span class="tz-picker__city">{{ c.city }}</span>
          <span class="tz-picker__zone">{{ c.iana }}</span>
        </span>
        <span class="tz-picker__meta">
          <span class="tz-picker__time">{{ timeAt(c.iana) }}</span>
          <span class="tz-picker__off">{{ formatUtcOffset(c.iana) }}</span>
        </span>
        <span v-if="c.iana === modelValue" class="tz-picker__check">
          <IconCheck :size="18" />
        </span>
      </button>
    </div>
    <p v-else class="tz-picker__empty">Город не найдено, уточните написание.</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { VInput } from '@/components/ui'
import { IconSearch, IconCheck } from '@/components/icons'
import { TIMEZONE_CITIES } from '@/utils/timezoneCities'
import { formatUtcOffset } from '@/utils/practiceOptions'
import { useKeyboardFieldScroll } from '@/composables/useKeyboardFieldScroll'

// Lift the city search above the soft keyboard once it settles (shared M5
// composable) so the field isn't left under the keyboard on focus (K3).
const { onFieldFocus } = useKeyboardFieldScroll()

withDefaults(
  defineProps<{
    /** Selected IANA zone id (what the backend stores). */
    modelValue?: string
    placeholder?: string
  }>(),
  {
    modelValue: '',
    placeholder: 'Ваш город (Берлин, London)…',
  },
)

const emit = defineEmits<{ 'update:modelValue': [iana: string] }>()

const query = ref('')

const filtered = computed(() => {
  const t = query.value.trim().toLowerCase()
  if (!t) return TIMEZONE_CITIES
  return TIMEZONE_CITIES.filter((c) => c.city.toLowerCase().includes(t) || c.q.includes(t))
})

/** Current local time in the given zone ("14:35"), live + DST-aware. */
function timeAt(iana: string): string {
  try {
    return new Intl.DateTimeFormat('ru', {
      timeZone: iana,
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date())
  } catch {
    return ''
  }
}

function select(iana: string): void {
  emit('update:modelValue', iana)
}
</script>

<style scoped>
.tz-picker {
  display: flex;
  flex-direction: column;
}

.tz-picker__list {
  margin-top: var(--space-2);
  max-height: 320px;
  overflow-y: auto;
  scrollbar-width: none;
  /* Crisp white plate (was murky glass-blue over the photo bg, operator 2026-06-19). */
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
}

.tz-picker__list::-webkit-scrollbar {
  display: none;
}

.tz-picker__row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  font-family: var(--font-body);
}

.tz-picker__row + .tz-picker__row {
  border-top: 1px solid var(--velo-border-light);
}

.tz-picker__row--active {
  background: var(--velo-glass-blue-15);
}

.tz-picker__main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.tz-picker__city {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.tz-picker__zone {
  font-size: var(--text-12);
  color: var(--velo-text-secondary);
}

.tz-picker__meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex-shrink: 0;
}

.tz-picker__time {
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
}

.tz-picker__off {
  font-size: var(--text-12);
  color: var(--velo-text-secondary);
}

.tz-picker__check {
  display: inline-flex;
  align-items: center;
  color: var(--velo-teal-600);
  flex-shrink: 0;
}

.tz-picker__empty {
  margin: var(--space-3) 0 0;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  text-align: center;
}
</style>
