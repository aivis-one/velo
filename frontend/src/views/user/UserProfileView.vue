<!--
  VELO Frontend -- UserProfileView (Phase F4.2, updated TD-FE-ROLE-SWITCH)

  User profile screen. Matches mockup screen-profile layout:
    - Profile header: avatar, name, email
    - Stats row: practices count, hours
    - Balance card (Phase F4.2)
    - Menu sections: account, settings, help, logout

  Balance is displayed as a dedicated card below the stats row.
  Other menu items (edit profile, messages, notifications, etc.)
  are stubs navigating to future phase views.

  TD-FE-ROLE-SWITCH: If current user role is 'master' or 'admin', show a
  "Вернуться в режим мастера/админа" button above logout. Button resets
  uiMode to 'default' and navigates to the appropriate dashboard.

  Route: /user/profile (name: 'user-profile')
-->

<template>
  <div class="profile">
    <!-- Header -->
    <div class="profile__header">
      <div class="profile__avatar">
        <VAvatar
          :name="displayName"
          :url="user?.avatar_url ?? undefined"
          size="lg"
        />
      </div>
      <h1 class="profile__name">{{ displayName }}</h1>

      <!-- Stats -->
      <div class="profile__stats">
        <div class="profile__stat">
          <div class="profile__stat-value">{{ bookingsCount }}</div>
          <div class="profile__stat-label">практик</div>
        </div>
      </div>
    </div>

    <!-- Balance card -->
    <div class="profile__balance" @click="onTopup">
      <div class="profile__balance-left">
        <span class="profile__balance-label">Баланс</span>
        <span class="profile__balance-value">{{ balanceStore.formattedBalance }}</span>
      </div>
      <VButton size="sm" variant="secondary">Пополнить</VButton>
    </div>

    <!-- Menu sections -->
    <div class="profile__menus">
      <!-- Account -->
      <div class="profile__menu-section">
        <div class="profile__menu-title">Аккаунт</div>
        <div class="profile__menu-list">
          <div class="profile__menu-item" @click="router.push({ name: 'user-bookings' })">
            <span class="profile__menu-icon">📋</span>
            <span class="profile__menu-text">Мои бронирования</span>
            <span class="profile__menu-arrow">→</span>
          </div>
        </div>
      </div>

      <!-- Settings -->
      <div class="profile__menu-section">
        <div class="profile__menu-title">Настройки</div>
        <div class="profile__menu-list">
          <div class="profile__menu-item" @click="toast.info('Уведомления будут доступны в следующем обновлении')">
            <span class="profile__menu-icon">🔔</span>
            <span class="profile__menu-text">Уведомления</span>
            <span class="profile__menu-arrow">→</span>
          </div>
          <div class="profile__menu-item" @click="toast.info('Настройки языка будут доступны в следующем обновлении')">
            <span class="profile__menu-icon">🌐</span>
            <span class="profile__menu-text">Язык / Часовой пояс</span>
            <span class="profile__menu-arrow">→</span>
          </div>
        </div>
      </div>

      <!-- Help -->
      <div class="profile__menu-section">
        <div class="profile__menu-title">Помощь</div>
        <div class="profile__menu-list">
          <div class="profile__menu-item" @click="toast.info('Поддержка будет доступна в следующем обновлении')">
            <span class="profile__menu-icon">🛡️</span>
            <span class="profile__menu-text">Поддержка</span>
            <span class="profile__menu-arrow">→</span>
          </div>
        </div>
      </div>

      <!-- Return to master/admin mode (TD-FE-ROLE-SWITCH) -->
      <div
        v-if="authStore.role === 'master' || authStore.role === 'admin'"
        class="profile__menu-section"
      >
        <div class="profile__menu-list">
          <div class="profile__menu-item profile__menu-item--switch" @click="returnToNativeMode">
            <span class="profile__menu-icon">🔄</span>
            <span class="profile__menu-text">
              {{ authStore.role === 'admin' ? 'Вернуться в режим администратора' : 'Вернуться в режим мастера' }}
            </span>
            <span class="profile__menu-arrow">→</span>
          </div>
        </div>
      </div>

      <!-- Logout -->
      <div class="profile__menu-section">
        <div class="profile__menu-list">
          <div class="profile__menu-item profile__menu-item--danger" @click="onLogout">
            <span class="profile__menu-icon">🚪</span>
            <span class="profile__menu-text">Выйти</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBalanceStore } from '@/stores/balance'
