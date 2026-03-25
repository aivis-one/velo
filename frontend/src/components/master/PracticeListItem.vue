<!--
  VELO Frontend -- PracticeListItem Component (Phase F6)

  Reusable practice card for master-facing lists (MasterPracticesView,
  dashboard nearest practice). Matches mockup .practice-card layout.

  Shows: type emoji, title, date/time + duration, participants, price,
  status badge.

  Optional #action slot for extra buttons (e.g. "Явка" in past tab).
  Not clickable itself -- parent wraps it in a click handler.
-->

<template>
  <div class="pli">
    <div class="pli__header">
      <span class="pli__icon">{{ typeEmoji }}</span>
      <div class="pli__info">
        <div class="pli__title">{{ practice.title }}</div>
        <div class="pli__meta">
          {{ formatDate(practice.scheduled_at, practice.timezone) }}
          · {{ formatDuration(practice.duration_minutes) }}
        </div>
      </div>
      <VBadge :variant="statusVariant">{{ statusLabel }}</VBadge>
    </div>

    <div class="pli__details">
      <span>👥 {{ formatParticipants(practice.current_participants, practice.max_participants) }}</span>
      <span>{{ formatMoney(practice.price_cents, practice.currency) }}</span>
    </div>

    <!-- Optional action slot (e.g. attendance button) -->
    <div v-if="$slots.action" class="pli__actions" @click.stop>
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VBadge } from '@/components/ui'
import { formatDate, formatDuration, formatMoney, formatParticipants } from '@/utils/format'
import { PRACTICE_TYPE_EMOJI } from '@/utils/displayHelpers'
import type { PracticeResponse, PracticeStatus } from '@/api/types'

const props = defineProps<{
  practice: PracticeResponse
}>()

// -- Type emoji -- imported from displayHelpers
const typeEmoji = computed((): string => PRACTICE_TYPE_EMOJI[props.practice.practice_type] ?? '🧘')

// -- Status label --
const STATUS_LABEL: Record<PracticeStatus, string> = {
  draft: 'Черновик',
  scheduled: 'Запланирована',
  live: 'В эфире',
  completed: 'Завершена',
  cancelled: 'Отменена',
  deleted: 'Удалена',
}

const statusLabel = computed((): string => STATUS_LABEL[props.practice.status] ?? props.practice.status)

// -- Status badge variant --
const statusVariant = computed((): 'success' | 'warning' | 'error' | 'info' => {
  switch (props.practice.status) {
    case 'live':      return 'success'
    case 'scheduled': return 'info'
    case 'draft':     return 'warning'
    case 'completed': return 'info'
    default:          return 'error'
  }
})
</script>

<style scoped>
.pli {
  background: var(--velo-bg-card);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  transition: opacity var(--transition-fast);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.pli:active {
  opacity: 0.8;
}

.pli__header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
}

.pli__icon {
  font-size: 22px;
  flex-shrink: 0;
  line-height: 1.2;
}

.pli__info {
  flex: 1;
  min-width: 0;
}

.pli__title {
  font-family: var(--font-body);
  font-weight: 400;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pli__meta {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-muted);
  margin-top: 2px;
}

.pli__details {
  display: flex;
  gap: var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.pli__actions {
  display: flex;
  gap: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px solid var(--velo-border-light);
}
</style>
