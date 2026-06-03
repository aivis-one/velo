<!--
  VELO Frontend -- VeloLogo Component (DS-6)

  Uses the actual VELΘ mandala logo from Design_prototype.
  Two variants: default (colored) and white.
  Logo SVGs are in public/icons/ (too large for inline).

  Props:
    size    — width/height in px (default 64)
    variant — 'default' | 'white' (default 'default')
    spin    — white only: rotate the mandala ring slowly while the VELΘ wordmark
              stays static. Layers two sliced assets (mandala-white.svg +
              velo-word-filled.svg) so the ring spins and the word does not.
              Motion (operator-tuned): still 0.5s -> ease-in ramp ~4s -> steady
              120s/rev. Respects prefers-reduced-motion.
-->

<template>
  <!-- Spinning white logo: rotating mandala ring under a static filled wordmark.
       The word sits at the ring centre, so rotating around the box centre keeps
       it perfectly still. -->
  <div
    v-if="spin && variant === 'white'"
    class="velo-logo velo-logo--spin"
    :style="{ width: size + 'px', height: size + 'px' }"
  >
    <div class="velo-logo__intro">
      <div class="velo-logo__steady">
        <img
          class="velo-logo__layer velo-logo__mandala"
          src="/icons/mandala-white.png"
          alt=""
          aria-hidden="true"
        />
      </div>
    </div>
    <img
      class="velo-logo__layer velo-logo__word"
      src="/icons/velo-word-filled.svg"
      alt="VELΘ"
    />
  </div>
  <img
    v-else
    :src="logoSrc"
    :width="size"
    :height="size"
    alt="VELΘ"
    class="velo-logo"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    size?: number
    variant?: 'default' | 'white'
    /** White only: slowly rotate the mandala ring with the wordmark static. */
    spin?: boolean
  }>(),
  { size: 64, variant: 'default', spin: false },
)

const logoSrc = computed(() =>
  props.variant === 'white' ? '/icons/logo-white.svg' : '/icons/logo.svg',
)
</script>

<style scoped>
.velo-logo {
  display: block;
  object-fit: contain;
}

.velo-logo--spin {
  position: relative;
}

.velo-logo__layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

/* Operator-calibrated layer offsets (see .handoff preview, calibrated at size 440).
   Expressed as % of the layer (= % of `size`) so they scale with any size.
   The mandala offset sits on the IMG inside the spinning wrappers, so it rotates
   rigidly with the ring -- this places the mandala's visual centre on the rotation
   axis, keeping it spinning in place (px@440: x +8, y -3). */
.velo-logo__mandala {
  transform: translate(1.818%, -0.682%);
}

.velo-logo__word {
  z-index: 2;
  /* px@440: x +1, y -7 */
  transform: translate(0.227%, -1.591%);
}

.velo-logo__intro,
.velo-logo__steady {
  position: absolute;
  inset: 0;
  transform-origin: 50% 50%;
}

/* Stand still 0.5s -> ease-in ramp 4s (one-shot, holds 6deg) -> steady spin
   120s/rev (starts right after the ramp). The ramp ends near the steady angular
   velocity, so the hand-off has no visible jolt. */
.velo-logo__intro {
  animation: velo-logo-intro 4s cubic-bezier(0.45, 0, 0.9, 0.85) 0.5s 1 forwards;
}

.velo-logo__steady {
  animation: velo-logo-steady 120s linear 4.5s infinite;
}

@keyframes velo-logo-intro {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(6deg);
  }
}

@keyframes velo-logo-steady {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Accessibility: no spin for users who prefer reduced motion. */
@media (prefers-reduced-motion: reduce) {
  .velo-logo__intro,
  .velo-logo__steady {
    animation: none;
  }
}
</style>
