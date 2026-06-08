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
      <!-- Date node: a flourish on each side of the label (Figma Group 2355,
           ±57px from the axis). -->
      <div class="timeline__date-node">
        <IconDateOrnament class="timeline__flourish" :size="28" />
        <span class="timeline__date-label">{{ group.label }}</span>
        <IconDateOrnament
          class="timeline__flourish timeline__flourish--right"
          :size="28"
        />
      </div>

      <!-- Axis link from the date node down to the day's first card
           (Figma Group 2429). -->
      <div class="timeline__connector">
        <IconAxisConnector :size="31" />
      </div>

      <!-- Cards of this day, centered on the axis, joined by the between-cards
           axis dot (Figma Vector 110) — shown between cards, not before the
           first one. -->
      <template v-for="(item, i) in group.items" :key="item.id">
        <div v-if="i > 0" class="timeline__dot">
          <IconAxisDot :size="18" />
        </div>
        <div class="timeline__row">
          <DiaryThreadCard
            :item="item"
            :timezone="timezone"
            @tap="(p) => emit('tap', p)"
          />
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DiaryThreadCard from '@/components/shared/DiaryThreadCard.vue'
import {
  IconDateOrnament,
  IconAxisConnector,
  IconAxisDot,
} from '@/components/icons'
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

/* -- Date node: flourish + label + flourish (Figma Group 2355). The flourishes
   sit ±57px from the axis (label centered on the axis). No beads here — the
   bead links live on the axis BETWEEN rows (see __connector / __dot). -- */
.timeline__date-node {
  position: relative;
  z-index: var(--z-content);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-5);
  margin: var(--space-2) 0;
  color: var(--velo-text-primary);
}

/* Side flourishes (decorative vector, Group 2355, 28×34). Left as-is, right
   mirrored. */
.timeline__flourish {
  flex-shrink: 0;
  color: var(--velo-text-primary);
}
.timeline__flourish--right {
  transform: scaleX(-1);
}

.timeline__date-label {
  /* opaque-ish backdrop blends with the app background and masks the axis
     stroke behind the text (so the line doesn't run through the label). */
  background: var(--velo-bg-start);
  padding: 0 var(--space-2);
  font-family: var(--font-body);
  font-size: var(--text-base);
  letter-spacing: 0.36px;
  color: var(--velo-text-primary);
  white-space: nowrap;
}

/* Axis links on the central thread, with small breathing room around them
   (Figma: the link floats between elements, not flush). */
.timeline__connector,
.timeline__dot {
  position: relative;
  z-index: var(--z-content);
  display: flex;
  justify-content: center;
  color: var(--velo-text-primary);
}
.timeline__connector {
  /* date node -> first card (Group 2429): ~4px above, ~11px below per export */
  padding: 4px 0 11px;
}
.timeline__dot {
  /* between cards (Vector 110): symmetric breathing room */
  padding: 6px 0;
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
