// =============================================================================
// VELO Frontend -- UI Store (TD-FE-ROLE-SWITCH)
// =============================================================================
//
// Manages UI mode for master/admin users who want to browse the user interface.
// Not persisted -- resets to 'default' on every app open.
// =============================================================================

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserRole } from '@/api/types'

export type UiMode = 'default' | 'user'

export const useUiStore = defineStore('ui', () => {
  // Not persisted intentionally -- resets on every session start.
  const uiMode = ref<UiMode>('default')

  function setUiMode(mode: UiMode): void {
    uiMode.value = mode
  }

  // TEST-ONLY replay signal. Set by RoleSwitchSection (rendered only when the
  // backend exposes role_switch = test server) when a tester switches role, to
  // force the target role's onboarding to replay — bypassing the
  // completed/shown-this-session guards. Session-scoped (not persisted); never
  // set in production, where there is no role-switch UI.
  const forceOnboarding = ref<UserRole | null>(null)

  function setForceOnboarding(role: UserRole | null): void {
    forceOnboarding.value = role
  }

  function clearForceOnboarding(): void {
    forceOnboarding.value = null
  }

  return { uiMode, setUiMode, forceOnboarding, setForceOnboarding, clearForceOnboarding }
})
