// =============================================================================
// VELO Frontend -- useAuth Composable (Phase F1.3, fixed 10.4)
// =============================================================================
//
// FIX 10.4: isReady/isStandalone are reactive refs inside composable scope,
// but shared via module-level refs (Vue pattern for singleton composables).
// Testable: reset by calling initAuth() in test setup.
// =============================================================================

import { ref, computed } from 'vue'
import { platform } from '@/platform'
import { useAuthStore } from '@/stores/auth'

/** Whether auth initialization has completed. */
const isReady = ref(false)

/** Whether we're in standalone mode (no Telegram initData). */
const isStandalone = ref(false)

/**
 * Reset auth state (for testing).
 */
function resetAuthState(): void {
  isReady.value = false
  isStandalone.value = false
}

/**
 * Run the full auth initialization flow.
 * Should be called once from App.vue on mount.
 */
async function initAuth(): Promise<void> {
  const authStore = useAuthStore()

  // Reset in case of re-initialization.
  resetAuthState()

  await platform.init()

  // Step 1: try to restore existing session (page reload).
  const restored = await authStore.restoreSession()
  if (restored) {
    isReady.value = true
    return
  }

  // Step 2: try platform-specific login.
  const initData = platform.getInitData()

  if (initData) {
    await authStore.loginViaTelegram(initData)
    isReady.value = true
    return
  }

  // Standalone: no auto-login possible.
  isStandalone.value = true
  isReady.value = true
}

export function useAuth() {
  const authStore = useAuthStore()

  return {
    isReady,
    isAuthenticated: computed(() => authStore.isAuthenticated),
    isStandalone,
    initAuth,
    /** Exposed for testing (10.4). */
    resetAuthState,
  }
}
