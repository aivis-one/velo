// =============================================================================
// VELO Frontend -- Auth Store (Phase F1.3)
// =============================================================================
//
// Pinia store for authentication state.
//
// STATE:
//   user: UserResponse | null   -- current logged-in user
//   token: string | null         -- session token (Bearer)
//   loading: boolean             -- auth in progress
//
// ACTIONS:
//   loginViaTelegram(initData)   -- POST /auth/telegram
//   logout()                     -- POST /auth/logout + clear state
//   fetchMe()                    -- GET /users/me (refresh user data)
//
// TOKEN PERSISTENCE:
//   sessionStorage (not localStorage) -- Telegram WebApp closes the tab,
//   so sessionStorage clears automatically. localStorage would leave
//   stale tokens. See Frontend Spec section 6 (known decisions).
// =============================================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, setAuthToken, ApiResponseError } from '@/api/client'
import type { AuthResponse, UserResponse } from '@/api/types'

const TOKEN_KEY = 'velo_token'

export const useAuthStore = defineStore('auth', () => {
  // -- State --
  const user = ref<UserResponse | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)

  // -- Getters --
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const role = computed(() => user.value?.role ?? 'user')

  // -- Internal helpers --

  /** Persist token to sessionStorage and sync with API client. */
  function _setToken(newToken: string | null): void {
    token.value = newToken
    setAuthToken(newToken)

    if (newToken) {
      sessionStorage.setItem(TOKEN_KEY, newToken)
    } else {
      sessionStorage.removeItem(TOKEN_KEY)
    }
  }

  /** Set user data (FP-02: mutations only through actions). */
  function _setUser(newUser: UserResponse | null): void {
    user.value = newUser
  }

  // -- Actions --

  /**
   * Login via Telegram initData.
   * Called automatically when app opens inside Telegram.
   */
  async function loginViaTelegram(initData: string): Promise<boolean> {
    loading.value = true
    try {
      const response = await api.post<AuthResponse>(
        '/api/v1/auth/telegram',
        { init_data: initData },
      )
      _setToken(response.session_token)
      _setUser(response.user)
      return true
    } catch (error) {
      _setToken(null)
      _setUser(null)
      if (error instanceof ApiResponseError) {
        console.error('Telegram auth failed:', error.detail)
      }
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Restore session from sessionStorage token.
   * Called on app startup (page reload inside Telegram).
   */
  async function restoreSession(): Promise<boolean> {
    const savedToken = sessionStorage.getItem(TOKEN_KEY)
    if (!savedToken) return false

    _setToken(savedToken)
    loading.value = true

    try {
      const me = await api.get<UserResponse>('/api/v1/users/me')
      _setUser(me)
      return true
    } catch {
      // Token expired or invalid -- clean up.
      _setToken(null)
      _setUser(null)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Refresh user data from backend.
   * Called after profile updates, role changes, etc.
   */
  async function fetchMe(): Promise<void> {
    if (!token.value) return

    try {
      const me = await api.get<UserResponse>('/api/v1/users/me')
      _setUser(me)
    } catch (error) {
      if (error instanceof ApiResponseError && error.status === 401) {
        _setToken(null)
        _setUser(null)
      }
    }
  }

  /**
   * Logout -- clear session on backend and locally.
   */
  async function logout(): Promise<void> {
    try {
      await api.post('/api/v1/auth/logout')
    } catch {
      // Ignore errors -- we're logging out anyway.
    } finally {
      _setToken(null)
      _setUser(null)
    }
  }

  return {
    // State
    user,
    token,
    loading,
    // Getters
    isAuthenticated,
    role,
    // Actions
    loginViaTelegram,
    restoreSession,
    fetchMe,
    logout,
  }
})
