<template>
  <!-- Pen / quill glyph for diary "note" cards (Дневник). Monochrome
       currentColor, fits the card-icon DS contract (size prop, no inline
       color). Shape: a writing nib with a stroke line under it. -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M16.7 2.29a1 1 0 0 1 1.41 0l3.6 3.6a1 1 0 0 1 0 1.41l-11 11a1 1 0 0 1-.46.26l-5 1.34a1 1 0 0 1-1.22-1.22l1.34-5a1 1 0 0 1 .26-.46l11-11Zm.7 2.12-1.3 1.3 2.18 2.18 1.3-1.3-2.18-2.18ZM6.43 14.66l-1.9.51a.5.5 0 0 0-.35.35l-.51 1.9 1.41 1.41 1.9-.51a.5.5 0 0 0 .35-.35l.51-1.9-1.41-1.41Z" />
    <path d="M3 21.5h9a.75.75 0 0 1 0 1.5H3a.75.75 0 0 1 0-1.5Z" opacity="0.55" />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
