<!--
  VELO Frontend -- AdminProfileView

  Minimal admin profile screen. Route: /admin/profile (tab "Я").
  Refreshed S4 P15 C67 under Velo DS (Path Y MEDIUM #047, no-emoji #048).

  Sections:
    1. Profile header — avatar, display name, admin badge.
    2. Administration — quick links to admin routes via ProfileMenuItem.
    3. Mode — RoleSwitcher (See RoleSwitcher.vue — TD-FE-ROLE-SWITCH centralized at S4-P15+ post-verify fix).
    4. Account — Logout red row (IconLogout replaces legacy door glyph).
-->

<template>
  <div class="admin-profile">
    <!-- Section 1 — Profile header -->
    <section class="admin-profile__header">
      <VAvatar
        :name="displayName"
        size="xl"
      />
      <div class="admin-profile__header-info">
        <h1 class="admin-profile__name">
          {{ displayName }}
        </h1>
        <VBadge variant="info">
          Администратор
        </VBadge>
      </div>
    </section>

    <!-- Section 2 — Администрирование -->
    <section class="admin-profile__menu">
      <h3 class="admin-profile__menu-title">
        Администрирование
      </h3>
      <ProfileMenuItem
        :icon="IconHome"
        label="Дашборд"
        to="/admin/dashboard"
      />
      <ProfileMenuItem
        :icon="IconGroup"
        label="Мастера"
        to="/admin/masters"
      />
      <ProfileMenuItem
        :icon="IconWarning"
        label="Жалобы"
        to="/admin/reports"
      />
      <ProfileMenuItem
        :icon="IconCheck"
        label="Сверка"
        to="/admin/consistency"
      />
    </section>

    <!-- Section 3 — Режим -->
    <RoleSwitcher />

    <!-- Section 4 — Аккаунт -->
    <section class="admin-profile__menu">
      <h3 class="admin-profile__menu-title">
        Аккаунт
      </h3>
      <ProfileMenuItem
        :icon="IconLogout"
        label="Выйти"
        danger
        @click="onLogout"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VAvatar, VBadge } from '@/components/ui'
import {
  IconHome,
  IconGroup,
  IconWarning,
  IconCheck,
  IconLogout,
} from '@/components/icons'
import ProfileMenuItem from '@/components/shared/ProfileMenuItem.vue'
import RoleSwitcher from '@/components/shared/RoleSwitcher.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loggingOut = ref(false)

const displayName = computed(() => {
  if (!authStore.user) return 'Администратор'
  const parts = [authStore.user.first_name, authStore.user.last_name].filter(Boolean)
  return parts.length > 0 ? parts.join(' ') : 'Администратор'
})

// -- Logout --
async function onLogout(): Promise<void> {
  if (loggingOut.value) return
  loggingOut.value = true
  try {
    await authStore.logout()
    router.replace({ path: '/welcome' })
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

/* Section 1 — Header */
.admin-profile__header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
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
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
  word-break: break-word;
  letter-spacing: 0.02em;
}

/* Sections 2/3/4 — Menu blocks */
.admin-profile__menu {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.admin-profile__menu-title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin: 0 0 var(--space-1);
  font-weight: 400;
}

.admin-profile__section-desc {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 var(--space-1);
  padding: 0 var(--space-4);
}
</style>
