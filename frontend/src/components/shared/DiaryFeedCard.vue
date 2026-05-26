<!--
  VELO Frontend -- DiaryFeedCard (Diary redesign)

  Dumb presentational card for one DiaryEvent in the unified feed. Three
  visual forms, chosen by `item.kind`:

    banner   -- booking_confirmed / booking_cancelled_by_user /
                practice_rescheduled / practice_cancelled_by_master
                (pill-ish status banner; teal accent for the positive
                "confirmed" case, neutral slate for cancels/reschedules)
    practice -- practice_outcome (taller white card: title + master row +
                date row + Done / "Не состоялась" outcome badge)
    standard -- checkin / feedback / note / dream (white card: leading icon
                + title + content preview + date line)

  The card reads loosely-typed fields from `item.snapshot` (an open dict
  whose shape depends on kind -- see DiaryFeedItem). Missing fields degrade
  gracefully (the element is simply omitted).

  Interaction: emits `tap` with the item and an `editable` flag (true for
  note/dream). The parent view decides what to do -- in this iteration it
  shows a "coming soon" toast for editable cards and ignores the rest.

  kind/mood/rating -> icon COMPONENT maps live here, NOT in displayHelpers:
  the utils layer must not import .vue files (mirrors MOOD_ICON in CheckinView).
-->

<template>
  <!-- ===================== BANNER ===================== -->
  <div
    v-if="form === 'banner'"
    class="feed-card feed-card--banner"
    :class="`feed-card--banner-${bannerTone}`"
  >
    <p class="feed-card__banner-title">{{ title }}</p>
    <p v-if="bannerSubtitle" class="feed-card__banner-subtitle">
      {{ bannerSubtitle }}
    </p>
  </div>

  <!-- ===================== PRACTICE ===================== -->
  <div
    v-else-if="form === 'practice'"
    class="feed-card feed-card--practice feed-card--tappable"
    role="button"
    tabindex="0"
    @click="onTap"
    @keydown.enter="onTap"
    @keydown.space.prevent="onTap"
  >
    <p class="feed-card__practice-title">{{ practiceTitle }}</p>

    <div class="feed-card__practice-master">
      <span class="feed-card__avatar" aria-hidden="true">
        <img
          v-if="masterAvatarUrl"
          :src="masterAvatarUrl"
          alt=""
          class="feed-card__avatar-img"
        />
      </span>
      <span class="feed-card__master-name">{{ masterName }}</span>
      <IconCheck v-if="masterVerified" :size="14" class="feed-card__verified" />
    </div>

    <div class="feed-card__practice-bottom">
      <span class="feed-card__practice-date">
        <IconCalendar :size="14" class="feed-card__date-icon" />
        {{ practiceDate }}
      </span>
      <span
        class="feed-card__outcome"
        :class="`feed-card__outcome--${outcomeStatus}`"
      >
        <IconCheck v-if="outcomeStatus === 'attended'" :size="12" />
        {{ outcomeLabel }}
      </span>
    </div>

    <!-- Practice direction glyph, top-left. -->
    <component
      :is="directionIcon"
      :size="40"
      class="feed-card__practice-icon"
    />
  </div>

  <!-- ===================== STANDARD ===================== -->
  <button
    v-else
    type="button"
    class="feed-card feed-card--standard"
    @click="onTap"
  >
    <p class="feed-card__date">{{ dateLine }}</p>
    <div class="feed-card__body">
      <span class="feed-card__icon" :class="`feed-card__icon--${item.kind}`">
        <component :is="standardIcon" :size="standardIconSize" />
      </span>
      <span class="feed-card__text">
        <span class="feed-card__title">{{ title }}</span>
        <span v-if="preview" class="feed-card__preview">{{ preview }}</span>
      </span>
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import {
  IconCheck,
  IconCalendar,
  IconMoodLow,
  IconMoodMid,
  IconMoodHigh,
  IconRatingFire,
  IconRatingGood,
  IconRatingConfused,
  IconMeditation,
  IconYoga,
  IconBreathwork,
  IconPen,
  IconDreamBook,
  IconDots,
} from '@/components/icons'
import {
  FEED_KIND_TITLE,
  OUTCOME_LABEL,
  MOOD_LABEL,
  RATING_LABEL,
} from '@/utils/displayHelpers'
import { formatFeedDateTime, formatDate } from '@/utils/format'
import type { DiaryFeedItem, DiaryEventKind } from '@/api/types'

const props = defineProps<{
  item: DiaryFeedItem
  /** User timezone for date formatting (diary is a personal timeline). */
  timezone?: string
}>()

