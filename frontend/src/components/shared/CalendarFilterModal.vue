<!--
  VELO Frontend -- CalendarFilterModal (Calendar iteration, frame 2)

  Filter modal for the Calendar feed. Groups (per Figma 22_Calendar filter):
    - Направление практики (direction)  -- "Все" + multi-select chips
    - Вид практики  (style)             -- dropdown (VSelect, STYLE_OPTIONS)
    - Сложность     (difficulty)        -- "Все" + multi-select chips
    - Длительность  (duration_bucket)   -- "Все" + single-select chips
    - Время         (time_of_day)       -- "Все" + single-select chips

  Works on a local DRAFT copy of the facets; nothing is applied until the
  user taps "Применить" (-> emits `apply`). "Сбросить" clears the draft.

  Usage:
    <CalendarFilterModal
      :open="showFilter"
      :filters="store.filters"
      @apply="store.applyFilters"
      @close="showFilter = false"
    />
-->

<template>
  <VModal :open="open" @close="$emit('close')">
    <div class="cal-filter">
      <h2 class="cal-filter__heading">Фильтр</h2>

      <!-- Направление практики -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Направление практики</h3>
        <div class="cal-filter__chips">
          <button
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.direction.length === 0 }"
            @click="clearArray('direction')"
          >
            Все
          </button>
          <button
            v-for="opt in DIRECTION_CHIPS"
            :key="opt.value"
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.direction.includes(opt.value) }"
            @click="toggleArray('direction', opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </section>

      <!-- Вид практики (style dropdown) -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Вид практики</h3>
        <VSelect v-model="draft.style" :options="STYLE_SELECT_OPTIONS" />
      </section>

      <!-- Сложность -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Сложность</h3>
        <div class="cal-filter__chips">
          <button
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.difficulty.length === 0 }"
            @click="clearArray('difficulty')"
          >
            Все
          </button>
          <button
            v-for="opt in DIFFICULTY_CHIPS"
            :key="opt.value"
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.difficulty.includes(opt.value) }"
            @click="toggleArray('difficulty', opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </section>

      <!-- Длительность (single-select) -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Длительность</h3>
        <div class="cal-filter__chips">
          <button
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.duration_bucket === undefined }"
            @click="clearSingle('duration_bucket')"
          >
            Все
          </button>
          <button
            v-for="opt in DURATION_CHIPS"
            :key="opt.value"
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.duration_bucket === opt.value }"
            @click="toggleSingle('duration_bucket', opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </section>

      <!-- Время (single-select) -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Время</h3>
        <div class="cal-filter__chips">
          <button
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.time_of_day === undefined }"
            @click="clearSingle('time_of_day')"
          >
            Все
          </button>
          <button
            v-for="opt in TIME_CHIPS"
            :key="opt.value"
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.time_of_day === opt.value }"
            @click="toggleSingle('time_of_day', opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </section>

      <!-- Actions -->
      <div class="cal-filter__actions">
        <VButton variant="secondary" block @click="onReset">Сбросить</VButton>
        <VButton variant="primary" block @click="onApply">Применить</VButton>
      </div>
    </div>
  </VModal>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { VModal, VButton, VSelect } from '@/components/ui'
import {
  DIRECTION_LABEL,
  DIFFICULTY_LABEL,
  TIME_OF_DAY_LABEL,
} from '@/utils/displayHelpers'
import { STYLE_OPTIONS } from '@/utils/practiceOptions'
import type { CalendarFacetFilters } from '@/stores/calendar'
import type {
  PracticeDirection,
  PracticeDifficulty,
  DurationBucket,
  TimeOfDay,
} from '@/api/types'

const props = defineProps<{
  open: boolean
  filters: CalendarFacetFilters
}>()

const emit = defineEmits<{
  apply: [filters: CalendarFacetFilters]
  close: []
}>()

// -- Chip option lists (label + value), values match the backend literals --
// Direction: kundalini is intentionally hidden from the chips (it belongs to
// "Вид практики" now); the value stays in the type/union, just not shown here.
const DIRECTION_CHIPS: { value: PracticeDirection; label: string }[] = (
  [
    'meditation',
    'yoga',
    'breathwork',
    'somatic',
    'tantra',
    'womens_circle',
    'mens_circle',
  ] as PracticeDirection[]
).map((v) => ({ value: v, label: DIRECTION_LABEL[v] }))

