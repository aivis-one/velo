// =============================================================================
// VELO Frontend -- useAuth Composable (Phase F1.3)
// =============================================================================
//
// Orchestrates the full auth flow on app startup:
//   1. Try to restore session from sessionStorage (page reload)
//   2. If no session: check platform
//      - Telegram: auto-login via initData
//      - Standalone: show "Open via Telegram" stub
//
// USAGE (in App.vue):
//   const { isReady, isAuthenticated, isStandalone } = useAuth()
//   await initAuth()
// =============================================================================

import { ref } from 'vue'
import { platform } from '@/platform'
import { useAuthStore } from '@/stores/auth'

/** Whether auth initialization has completed (success or failure). */
const isReady = ref(false)

/** Whether we're in standalone mode (no Telegram initData). */
const isStandalone = ref(false)

/**
 * Run the full auth initialization flow.
 * Should be called once from App.vue on mount.
 */
async function initAuth(): Promise<void> {
  const authStore = useAuthStore()

  // Initialize the platform (Telegram: ready + expand, standalone: no-op).
  await platform.init()

  // Step 1: try to restore existing session (page reload scenario).
  const restored = await authStore.restoreSession()
  if (restored) {
    isReady.value = true
    return
  }

  // Step 2: no saved session -- try platform-specific login.
  const initData = platform.getInitData()

  if (initData) {
    // Telegram: auto-login with signed initData.
    await authStore.loginViaTelegram(initData)
    isReady.value = true
    return
  }

  // Standalone: no initData available, can't auto-login.
  isStandalone.value = true
  isReady.value = true
}

/**
 * Composable for auth state and initialization.
 */
export function useAuth() {
  const authStore = useAuthStore()

  return {
    /** Auth flow has finished (may or may not be logged in). */
    isReady,
    /** User is logged in with a valid session. */
    isAuthenticated: authStore.isAuthenticated,
    /** App is running outside Telegram (no auto-login possible). */
    isStandalone,
    /** Run the auth flow (call once from App.vue). */
    initAuth,
  }
}
