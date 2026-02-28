<!--
  VELO Frontend -- Семафоры (Phase F2.2 stub)
  Implementation: Phase F8.3
-->

<template>
  <div class="view-stub">
    <span class="view-stub__icon">🚦</span>
    <h2 class="view-stub__title">Семафоры</h2>
    <p class="view-stub__phase">Phase F8.3</p>
  </div>
</template>

<style scoped>
.view-stub {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: var(--space-6);
}
.view-stub__icon { font-size: 48px; margin-bottom: var(--space-3); }
.view-stub__title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  color: var(--velo-text-primary);
  margin-bottom: var(--space-2);
}
.view-stub__phase {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
}
</style>
