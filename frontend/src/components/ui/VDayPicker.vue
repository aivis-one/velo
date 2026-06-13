<!--
  VELO Frontend -- VDayPicker Component (master notifications schedule)

  Day-of-week selector: a row of seven circular toggles (ПН…ВС). A selected day
  is a filled primary circle; an unselected one is an outline. Multi-select,
  Mon-first.

  Introduced for the master «График уведомлений» block (operator SVG
  «6 Notifications 3»). Reusable: any future "which days" setting should use this.

  Usage:
    <VDayPicker v-model="days" />   // days: string[] of 'mon'..'sun'
-->
<template>
  <div class="v-day-picker" role="group" :aria-label="ariaLabel || 'Дни недели'">
    <button
      v-for="d in DAYS"
      :key="d.value"
      type="button"
      class="v-day-picker__day"
      :class="{ 'v-day-picker__day--on': isOn(d.value) }"
      :aria-pressed="isOn(d.value)"
      :aria-label="d.full"
      @click="toggle(d.value)"
    >
      {{ d.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    /** Selected day codes, e.g. ['mon','wed','fri']. */
    modelValue?: string[]
    ariaLabel?: string
  }>(),
  {
    modelValue: () => [],
    ariaLabel: '',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

interface Day {
  value: string
  label: string
  full: string
}

// Mon-first, matching the calendar / onboarding week convention.
const DAYS: Day[] = [
  { value: 'mon', label: 'ПН', full: 'Понедельник' },
  { value: 'tue', label: 'ВТ', full: 'Вторник' },
  { value: 'wed', label: 'СР', full: 'Среда' },
  { value: 'thu', label: 'ЧТ', full: 'Четверг' },
  { value: 'fri', label: 'ПТ', full: 'Пятница' },
  { value: 'sat', label: 'СБ', full: 'Суббота' },
  { value: 'sun', label: 'ВС', full: 'Воскресенье' },
]

function isOn(value: string): boolean {
  return props.modelValue.includes(value)
}

function toggle(value: string): void {
  const next = isOn(value)
    ? props.modelValue.filter((v) => v !== value)
    : [...props.modelValue, value]
  // Emit in canonical Mon→Sun order regardless of click sequence.
  emit(
    'update:modelValue',
    DAYS.map((d) => d.value).filter((v) => next.includes(v)),
  )
}
</script>

<style scoped>
.v-day-picker {
  display: flex;
  gap: var(--space-2);
  justify-content: space-between;
}

.v-day-picker__day {
  flex-shrink: 0;
  width: 42px;
  height: 42px;
  padding: 0;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  letter-spacing: 0.02em;
  color: var(--velo-text-primary);
  background: transparent;
  border: 1.5px solid var(--velo-border);
  cursor: pointer;
  transition:
    background-color var(--transition-base),
    border-color var(--transition-base),
    color var(--transition-base);
}

.v-day-picker__day--on {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: var(--velo-white);
}
</style>
