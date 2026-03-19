// =============================================================================
// VELO Frontend -- useAuth Composable (Phase F1.3, fixed 10.4, BUG-role-redirect, TD-F01)
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
//
// P-3: waitUntilReady() has a 10s timeout. If initAuth() hangs (network
// failure, frozen platform SDK), the guard resolves anyway instead of
// leaving the user on a white screen forever. A console warning is logged.
//
// TD-F01: Deep link handling.
// After auth, read platform.getStartParam() and parse open_practice__{uuid}.
// Store the target route in pendingDeepLink so roleRedirect can consume it.
// pendingDeepLink is cleared after first use to prevent stale redirects.
// =============================================================================

import { ref, computed, watch } from 'vue'
import { platform } from '@/platform'
import { useAuthStore } from '@/stores/auth'

/** Whether auth initialization has completed. */
const isReady = ref(false)

/** Whether we're in standalone mode (no Telegram initData). */
const isStandalone = ref(false)

/**
 * Pending deep link route from startapp parameter (TD-F01).
 * Consumed once by roleRedirect, then cleared.
 * Format: { name: string, params?: Record<string, string> }
 */
export const pendingDeepLink = ref<{ name: string; params?: Record<string, string> } | null>(null)

/** Timeout for waitUntilReady() in milliseconds (P-3). */
const READY_TIMEOUT_MS = 10_000

/**
 * Parse the Telegram startapp parameter into a router location.
 * Returns null if the parameter is absent or unrecognized.
 *
 * Supported formats:
 *   open_practice__{uuid} -> { name: 'practice-detail', params: { id: uuid } }
 */
function parseStartParam(startParam: string | null): { name: string; params?: Record<string, string> } | null {
  if (!startParam) return null

  const practiceMatch = startParam.match(/^open_practice__([0-9a-f-]{36})$/)
  if (practiceMatch?.[1]) {
    return { name: 'practice-detail', params: { id: practiceMatch[1] } }
  }

  return null
}

/**
 * Reset auth state (for testing).
 */
export function resetAuthState(): void {
  isReady.value = false
  isStandalone.value = false
  pendingDeepLink.value = null
}

/**
 * Returns a Promise that resolves once isReady becomes true.
 * If isReady is already true, resolves immediately.
 *
 * P-3: Races against a 10s timeout. If initAuth() hangs (network issue,
 * frozen Telegram SDK), the promise resolves anyway so the router guard
 * doesn't block forever. Logs a console warning on timeout.
 *
 * Used by roleRedirect guard and router beforeEach.
 * Safe to call multiple times -- each call gets its own Promise.
 */
export function waitUntilReady(): Promise<void> {
  if (isReady.value) return Promise.resolve()

  const waitPromise = new Promise<void>((resolve) => {
    const stop = watch(isReady, (ready) => {
      if (ready) {
        stop()
        resolve()
      }
    })
  })

  const timeoutPromise = new Promise<void>((resolve) => {
    setTimeout(() => {
      console.warn('[useAuth] waitUntilReady() timed out after', READY_TIMEOUT_MS, 'ms -- proceeding anyway')
      resolve()
    }, READY_TIMEOUT_MS)
  })

  return Promise.race([waitPromise, timeoutPromise])
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

  // TD-F01: read startapp param before auth so it's available regardless
  // of whether we restore a session or do a fresh login.
  const startParam = platform.getStartParam()
  pendingDeepLink.value = parseStartParam(startParam)

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