const DIFFICULTY_CHIPS: { value: PracticeDifficulty; label: string }[] = (
  ['beginner', 'medium', 'high'] as PracticeDifficulty[]
).map((v) => ({ value: v, label: DIFFICULTY_LABEL[v] }))

// Duration labels are LOCAL here (per the filter mock: "30 - 45 мин" /
// "1 час и более"). The global DURATION_BUCKET_LABEL is left untouched so
// other surfaces (cards / detail) keep their wording.
const DURATION_CHIPS: { value: DurationBucket; label: string }[] = [
  { value: 'short', label: '30 - 45 мин' },
  { value: 'long', label: '1 час и более' },
]

const TIME_CHIPS: { value: TimeOfDay; label: string }[] = (
  ['morning', 'day', 'evening', 'night'] as TimeOfDay[]
).map((v) => ({ value: v, label: TIME_OF_DAY_LABEL[v] }))

// "Вид практики" dropdown: a leading empty option = "Все" (no style filter),
// then the catalog from practiceOptions (mirrors backend allowed styles).
const STYLE_SELECT_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'Все' },
  ...STYLE_OPTIONS,
]

// -- Local draft state (arrays always defined for easy toggling) --
interface Draft {
  direction: PracticeDirection[]
  difficulty: PracticeDifficulty[]
  style: string
  duration_bucket: DurationBucket | undefined
  time_of_day: TimeOfDay | undefined
}

const draft = reactive<Draft>({
  direction: [],
  difficulty: [],
  style: '',
  duration_bucket: undefined,
  time_of_day: undefined,
})

/** Sync the draft from incoming filters whenever the modal opens. */
function syncFromProps(): void {
  draft.direction = [...(props.filters.direction ?? [])]
  draft.difficulty = [...(props.filters.difficulty ?? [])]
  draft.style = props.filters.style ?? ''
  draft.duration_bucket = props.filters.duration_bucket
  draft.time_of_day = props.filters.time_of_day
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) syncFromProps()
  },
  { immediate: true },
)

// -- Toggle helpers --
type ArrayKey = 'direction' | 'difficulty'

function toggleArray(key: ArrayKey, value: string): void {
  const arr = draft[key] as string[]
  const idx = arr.indexOf(value)
  if (idx === -1) arr.push(value)
  else arr.splice(idx, 1)
}

/** "Все" for a multi-select axis = empty the array. */
function clearArray(key: ArrayKey): void {
  ;(draft[key] as string[]).length = 0
}

type SingleKey = 'duration_bucket' | 'time_of_day'

function toggleSingle(key: SingleKey, value: DurationBucket | TimeOfDay): void {
  // Tap the active chip again to clear it (acts like an "Все" reset).
  draft[key] = (draft[key] === value ? undefined : value) as never
}

/** "Все" for a single-select axis = clear it. */
function clearSingle(key: SingleKey): void {
  draft[key] = undefined as never
}

// -- Build the facet filters object, omitting empty axes (undefined). --
function buildFilters(): CalendarFacetFilters {
  const style = draft.style.trim()
  return {
    direction: draft.direction.length ? [...draft.direction] : undefined,
    difficulty: draft.difficulty.length ? [...draft.difficulty] : undefined,
    style: style || undefined,
    duration_bucket: draft.duration_bucket,
    time_of_day: draft.time_of_day,
  }
}

function onApply(): void {
  emit('apply', buildFilters())
  emit('close')
}

function onReset(): void {
  draft.direction = []
  draft.difficulty = []
  draft.style = ''
  draft.duration_bucket = undefined
  draft.time_of_day = undefined
}
</script>

<style scoped>
.cal-filter {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.cal-filter__heading {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0;
}

.cal-filter__group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.cal-filter__label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin: 0;
}

.cal-filter__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.cal-filter__chip {
  padding: var(--space-2) var(--space-4);
  border: 1px solid #ffffff;
  background: var(--velo-glass-blue-15);
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.cal-filter__chip:hover {
  opacity: 0.85;
}

.cal-filter__chip--on {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: #ffffff;
}

.cal-filter__actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-2);
}
</style>
