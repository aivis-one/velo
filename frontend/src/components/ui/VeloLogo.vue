<!--
  VELO Frontend -- VeloLogo Component (DS-6)

  Uses the actual VELΘ mandala logo from Design_prototype.
  Two variants: default (colored) and white.
  Logo SVGs are in public/icons/ (too large for inline).

  Props:
    size — width/height in px (default 64)
    variant — 'default' | 'white' (default 'default')
-->

<template>
  <img
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
  }>(),
  { size: 64, variant: 'default' },
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
</style>
