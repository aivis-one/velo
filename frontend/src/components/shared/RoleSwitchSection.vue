<!--
  VELO Frontend -- RoleSwitchSection (TEST-ONLY tester tool)

  Settings section that lets a whitelisted tester switch their own account
  role. Renders one VMenuRow per allowed role EXCEPT the current one
  (admin tester -> 2 buttons, master/user tester -> 1 button). Renders
  nothing for normal accounts and on production (allowedRoles is empty when
  the backend ROLE_SWITCH_ENABLED flag is off).

  Used in the three profile screens (user / master / admin) so a tester can
  move between any of their allowed roles from wherever they are. The switch
  rewrites the role server-side; we reset uiMode and navigate to the target
  role's dashboard so the whole shell (tabs, guards) re-resolves.
-->

<template>
  <div v-if="targets.length > 0" class="role-switch">
    <div class="role-switch__title">Режим тестировщика</div>
    <div class="role-switch__list">
      <VMenuRow
        v-for="t in targets"
        :key="t"
        variant="primary"
        :label="ROLE_LABEL[t]"
        @click="onSwitch(t)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { VMenuRow } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useToast } from '@/composables/useToast'
import type { UserRole } from '@/api/types'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()
const toast = useToast()

const ROLE_LABEL: Record<UserRole, string> = {
  user: 'Режим пользователя',
  master: 'Режим мастера',
  admin: 'Режим администратора',
}

const ROLE_DASHBOARD: Record<UserRole, string> = {
  user: 'user-dashboard',
  master: 'master-dashboard',
  admin: 'admin-dashboard',
}

// Allowed roles minus the current one — the set of switch targets.
const targets = computed<UserRole[]>(() =>
  authStore.allowedRoles.filter((r) => r !== authStore.role),
)

const switching = ref(false)

async function onSwitch(target: UserRole): Promise<void> {
  if (switching.value) return
  switching.value = true
  try {
    await authStore.switchRole(target)
    // Drop any user-mode preview so the native shell of the new role shows.
    uiStore.setUiMode('default')
    await router.push({ name: ROLE_DASHBOARD[target] })
  } catch {
    toast.error('Не удалось переключить роль')
  } finally {
    switching.value = false
  }
}
</script>

<style scoped>
.role-switch {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.role-switch__title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.role-switch__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
