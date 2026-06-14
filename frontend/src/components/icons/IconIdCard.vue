<!--
  VELO Frontend -- IconIdCard (Admin DS 2026-06-14, operator SVG "2 Master's request")

  ID-card placeholder glyph for the master-application profile card when no avatar
  photo is set. Single-tone (currentColor), outline style, matches the operator
  reference. Aspect 120×96 — letterboxed into a square size box.
-->
<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 120 96"
    fill="none"
    preserveAspectRatio="xMidYMid meet"
  >
    <rect x="4" y="4" width="112" height="88" rx="16" stroke="currentColor" stroke-width="5" />
    <circle cx="60" cy="40" r="15" stroke="currentColor" stroke-width="5" />
    <path
      d="M38 78c0-13 10-21 22-21s22 8 22 21"
      stroke="currentColor"
      stroke-width="5"
      stroke-linecap="round"
    />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
