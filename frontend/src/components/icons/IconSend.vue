<template>
  <!-- Upward arrow "send" glyph for the composer submit button.
       Monochrome currentColor, DS contract. -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M12 3a1 1 0 0 1 .71.29l6 6a1 1 0 0 1-1.42 1.42L13 6.41V20a1 1 0 0 1-2 0V6.41l-4.29 4.3a1 1 0 0 1-1.42-1.42l6-6A1 1 0 0 1 12 3Z" />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
