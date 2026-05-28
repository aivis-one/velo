<!--
  VELO Frontend -- PracticeListCard (DS, 2026-05)

  Shared list-item card for a practice. Used in:
    - UserDashboardView "Ближайшая практика"
    - CalendarPracticeCard (calendar day list)
    - BookingCard (my reservations list)
    - Booking Detail (embedded practice info)

  Visual spec (Figma SVGs dashboard / calendar-list / my-reservations):
    - Card 336×104, padding 13/15, white background, 1px white border, radius 15
    - Icon position: absolute left 15, top 13, size 46×46 (icon itself carries
      the circle outline — wrapper is just a slot for color)
    - Title text-align LEFT (2026-05-29 fix: ранее center, но при разной
      длине строк левый край title плавал ±6px относительно линии иконки —
      зрительно текст «прыгал»). Начало колонки: 70px от левого края card
      (= padding-x 15 + icon 46 + 9 gap) — токен --velo-card-content-indent.
      font-size 18, letter-spacing 0.36px, line-height 1, ellipsis-truncated.
    - Master row LEFT по той же линии, что title (выровнено с заголовком).
      font-size 14, gap 10, letter-spacing 0.28px, margin-bottom 19.
    - Footer: flex space-between (meta cluster left + badge slot right)

  Slots:
    #meta-left -- left content of the footer (e.g. date + duration with icons).
                  When empty, footer is hidden entirely.
    #badge     -- right content of the footer (e.g. VBadge "Оплачено").

  Title is taken from the prop `title` (override) or from `practice.title`.
  Master name from `practice.master_name`; falls back to "Мастер".

  Usage:
    <PracticeListCard
      :practice="bookingData.practice"
      @click="openPractice"
    >
      <template #meta-left>
        <span class="cell"><IconCalendar :size="14" /> {{ date }}</span>
        <span class="cell"><IconClock :size="14" /> {{ duration }}</span>
      </template>
      <template #badge>
        <VBadge variant="success">Оплачено</VBadge>
      </template>
    </PracticeListCard>
-->

<template>
  <component
    :is="clickable ? 'button' : 'div'"
    :type="clickable ? 'button' : undefined"
    class="practice-list-card"
    :class="{ 'practice-list-card--clickable': clickable }"
    @click="clickable ? $emit('click') : null"
  >
    <span class="practice-list-card__icon">
      <component :is="icon" :size="46" />
    </span>

    <h4 class="practice-list-card__title">{{ titleText }}</h4>

    <p class="practice-list-card__master">
      <span class="practice-list-card__master-avatar">{{ masterInitial }}</span>
      <span class="practice-list-card__master-name">{{ masterName }}</span>
      <span v-if="showVerified" class="practice-list-card__verified">
        <IconCheck :size="11" />
      </span>
    </p>

    <div v-if="$slots['meta-left'] || $slots.badge" class="practice-list-card__footer">
      <span class="practice-list-card__meta-left">
        <slot name="meta-left" />
      </span>
      <span class="practice-list-card__badge-slot">
        <slot name="badge" />
      </span>
    </div>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IconCheck } from '@/components/icons'
import { practiceIconFor } from '@/utils/displayHelpers'

interface PracticeLike {
  /** Direction picks the icon. */
  direction?: string | null
  /** Title; can be overridden via `title` prop (e.g. strip "(эфир)" suffix). */
  title?: string | null
  /** Master name; defaults to "Мастер" if missing. */
  master_name?: string | null
}

const props = withDefaults(
  defineProps<{
    practice: PracticeLike
    /** Override title (e.g. cleaned of "(эфир)"). Defaults to practice.title. */
    title?: string
    /** Show the teal-circle "verified" check next to the master name. Default true. */
    showVerified?: boolean
    /** When true (default), the whole card is a button and emits @click. */
    clickable?: boolean
  }>(),
  {
    title: undefined,
    showVerified: true,
    clickable: true,
  },
)

defineEmits<{ click: [] }>()

// Icon by direction (or title-heuristic for PracticeSummary, see displayHelpers).
const icon = computed(() => practiceIconFor(props.practice))

// Title: explicit prop > practice.title > empty
const titleText = computed(() => props.title ?? props.practice.title ?? '')

// Master name with sensible fallback
const masterName = computed(() => props.practice.master_name ?? 'Мастер')

// First letter of master name for the avatar placeholder
const masterInitial = computed(() => {
  const name = (props.practice.master_name ?? 'М').trim()
  return (name.charAt(0) || 'М').toUpperCase()
})
</script>

<style scoped>
.practice-list-card {
  position: relative;
  display: block;
  width: 100%;
  height: var(--velo-card-height-list);
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--velo-card-padding-y) var(--velo-card-padding-x);
  text-align: left;
  font-family: var(--font-body);
  color: var(--velo-text-primary);
  transition: opacity var(--transition-fast);
}

.practice-list-card--clickable {
  cursor: pointer;
}

.practice-list-card--clickable:active {
  opacity: 0.85;
}

.practice-list-card__icon {
  position: absolute;
  left: var(--velo-card-padding-x);
  top: var(--velo-card-padding-y);
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Иконка сама несёт circle-обводку (см. IconMeditation/Breathwork) —
   * подложки/border-radius на обёртке не нужны. */
  color: var(--velo-text-primary);
}

.practice-list-card__title {
  /* 2026-05-29: text-align LEFT, фиксированный левый край (--velo-card-content-indent).
   * Раньше был center — при разной длине titles текст «прыгал» ±6px
   * по горизонтали относительно иконки. */
  text-align: left;
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: var(--velo-card-letter-spacing-title);
  line-height: 1;
  margin: 0 var(--velo-card-padding-x) var(--velo-card-gap-icon-title)
          var(--velo-card-content-indent);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.practice-list-card__master {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: var(--velo-card-meta-row-gap);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: var(--velo-card-letter-spacing-meta);
  /* Левая колонка выровнена с title (--velo-card-content-indent),
   * правая граница как у title (padding-x). */
  margin: 0 var(--velo-card-padding-x) var(--velo-card-gap-meta-footer)
          var(--velo-card-content-indent);
}

.practice-list-card__master-avatar {
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

.practice-list-card__master-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.practice-list-card__verified {
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

.practice-list-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
}

.practice-list-card__meta-left {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.practice-list-card__badge-slot {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
}

/* Helper class for items inside #meta-left (so views don't need to duplicate
 * inline-flex styles). Visible to slot content via :slotted(). */
:slotted(.plc-meta-item) {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
}
</style>
