<!--
  VELO Frontend -- VLoader Component (Phase F2.1)

  CSS-only loading spinner. Matches LoadingView spinner style.

  Usage:
    <VLoader />
    <VLoader size="lg" />
-->

<template>
  <div class="v-loader" :class="`v-loader--${size}`" />
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: 'sm' | 'md' | 'lg'
  }>(),
  {
    size: 'md',
  },
)
</script>

<style scoped>
.v-loader {
  border-style: solid;
  border-color: var(--velo-border);
  border-top-color: var(--velo-primary);
  border-radius: var(--radius-full);
  animation: v-loader-spin 0.7s linear infinite;
}

.v-loader--sm {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

.v-loader--md {
  width: 32px;
  height: 32px;
  border-width: 3px;
}

.v-loader--lg {
  width: 48px;
  height: 48px;
  border-width: 4px;
}

@keyframes v-loader-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
