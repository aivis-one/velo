<!--
  VELO Frontend -- Loading View (DS-6)

  Displayed while auth initialization is in progress.
  Shows VELΘ mandala logo with subtle loading spinner.
  Matches 04_OAuth.png mockup style.
-->

<template>
  <div class="loading">
    <div class="loading__logo">
      <VeloLogo :size="120" />
    </div>
    <h1 class="loading__title">VELΘ</h1>
    <div class="loading__spinner" />
  </div>
</template>

<script setup lang="ts">
import VeloLogo from '@/components/ui/VeloLogo.vue'
</script>

<style scoped>
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  background: transparent;
  gap: var(--space-4);
}

.loading__logo {
  animation: pulse 2s ease-in-out infinite;
}

.loading__title {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.loading__spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--velo-border-light);
  border-top-color: var(--velo-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-top: var(--space-4);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
</style>
