// =============================================================================
// VELO Frontend -- Auth Store (Phase F1.3, fixed 10.2)
// =============================================================================
//
// FIX 10.2: registers onUnauthorized callback with API client.
// =============================================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, setAuthToken, setOnUnauthorized, ApiResponseError } from '@/api/client'
import type { AuthResponse, UserResponse } from '@/api/types'

const TOKEN_KEY = 'velo_token'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserResponse | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const role = computed(() => user.value?.role ?? 'user')

  function _setToken(newToken: string | null): void {
    token.value = newToken
    setAuthToken(newToken)
    if (newToken) {
      sessionStorage.setItem(TOKEN_KEY, newToken)
    } else {
      sessionStorage.removeItem(TOKEN_KEY)
    }
  }

  function _setUser(newUser: UserResponse | null): void {
    user.value = newUser
  }

  /** Clear all auth state (used by 401 handler and logout). */
  function _clearSession(): void {
    _setToken(null)
    _setUser(null)
  }

  // 10.2: register callback so API client delegates 401 handling here.
  setOnUnauthorized(() => _clearSession())

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
      _clearSession()
      if (error instanceof ApiResponseError) {
        console.error('Telegram auth failed:', error.detail)
      }
      return false
    } finally {
      loading.value = false
    }
  }

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
      _clearSession()
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchMe(): Promise<void> {
    if (!token.value) return
    try {
      const me = await api.get<UserResponse>('/api/v1/users/me')
      _setUser(me)
    } catch (error) {
      if (error instanceof ApiResponseError && error.status === 401) {
        _clearSession()
      }
    }
  }

  async function logout(): Promise<void> {
    try {
      await api.post('/api/v1/auth/logout')
    } catch {
      // Ignore -- logging out anyway.
    } finally {
      _clearSession()
    }
  }

  return {
    user, token, loading,
    isAuthenticated, role,
    loginViaTelegram, restoreSession, fetchMe, logout,
  }
})