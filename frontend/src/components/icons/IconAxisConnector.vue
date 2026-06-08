<!--
  VELO Frontend -- IconAxisConnector (Diary map: date-node -> first card link)

  The vertical bead-link that sits on the thread axis between a date node and
  the first card of that day (Figma Group 2429): a top ring (r=2.5) + a thin
  stroke + a small bead (r=1.1) + a bottom bead (r=2.38). 1:1 from the export.
  Colour via currentColor.
-->
<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="6"
    :height="height"
    viewBox="0 0 6 31"
    fill="currentColor"
    aria-hidden="true"
  >
    <path d="M2.87695 28.1241L2.87695 3.19629" stroke="currentColor" />
    <path d="M3 5.5C1.61929 5.5 0.5 4.38071 0.5 3C0.500001 1.61929 1.61929 0.5 3 0.5C4.38071 0.5 5.5 1.61929 5.5 3C5.5 4.38071 4.38071 5.5 3 5.5Z" stroke="currentColor" />
    <circle cx="2.87762" cy="28.1237" r="2.37629" transform="rotate(-180 2.87762 28.1237)" stroke="currentColor" />
    <circle cx="2.87667" cy="15.3415" r="1.09794" transform="rotate(-180 2.87667 15.3415)" stroke="currentColor" />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Source is 6×31; keep ratio when only height is driven.
const props = withDefaults(defineProps<{ size?: number }>(), { size: 31 })
const height = computed(() => props.size)
</script>
