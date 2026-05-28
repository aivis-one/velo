<!--
  VELO Frontend -- PracticePlaceholder (shared)

  Themed 336x199 placeholder used in place of a real video stream on the
  practice screens (PracticeLiveView) and anywhere we need a "video would
  be here" visual that hints at the practice direction.

  Layout: glass-blue card with one large centered direction icon (white,
  ~80px), DS-aligned border + glow shadow. Picks the icon via the same
  DIRECTION_ICON map used by PracticeHeroCard / PracticeListCard so a
  single Icon{Direction}.vue component drives every surface.

  Props:
    direction -- PracticeDirection key. When undefined / unknown, falls back
                 to the neutral IconDots glyph (same as DIRECTION_ICON_FALLBACK).
    title     -- optional title for PracticeSummary callers that don't carry
                 direction yet (handoff §9 B-1) — title heuristic mirrors
                 displayHelpers.practiceIconFor.

  Usage:
    <PracticePlaceholder :direction="practice?.direction" />
-->

<template>
  <div class="ph">
    <component :is="iconComponent" class="ph__icon" :size="80" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { practiceIconFor } from '@/utils/displayHelpers'
import type { PracticeDirection } from '@/api/types'

const props = withDefaults(
  defineProps<{
    direction?: PracticeDirection | string | null
    title?: string | null
  }>(),
  {
    direction: null,
    title: null,
  },
)

const iconComponent = computed(() =>
  practiceIconFor({ direction: props.direction ?? null, title: props.title ?? null }),
)
</script>

<style scoped>
.ph {
  width: 336px;
  max-width: 100%;
  aspect-ratio: 336 / 199;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--velo-glass-blue-60);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  box-shadow: var(--velo-shadow-glow);
}

.ph__icon {
  color: #ffffff;
}
</style>
