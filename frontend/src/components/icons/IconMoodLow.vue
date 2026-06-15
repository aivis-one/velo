<template>
  <!-- Mood face: low ("Не очень"). Illustrative asset with its own pastel
       gradient (kept as-is by design, like VeloLogo) -- not a monochrome
       currentColor icon. Gradient id is made unique per-instance to avoid
       clashes when several mood faces render on the same screen. -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="4.85156 0 40.4352 40.4352"
    fill="none"
  >
    <rect x="4.85156" width="40.4352" height="40.4352" rx="20.2176" :fill="`url(#${gid})`" />
    <path
      d="M39.4472 16.9826L35.7722 19.9374L40.1088 21.7895"
      stroke="#4C6589"
      stroke-width="1.2767"
      stroke-linecap="round"
    />
    <path
      d="M11.17 16.9826L14.845 19.9374L10.5084 21.7895"
      stroke="#4C6589"
      stroke-width="1.2767"
      stroke-linecap="round"
    />
    <path
      d="M30.7285 24.1099C27.2801 21.893 22.8551 21.893 19.4067 24.1099"
      stroke="#4C6589"
      stroke-width="1.2767"
      stroke-linecap="round"
    />
    <defs>
      <linearGradient
        :id="gid"
        x1="4.85156"
        y1="20.2176"
        x2="45.2868"
        y2="20.2176"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="#DCE6F3" />
        <stop offset="1" stop-color="#BDECF1" />
      </linearGradient>
    </defs>
  </svg>
</template>

<script setup lang="ts">
import { useId } from 'vue'

withDefaults(defineProps<{ size?: number | string }>(), { size: 40 })

// Unique gradient id per component instance (avoids duplicate-id clashes).
const gid = `mood-low-${useId()}`
</script>