const emit = defineEmits<{
  tap: [payload: { item: DiaryFeedItem; editable: boolean }]
}>()

// -- kind -> visual form -----------------------------------------------------

const BANNER_KINDS: DiaryEventKind[] = [
  'booking_confirmed',
  'booking_cancelled_by_user',
  'practice_rescheduled',
  'practice_cancelled_by_master',
]

const form = computed<'banner' | 'practice' | 'standard'>(() => {
  const kind = props.item.kind as DiaryEventKind
  if (BANNER_KINDS.includes(kind)) return 'banner'
  if (kind === 'practice_outcome') return 'practice'
  return 'standard'
})

// -- snapshot accessors (open dict -- read defensively) ----------------------

const snap = computed<Record<string, unknown>>(
  () => props.item.snapshot ?? {},
)

function snapStr(key: string): string | null {
  const v = snap.value[key]
  return typeof v === 'string' && v.length > 0 ? v : null
}

const tz = computed(() => props.timezone ?? 'UTC')

// -- standard / banner icon maps (kind|mood|rating -> component) -------------

const MOOD_ICON: Record<string, Component> = {
  low: IconMoodLow,
  mid: IconMoodMid,
  high: IconMoodHigh,
}

const RATING_ICON: Record<string, Component> = {
  fire: IconRatingFire,
  good: IconRatingGood,
  confused: IconRatingConfused,
}

// Only the three directions with real assets are mapped; the five newer ones
// (somatic / tantra / womens_circle / mens_circle / kundalini) fall back to a
// neutral glyph below (see directionIcon) until their icons land -- same
// reasoning as DIRECTION_ICON_FALLBACK in displayHelpers.
const DIRECTION_ICON_LOCAL: Record<string, Component> = {
  meditation: IconMeditation,
  yoga: IconYoga,
  breathwork: IconBreathwork,
}

// -- titles / labels ---------------------------------------------------------

const kind = computed(() => props.item.kind as DiaryEventKind)

const title = computed(() => {
  const base = FEED_KIND_TITLE[kind.value] ?? ''
  if (kind.value === 'checkin') {
    const mood = snapStr('mood')
    return mood ? `${base}: ${MOOD_LABEL[mood] ?? ''}`.trim() : base
  }
  if (kind.value === 'feedback') {
    const rating = snapStr('rating')
    return rating ? `${base}: ${RATING_LABEL[rating] ?? ''}`.trim() : base
  }
  // booking_confirmed shows the practice title on the second banner line,
  // so the title line stays the kind label ("Вы записались").
  return base
})

const preview = computed(() => {
  // Standard cards: content preview (note/dream) or comment (checkin/feedback).
  return snapStr('content_preview') ?? snapStr('comment_preview') ?? snapStr('comment')
})

// -- banner ------------------------------------------------------------------

const bannerTone = computed<'teal' | 'neutral'>(() =>
  kind.value === 'booking_confirmed' ? 'teal' : 'neutral',
)

const bannerSubtitle = computed(() => {
  // booking_confirmed: practice title on the 2nd line.
  // reschedule: old -> new time. cancel: practice title if present.
  if (kind.value === 'booking_confirmed' || kind.value === 'practice_cancelled_by_master') {
    return snapStr('practice_title')
  }
  if (kind.value === 'practice_rescheduled') {
    const oldAt = snapStr('old_scheduled_at')
    const newAt = snapStr('new_scheduled_at') ?? snapStr('scheduled_at')
    if (oldAt && newAt) {
      return `${formatDate(oldAt, tz.value)} → ${formatDate(newAt, tz.value)}`
    }
    return snapStr('practice_title')
  }
  // booking_cancelled_by_user
  return snapStr('practice_title')
})

// -- practice ----------------------------------------------------------------

const practiceTitle = computed(
  () => snapStr('practice_title') ?? 'Практика',
)
const masterName = computed(() => snapStr('master_name') ?? '')
const masterAvatarUrl = computed(() => snapStr('master_avatar_url'))
const masterVerified = computed(() => snap.value['master_verified'] === true)

const practiceDate = computed(() => {
  const at = snapStr('scheduled_at')
  return at ? formatDate(at, tz.value) : ''
})

const outcomeStatus = computed(() => snapStr('outcome_status') ?? 'attended')
const outcomeLabel = computed(
  () => OUTCOME_LABEL[outcomeStatus.value] ?? '',
)

const directionIcon = computed<Component>(() => {
  const dir = snapStr('direction') ?? ''
  // Neutral placeholder (not IconMeditation) for unmapped directions.
  return DIRECTION_ICON_LOCAL[dir] ?? IconDots
})

// -- standard icon -----------------------------------------------------------

