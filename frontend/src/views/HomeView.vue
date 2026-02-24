<!--
  VELO Frontend -- Home View (Phase F0.1 placeholder)

  Temporary landing page. Replaced by role-based redirect in Phase F2.
-->

<template>
  <div class="home">
    <div class="home__logo">
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
    <h1 class="home__title">VELO</h1>
    <p class="home__subtitle">Platform for wellness practice facilitators</p>
    <p class="home__version">v0.1.0</p>
  </div>
</template>

<script setup lang="ts">
// No logic needed for placeholder.
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--space-6);
  text-align: center;
  background: var(--velo-bg-start);
}

.home__logo {
  margin-bottom: var(--space-4);
}

.home__title {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--velo-text-primary);
  margin: 0 0 var(--space-2) 0;
  letter-spacing: 0.1em;
}

.home__subtitle {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  margin: 0 0 var(--space-6) 0;
}

.home__version {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  margin: 0;
}
</style>
