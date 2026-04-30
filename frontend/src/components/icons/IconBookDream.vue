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
    <path d="M14 8a3.5 3.5 0 1 0 3 3 2.6 2.6 0 0 1-3-3z" />
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
