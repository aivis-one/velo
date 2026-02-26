<!--
  VELO Frontend -- Loading View (Phase F1.3)

  Displayed while auth initialization is in progress.
  Shows VELO logo + subtle loading indicator.
  Replaced by actual content once auth completes.
-->

<template>
  <div class="loading">
    <div class="loading__logo">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
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
    </div>
    <h1 class="loading__title">VELO</h1>
    <div class="loading__spinner" />
  </div>
</template>

<script setup lang="ts">
// No logic -- purely visual placeholder during auth.
</script>

<style scoped>
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--velo-bg-start);
  gap: var(--space-4);
}

.loading__logo {
  animation: pulse 2s ease-in-out infinite;
}

.loading__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--velo-text-primary);
  letter-spacing: 0.1em;
  margin: 0;
}

.loading__spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--velo-border);
  border-top-color: var(--velo-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-top: var(--space-4);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
