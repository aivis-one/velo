<template>
  <!-- Mood face: high ("Хорошо"). Illustrative asset with its own pastel
       gradient (kept as-is by design). Gradient id unique per-instance. -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 40 40"
    fill="none"
  >
    <rect width="40" height="40" rx="20" :fill="`url(#${gid})`" />
    <path
      d="M14.4003 23.2002C17.8116 25.3932 22.189 25.3932 25.6003 23.2002"
      stroke="#4C6589"
      stroke-width="1.27667"
      stroke-linecap="round"
    />
    <path
      d="M4.79883 18.3999C6.15947 20.3437 9.03818 20.3437 10.3988 18.3999"
      stroke="#4C6589"
      stroke-width="1.27667"
      stroke-linecap="round"
    />
    <path
      d="M28.7988 18.3999C30.1595 20.3437 33.0382 20.3437 34.3988 18.3999"
      stroke="#4C6589"
      stroke-width="1.27667"
      stroke-linecap="round"
    />
    <defs>
      <linearGradient :id="gid" x1="0" y1="20" x2="40" y2="20" gradientUnits="userSpaceOnUse">
        <stop stop-color="#F9CBD1" />
        <stop offset="1" stop-color="#FDDFC4" />
      </linearGradient>
    </defs>
  </svg>
</template>

<script setup lang="ts">
import { useId } from 'vue'

withDefaults(defineProps<{ size?: number | string }>(), { size: 40 })

// Unique gradient id per component instance (avoids duplicate-id clashes).
const gid = `mood-high-${useId()}`
</script>
