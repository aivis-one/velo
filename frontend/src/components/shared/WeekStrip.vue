<!--
  VELO Frontend -- WeekStrip (Calendar iteration, frame 1)

  Horizontal week selector for the Calendar screen:
    - 7 day pills (Mon..Sun): weekday label + day number + dot marker
      (marker shown when that day has at least one practice)
    - Selected day filled with the primary color
    - Prev / next week arrows below the strip

  Dumb component: the parent (CalendarView via useCalendarStore) owns the
  week data and selection. This just renders and emits.

  Usage:
    <WeekStrip
      :days="store.days"
      :selected-date="store.selectedDate"
      :days-with-practices="store.daysWithPractices"
      :local-date-key="store.localDateKey"
      :can-go-prev="store.canGoPrev"
      @select-day="store.selectDay"
      @prev-week="store.prevWeek"
      @next-week="store.nextWeek"
    />
-->

<template>
  <div class="week-strip">
    <div class="week-strip__days">
      <button
        v-for="cell in cells"
        :key="cell.key"
        type="button"
        class="week-strip__day"
        :class="{ 'week-strip__day--active': cell.key === selectedDate }"
        @click="$emit('select-day', cell.key)"
      >
        <span class="week-strip__weekday">{{ cell.weekday }}</span>
        <span class="week-strip__num">{{ cell.num }}</span>
        <span
          class="week-strip__dot"
          :class="{ 'week-strip__dot--visible': cell.hasPractices }"
        />
      </button>
    </div>

    <div class="week-strip__nav">
      <button
        type="button"
        class="week-strip__arrow"
        aria-label="Предыдущая неделя"
        :disabled="!canGoPrev"
        @click="$emit('prev-week')"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path
            d="M15 18l-6-6 6-6"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
      <button
        type="button"
        class="week-strip__arrow"
        aria-label="Следующая неделя"
        @click="$emit('next-week')"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path
            d="M9 18l6-6-6-6"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  /** The 7 day-Dates of the current window (today-anchored). */
  days: Date[]
  /** Selected day key (YYYY-MM-DD, local). */
  selectedDate: string
  /** Set of local-day keys that have at least one practice. */
  daysWithPractices: Set<string>
  /** Local-day key formatter (shared with the store). */
  localDateKey: (d: Date) => string
  /** Whether the prev-window arrow is enabled (false when window starts today). */
  canGoPrev: boolean
}>()

defineEmits<{
  'select-day': [dateKey: string]
  'prev-week': []
  'next-week': []
}>()

// Short Russian weekday labels, Monday-first (Date.getDay: 0=Sun..6=Sat).
const WEEKDAY_LABELS = ['ВС', 'ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']

interface Cell {
  key: string
  weekday: string
  num: number
  hasPractices: boolean
}

const cells = computed<Cell[]>(() =>
  props.days.map((d) => {
    const key = props.localDateKey(d)
    return {
      key,
      weekday: WEEKDAY_LABELS[d.getDay()]!,
      num: d.getDate(),
      hasPractices: props.daysWithPractices.has(key),
    }
  }),
)
</script>

<style scoped>
.week-strip {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.week-strip__days {
  display: flex;
  /* Figma 2266:2307 — gap между day-pills = 5px, не --space-2 (8). */
  gap: 5px;
  justify-content: space-between;
}

.week-strip__day {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  /* Figma: 44x71 rounded-15 white pill (not a full-round circle). */
  padding: var(--space-3) 0;
  border: 1px solid var(--velo-glass-border);
  background: var(--velo-white);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.week-strip__day:hover {
  opacity: 0.85;
}

.week-strip__day--active {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
}

.week-strip__weekday {
  font-family: var(--font-body);
  font-size: 10px;
  font-weight: 400;
  color: var(--velo-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.week-strip__num {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  line-height: 1.2;
}

.week-strip__day--active .week-strip__weekday,
.week-strip__day--active .week-strip__num {
  color: var(--velo-white);
}

/* Dot marker: reserves space always; visible only when day has practices. */
.week-strip__dot {
  width: 4px;
  height: 4px;
  border-radius: var(--radius-full);
  background: transparent;
}

.week-strip__dot--visible {
  background: var(--velo-primary);
}

.week-strip__day--active .week-strip__dot--visible {
  background: var(--velo-white);
}

.week-strip__nav {
  display: flex;
  justify-content: space-between;
}

.week-strip__arrow {
  width: 44px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--velo-glass-border);
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-full);
  color: var(--velo-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.week-strip__arrow:hover {
  opacity: 0.85;
}

.week-strip__arrow:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.week-strip__arrow:disabled:hover {
  opacity: 0.35;
}
</style>
