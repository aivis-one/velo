<template>
  <!-- Mood face: mid ("Нормально"). Illustrative asset with its own pastel
       gradient (kept as-is by design). Gradient id unique per-instance. -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 40 40"
    fill="none"
  >
    <rect width="40" height="40" rx="20" :fill="`url(#${gid})`" />
    <circle cx="13" cy="19" r="2" fill="#4C6589" />
    <circle cx="27" cy="19" r="2" fill="#4C6589" />
    <path d="M14.3987 23.2002H25.5987" stroke="#4C6589" stroke-width="1.24101" stroke-linecap="round" />
    <defs>
      <linearGradient :id="gid" x1="0" y1="20" x2="40" y2="20" gradientUnits="userSpaceOnUse">
        <stop stop-color="#BDECF1" />
        <stop offset="1" stop-color="#F9CBD1" />
      </linearGradient>
    </defs>
  </svg>
</template>

<script setup lang="ts">
import { useId } from 'vue'

withDefaults(defineProps<{ size?: number | string }>(), { size: 40 })

// Unique gradient id per component instance (avoids duplicate-id clashes).
const gid = `mood-mid-${useId()}`
</script>
