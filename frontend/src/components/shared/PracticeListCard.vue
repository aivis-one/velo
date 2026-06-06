<!--
  VELO Frontend -- PracticeListCard (DS, unified 2026-06)

  Shared list-item card for a practice. Used in:
    - UserDashboardView "Ближайшая практика"
    - CalendarPracticeCard (calendar day list / master public upcoming)
    - BookingCard (my reservations list)
    - DetailView / EntryView (diary linked-practice header)

  Layout (unified canon, approved 2026-06):
    - White card, --velo-border-card, --radius-md, adaptive min-height 104.
    - Left column (--velo-card-iconcol-w): direction icon on top, and the
      date/time (`when`) centered UNDER it on the bottom meta line — no leading
      calendar icon. Short date via formatShortDate ("9 июня" / "12 сент.").
    - Content column (icon col + space-3): title (ellipsis) + master row.
    - Bottom meta line (one row): `when` (under the icon) · duration with clock
      icon (under the title) · #badge slot (status, right edge, symmetric padding).

  Props:
    practice     -- icon/title/master source.
    title?       -- override title (e.g. cleaned of "(эфир)").
    when         -- pre-formatted date OR time string shown under the icon.
    duration?    -- pre-formatted duration ("45 мин"); omitted = no duration cell.
    showVerified -- show the teal verified check next to the master (default true).
    clickable    -- whole card is a button emitting @click (default true).

  Slot:
    #badge -- status badge on the right of the meta line (e.g. <VBadge>).
-->

<template>
  <component
    :is="clickable ? 'button' : 'div'"
    :type="clickable ? 'button' : undefined"
    class="practice-list-card"
    :class="{ 'practice-list-card--clickable': clickable }"
    @click="clickable ? $emit('click') : null"
  >
    <div class="practice-list-card__top">
      <span class="practice-list-card__iconcol">
        <component :is="icon" :size="46" />
      </span>
      <div class="practice-list-card__content">
        <h4 class="practice-list-card__title">{{ titleText }}</h4>
        <p class="practice-list-card__master">
          <span class="practice-list-card__master-avatar">{{ masterInitial }}</span>
          <span class="practice-list-card__master-name">{{ masterName }}</span>
          <span v-if="showVerified" class="practice-list-card__verified">
            <IconCheck :size="11" />
          </span>
        </p>
      </div>
    </div>

    <div class="practice-list-card__meta">
      <span class="practice-list-card__when">{{ when }}</span>
      <span class="practice-list-card__rest">
        <span v-if="duration" class="practice-list-card__dur">
          <IconClock :size="14" /> {{ duration }}
        </span>
        <span v-else class="practice-list-card__dur-empty" />
        <span class="practice-list-card__badge">
          <slot name="badge" />
        </span>
      </span>
    </div>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IconCheck, IconClock } from '@/components/icons'
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
    /** Pre-formatted date or time shown under the icon (e.g. "9 июня" / "19:00"). */
    when?: string
    /** Pre-formatted duration ("45 мин"); omitted = no duration cell. */
    duration?: string
    /** Show the teal-circle "verified" check next to the master name. Default true. */
    showVerified?: boolean
    /** When true (default), the whole card is a button and emits @click. */
    clickable?: boolean
  }>(),
  {
    title: undefined,
    when: '',
    duration: undefined,
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
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  width: 100%;
  min-height: var(--velo-card-height-list);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
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

/* Top: icon column + content (title/master) */
.practice-list-card__top {
  display: flex;
  gap: var(--space-3);
}

.practice-list-card__iconcol {
  width: var(--velo-card-iconcol-w);
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  /* Иконка сама несёт circle-обводку — подложки на обёртке не нужны. */
  color: var(--velo-text-primary);
}

.practice-list-card__content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--velo-card-gap-icon-title);
}

.practice-list-card__title {
  font-size: var(--text-base);
  font-weight: 400;
  letter-spacing: var(--velo-card-letter-spacing-title);
  line-height: 1.05;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.practice-list-card__master {
  display: flex;
  align-items: center;
  gap: var(--velo-card-meta-row-gap);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: var(--velo-card-letter-spacing-meta);
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
  font-size: var(--text-8);
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

/* Bottom meta line: when (under icon) · duration (under title) · badge (right) */
.practice-list-card__meta {
  display: flex;
  align-items: center;
  margin-top: auto;
}

.practice-list-card__when {
  width: var(--velo-card-iconcol-w);
  flex-shrink: 0;
  text-align: center;
  white-space: nowrap;
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: var(--velo-card-letter-spacing-meta);
}

.practice-list-card__rest {
  flex: 1;
  min-width: 0;
  margin-left: var(--space-3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.practice-list-card__dur {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.practice-list-card__badge {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
}
</style>
