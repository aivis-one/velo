<!--
  VELO Frontend -- CalendarFilterModal (Calendar iteration, F-8)

  Filter modal for the Calendar feed. Groups (per Figma 22_Calendar filter):
    - Направление практики (direction)  -- SINGLE-select chips (incl. "Все")
    - Вид практики        (style)       -- MULTI-select chips, shown ONLY when
                                            the current direction has styles
                                            (meditation / yoga / circles)
    - Сложность           (difficulty)  -- "Все" + multi-select chips
    - Длительность        (duration_bucket) -- "Все" + single-select chips
    - Время               (time_of_day) -- "Все" + single-select chips

  F-8 (2026-05-29):
    1. No "Применить" button — every chip click immediately emits `apply`.
       Modal stays open; user closes via the X (VModal close emit) when done.
    2. Style switched from VSelect dropdown to multi-select chips (same UX
       as direction/difficulty). Requires backend B-4 (style: list[str]).
    3. "Сбросить" clears all axes (also emits apply via the auto-apply path).

  Why direction is single-select (2026-05-28): styles are
  direction-conditional (см. utils/practiceOptions STYLE_OPTIONS_BY_DIRECTION),
  so showing a meaningful style picker requires knowing the single direction.
  Type CalendarFacetFilters.direction stays as PracticeDirection[] for
  backend compatibility — we just always send 0 or 1 element.

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

      <!-- Направление практики (single-select) -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Направление практики</h3>
        <div class="cal-filter__chips">
          <button
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': selectedDirection === undefined }"
            @click="clearDirection"
          >
            Все
          </button>
          <button
            v-for="opt in DIRECTION_CHIPS"
            :key="opt.value"
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': selectedDirection === opt.value }"
            @click="setDirection(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </section>

      <!-- Вид практики (direction-dependent multi-select chips) -->
      <section v-if="styleOptions.length > 0" class="cal-filter__group">
        <h3 class="cal-filter__label">Вид практики</h3>
        <div class="cal-filter__chips">
          <button
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.style.length === 0 }"
            @click="clearStyle"
          >
            Все
          </button>
          <button
            v-for="opt in styleOptions"
            :key="opt.value"
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.style.includes(opt.value) }"
            @click="toggleStyle(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </section>

      <!-- Сложность -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Сложность</h3>
        <div class="cal-filter__chips">
          <button
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.difficulty.length === 0 }"
            @click="clearDifficulty"
          >
            Все
          </button>
          <button
            v-for="opt in DIFFICULTY_CHIPS"
            :key="opt.value"
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.difficulty.includes(opt.value) }"
            @click="toggleDifficulty(opt.value)"
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

      <!-- F-8: Только «Сбросить». «Применить» удалён — каждое нажатие на
           чип уже эмитит apply. Закрыть модалку = X в VModal-шапке. -->
      <div class="cal-filter__actions">
        <VButton variant="secondary" block @click="onReset">Сбросить</VButton>
      </div>
    </div>
  </VModal>
</template>

<script setup lang="ts">
import { reactive, watch, computed } from 'vue'
import { VModal, VButton } from '@/components/ui'
import {
  DIRECTION_LABEL,
  DIFFICULTY_LABEL,
  TIME_OF_DAY_LABEL,
} from '@/utils/displayHelpers'
import { stylesForDirection } from '@/utils/practiceOptions'
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
const DIRECTION_CHIPS: { value: PracticeDirection; label: string }[] = (
  [
    'meditation',
    'yoga',
    'breathwork',
    'somatic',
    'tantra',
    'circles',
    'sound_healing',
    'art',
    'narrative',
    'movement',
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

// -- Local draft state (single direction; array kept for type compat) --
// F-8: style now multi-select (array). buildFilters omits empty axes.
interface Draft {
  direction: PracticeDirection[]
  difficulty: PracticeDifficulty[]
  style: string[]
  duration_bucket: DurationBucket | undefined
  time_of_day: TimeOfDay | undefined
}

const draft = reactive<Draft>({
  direction: [],
  difficulty: [],
  style: [],
  duration_bucket: undefined,
  time_of_day: undefined,
})

/** Convenience accessor: the single selected direction, or undefined for "Все". */
const selectedDirection = computed<PracticeDirection | undefined>(() =>
  draft.direction[0],
)

/** Style options for the currently selected direction (empty when "Все"
 *  or when the direction has no styles). */
const styleOptions = computed(() => stylesForDirection(selectedDirection.value))

/** Sync the draft from incoming filters whenever the modal opens. */
function syncFromProps(): void {
  const incoming = props.filters.direction ?? []
  const first = incoming[0]
  draft.direction = first !== undefined ? [first] : []
  draft.difficulty = [...(props.filters.difficulty ?? [])]
  draft.style = [...(props.filters.style ?? [])]
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

// -- Build the facet filters object, omitting empty axes (undefined). --
function buildFilters(): CalendarFacetFilters {
  return {
    direction: draft.direction.length ? [...draft.direction] : undefined,
    difficulty: draft.difficulty.length ? [...draft.difficulty] : undefined,
    style: draft.style.length ? [...draft.style] : undefined,
    duration_bucket: draft.duration_bucket,
    time_of_day: draft.time_of_day,
  }
}

/** F-8: apply current draft immediately. Modal stays open. */
function applyNow(): void {
  emit('apply', buildFilters())
}

// -- Direction (single-select) --
function setDirection(value: PracticeDirection): void {
  if (draft.direction[0] === value) {
    // Tap the active chip again to clear it (acts like "Все" reset).
    draft.direction = []
  } else {
    draft.direction = [value]
  }
  // Selected direction changed -> the previous styles might be invalid for
  // the new direction; clear them. (The style chips section also disappears
  // if the new direction has no styles.)
  draft.style = []
  applyNow()
}

function clearDirection(): void {
  draft.direction = []
  draft.style = []
  applyNow()
}

// -- Style (multi-select) --
function toggleStyle(value: string): void {
  const idx = draft.style.indexOf(value)
  if (idx === -1) draft.style.push(value)
  else draft.style.splice(idx, 1)
  applyNow()
}

function clearStyle(): void {
  draft.style = []
  applyNow()
}

// -- Difficulty (multi-select) --
function toggleDifficulty(value: PracticeDifficulty): void {
  const idx = draft.difficulty.indexOf(value)
  if (idx === -1) draft.difficulty.push(value)
  else draft.difficulty.splice(idx, 1)
  applyNow()
}

function clearDifficulty(): void {
  draft.difficulty = []
  applyNow()
}

// -- Single-select axes (duration_bucket / time_of_day) --
type SingleKey = 'duration_bucket' | 'time_of_day'

function toggleSingle(key: SingleKey, value: DurationBucket | TimeOfDay): void {
  draft[key] = (draft[key] === value ? undefined : value) as never
  applyNow()
}

function clearSingle(key: SingleKey): void {
  draft[key] = undefined as never
  applyNow()
}

/** F-8: "Сбросить" clears every axis then applies (lenta returns full feed).
 *  Modal stays open — user closes via X when done. */
function onReset(): void {
  draft.direction = []
  draft.difficulty = []
  draft.style = []
  draft.duration_bucket = undefined
  draft.time_of_day = undefined
  applyNow()
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