import { useBookingsStore } from '@/stores/bookings'
import { useUiStore } from '@/stores/ui'
import { VAvatar, VButton } from '@/components/ui'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const authStore = useAuthStore()
const balanceStore = useBalanceStore()
const bookingsStore = useBookingsStore()
const uiStore = useUiStore()
const toast = useToast()

const user = computed(() => authStore.user)

const displayName = computed(() => {
  if (!user.value) return ''
  const parts = [user.value.first_name, user.value.last_name].filter(Boolean)
  return parts.length > 0 ? parts.join(' ') : 'Пользователь'
})

const bookingsCount = computed(() => bookingsStore.total)

// -- Actions --

function onTopup(): void {
  router.push({ name: 'user-topup' })
}

async function onLogout(): Promise<void> {
  await authStore.logout()
  router.replace({ path: '/' })
}

/** Return to native role dashboard and reset uiMode (TD-FE-ROLE-SWITCH). */
function returnToNativeMode(): void {
  uiStore.setUiMode('default')
  if (authStore.role === 'admin') {
    router.push({ name: 'admin-dashboard' })
  } else {
    router.push({ name: 'master-dashboard' })
  }
}

// -- Lifecycle --
onMounted(async () => {
  // NEW-7: wrapped in try/catch -- unhandled rejection on balance/bookings
  // fetch failure would leave the profile screen silently broken.
  try {
    await Promise.all([
      balanceStore.refresh(),
      bookingsStore.fetchMyBookings(),
    ])
  } catch {
    // Non-critical -- profile still renders without fresh counts.
  }
})
</script>

<style scoped>
.profile {
  display: flex;
  flex-direction: column;
  margin: calc(-1 * var(--space-4));
}

/* Header */
.profile__header {
  text-align: center;
  padding: var(--space-6);
  background: transparent;
}

.profile__avatar {
  margin-bottom: var(--space-3);
}

.profile__name {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-4);
}

/* Stats */
.profile__stats {
  display: flex;
  justify-content: center;
  gap: var(--space-8);
}

.profile__stat {
  text-align: center;
}

.profile__stat-value {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--velo-primary);
}

.profile__stat-label {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-muted);
}

/* Balance card */
.profile__balance {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: var(--space-4);
  padding: var(--space-4);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  cursor: pointer;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  transition: opacity var(--transition-fast);
}

.profile__balance:hover {
  opacity: 0.9;
}

.profile__balance-left {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.profile__balance-label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-muted);
}

.profile__balance-value {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-primary);
}

/* Menu sections */
.profile__menus {
  padding: 0 var(--space-4) var(--space-4);
}

.profile__menu-section {
  margin-bottom: var(--space-4);
}

.profile__menu-title {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}

.profile__menu-list {
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  overflow: hidden;
}

.profile__menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.profile__menu-item + .profile__menu-item {
  border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.profile__menu-item:active {
  background: rgba(255, 255, 255, 0.1);
}

.profile__menu-icon {
  font-size: var(--text-lg);
  flex-shrink: 0;
}

.profile__menu-text {
  flex: 1;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
}

.profile__menu-arrow {
  font-size: var(--text-base);
  color: var(--velo-text-muted);
}

.profile__menu-item--danger .profile__menu-text {
  color: var(--velo-error-text);
}

.profile__menu-item--switch .profile__menu-text {
  color: var(--velo-primary);
}
</style>
