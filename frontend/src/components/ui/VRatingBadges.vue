<!--
  VELO Frontend -- VRatingBadges (DS, extracted 2026-06-17)

  The fire / good / confused rating-distribution badge trio, each a coloured
  chip with its bucket icon + percentage. Previously duplicated inline in
  AnalyticsView (past-practice cards), MasterPracticesView (past cards) and
  MasterPracticeDetailView (PAST hero). DRY extraction — same visual.

  Colours are the rating palette (sand/pink/blue fills + --velo-rating-* /
  --velo-blue-400 accents), matching the anonymous-insights distribution.

  A «?» (IconHint) trailing the trio opens a bottom-sheet that explains what the
  ratings mean (operator 2026-06-18 — the percentages were unclear). The trigger
  stops propagation so it never fires the click of a surrounding card.

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

    <!-- «?» — что значат проценты (статичное описание, без расчётов).
         Скрывается через :hint="false" (мастер-карта / детали — operator ПРОМТ №159). -->
    <button
      v-if="hint"
      type="button"
      class="v-rating-badges__info"
      aria-label="Что значат оценки?"
      @click.stop="open = true"
    >
      <IconHint :size="iconSize" />
    </button>

    <VBottomSheet :open="open" title="Оценки участников" @close="open = false">
      <p class="v-rating-badges__intro">
        После практики участники анонимно ставят оценку. Проценты — доля каждой оценки среди
        ответивших.
      </p>
      <ul class="v-rating-badges__legend">
        <li class="v-rating-badges__legend-row">
          <span class="v-rating-badges__badge v-rating-badges__badge--fire">
            <IconRatingFire :size="16" />Огонь!
          </span>
          <span class="v-rating-badges__legend-desc">практика очень понравилась, вдохновила.</span>
        </li>
        <li class="v-rating-badges__legend-row">
          <span class="v-rating-badges__badge v-rating-badges__badge--good">
            <IconRatingGood :size="16" />Хорошо
          </span>
          <span class="v-rating-badges__legend-desc">понравилась, прошла хорошо.</span>
        </li>
        <li class="v-rating-badges__legend-row">
          <span class="v-rating-badges__badge v-rating-badges__badge--confused">
            <IconRatingConfused :size="16" />Есть вопросы
          </span>
          <span class="v-rating-badges__legend-desc">
            остались сомнения или непонятные моменты.
          </span>
        </li>
      </ul>
    </VBottomSheet>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { IconRatingFire, IconRatingGood, IconRatingConfused, IconHint } from '@/components/icons'
import VBottomSheet from '@/components/ui/VBottomSheet.vue'

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
    /** Show the trailing «?» explainer trigger. Default true; pass false to hide it. */
    hint?: boolean
  }>(),
  { size: 'sm', hint: true },
)

const iconSize = computed((): number => (props.size === 'lg' ? 16 : 14))
const open = ref(false)
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

/* «?» trigger — muted, unobtrusive; sits after the trio. */
.v-rating-badges__info {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  border: none;
  background: transparent;
  color: var(--velo-text-muted);
  cursor: pointer;
}

/* -- Description sheet -- */
.v-rating-badges__intro {
  margin: 0 0 18px;
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.5;
}

.v-rating-badges__legend {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.v-rating-badges__legend-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.v-rating-badges__legend-row .v-rating-badges__badge {
  flex-shrink: 0;
  padding: 4px 10px;
}

.v-rating-badges__legend-desc {
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  line-height: 1.4;
}
</style>
