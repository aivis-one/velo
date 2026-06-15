<!--
  VELO Frontend -- DiaryThreadCard (Diary redesign, screen 40 "map")

  Compact, map-scale rendering of one DiaryEvent for the thread (DiaryTimeline).
  The flat-list / detail rendering lives in DiaryFeedCard; this is the smaller
  "bead on the thread" form, centered on the axis (no left/right alternation).

  Visual forms by kind (Figma map screens, ~0.75 of the list scale):
    banner   -- booking_* / practice_*_by_master  -> centered status banner
    checkin  -- compact: mood glyph + label ("Check-in: Хорошо")
    note/dream -- mini card: 47x47 icon box + body (title + date)
    feedback / practice_outcome -- side card 217: leading glyph + title + tag

  The kind->title/icon/label model comes from the shared useDiaryCardModel
  composable (same source as DiaryFeedCard); this component only owns the
  compact thread layout + the side-card compositions (sideIcon/title/tag).
-->

<template>
  <!-- ===================== BANNER (centered) ===================== -->
  <div v-if="form === 'banner'" class="tcard tcard--banner" :class="`tcard--banner-${bannerTone}`">
    <p class="tcard__banner-title">{{ title }}</p>
    <p v-if="bannerSubtitle" class="tcard__banner-subtitle">{{ bannerSubtitle }}</p>
  </div>

  <!-- ===================== CHECK-IN (compact glyph + label) ===================== -->
  <button v-else-if="kind === 'checkin'" type="button" class="tcard tcard--checkin" @click="onTap">
    <span class="tcard__gico"><component :is="standardIcon" :size="34" /></span>
    <span class="tcard__lbl">{{ title }}</span>
  </button>

  <!-- ===================== NOTE / DREAM (mini card) ===================== -->
  <button
    v-else-if="kind === 'note' || kind === 'dream'"
    type="button"
    class="tcard tcard--mini"
    @click="onTap"
  >
    <span class="tcard__ibox" :class="`tcard__ibox--${kind}`">
      <component :is="standardIcon" :size="22" />
    </span>
    <span class="tcard__mbody">
      <span class="tcard__mt">{{ title }}</span>
      <span class="tcard__md">{{ dateLine }}</span>
    </span>
  </button>

  <!-- ===================== FEEDBACK / PRACTICE (side card 217) ===================== -->
  <button v-else type="button" class="tcard tcard--side" @click="onTap">
    <span class="tcard__ava" :class="{ 'tcard__ava--feedback': kind === 'feedback' }">
      <component :is="sideIcon" :size="22" />
    </span>
    <span class="tcard__tx">
      <span class="tcard__t1">{{ sideTitle }}</span>
      <!-- Mood/rating scale dots (Figma map side card), feedback only. -->
      <span v-if="kind === 'feedback'" class="tcard__scale" aria-hidden="true">
        <i class="tcard__dot tcard__dot--a" />
        <i class="tcard__dot tcard__dot--b" />
      </span>
    </span>
    <span v-if="outcomeAttended" class="tcard__tag tcard__tag--done">
      <IconCheck :size="12" />
    </span>
    <span v-else-if="sideTag" class="tcard__tag">{{ sideTag }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useDiaryCardModel } from '@/composables/useDiaryCardModel'
import { IconCheck } from '@/components/icons'
import type { DiaryFeedItem } from '@/api/types'

const props = defineProps<{
  item: DiaryFeedItem
  timezone?: string
}>()

const emit = defineEmits<{
  tap: [payload: { item: DiaryFeedItem; editable: boolean }]
}>()

// Shared card model (same source as DiaryFeedCard).
const {
  kind,
  form,
  baseTitle,
  title,
  dateLine,
  standardIcon,
  directionIcon,
  bannerTone,
  bannerSubtitle,
  practiceTitle,
  outcomeStatus,
  outcomeLabel,
  ratingLabel,
  editable,
} = useDiaryCardModel(
  () => props.item,
  () => props.timezone,
)

