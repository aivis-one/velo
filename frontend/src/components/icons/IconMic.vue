<template>
  <!-- Microphone glyph for the composer (voice input -- stub in this
       iteration: tapping shows a "coming soon" toast). Monochrome
       currentColor, DS contract. -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M12 2a3.5 3.5 0 0 0-3.5 3.5v6a3.5 3.5 0 0 0 7 0v-6A3.5 3.5 0 0 0 12 2Z" />
    <path d="M5.5 11a.9.9 0 0 1 .9.9 5.6 5.6 0 0 0 11.2 0 .9.9 0 1 1 1.8 0 7.4 7.4 0 0 1-6.5 7.34V21h2.3a.9.9 0 0 1 0 1.8H8.8a.9.9 0 0 1 0-1.8h2.3v-1.76A7.4 7.4 0 0 1 4.6 11.9a.9.9 0 0 1 .9-.9Z" />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
