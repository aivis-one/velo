<!--
  VELO Frontend -- WeekStrip (S2 P07 C23)

  7-day horizontal strip with current-day highlight + dot indicator for
  days with practices. Two arrow buttons for week navigation.
-->

<template>
  <div class="ws">
    <button
      type="button"
      class="ws__nav"
      aria-label="Предыдущая неделя"
      @click="prevWeek"
    >
      <IconArrowBack :size="18" />
    </button>
    <div class="ws__days">
      <button
        v-for="d in days"
        :key="d.iso"
        type="button"
        class="ws__day"
        :class="{
          'ws__day--active': d.iso === selectedIso,
          'ws__day--has': practiceDays.has(d.iso),
        }"
        @click="onSelect(d.iso)"
      >
        <span class="ws__weekday">{{ d.weekday }}</span>
        <span class="ws__num">{{ d.day }}</span>
        <span
          v-if="practiceDays.has(d.iso)"
          class="ws__dot"
        />
      </button>
    </div>
    <button
      type="button"
      class="ws__nav"
      aria-label="Следующая неделя"
      @click="nextWeek"
    >
      <IconArrowForward :size="18" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IconArrowBack, IconArrowForward } from '@/components/icons'

const props = defineProps<{
  selectedIso: string
  practiceDays: Set<string>
}>()

const emit = defineEmits<{ 'update:selectedIso': [iso: string] }>()

const WEEKDAY_RU = ['ВС', 'ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']

interface Day {
  iso: string
  day: number
  weekday: string
}

function isoOf(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function startOfWeek(d: Date): Date {
  const out = new Date(d)
  // Mon..Sun (Russian convention): shift so Monday is index 0.
  const dow = out.getDay() // 0=Sun..6=Sat
  const diff = (dow + 6) % 7
  out.setDate(out.getDate() - diff)
  out.setHours(0, 0, 0, 0)
  return out
}

const days = computed<Day[]>(() => {
  const start = startOfWeek(new Date(props.selectedIso))
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    return {
      iso: isoOf(d),
      day: d.getDate(),
      weekday: WEEKDAY_RU[d.getDay()] ?? '',
    }
  })
})

function onSelect(iso: string): void {
  emit('update:selectedIso', iso)
}

function prevWeek(): void {
  const d = new Date(props.selectedIso)
  d.setDate(d.getDate() - 7)
  emit('update:selectedIso', isoOf(d))
}

function nextWeek(): void {
  const d = new Date(props.selectedIso)
  d.setDate(d.getDate() + 7)
  emit('update:selectedIso', isoOf(d))
}
</script>

<style scoped>
.ws {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2);
  background: var(--surface-steel-alpha-15);
  border-radius: var(--radius-lg);
  border: 1px solid #ffffff;
}

.ws__nav {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.ws__nav:hover {
  background: var(--surface-default);
}

.ws__days {
  flex: 1;
  display: flex;
  gap: var(--space-1);
}

.ws__day {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: var(--space-2) var(--space-1);
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: var(--font-body);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  transition: background var(--transition-fast);
}

.ws__day:hover {
  background: var(--surface-default);
}

.ws__day--active {
  background: var(--steel-button);
  color: white;
}

.ws__weekday {
  font-size: var(--text-xs);
  text-transform: uppercase;
  opacity: 0.75;
}

.ws__num {
  font-size: var(--text-base);
  font-weight: 400;
}

.ws__dot {
  width: 4px;
  height: 4px;
  border-radius: var(--radius-full);
  background: var(--steel-button);
}

.ws__day--active .ws__dot {
  background: white;
}
</style>
