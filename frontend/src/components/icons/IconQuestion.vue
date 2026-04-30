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
    <circle
      cx="12"
      cy="12"
      r="10"
    />
    <path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 5" />
    <line
      x1="12"
      y1="17"
      x2="12"
      y2="17.5"
    />
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
