<!--
  VELO Frontend -- CalendarPracticeCard (Calendar iteration, frame 1)

  Practice card for the Calendar day list. Built on the BookingCard visual
  language (icon-in-circle, master + verified, meta row, badge) but bound to
  a full PracticeResponse from the public feed.

  Badge (BookingCard style, agreed):
    - is_paid       -> "Оплачено"  (teal)
    - else is_free  -> "Бесплатно" (blue)
    - else          -> price        (blue)

  Dumb component: parent owns navigation. Emits `click` with the practice id.

  Usage:
    <CalendarPracticeCard :practice="p" @click="goToDetail" />
-->

<template>
  <!-- Layout по Figma 2266:2307: card 336×104 фиксированной высоты,
       icon absolute слева, title и master row центрированы,
       footer (meta + badge) внизу. -->
  <div class="cal-card" @click="$emit('click', practice.id)">
    <span class="cal-card__icon">
      <component :is="typeIcon" :size="46" />
    </span>

    <h4 class="cal-card__title">{{ practice.title }}</h4>

    <p class="cal-card__master">
      <span class="cal-card__master-avatar">{{ masterInitial }}</span>
      <span class="cal-card__master-name">
        {{ practice.master_name ?? 'Мастер' }}
      </span>
      <span class="cal-card__verified"><IconCheck :size="11" /></span>
    </p>

    <div class="cal-card__footer">
      <span class="cal-card__meta">
        <span class="cal-card__meta-item">
          <IconCalendar :size="14" /> {{ time }}
        </span>
        <span class="cal-card__meta-item">
          <IconClock :size="14" /> {{ duration }}
        </span>
      </span>

      <span class="cal-card__badge" :class="`cal-card__badge--${badge.variant}`">
        <IconCheck v-if="badge.variant === 'paid'" :size="12" />
        {{ badge.label }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatTime, formatDuration, formatMoney } from '@/utils/format'
import {
  IconCheck,
  IconCalendar,
  IconClock,
} from '@/components/icons'
import { practiceIconFor } from '@/utils/displayHelpers'
import type { PracticeResponse } from '@/api/types'

const props = defineProps<{
  practice: PracticeResponse
}>()

defineEmits<{
  click: [id: string]
}>()

// Иконка практики — по `direction` из полной PracticeResponse.
// practiceIconFor вернёт DIRECTION_ICON[dir] для known direction либо
// title-heuristic / IconDots fallback (см. displayHelpers).
const typeIcon = computed(() => practiceIconFor(props.practice))

const masterInitial = computed(() => {
  const name = props.practice.master_name?.trim()
  return name ? name.charAt(0).toUpperCase() : 'М'
})

const time = computed(() =>
  formatTime(props.practice.scheduled_at, props.practice.timezone),
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
/* Figma 2266:2307 — card 336×104, padding 13/15, icon absolute слева,
 * title и master row центрированы по карточке, footer внизу. */
.cal-card {
  position: relative;
  height: 104px;
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: 13px 15px;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.cal-card:hover {
  opacity: 0.9;
}

.cal-card__icon {
  position: absolute;
  left: 15px;
  top: 13px;
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Иконка сама несёт circle-обводку (IconMeditation.vue) — без teal-подложки. */
  color: var(--velo-text-primary);
}

.cal-card__title {
  text-align: center;
  font-family: var(--font-body);
  font-weight: 400;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.36px;
  line-height: 1;
  margin: 0 0 5px;
}

.cal-card__master {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: 0.28px;
  margin: 0 0 19px;
}

.cal-card__master-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  color: var(--velo-text-secondary);
  font-size: 9px;
  flex-shrink: 0;
}

.cal-card__verified {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
  flex-shrink: 0;
}

.cal-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.cal-card__meta {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.cal-card__meta-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
}

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

/* Paid -- teal (matches BookingCard "done"/"today" tone) */
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
