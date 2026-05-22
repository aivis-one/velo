<!--
  VELO Frontend -- CalendarFilterModal (Calendar iteration, frame 2)

  Filter modal for the Calendar feed. Groups (per Figma frame 2):
    - Направление   (direction)      -- multi-select chips
    - Вид практики  (style)          -- free-text input (backend matches the
                                        free-form data.taxonomy.style string)
    - Сложность     (difficulty)     -- multi-select chips
    - Длительность  (duration_bucket)-- single-select chips (short / long)
    - Время         (time_of_day)    -- single-select chips (4 buckets)
    - Тип практики  (practice_type)  -- multi-select chips

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

      <!-- Направление -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Направление</h3>
        <div class="cal-filter__chips">
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

      <!-- Вид практики (free-form style) -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Вид практики</h3>
        <VInput v-model="draft.style" placeholder="Например, Кундалини йога" />
      </section>

      <!-- Сложность -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Сложность</h3>
        <div class="cal-filter__chips">
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

      <!-- Время (single-select, 4 buckets) -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Время</h3>
        <div class="cal-filter__chips">
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

      <!-- Тип практики -->
      <section class="cal-filter__group">
        <h3 class="cal-filter__label">Тип практики</h3>
        <div class="cal-filter__chips">
          <button
            v-for="opt in TYPE_CHIPS"
            :key="opt.value"
            type="button"
            class="cal-filter__chip"
            :class="{ 'cal-filter__chip--on': draft.practice_type.includes(opt.value) }"
            @click="toggleArray('practice_type', opt.value)"
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
import { VModal, VButton, VInput } from '@/components/ui'
import {
  DIRECTION_LABEL,
  DIFFICULTY_LABEL,
  DURATION_BUCKET_LABEL,
  TIME_OF_DAY_LABEL,
  PRACTICE_TYPE_EMOJI,
} from '@/utils/displayHelpers'
import type { CalendarFacetFilters } from '@/stores/calendar'
import type {
  PracticeDirection,
  PracticeDifficulty,
  PracticeType,
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
  ['meditation', 'yoga', 'breathwork'] as PracticeDirection[]
).map((v) => ({ value: v, label: DIRECTION_LABEL[v] }))

const DIFFICULTY_CHIPS: { value: PracticeDifficulty; label: string }[] = (
  ['beginner', 'medium', 'high'] as PracticeDifficulty[]
).map((v) => ({ value: v, label: DIFFICULTY_LABEL[v] }))

const DURATION_CHIPS: { value: DurationBucket; label: string }[] = (
  ['short', 'long'] as DurationBucket[]
).map((v) => ({ value: v, label: DURATION_BUCKET_LABEL[v] }))

const TIME_CHIPS: { value: TimeOfDay; label: string }[] = (
  ['morning', 'day', 'evening', 'night'] as TimeOfDay[]
).map((v) => ({ value: v, label: TIME_OF_DAY_LABEL[v] }))

const TYPE_LABEL: Record<PracticeType, string> = {
  live: 'Live',
  series: 'Серии',
  one_on_one: 'Личные',
  replay: 'Записи',
}
const TYPE_CHIPS: { value: PracticeType; label: string }[] = (
  ['live', 'series', 'one_on_one', 'replay'] as PracticeType[]
).map((v) => ({ value: v, label: `${PRACTICE_TYPE_EMOJI[v]} ${TYPE_LABEL[v]}` }))

// -- Local draft state (arrays always defined for easy toggling) --
interface Draft {
  direction: PracticeDirection[]
  difficulty: PracticeDifficulty[]
  practice_type: PracticeType[]
  style: string
  duration_bucket: DurationBucket | undefined
  time_of_day: TimeOfDay | undefined
}

const draft = reactive<Draft>({
  direction: [],
  difficulty: [],
  practice_type: [],
  style: '',
  duration_bucket: undefined,
  time_of_day: undefined,
})

/** Sync the draft from incoming filters whenever the modal opens. */
function syncFromProps(): void {
  draft.direction = [...(props.filters.direction ?? [])]
  draft.difficulty = [...(props.filters.difficulty ?? [])]
  draft.practice_type = [...(props.filters.practice_type ?? [])]
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
type ArrayKey = 'direction' | 'difficulty' | 'practice_type'

function toggleArray(key: ArrayKey, value: string): void {
  const arr = draft[key] as string[]
  const idx = arr.indexOf(value)
  if (idx === -1) arr.push(value)
  else arr.splice(idx, 1)
}

type SingleKey = 'duration_bucket' | 'time_of_day'

function toggleSingle(key: SingleKey, value: DurationBucket | TimeOfDay): void {
  // Tap the active chip again to clear it (acts like an "Все" reset).
  draft[key] = (draft[key] === value ? undefined : value) as never
}

// -- Build the facet filters object, omitting empty axes (undefined). --
function buildFilters(): CalendarFacetFilters {
  const style = draft.style.trim()
  return {
    direction: draft.direction.length ? [...draft.direction] : undefined,
    difficulty: draft.difficulty.length ? [...draft.difficulty] : undefined,
    practice_type: draft.practice_type.length ? [...draft.practice_type] : undefined,
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
  draft.practice_type = []
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
