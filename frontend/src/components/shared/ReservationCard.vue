<!--
  VELO Frontend — ReservationCard (S2-S3 SPEEDRUN MEGA-2 §C52)

  Booking card with practice icon + name + time + status chip.
-->

<template>
  <button
    type="button"
    class="rc"
    @click="$emit('click')"
  >
    <span class="rc__icon">
      <component
        :is="icon"
        :size="22"
      />
    </span>
    <span class="rc__body">
      <span class="rc__title">{{ booking.practice.title }}</span>
      <span class="rc__sub">с {{ booking.practice.master_name ?? 'Мастером' }}</span>
      <span class="rc__time">{{ humanTime(booking.practice.scheduled_at) }}</span>
    </span>
    <span
      class="rc__chip"
      :class="`rc__chip--${chip.variant}`"
    >
      {{ chip.label }}
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import {
  IconMeditation,
  IconBreathwork,
  IconProfile,
  IconGroup,
} from '@/components/icons'
import type { BookingWithPracticeResponse } from '@/api/types'

const props = defineProps<{
  booking: BookingWithPracticeResponse
  chip: { label: string; variant: 'amber' | 'mint' | 'pink' | 'gray' }
}>()

defineEmits<{ (e: 'click'): void }>()

const ICONS: Record<string, Component> = {
  live: IconMeditation,
  series: IconBreathwork,
  one_on_one: IconProfile,
  replay: IconGroup,
}

const icon = computed(
  () => ICONS[props.booking.practice.practice_type] ?? IconMeditation,
)

function humanTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}
</script>

<style scoped>
.rc {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.rc__icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-steel-alpha-15);
  border: 1px solid var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}

.rc__body {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.rc__title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rc__sub {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.rc__time {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.rc__chip {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-family: var(--font-body);
  border: 1px solid var(--text-primary);
}

.rc__chip--amber {
  background: var(--warm-deep, var(--surface-steel-alpha-15));
  color: white;
  border-color: var(--warm-deep, var(--text-primary));
}

.rc__chip--mint {
  background: var(--mint-primary, var(--surface-steel-alpha-15));
  color: white;
  border-color: var(--mint-primary, var(--text-primary));
}

.rc__chip--pink {
  background: var(--pink-primary, var(--surface-steel-alpha-15));
  color: white;
  border-color: var(--pink-primary, var(--text-primary));
}

.rc__chip--gray {
  background: var(--surface-default);
  color: var(--text-secondary);
}
</style>
