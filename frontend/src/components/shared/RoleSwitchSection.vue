<!--
  VELO Frontend -- RoleSwitchSection (self role-switch)

  Settings section that lets an account switch its own role. Renders one
  VMenuRow per allowed role EXCEPT the current one. Since №256 the allowed
  set is CAPABILITY-DERIVED by the backend (verified master -> user/master;
  admin -> all three; plain user -> empty, so no section). The old
  ROLE_SWITCH_ENABLED flag is gone — meaning this section now also renders
  in PROD for verified masters/admins (open operator ruling: rename/trim
  the «Режим тестировщика» framing + the apply-preview entry for prod).

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
      <!-- Page through the master application journey (Landing → apply wizard
           → «Заявка отправлена») without filing anything. Shares this
           section's gate (targets > 0). NOTE (№256): allowedRoles is now
           capability-derived, so this entry ALSO renders in prod for verified
           masters/admins — open operator ruling (see the header comment). -->
      <VMenuRow
        variant="primary"
        label="Просмотреть экраны заявки"
        @click="onPreviewApply"
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
    // TEST-ONLY: replay the target role's onboarding on switch. Bound to the
    // same gate as this whole section (allowedRoles non-empty = backend
    // role_switch present = test server) — never fires in prod. user/master
    // have onboarding; admin does not.
    if (authStore.allowedRoles.length && (target === 'user' || target === 'master')) {
      uiStore.setForceOnboarding(target)
    }
    await router.push({ name: ROLE_DASHBOARD[target] })
  } catch {
    toast.error('Не удалось переключить роль')
  } finally {
    switching.value = false
  }
}

// TEST-ONLY: enter the read-only apply-flow preview (see stores/ui.ts). Sets the
// session signal then routes to screen 1 (the parked /auth Landing). Reachable
// only from this prod-gated section, so the signal can never be set in prod.
function onPreviewApply(): void {
  uiStore.setPreviewApplyFlow(true)
  router.push({ name: 'auth-landing' })
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
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.role-switch__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
