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
      r="4"
    />
    <ellipse
      cx="12"
      cy="12"
      rx="10"
      ry="4"
      transform="rotate(-30 12 12)"
    />
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
