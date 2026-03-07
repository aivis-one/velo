// =============================================================================
// VELO Frontend -- useAuth Composable (Phase F1.3, fixed 10.4, BUG-role-redirect)
// =============================================================================
//
// FIX 10.4: isReady/isStandalone are reactive refs inside composable scope,
// but shared via module-level refs (Vue pattern for singleton composables).
// Testable: reset by calling initAuth() in test setup.
//
// BUG-role-redirect: Vue Router is created and begins its first navigation
// before App.vue mounts and calls initAuth(). This means roleRedirect fires
// while auth.role is still null, and every user is sent to /user/dashboard.
// Fix: export waitUntilReady() so roleRedirect can await auth completion
// before reading auth.role.
// =============================================================================

import { ref, computed, watch } from 'vue'
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
 * Returns a Promise that resolves once isReady becomes true.
 * If isReady is already true, resolves immediately (synchronously in microtask).
 *
 * Used by roleRedirect guard to wait for auth before reading auth.role.
 * Safe to call multiple times -- each call gets its own Promise.
 */
export function waitUntilReady(): Promise<void> {
  if (isReady.value) return Promise.resolve()

  return new Promise<void>((resolve) => {
    const stop = watch(isReady, (ready) => {
      if (ready) {
        stop()
        resolve()
      }
    })
  })
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
