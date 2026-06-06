<!--
  VELO Frontend -- CalendarPracticeCard (DS, 2026-05)

  Thin wrapper around the shared PracticeListCard. Adds calendar-list-specific
  metadata (time + duration) and a paid/free badge derived from the practice.

  Layout / spacing live in PracticeListCard.vue (DS).

  Usage:
    <CalendarPracticeCard :practice="p" @click="goToDetail" />
-->

<template>
  <PracticeListCard
    :practice="practice"
    :when="time"
    :duration="duration"
    @click="$emit('click', practice.id)"
  >
    <template #badge>
      <span class="cal-card__badge" :class="`cal-card__badge--${badge.variant}`">
        <IconCheck v-if="badge.variant === 'paid'" :size="12" />
        {{ badge.label }}
      </span>
    </template>
  </PracticeListCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatShortDate, formatTime, formatDuration, formatMoney } from '@/utils/format'
import { IconCheck } from '@/components/icons'
import PracticeListCard from '@/components/shared/PracticeListCard.vue'
import { useViewerTimezone } from '@/composables/useViewerTimezone'
import type { PracticeResponse } from '@/api/types'

const props = withDefaults(
  defineProps<{
    practice: PracticeResponse
    /** Показать дату+время вместо только времени. Календарь группирует по дню,
     *  поэтому там дата не нужна (default). На странице мастера практики идут
     *  в разные дни — там показываем дату (showDate). */
    showDate?: boolean
  }>(),
  { showDate: false },
)

defineEmits<{
  click: [id: string]
}>()

// F5: render the time in the viewer's own profile timezone (the profile decides).
const viewerTz = useViewerTimezone()

// Под иконкой (when): короткая дата (showDate, страница мастера — практики идут
// в разные дни) либо только время (календарь — уже сгруппирован по дню).
const time = computed(() =>
  props.showDate
    ? formatShortDate(props.practice.scheduled_at, viewerTz.value)
    : formatTime(props.practice.scheduled_at, viewerTz.value),
)

// Мета-ячейка длительности. На странице мастера (showDate) под иконкой стоит
// ДАТА, поэтому время суток складываем сюда: «09:00 · 1 ч 15 мин» — иначе
// практики одного дня в разное время были бы неразличимы. В календаре время
// уже под иконкой, поэтому остаётся только длительность.
const duration = computed(() => {
  const dur = formatDuration(props.practice.duration_minutes)
  if (!props.showDate) return dur
  return `${formatTime(props.practice.scheduled_at, viewerTz.value)} · ${dur}`
})

// Badge: paid (teal) > free (blue) > price (blue).
interface Badge {
  label: string
  variant: 'paid' | 'free'
}

const badge = computed<Badge>(() => {
  if (props.practice.is_paid) {
    return { label: 'Оплачено', variant: 'paid' }
  }
  if (props.practice.is_free) {
    return { label: 'Бесплатно', variant: 'free' }
  }
  return {
    label: formatMoney(props.practice.price_cents, props.practice.currency),
    variant: 'free',
  }
})
</script>

<style scoped>
.cal-card__badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 4px 10px;
  border-radius: var(--velo-radius-badge);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  white-space: nowrap;
}

/* Paid -- teal (matches the "done"/"today" tone elsewhere) */
.cal-card__badge--paid {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-700);
}

/* Free / price -- blue */
.cal-card__badge--free {
  background: var(--velo-blue-100);
  color: var(--velo-primary);
}
</style>