// -- thread-specific compositions of the shared model ------------------------
// feedback / practice render as a compact "side card 217": one leading glyph,
// the bare kind/practice title, and a tag (rating label / outcome label).
const sideIcon = computed<Component>(() =>
  kind.value === 'practice_outcome' ? directionIcon.value : standardIcon.value,
)
const sideTitle = computed(() =>
  kind.value === 'practice_outcome' ? practiceTitle.value : baseTitle.value,
)
// Attended practice shows just a check (not the word "Done"); a miss keeps its
// "Не состоялась" label. Feedback keeps its rating label.
const outcomeAttended = computed(
  () => kind.value === 'practice_outcome' && outcomeStatus.value === 'attended',
)
const sideTag = computed(() => {
  if (kind.value === 'practice_outcome') {
    return outcomeStatus.value === 'attended' ? '' : outcomeLabel.value
  }
  if (kind.value === 'feedback') return ratingLabel.value
  return ''
})

function onTap(): void {
  emit('tap', { item: props.item, editable: editable.value })
}
</script>

<style scoped>
/* Map-scale ("bead on the thread") cards. Tokens for color; px dims come from
   the Figma map screens (side card 217x67, icon box 47, avatar ring 28). */
.tcard {
  font-family: var(--font-body);
  color: var(--velo-text-primary);
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
}

/* ---- banner (centered) ---- */
.tcard--banner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  border: 1.5px solid;
  text-align: center;
  max-width: 240px;
  cursor: default;
}
.tcard--banner-teal {
  background: var(--velo-glass-teal-40);
  border-color: var(--velo-teal-400);
  color: var(--velo-teal-600);
}
.tcard--banner-neutral {
  background: var(--velo-glass-blue-15);
  border-color: var(--velo-border);
  color: var(--velo-text-secondary);
}
.tcard__banner-title {
  font-size: 11px;
  letter-spacing: 0.22px;
}
.tcard__banner-subtitle {
  font-size: 11px;
  opacity: 0.85;
}

/* ---- check-in (compact glyph + label) ---- */
.tcard--checkin {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
}
.tcard__gico {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.tcard__lbl {
  font-size: 11px;
  color: var(--velo-text-secondary);
}

/* ---- note / dream (mini card: icon box + body) ---- */
.tcard--mini {
  display: flex;
  gap: var(--space-1);
}
.tcard__ibox {
  width: 47px;
  height: 47px;
  flex: 0 0 47px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  background: var(--velo-bg-card-solid);
  color: var(--velo-text-primary);
}
.tcard__mbody {
  width: 200px;
  height: 47px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
  padding: 0 var(--space-3);
  border-radius: 5px;
  background: var(--velo-bg-card-solid);
}
.tcard__mt {
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tcard__md {
  font-size: 10px;
  color: var(--velo-text-secondary);
}

/* ---- feedback / practice (side card 217) ---- */
.tcard--side {
  width: 217px;
  min-height: 64px;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: 10px;
  background: var(--velo-bg-card-solid);
}
.tcard__ava {
  width: 28px;
  height: 28px;
  flex: 0 0 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--velo-text-primary);
}
.tcard__ava--feedback {
  color: var(--velo-teal-400);
}
.tcard__tx {
  flex: 1;
  min-width: 0;
}
.tcard__t1 {
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.tcard__scale {
  display: inline-flex;
  gap: 5px;
  margin-top: 4px;
}

.tcard__dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  display: block;
}

.tcard__dot--a {
  background: var(--velo-text-primary);
}

.tcard__dot--b {
  background: var(--velo-teal-400);
}
.tcard__tag {
  flex-shrink: 0;
  padding: 2px var(--space-2);
  border-radius: 4px;
  font-size: 10px;
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
  white-space: nowrap;
}
</style>
