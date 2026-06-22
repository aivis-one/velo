<!--
  VELO Frontend -- VRatingDistribution (shared, WS-3b T2)

  Rating-distribution bars (Огонь! / Хорошо / Есть вопросы) on a VCard plate.
  Extracted verbatim from AnalyticsView «Общая статистика» and
  PracticeReviewsView «Распределение» (identical markup + CSS).

  API = COUNTS-IN: the caller passes raw feedback counts; the component owns the
  bar config (icons/labels), the two palettes (fill = RATING_COLOR, accent =
  RATING_ICON_COLOR), the percentage maths and the bar markup/CSS. Bars render
  even at 0% (empty distribution) — same as the originals.

  Usage:
    <VRatingDistribution :fire="12" :good="5" :confused="2" />
-->

<template>
  <VCard class="v-rating-dist">
    <div v-for="bar in bars" :key="bar.key" class="v-rating-dist__row">
      <span class="v-rating-dist__head">
        <component :is="bar.icon" :size="22" :style="{ color: bar.iconColor }" />
        {{ bar.label }}
      </span>
      <div class="v-rating-dist__track">
        <div
          class="v-rating-dist__fill"
          :style="{ width: `${bar.pct}%`, background: bar.barColor }"
        />
      </div>
      <span class="v-rating-dist__meta">{{ bar.pct }}% ({{ bar.count }})</span>
    </div>
  </VCard>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { VCard } from '@/components/ui'
import { IconRatingFire, IconRatingGood, IconRatingConfused } from '@/components/icons'
import { RATING_COLOR, RATING_ICON_COLOR } from '@/utils/displayHelpers'

const props = defineProps<{
  /** Raw "огонь" feedback count. */
  fire: number
  /** Raw "хорошо" feedback count. */
  good: number
  /** Raw "есть вопросы" feedback count. */
  confused: number
}>()

interface RatingBar {
  key: 'fire' | 'good' | 'confused'
  icon: Component
  label: string
  count: number
  pct: number
  iconColor: string
  barColor: string
}

// Bar fill = RATING_COLOR (peach-300 / pink-300 / blue-400); icon accent =
// RATING_ICON_COLOR (--velo-rating-*). Two palettes on purpose (see displayHelpers).
const RATING_BARS_CONFIG: Array<{
  key: 'fire' | 'good' | 'confused'
  icon: Component
  label: string
}> = [
  { key: 'fire', icon: IconRatingFire, label: 'Огонь!' },
  { key: 'good', icon: IconRatingGood, label: 'Хорошо' },
  { key: 'confused', icon: IconRatingConfused, label: 'Есть вопросы' },
]

const bars = computed((): RatingBar[] => {
  const totals = { fire: props.fire, good: props.good, confused: props.confused }
  const total = totals.fire + totals.good + totals.confused
  return RATING_BARS_CONFIG.map((cfg) => ({
    ...cfg,
    iconColor: RATING_ICON_COLOR[cfg.key],
    barColor: RATING_COLOR[cfg.key],
    count: totals[cfg.key],
    pct: total > 0 ? Math.round((totals[cfg.key] / total) * 100) : 0,
  }))
})
</script>

<style scoped>
.v-rating-dist {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.v-rating-dist__row {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.v-rating-dist__head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.v-rating-dist__track {
  height: 10px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  overflow: hidden;
}

.v-rating-dist__fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.4s ease;
}

.v-rating-dist__meta {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}
</style>
