<!--
  VELO Frontend -- VRatingBadges (DS, extracted 2026-06-17)

  The fire / good / confused rating-distribution badge trio, each a coloured
  chip with its bucket icon + percentage. Previously duplicated inline in
  AnalyticsView (past-practice cards), MasterPracticesView (past cards) and
  MasterPracticeDetailView (PAST hero). DRY extraction — same visual.

  Colours are the rating palette (sand/pink/blue fills + --velo-rating-* /
  --velo-blue-400 accents), matching the anonymous-insights distribution.

  size:
    'sm' (default) -- list / analytics cards (icon 14).
    'lg'           -- practice-detail hero (icon 16).

  Usage:
    <VRatingBadges :fire="58" :good="30" :confused="12" />
    <VRatingBadges :fire="f" :good="g" :confused="c" size="lg" />
-->

<template>
  <div class="v-rating-badges" :class="`v-rating-badges--${size}`">
    <span class="v-rating-badges__badge v-rating-badges__badge--fire">
      <IconRatingFire :size="iconSize" />{{ fire }}%
    </span>
    <span class="v-rating-badges__badge v-rating-badges__badge--good">
      <IconRatingGood :size="iconSize" />{{ good }}%
    </span>
    <span class="v-rating-badges__badge v-rating-badges__badge--confused">
      <IconRatingConfused :size="iconSize" />{{ confused }}%
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IconRatingFire, IconRatingGood, IconRatingConfused } from '@/components/icons'

const props = withDefaults(
  defineProps<{
    /** Percent in the fire bucket (rating 8-10). */
    fire: number
    /** Percent in the good bucket (rating 4-7). */
    good: number
    /** Percent in the confused bucket (rating 1-3). */
    confused: number
    /** 'sm' (list/analytics cards, icon 14) or 'lg' (practice-detail hero, icon 16). */
    size?: 'sm' | 'lg'
  }>(),
  { size: 'sm' },
)

const iconSize = computed((): number => (props.size === 'lg' ? 16 : 14))
</script>

<style scoped>
.v-rating-badges {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.v-rating-badges__badge {
  display: inline-flex;
  align-items: center;
  gap: var(--velo-card-gap-icon-title);
  border-radius: var(--velo-radius-badge);
  font-size: var(--text-xs);
}

.v-rating-badges--sm .v-rating-badges__badge {
  padding: 4px 10px;
}

.v-rating-badges--lg .v-rating-badges__badge {
  padding: 3px 12px;
}

.v-rating-badges__badge--fire {
  background: var(--velo-sand-100);
  color: var(--velo-rating-fire);
}

.v-rating-badges__badge--good {
  background: var(--velo-pink-100);
  color: var(--velo-rating-good);
}

.v-rating-badges__badge--confused {
  background: var(--velo-blue-100);
  color: var(--velo-blue-400);
}
</style>
