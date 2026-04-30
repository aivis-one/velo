<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <circle
      cx="12"
      cy="5"
      r="2"
    />
    <circle
      cx="12"
      cy="12"
      r="2"
    />
    <circle
      cx="12"
      cy="19"
      r="2"
    />
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
