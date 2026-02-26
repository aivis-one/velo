<!--
  VELO Frontend -- Home View (Phase F1.3, fixed 10.7)

  FIX 10.7: logout uses Vue reactivity, no window.location.reload().
  App.vue watches isAuthenticated and shows StandaloneStub automatically.
-->

<template>
  <div class="home">
    <div class="home__logo">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="32" cy="32" r="30" fill="var(--velo-primary)" />
        <text x="32" y="40" text-anchor="middle" fill="white" font-size="24" font-weight="700" font-family="system-ui, sans-serif">V</text>
      </svg>
    </div>
    <h1 class="home__title">VELO</h1>
    <div v-if="user" class="home__user">
      <p class="home__greeting">{{ greeting }}, {{ user.first_name }}!</p>
      <div class="home__details">
        <span class="home__role">{{ user.role }}</span>
        <span class="home__id">@{{ user.username || 'no username' }}</span>
      </div>
    </div>
    <p class="home__version">v0.1.0</p>
    <button v-if="user" class="home__logout" @click="handleLogout">Выйти</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return 'Доброй ночи'
  if (hour < 12) return 'Доброе утро'
  if (hour < 18) return 'Добрый день'
  return 'Добрый вечер'
})

// FIX 10.7: no reload — App.vue reactivity shows stub when isAuthenticated becomes false.
async function handleLogout(): Promise<void> {
  await authStore.logout()
}
</script>

<style scoped>
.home {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 100vh; min-height: 100dvh; padding: var(--space-6);
  text-align: center; background: var(--velo-bg-start);
}
.home__logo { margin-bottom: var(--space-4); }
.home__title {
  font-family: var(--font-heading); font-size: var(--text-3xl); font-weight: 700;
  color: var(--velo-text-primary); margin: 0 0 var(--space-6) 0; letter-spacing: 0.1em;
}
.home__user { margin-bottom: var(--space-6); }
.home__greeting { font-size: var(--text-xl); font-weight: 600; color: var(--velo-text-primary); margin: 0 0 var(--space-2) 0; }
.home__details { display: flex; align-items: center; justify-content: center; gap: var(--space-3); }
.home__role {
  display: inline-block; padding: var(--space-1) var(--space-3); background: var(--velo-primary);
  color: white; font-size: var(--text-xs); font-weight: 700; text-transform: uppercase;
  border-radius: var(--radius-full); letter-spacing: 0.05em;
}
.home__id { font-size: var(--text-sm); color: var(--velo-text-muted); }
.home__version { font-size: var(--text-xs); color: var(--velo-text-muted); margin: 0 0 var(--space-6) 0; }
.home__logout {
  padding: var(--space-2) var(--space-5); background: transparent; color: var(--velo-text-muted);
  font-size: var(--text-sm); border: 1px solid var(--velo-border); border-radius: var(--radius-md);
  cursor: pointer; transition: all var(--transition-fast);
}
.home__logout:hover { color: var(--velo-error); border-color: var(--velo-error); }
</style>