const standardIcon = computed<Component>(() => {
  switch (kind.value) {
    case 'checkin':
      return MOOD_ICON[snapStr('mood') ?? 'mid'] ?? IconMoodMid
    case 'feedback':
      return RATING_ICON[snapStr('rating') ?? 'good'] ?? IconRatingGood
    case 'note':
      return IconPen
    case 'dream':
      return IconDreamBook
    default:
      return IconPen
  }
})

// Mood faces are illustrative (default 40); glyphs read better a touch smaller.
const standardIconSize = computed(() =>
  kind.value === 'checkin' ? 37 : 32,
)

// -- date line ---------------------------------------------------------------

const dateLine = computed(() =>
  formatFeedDateTime(props.item.occurred_at, tz.value),
)

// -- interaction -------------------------------------------------------------

const editable = computed(
  () => kind.value === 'note' || kind.value === 'dream',
)

function onTap(): void {
  emit('tap', { item: props.item, editable: editable.value })
}
</script>

<style scoped>
/* All colors/spacing via design tokens (variables.css) -- no hardcoded hex
   (P1 audit) and no ad-hoc px for padding/margin/gap (P3 audit). Font sizes
   use the exact Figma values (16 / 12.375px); the type scale has no 16px
   token and the audit does not gate font-size. */

.feed-card {
  width: 100%;
  box-sizing: border-box;
  font-family: var(--font-body);
  color: var(--velo-text-primary);
}

/* ---------------- Banner ---------------- */

.feed-card--banner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: 1.829px solid;
  text-align: center;
}

.feed-card--banner-teal {
  background: var(--velo-glass-teal-40);
  border-color: var(--velo-teal-400);
  color: var(--velo-teal-600);
}

.feed-card--banner-neutral {
  background: var(--velo-glass-blue-15);
  border-color: var(--velo-border);
  color: var(--velo-text-secondary);
}

.feed-card__banner-title {
  font-size: 12px;
  letter-spacing: 0.24px;
}

.feed-card__banner-subtitle {
  font-size: 12px;
  letter-spacing: 0.24px;
  opacity: 0.85;
}

/* ---------------- Practice ---------------- */

.feed-card--practice {
  position: relative;
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Practice card is tappable (-> practice detail). */
.feed-card--tappable {
  cursor: pointer;
}

.feed-card__practice-title {
  font-size: 16px;
  text-align: center;
  letter-spacing: 0.32px;
}

.feed-card__practice-master {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
}

.feed-card__avatar {
  width: 14px;
  height: 14px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-40);
  overflow: hidden;
  flex-shrink: 0;
}

.feed-card__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.feed-card__master-name {
  font-size: 12px;
  color: var(--velo-text-secondary);
}

.feed-card__verified {
  color: var(--velo-teal-400);
}

.feed-card__practice-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.feed-card__practice-date {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 12px;
  color: var(--velo-text-secondary);
}

.feed-card__date-icon {
  color: var(--velo-text-secondary);
}

.feed-card__outcome {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 3px var(--space-2);
  border-radius: 4.325px;
  font-size: 12px;
}

.feed-card__outcome--attended {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}

.feed-card__outcome--no_show {
  background: var(--velo-glass-blue-15);
  color: var(--velo-text-secondary);
}

.feed-card__practice-icon {
  position: absolute;
  top: var(--space-3);
  left: var(--space-4);
  color: var(--velo-teal-400);
}

/* ---------------- Standard ---------------- */

.feed-card--standard {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--velo-bg-card-solid);
  text-align: left;
  border: none;
  cursor: pointer;
}

.feed-card__date {
  font-size: 12.375px;
  letter-spacing: 0.2475px;
  opacity: 0.6;
}

.feed-card__body {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  /* Allow the text column to shrink below its content width so long
     previews clamp instead of pushing the card wider. */
  min-width: 0;
}

.feed-card__icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
}

/* Monochrome glyphs take the brand text color; mood faces carry their own
   gradient and ignore this. */
.feed-card__icon--note,
.feed-card__icon--dream {
  color: var(--velo-text-primary);
}

.feed-card__icon--feedback {
  color: var(--velo-teal-400);
}

.feed-card__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.feed-card__title {
  font-size: 16px;
  letter-spacing: 0.32px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.feed-card__preview {
  font-size: 12.375px;
  letter-spacing: 0.2475px;
  opacity: 0.6;
  /* Two-line teaser; the full text opens on tap (Variant B). line-clamp
     supplies the ellipsis, so no white-space/text-overflow here. */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  /* Clip an unbroken long token (e.g. a URL) instead of overflowing. */
  overflow-wrap: anywhere;
}
</style>
