<template>
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
    <path d="M4 4h11a3 3 0 0 1 3 3v13H7a3 3 0 0 1-3-3V4z" />
    <path d="M4 17h14" />
    <path d="M9 7l6 6" />
    <path d="M15 7l-3 3" />
    <path d="M15 7l-3 6" />
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
