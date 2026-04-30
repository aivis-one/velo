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
    <path d="M5 12V7a2 2 0 0 1 4 0v5" />
    <path d="M9 12V5a2 2 0 0 1 4 0v7" />
    <path d="M13 12V7a2 2 0 0 1 4 0v8a6 6 0 0 1-6 6h-2c-2 0-3-1-4-3l-2-4a2 2 0 0 1 4-2l1 2" />
    <line
      x1="3"
      y1="3"
      x2="5"
      y2="5"
    />
    <line
      x1="19"
      y1="3"
      x2="17"
      y2="5"
    />
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
