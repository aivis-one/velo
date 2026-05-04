<!--
  VELO Frontend -- RoleSwitcher (S4-P15+ post-verify fix; TD-FE-ROLE-SWITCH centralized)

  One row per role available to current account. Active role (derived from
  route prefix) marked with IconCheck + distinct tint. Inactive tap →
  setUiMode + router.push to that role's home; active tap is no-op.
  Hidden via v-if when account has only `user` role (single-button useless).

  Backend hierarchy ADMIN > MASTER > USER per backend/scripts/seed.py
  (admin always master). Encoded here because UserResponse has single
  `role` field, not roles[].
-->

<template>
  <div
    v-if="shouldRender"
    class="role-switcher"
    role="group"
    aria-label="Переключение режима"
  >
    <button
      v-for="role in availableRoles"
      :key="role"
      type="button"
      class="role-switcher__row"
      :class="{ 'role-switcher__row--active': role === currentActive }"
      :aria-current="role === currentActive ? 'page' : undefined"
      @click="onSelect(role)"
    >
      <component
        :is="ROLE_CONFIG[role].icon"
        class="role-switcher__icon"
        :size="20"
      />
      <span class="role-switcher__label">{{ ROLE_CONFIG[role].label }}</span>
      <IconCheck
        v-if="role === currentActive"
        class="role-switcher__check"
        :size="18"
      />
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore, type UiMode } from '@/stores/ui'
import { IconShield, IconBrain, IconProfile, IconCheck } from '@/components/icons'
import type { UserRole } from '@/api/generated'

const auth = useAuthStore()
const ui = useUiStore()
const route = useRoute()
const router = useRouter()

// Backend hierarchy admin > master > user (see header comment).
const ROLE_HIERARCHY: Record<UserRole, UserRole[]> = {
  admin: ['admin', 'master', 'user'],
  master: ['master', 'user'],
  user: ['user'],
}

const ROLE_CONFIG: Record<UserRole, { icon: Component; label: string; path: string; uiMode: UiMode }> = {
  admin:  { icon: IconShield,  label: 'Режим админа',       path: '/admin/dashboard',  uiMode: 'default' },
  master: { icon: IconBrain,   label: 'Режим мастера',      path: '/master/dashboard', uiMode: 'default' },
  user:   { icon: IconProfile, label: 'Режим пользователя', path: '/user/dashboard',   uiMode: 'user' },
}

const availableRoles = computed<UserRole[]>(() => ROLE_HIERARCHY[auth.user?.role ?? 'user'] ?? ['user'])

const currentActive = computed<UserRole>(() => {
  const p = route.path
  if (p.startsWith('/admin')) return 'admin'
  if (p.startsWith('/master')) return 'master'
  return 'user'
})

const shouldRender = computed(() => availableRoles.value.length > 1)

function onSelect(role: UserRole): void {
  if (role === currentActive.value) return
  const cfg = ROLE_CONFIG[role]
  ui.setUiMode(cfg.uiMode)
  router.push(cfg.path)
}
</script>

<style scoped>
.role-switcher {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.role-switcher__row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  cursor: pointer;
  text-align: left;
  transition: background var(--transition-fast);
}
.role-switcher__row:hover,
.role-switcher__row--active {
  background: var(--surface-steel-alpha-15);
}
.role-switcher__row--active {
  cursor: default;
}
.role-switcher__icon {
  flex-shrink: 0;
  color: currentColor;
}
.role-switcher__label {
  flex: 1;
}
.role-switcher__check {
  color: var(--steel-button);
  flex-shrink: 0;
}
</style>
