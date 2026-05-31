<!--
  VELO Frontend -- CalendarPracticeCard (DS, 2026-05)

  Thin wrapper around the shared PracticeListCard. Adds calendar-list-specific
  metadata (time + duration) and a paid/free badge derived from the practice.

  Layout / spacing live in PracticeListCard.vue (DS).

  Usage:
    <CalendarPracticeCard :practice="p" @click="goToDetail" />
-->

<template>
  <PracticeListCard :practice="practice" @click="$emit('click', practice.id)">
    <template #meta-left>
      <span class="plc-meta-item">
        <IconCalendar :size="14" /> {{ time }}
      </span>
      <span class="plc-meta-item">
        <IconClock :size="14" /> {{ duration }}
      </span>
    </template>
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
import { formatTime, formatDuration, formatMoney } from '@/utils/format'
import { IconCheck, IconCalendar, IconClock } from '@/components/icons'
import PracticeListCard from '@/components/shared/PracticeListCard.vue'
import { useViewerTimezone } from '@/composables/useViewerTimezone'
import type { PracticeResponse } from '@/api/types'

const props = defineProps<{
  practice: PracticeResponse
}>()

defineEmits<{
  click: [id: string]
}>()

// F5: render the time in the viewer's own profile timezone (the profile decides).
const viewerTz = useViewerTimezone()

const time = computed(() =>
  formatTime(props.practice.scheduled_at, viewerTz.value),
)

const duration = computed(() => formatDuration(props.practice.duration_minutes))

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
  border-radius: 5px;
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
