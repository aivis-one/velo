<!--
  VELO Frontend -- Home View (Phase 0 placeholder)

  Minimal placeholder. No store dependencies.
  Will be replaced when shells and auth flow are implemented.
-->

<template>
  <div class="home">
    <p class="home__title">VELΘ</p>
    <p class="home__version">v0.2.0</p>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  text-align: center;
}

.home__title {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  color: var(--velo-text-primary);
}

.home__version {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  margin-top: var(--space-2);
}
</style>