<!--
  VELO Frontend -- UserProfileView (Phase F4.2; Profile redesign Screen A)

  User profile main screen. Matches Figma node 4715:3464 (70_Profile):
    - Header: avatar, name (no email -- email is a future, separately
      collected field, NOT the Telegram username, so it is not shown here)
    - Stats row: two cards -- "Практик" (attended count) and "Часов"
      (attended hours), both from GET /api/v1/bookings/me/stats
    - Menu sections: account, settings, help, logout

  Stats source: /bookings/me/stats returns practices_attended + hours_attended,
  computed from attended bookings only, so the two numbers stay consistent.

  Menu navigation: items whose target screens (Edit profile, Notifications,
  Language/Timezone, Support, Share) are built in later steps of the profile
  redesign are wired as toast stubs for now; each becomes a real route when
  its screen lands. "Мои бронирования" already has a route and navigates.

  Vector icons (currentColor) from components/icons replace the previous
  emoji glyphs, matching the mockup.

  TD-FE-ROLE-SWITCH: master/admin see a "Вернуться в режим ..." row above
  logout that resets uiMode and navigates to their native dashboard.

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
    </div>

    <!-- Stats: practices + hours -->
    <div class="profile__stats">
      <div class="profile__stat-card">
        <div class="profile__stat-value">{{ practicesAttended }}</div>
        <div class="profile__stat-label">Практик</div>
      </div>
      <div class="profile__stat-card">
        <div class="profile__stat-value">{{ hoursLabel }}</div>
        <div class="profile__stat-label">Часов</div>
      </div>
    </div>

    <!-- Menu sections -->
    <div class="profile__menus">
      <!-- Account -->
      <div class="profile__menu-section">
        <div class="profile__menu-title">Аккаунт</div>
        <div class="profile__menu-list">
          <div class="profile__menu-item" @click="onEditProfile">
            <span class="profile__menu-icon"><IconEdit :size="20" /></span>
            <span class="profile__menu-text">Редактировать профиль</span>
            <span class="profile__menu-arrow"><IconArrowRight :size="16" /></span>
          </div>
          <div class="profile__menu-item" @click="router.push({ name: 'user-bookings' })">
            <span class="profile__menu-icon"><IconBookings :size="20" /></span>
            <span class="profile__menu-text">Мои бронирования</span>
            <span class="profile__menu-arrow"><IconArrowRight :size="16" /></span>
          </div>
        </div>
      </div>

      <!-- Settings -->
      <div class="profile__menu-section">
        <div class="profile__menu-title">Настройки</div>
        <div class="profile__menu-list">
          <div class="profile__menu-item" @click="onNotifications">
            <span class="profile__menu-icon"><IconBell :size="20" /></span>
            <span class="profile__menu-text">Уведомления</span>
            <span class="profile__menu-arrow"><IconArrowRight :size="16" /></span>
          </div>
          <div class="profile__menu-item" @click="onLanguageTimezone">
            <span class="profile__menu-icon"><IconGlobe :size="20" /></span>
            <span class="profile__menu-text">Язык / Часовой пояс</span>
            <span class="profile__menu-arrow"><IconArrowRight :size="16" /></span>
          </div>
        </div>
      </div>

      <!-- Help -->
      <div class="profile__menu-section">
        <div class="profile__menu-title">Помощь</div>
        <div class="profile__menu-list">
          <div class="profile__menu-item" @click="onSupport">
            <span class="profile__menu-icon"><IconSupport :size="20" /></span>
            <span class="profile__menu-text">Поддержка</span>
            <span class="profile__menu-arrow"><IconArrowRight :size="16" /></span>
          </div>
          <div class="profile__menu-item" @click="onShare">
            <span class="profile__menu-icon"><IconShare :size="20" /></span>
            <span class="profile__menu-text">Поделиться</span>
            <span class="profile__menu-arrow"><IconArrowRight :size="16" /></span>
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
            <span class="profile__menu-text">
              {{ authStore.role === 'admin' ? 'Вернуться в режим администратора' : 'Вернуться в режим мастера' }}
            </span>
            <span class="profile__menu-arrow"><IconArrowRight :size="16" /></span>
          </div>
        </div>
      </div>

      <!-- Logout -->
      <div class="profile__menu-section">
        <div class="profile__menu-list">
          <div class="profile__menu-item profile__menu-item--danger" @click="onLogout">
            <span class="profile__menu-icon"><IconLogout :size="20" /></span>
            <span class="profile__menu-text">Выйти</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { VAvatar } from '@/components/ui'
import {
  IconEdit,
  IconBookings,
  IconBell,
  IconGlobe,
  IconSupport,
  IconShare,
  IconLogout,
  IconArrowRight,
} from '@/components/icons'
import { useToast } from '@/composables/useToast'
import { getMyStats } from '@/api/bookings'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()
const toast = useToast()

const user = computed(() => authStore.user)

const displayName = computed(() => {
  if (!user.value) return ''
  const parts = [user.value.first_name, user.value.last_name].filter(Boolean)
  return parts.length > 0 ? parts.join(' ') : 'Пользователь'
})

// -- Stats (attended practices + hours) from /bookings/me/stats --
const practicesAttended = ref(0)
const hoursAttended = ref(0)

/**
 * Hours label: integers show without a trailing ".0" (e.g. "12"), while
 * fractional values use a comma to match the Russian mockup ("9,5").
 */
const hoursLabel = computed(() => {
  const h = hoursAttended.value
  return Number.isInteger(h) ? String(h) : String(h).replace('.', ',')
})

// -- Menu actions --

function onEditProfile(): void {
  // Wired to a real route when 72_Edit Profile (Screen C) lands.
  toast.info('Редактирование профиля будет доступно в следующем обновлении')
}

function onNotifications(): void {
  // Wired to a real route when 74_Notifications (Screen E) lands.
  toast.info('Уведомления будут доступны в следующем обновлении')
}

function onLanguageTimezone(): void {
  // Wired to a real route when 75_Language-Timezone (Screen F) lands.
  toast.info('Настройки языка будут доступны в следующем обновлении')
}

function onSupport(): void {
  // Wired to a real route when 76_Support (Screen G) lands.
  toast.info('Поддержка будет доступна в следующем обновлении')
}

function onShare(): void {
  toast.info('Поделиться будет доступно в следующем обновлении')
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
  // NEW-7: wrapped in try/catch -- a stats fetch failure must not leave the
  // profile screen broken; the cards just stay at 0 until the next visit.
  try {
    const stats = await getMyStats()
    practicesAttended.value = stats.practices_attended
    hoursAttended.value = stats.hours_attended
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
  padding: var(--space-6) var(--space-6) var(--space-4);
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
  margin: 0;
}

/* Stats: two cards */
.profile__stats {
  display: flex;
  gap: var(--space-4);
  padding: 0 var(--space-4);
  margin-bottom: var(--space-4);
}

.profile__stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  padding: var(--space-4);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.profile__stat-value {
  font-family: var(--font-body);
  font-size: var(--text-3xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.profile__stat-label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-muted);
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--velo-primary);
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
  display: inline-flex;
  align-items: center;
  color: var(--velo-text-muted);
}

.profile__menu-item--danger .profile__menu-icon,
.profile__menu-item--danger .profile__menu-text {
  color: var(--velo-error-text);
}

.profile__menu-item--switch .profile__menu-text {
  color: var(--velo-primary);
}
</style>
