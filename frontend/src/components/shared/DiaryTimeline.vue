<!--
  VELO Frontend -- DiaryTimeline (Diary redesign, screen 40 "map")

  The unified feed rendered as a vertical "thread": a central axis with cards
  hanging off it, alternating left/right, split into day groups by date-nodes.

  DETERMINISTIC ALTERNATION RULES (agreed):
    1. Banner kinds (booking_confirmed / booking_cancelled_by_user /
       practice_rescheduled / practice_cancelled_by_master) and the
       practice_outcome card sit CENTERED on the axis (full width); the thread
       passes through them.
    2. Standard cards (checkin / feedback / note / dream) alternate left/right.
    3. The alternation counter advances ONLY on standard cards -- centered
       cards do not disturb it.
    4. Side is a function of position in the sorted list (stable across
       pagination -- appending a page never reshuffles earlier cards).
    5. The counter RESETS each new day: the first standard card of a day is
       always on the left.
    6. A date-node splits the thread whenever the calendar day changes
       (computed in the user's timezone -- the diary is a personal timeline).

  The thread connectors are CSS strokes (not the Figma bezier art): Level-2
  "simplified" -- the visual idea (axis + alternation + date-nodes + a light
  date ornament) without pixel-perfect curves, so it survives real data of
  variable length.

  Cards themselves are delegated to DiaryFeedCard; this component only owns
  layout/positioning and the day grouping.
-->

<template>
  <div class="timeline">
    <template v-for="(group, gi) in dayGroups" :key="group.dayKey">
      <!-- Date node (centered on the axis) -->
      <div class="timeline__date-node">
        <span class="timeline__ornament timeline__ornament--left" aria-hidden="true">
          <IconDateLeaf :size="22" />
        </span>
        <span class="timeline__date-label">{{ group.label }}</span>
        <span class="timeline__ornament timeline__ornament--right" aria-hidden="true">
          <IconDateLeaf :size="22" mirrored />
        </span>
      </div>

      <!-- Cards of this day -->
      <div
        v-for="row in group.rows"
        :key="row.item.id"
        class="timeline__row"
        :class="`timeline__row--${row.placement}`"
      >
        <!-- Connector stub from axis to the card -->
        <span
          v-if="row.placement !== 'center'"
          class="timeline__connector"
          :class="`timeline__connector--${row.placement}`"
          aria-hidden="true"
        />
        <div class="timeline__card-wrap">
          <DiaryFeedCard
            :item="row.item"
            :timezone="timezone"
            @tap="(p) => emit('tap', p)"
          />
        </div>
      </div>

      <!-- Inter-group axis segment (not after the last group) -->
      <div
        v-if="gi < dayGroups.length - 1"
        class="timeline__axis-gap"
        aria-hidden="true"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DiaryFeedCard from '@/components/shared/DiaryFeedCard.vue'
import IconDateLeaf from '@/components/icons/IconDateLeaf.vue'
import type { DiaryFeedItem, DiaryEventKind } from '@/api/types'

const props = defineProps<{
  items: DiaryFeedItem[]
  timezone?: string
}>()

const emit = defineEmits<{
  tap: [payload: { item: DiaryFeedItem; editable: boolean }]
}>()

const tz = computed(() => props.timezone ?? 'UTC')

// -- placement decision per kind ---------------------------------------------

const CENTER_KINDS: DiaryEventKind[] = [
  'booking_confirmed',
  'booking_cancelled_by_user',
  'practice_rescheduled',
  'practice_cancelled_by_master',
  'practice_outcome',
]

function isCenter(kind: string): boolean {
  return CENTER_KINDS.includes(kind as DiaryEventKind)
}

// -- day key + label in the user's timezone ----------------------------------

// YYYY-MM-DD in the target tz, used to detect calendar-day boundaries.
function dayKeyOf(iso: string): string {
  return new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: tz.value,
  }).format(new Date(iso))
}

// "Сегодня" / "Вчера" / "24 января" for the date node.
function dayLabelOf(iso: string): string {
  const key = dayKeyOf(iso)
  const todayKey = dayKeyOf(new Date().toISOString())
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  const yesterdayKey = dayKeyOf(yesterday.toISOString())

  if (key === todayKey) return 'Сегодня'
  if (key === yesterdayKey) return 'Вчера'
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'long',
    timeZone: tz.value,
  }).format(new Date(iso))
}

// -- group into days, assign deterministic placement -------------------------

type Placement = 'center' | 'left' | 'right'
interface Row {
  item: DiaryFeedItem
  placement: Placement
}
interface DayGroup {
  dayKey: string
  label: string
  rows: Row[]
}

const dayGroups = computed<DayGroup[]>(() => {
  const groups: DayGroup[] = []
  let current: DayGroup | null = null
  // Standard-card counter, reset on each new day (rule 5).
  let standardIdx = 0

  for (const item of props.items) {
    const key = dayKeyOf(item.occurred_at)
    if (!current || current.dayKey !== key) {
      current = {
        dayKey: key,
        label: dayLabelOf(item.occurred_at),
        rows: [],
      }
      groups.push(current)
      standardIdx = 0
    }

    let placement: Placement
    if (isCenter(item.kind)) {
      placement = 'center' // rule 1, does not advance the counter (rule 3)
    } else {
      // rule 2 + 4 + 5: even -> left, odd -> right, reset per day
      placement = standardIdx % 2 === 0 ? 'left' : 'right'
      standardIdx += 1
    }
    current.rows.push({ item, placement })
  }

  return groups
})
</script>

<style scoped>
.timeline {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3) 0;
}

/* Central vertical axis behind everything. */
.timeline::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  transform: translateX(-50%);
  background: var(--velo-border-light);
  z-index: var(--z-background);
}

/* -- Date node -- */
.timeline__date-node {
  position: relative;
  z-index: var(--z-content);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  background: var(--velo-bg-start);
  border-radius: var(--radius-full);
}

.timeline__date-label {
  font-family: var(--font-body);
  font-size: var(--text-base);
  letter-spacing: 0.36px;
  color: var(--velo-text-primary);
}

.timeline__ornament {
  display: inline-flex;
  color: var(--velo-text-primary);
}

/* -- Card rows -- */
.timeline__row {
  position: relative;
  z-index: var(--z-content);
  display: flex;
  width: 100%;
}

.timeline__row--center {
  justify-content: center;
}

.timeline__row--left {
  justify-content: flex-start;
}

.timeline__row--right {
  justify-content: flex-end;
}

.timeline__card-wrap {
  /* Side cards take a little under half so they read as hanging off the axis;
     center cards (banner/practice) use the standard content width. */
  width: 100%;
  max-width: var(--velo-content-width);
}

.timeline__row--left .timeline__card-wrap,
.timeline__row--right .timeline__card-wrap {
  max-width: 76%;
}

/* Connector stub from the axis to a side card. */
.timeline__connector {
  position: absolute;
  top: 50%;
  width: 12%;
  height: 2px;
  background: var(--velo-border-light);
  transform: translateY(-50%);
  z-index: var(--z-background);
}

.timeline__connector--left {
  left: 50%;
  transform: translate(-100%, -50%);
}

.timeline__connector--right {
  right: 50%;
  transform: translate(100%, -50%);
}

/* Axis segment between day groups (the ::before already draws a continuous
   line; this just guarantees vertical rhythm between groups). */
.timeline__axis-gap {
  height: var(--space-3);
}
</style>
