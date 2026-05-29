<!--
  VELO Frontend -- DiaryTimeline (Diary redesign, screen 40 "map")

  The unified feed rendered as a vertical "thread": a central axis with cards
  strung along it as compact beads (DiaryThreadCard), split into day groups by
  date-nodes. Aligned to the Figma map screens (2026-05-29):
    - cards are CENTERED on the axis (no left/right alternation);
    - date-nodes are a centered label with small ornament dots on the axis;
    - the axis is a light vertical stroke behind the beads.

  ORDER (chat-mode): oldest at the TOP, newest at the BOTTOM. The feed arrives
  newest-first; we render a chronological copy so the newest entry sits at the
  bottom, next to the composer (see DiaryFeedView for the scroll handling).

  Cards themselves are delegated to DiaryThreadCard; this component only owns
  the axis/date-node layout and the day grouping. The flat-column view uses
  DiaryList + DiaryFeedCard instead (toggled in DiaryFeedView).
-->

<template>
  <div class="timeline">
    <template v-for="group in dayGroups" :key="group.dayKey">
      <!-- Date node: centered label + ornament dots on the axis -->
      <div class="timeline__date-node">
        <span class="timeline__date-label">{{ group.label }}</span>
      </div>

      <!-- Cards of this day, centered on the axis -->
      <div v-for="item in group.items" :key="item.id" class="timeline__row">
        <DiaryThreadCard
          :item="item"
          :timezone="timezone"
          @tap="(p) => emit('tap', p)"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DiaryThreadCard from '@/components/shared/DiaryThreadCard.vue'
import type { DiaryFeedItem } from '@/api/types'

const props = defineProps<{
  items: DiaryFeedItem[]
  timezone?: string
}>()

const emit = defineEmits<{
  tap: [payload: { item: DiaryFeedItem; editable: boolean }]
}>()

const tz = computed(() => props.timezone ?? 'UTC')

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

// -- group into days ---------------------------------------------------------

interface DayGroup {
  dayKey: string
  label: string
  items: DiaryFeedItem[]
}

const dayGroups = computed<DayGroup[]>(() => {
  const groups: DayGroup[] = []
  let current: DayGroup | null = null

  // Chat-mode: the feed arrives newest-first; render a chronological copy so
  // the newest entry is at the bottom. reverse() runs on a shallow copy;
  // props.items is not mutated.
  const chronological = [...props.items].reverse()

  for (const item of chronological) {
    const key = dayKeyOf(item.occurred_at)
    if (!current || current.dayKey !== key) {
      current = { dayKey: key, label: dayLabelOf(item.occurred_at), items: [] }
      groups.push(current)
    }
    current.items.push(item)
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
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-3) 0;
}

/* Central vertical axis behind the beads. */
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

/* -- Date node: centered label + two ornament dots on the axis above it -- */
.timeline__date-node {
  position: relative;
  z-index: var(--z-content);
  text-align: center;
  /* room for the ornament dots that sit on the axis above the label */
  padding-top: var(--space-5);
  margin: var(--space-2) 0;
}

/* bigger dot then a smaller one, centred on the axis above the label */
.timeline__date-node::before,
.timeline__date-node::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-radius: var(--radius-full);
  background: var(--velo-text-primary);
}
.timeline__date-node::before {
  top: 4px;
  width: 6px;
  height: 6px;
}
.timeline__date-node::after {
  top: 14px;
  width: 3px;
  height: 3px;
}

.timeline__date-label {
  display: inline-block;
  /* opaque-ish backdrop blends with the app background and masks the axis
     stroke behind the text (so the line doesn't run through the label). */
  background: var(--velo-bg-start);
  padding: 0 var(--space-3);
  font-family: var(--font-body);
  font-size: var(--text-base);
  letter-spacing: 0.36px;
  color: var(--velo-text-primary);
}

/* -- Card rows (all centered on the axis) -- */
.timeline__row {
  position: relative;
  z-index: var(--z-content);
  display: flex;
  justify-content: center;
  width: 100%;
}
</style>
