<!--
  VELO Frontend -- PracticeCard Component (Phase F3.1)

  Practice card for catalog lists (Dashboard, Calendar).
  Matches mockup .practice-card layout: emoji + title + master,
  date/time + duration, price + participants, status badge.

  Clicking the card navigates to /user/practices/:id.

  Usage:
    <PracticeCard :practice="item" @click="onCardClick(item.id)" />
-->

<template>
  <div class="practice-card" @click="$emit('click', practice.id)">
    <!-- Header: emoji + title + master -->
    <div class="practice-card__header">
      <span class="practice-card__emoji">{{ typeEmoji }}</span>
      <div class="practice-card__info">
        <h4 class="practice-card__title">{{ practice.title }}</h4>
        <p class="practice-card__master">
          {{ practice.master_name ?? 'Мастер' }}
        </p>
      </div>
      <VBadge v-if="practice.status === 'live'" variant="success">
        LIVE
      </VBadge>
    </div>

    <!-- Meta: date, time, duration -->
    <div class="practice-card__meta">
      <span class="practice-card__meta-item">
        🕐 {{ time }}
      </span>
      <span class="practice-card__meta-item">
        ⏱️ {{ duration }}
      </span>
    </div>

    <!-- Footer: price + participants -->
    <div class="practice-card__footer">
      <span class="practice-card__price" :class="{ 'practice-card__price--free': practice.is_free }">
        {{ price }}
      </span>
      <span class="practice-card__spots" :class="{ 'practice-card__spots--full': full }">
        {{ participants }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VBadge } from '@/components/ui'
import { formatMoney, formatTime, formatDuration, formatParticipants, isFull } from '@/utils/format'
import type { PracticeResponse, PracticeType } from '@/api/types'

const props = defineProps<{
  practice: PracticeResponse
}>()

defineEmits<{
  click: [id: string]
}>()

// -- Type → Emoji mapping --
const TYPE_EMOJI: Record<PracticeType, string> = {
  live: '🧘',
  series: '🔄',
  one_on_one: '👤',
  replay: '📹',
}

const typeEmoji = computed(() => TYPE_EMOJI[props.practice.practice_type] ?? '🧘')

const time = computed(() =>
  formatTime(props.practice.scheduled_at, props.practice.timezone),
)

const duration = computed(() =>
  formatDuration(props.practice.duration_minutes),
)

const price = computed(() =>
  formatMoney(props.practice.price_cents, props.practice.currency),
)

const participants = computed(() =>
  formatParticipants(props.practice.current_participants, props.practice.max_participants),
)

const full = computed(() =>
  isFull(props.practice.current_participants, props.practice.max_participants),
)
</script>

<style scoped>
.practice-card {
  background: white;
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  transition: all 0.2s;
}

.practice-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(51, 77, 110, 0.12);
}

.practice-card:active {
  transform: translateY(0);
}

.practice-card__header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.practice-card__emoji {
  font-size: 36px;
  line-height: 1;
  flex-shrink: 0;
}

.practice-card__info {
  flex: 1;
  min-width: 0;
}

.practice-card__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0 0 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.practice-card__master {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  margin: 0;
}

.practice-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.practice-card__meta-item {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
}

.practice-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.practice-card__price {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--velo-text-primary);
}

.practice-card__price--free {
  color: var(--velo-success, #16A34A);
}

.practice-card__spots {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

.practice-card__spots--full {
  color: var(--velo-error, #DC2626);
  font-weight: 600;
}
</style>
