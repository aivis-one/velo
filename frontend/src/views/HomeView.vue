<!--
  VELO Frontend -- Home View (DS-6)

  Landing page after auth. Shows VELΘ mandala logo, greeting, role badge.
  Glassmorphism styling, Marmelad font, transparent bg.
-->

<template>
  <div class="home">
    <div class="home__logo">
      <VeloLogo :size="120" />
    </div>
    <h1 class="home__title">VELΘ</h1>
    <div v-if="user" class="home__user">
      <p class="home__greeting">{{ greeting }}, {{ user.first_name }}!</p>
      <div class="home__details">
        <span class="home__role">{{ user.role }}</span>
      </div>
    </div>
    <p class="home__version">v0.1.0</p>
    <button v-if="user" class="home__logout" @click="handleLogout">
      Выйти
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import VeloLogo from '@/components/ui/VeloLogo.vue'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return 'Доброй ночи'
  if (hour < 12) return 'Доброе утро'
  if (hour < 18) return 'Добрый день'
  return 'Добрый вечер'
})

async function handleLogout(): Promise<void> {
  await authStore.logout()
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--space-5);
  text-align: center;
  background: transparent;
}

.home__logo {
  margin-bottom: var(--space-4);
}

.home__title {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0 0 var(--space-5) 0;
  letter-spacing: 0.02em;
}

.home__user {
  margin-bottom: var(--space-5);
}

.home__greeting {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0 0 var(--space-2) 0;
}

.home__details {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
}

.home__role {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  background: var(--velo-glass-blue-60);
  color: var(--velo-text-primary);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  text-transform: uppercase;
  border-radius: var(--radius-full);
  letter-spacing: 0.02em;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.home__version {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  margin: 0 0 var(--space-5) 0;
}

.home__logout {
  padding: var(--space-2) var(--space-5);
  background: var(--velo-glass-white-01);
  color: var(--velo-text-secondary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  border: 1px solid var(--velo-glass-border);
  border-radius: var(--radius-full);
  cursor: pointer;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  transition: opacity var(--transition-fast);
}

.home__logout:hover {
  opacity: 0.8;
}
</style>
