<template>
  <!-- Light decorative flourish flanking a timeline date node. A small
       leaf-on-a-stem curl. Monochrome currentColor; `mirrored` flips it
       horizontally so the same glyph works on both sides of the date.
       (The authentic Figma ornament is a 31KB masked SVG -- intentionally
       not used here; this is the lightweight stand-in.) -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    :style="mirrored ? 'transform: scaleX(-1)' : undefined"
  >
    <!-- stem -->
    <path d="M5 19c4-1 7-4 9-8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
    <!-- upper leaf -->
    <path
      d="M14 11c1.2-2.4 3.4-3.6 5.8-3.4-.2 2.4-1.6 4.4-3.8 5.2-.9.3-1.6.1-2-.4-.4-.5-.4-1 0-1.4Z"
      fill="currentColor"
    />
    <!-- lower leaf -->
    <path
      d="M9 15c-.4-1.9.3-3.7 1.9-4.9 1 1.5 1.1 3.4.2 5-.4.6-.9.9-1.4.7-.4-.1-.6-.5-.7-.8Z"
      fill="currentColor"
      opacity="0.7"
    />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string; mirrored?: boolean }>(), {
  size: 24,
  mirrored: false,
})
</script>
