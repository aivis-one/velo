<!--
  VELO Frontend — DiaryFilterOverlay (S2-S3 SPEEDRUN MEGA-2 §C37)

  Modal slide-up overlay. Header with IconFilter circle + "Фильтр" + IconClose.
  "Выбрать дату" pill button → expand month grid (single + range select).
  Type chip group (Все / Дневник / Сонник / Feedbacks / Check-ins) — single-select.
  "Применить" pill closes overlay; chip selects apply immediately to store.
-->

<template>
  <Teleport to="body">
    <div
      class="filter"
      role="dialog"
      aria-modal="true"
    >
      <div
        class="filter__backdrop"
        @click="$emit('close')"
      />
      <div class="filter__panel">
        <header class="filter__head">
          <div class="filter__icon-wrap">
            <IconFilter :size="18" />
          </div>
          <h2 class="filter__title">
            Фильтр
          </h2>
          <button
            type="button"
            class="filter__close"
            aria-label="Закрыть"
            @click="$emit('close')"
          >
            <IconClose :size="20" />
          </button>
        </header>

        <button
          type="button"
          class="filter__date-pill"
          @click="datePickerOpen = !datePickerOpen"
        >
          <span>{{ dateLabel }}</span>
          <IconChevronDown
            :size="20"
            :style="{ transform: datePickerOpen ? 'rotate(180deg)' : 'none' }"
          />
        </button>

        <div
          v-if="datePickerOpen"
          class="filter__date-picker"
        >
          <div class="filter__month-head">
            <button
              type="button"
              class="filter__month-nav"
              aria-label="Предыдущий месяц"
              @click="shiftMonth(-1)"
            >
              ‹
            </button>
            <span class="filter__month-label">{{ monthLabel }}</span>
            <button
              type="button"
              class="filter__month-nav"
              aria-label="Следующий месяц"
              @click="shiftMonth(1)"
            >
              ›
            </button>
          </div>
          <div class="filter__weekdays">
            <span
              v-for="d in WEEKDAYS"
              :key="d"
              class="filter__weekday"
            >{{ d }}</span>
          </div>
          <div class="filter__days">
            <button
              v-for="cell in monthCells"
              :key="cell.iso || cell.label"
              type="button"
              class="filter__day"
              :class="{
                'filter__day--filled': cell.iso === '',
                'filter__day--selected': isSelected(cell.iso),
                'filter__day--in-range': isInRange(cell.iso),
              }"
              :disabled="!cell.iso"
              @click="cell.iso && pickDay(cell.iso)"
            >
              {{ cell.label }}
            </button>
          </div>
        </div>

        <div class="filter__chips">
          <button
            v-for="opt in TYPE_OPTIONS"
            :key="opt.value"
            type="button"
            class="filter__chip"
            :class="{ 'filter__chip--active': diary.typeFilter === opt.value }"
            @click="setType(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>

        <button
          type="button"
          class="filter__apply"
          @click="$emit('close')"
        >
          Применить
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { IconFilter, IconClose, IconChevronDown } from '@/components/icons'
import { useDiaryStore } from '@/stores/diary'

defineEmits<{ (e: 'close'): void }>()

const diary = useDiaryStore()

const WEEKDAYS = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
const TYPE_OPTIONS = [
  { value: 'all', label: 'Все' },
  { value: 'journal', label: 'Дневник' },
  { value: 'dream', label: 'Сонник' },
  { value: 'insight', label: 'Insights' },
] as const

const datePickerOpen = ref(false)
const monthCursor = ref(new Date())
const rangeStart = ref<string | null>(null)
const rangeEnd = ref<string | null>(null)

const monthLabel = computed(() => {
  return monthCursor.value.toLocaleDateString('ru-RU', {
    month: 'long',
    year: 'numeric',
  })
})

const dateLabel = computed(() => {
  if (rangeStart.value && rangeEnd.value) {
    return `${rangeStart.value} — ${rangeEnd.value}`
  }
  if (rangeStart.value) return rangeStart.value
  return 'Выбрать дату'
})

interface DayCell {
  iso: string
  label: string
}

const monthCells = computed<DayCell[]>(() => {
  const y = monthCursor.value.getFullYear()
  const m = monthCursor.value.getMonth()
  const first = new Date(y, m, 1)
  const last = new Date(y, m + 1, 0)
  const offset = (first.getDay() + 6) % 7 // Monday-first

  const cells: DayCell[] = []
  for (let i = 0; i < offset; i++) {
    cells.push({ iso: '', label: '' })
  }
  for (let d = 1; d <= last.getDate(); d++) {
    const iso = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    cells.push({ iso, label: String(d) })
  }
  return cells
})

function shiftMonth(delta: number): void {
  const d = new Date(monthCursor.value)
  d.setMonth(d.getMonth() + delta)
  monthCursor.value = d
}

function pickDay(iso: string): void {
  if (!rangeStart.value || (rangeStart.value && rangeEnd.value)) {
    rangeStart.value = iso
    rangeEnd.value = null
    return
  }
  if (rangeStart.value && !rangeEnd.value) {
    if (iso < rangeStart.value) {
      rangeEnd.value = rangeStart.value
      rangeStart.value = iso
    } else {
      rangeEnd.value = iso
    }
  }
}

function isSelected(iso: string): boolean {
  return iso === rangeStart.value || iso === rangeEnd.value
}

function isInRange(iso: string): boolean {
  if (!rangeStart.value || !rangeEnd.value) return false
  return iso > rangeStart.value && iso < rangeEnd.value
}

function setType(v: typeof TYPE_OPTIONS[number]['value']): void {
  diary.typeFilter = v
}
</script>

<style scoped>
.filter {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: flex-end;
  justify-content: stretch;
}

.filter__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
}

.filter__panel {
  position: relative;
  background: var(--surface-default);
  border-top-left-radius: var(--radius-lg);
  border-top-right-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.filter__head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.filter__icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--surface-steel-alpha-15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}

.filter__title {
  flex: 1 1 auto;
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.filter__close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filter__date-pill {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
}

.filter__date-picker {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
}

.filter__month-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filter__month-nav {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 18px;
}

.filter__month-label {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  text-transform: capitalize;
  color: var(--text-primary);
}

.filter__weekdays,
.filter__days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.filter__weekday {
  text-align: center;
  font-size: var(--text-xs);
  color: var(--text-secondary);
  padding: 4px 0;
}

.filter__day {
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 0;
  border-radius: 50%;
  color: var(--text-primary);
  cursor: pointer;
  font-size: var(--text-sm);
  font-family: var(--font-body);
}

.filter__day:disabled {
  cursor: default;
}

.filter__day--filled {
  background: transparent;
}

.filter__day--selected {
  background: var(--steel-button);
  color: white;
}

.filter__day--in-range {
  background: var(--surface-steel-alpha-15);
}

.filter__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.filter__chip {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.filter__chip--active {
  background: var(--steel-button);
  color: white;
  border-color: var(--steel-button);
}

.filter__apply {
  width: 100%;
  padding: var(--space-3);
  background: var(--steel-button);
  color: white;
  border: 0;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 500;
}
</style>
