<!--
  VELO Frontend -- 404 Not Found (Phase F2.2)
-->

<template>
  <div class="not-found">
    <span class="not-found__icon">🔍</span>
    <h1 class="not-found__title">404</h1>
    <p class="not-found__text">Страница не найдена</p>
    <button class="not-found__btn" @click="router.push('/')">
      На главную
    </button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  text-align: center;
  padding: var(--space-6);
  background: var(--velo-bg-start);
}
.not-found__icon { font-size: 64px; margin-bottom: var(--space-4); }
.not-found__title {
  font-family: var(--font-heading);
  font-size: 48px;
  font-weight: 700;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-2);
}
.not-found__text {
  font-size: var(--text-lg);
  color: var(--velo-text-muted);
  margin-bottom: var(--space-6);
}
.not-found__btn {
  padding: 12px 24px;
  background: var(--velo-primary);
  color: white;
  font-weight: 600;
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
  transition: background var(--transition-base);
}
.not-found__btn:hover {
  background: var(--velo-primary-dark);
}
</style>
