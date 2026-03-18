<!--
  VELO Frontend -- AdminProfileView (TD-FE-ROLE-SWITCH)

  Minimal admin profile screen. Route: /admin/profile (tab "Я").

  Sections:
    1. Profile header -- avatar, display name, admin badge.
    2. Switch to user mode -- button visible to all admins.
       Sets uiMode = 'user' and navigates to /user/profile.
    3. Logout.
-->

<template>
  <div class="admin-profile">
    <!-- Header -->
    <div class="admin-profile__header">
      <VAvatar :name="displayName" size="xl" />
      <div class="admin-profile__header-info">
        <h1 class="admin-profile__name">{{ displayName }}</h1>
        <VBadge variant="info">Администратор</VBadge>
      </div>
    </div>

    <!-- Switch to user mode -->
    <div class="admin-profile__section">
      <div class="admin-profile__section-title">РЕЖИМ ПРОСМОТРА</div>
      <p class="admin-profile__section-desc">
        Перейдите в интерфейс пользователя, чтобы просматривать каталог и бронировать практики.
      </p>
      <VButton variant="secondary" @click="switchToUserMode">
        Перейти в интерфейс пользователя →
      </VButton>
    </div>

    <!-- Logout -->
    <div class="admin-profile__section">
      <VButton variant="ghost" :loading="loggingOut" @click="onLogout">
        🚪 Выйти
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VAvatar, VBadge, VButton } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()

const loggingOut = ref(false)

const displayName = computed(() => {
  if (!authStore.user) return 'Администратор'
  const parts = [authStore.user.first_name, authStore.user.last_name].filter(Boolean)
  return parts.length > 0 ? parts.join(' ') : 'Администратор'
})

// -- Switch to user mode --
function switchToUserMode(): void {
  uiStore.setUiMode('user')
  router.push({ name: 'user-profile' })
}

// -- Logout --
async function onLogout(): Promise<void> {
  loggingOut.value = true
  try {
    await authStore.logout()
    router.replace({ path: '/' })
  } finally {
    loggingOut.value = false
  }
}
</script>

<style scoped>
.admin-profile {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Header */
.admin-profile__header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.admin-profile__header-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  min-width: 0;
}

.admin-profile__name {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  line-height: 1.2;
  word-break: break-word;
  letter-spacing: 0.02em;
}

/* Sections */
.admin-profile__section {
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.admin-profile__section-title {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.admin-profile__section-desc {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.5;
}
</style>
