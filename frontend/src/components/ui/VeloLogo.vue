<!--
  VELO Frontend -- VeloLogo Component (Fix 10.8)

  Shared SVG logo. Was copy-pasted in HomeView, LoadingView,
  StandaloneStubView. Now a single source of truth.

  Props:
    size — width/height in px (default 64)
-->

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 64 64"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="32" cy="32" r="30" fill="var(--velo-primary)" />
    <text
      x="32"
      y="40"
      text-anchor="middle"
      fill="white"
      font-size="24"
      font-weight="700"
      font-family="system-ui, sans-serif"
    >V</text>
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 64 })
</script>
