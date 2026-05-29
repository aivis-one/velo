<template>
  <!-- Share glyph for "Поделиться" (Profile). The Figma node exports as an
       empty (mask-only) vector, so this is a clean standard share icon drawn
       in the same DS stroke style as IconArrowRight (currentColor, viewBox
       24). Three nodes connected by two links. -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <circle cx="18" cy="5" r="3" />
    <circle cx="6" cy="12" r="3" />
    <circle cx="18" cy="19" r="3" />
    <path d="M8.6 13.5L15.4 17.5" />
    <path d="M15.4 6.5L8.6 10.5" />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
