// =============================================================================
// VELO Frontend -- UI Store (TD-FE-ROLE-SWITCH + S2-S3 speedrun theme infra)
// =============================================================================
//
// Manages:
//   - uiMode: master/admin role-switch to user-mode browsing (TD-FE-ROLE-SWITCH).
//     Not persisted.
//   - theme: 'light' | 'dark' (S2 P07 C25). Persisted via localStorage
//     'velo:theme'. On boot, prefers stored value; falls back to
//     prefers-color-scheme media query.
// =============================================================================

import { defineStore } from 'pinia'
import { ref } from 'vue'

export type UiMode = 'default' | 'user'
export type Theme = 'light' | 'dark'

const THEME_KEY = 'velo:theme'

export const useUiStore = defineStore('ui', () => {
  // -- uiMode (not persisted) --
  const uiMode = ref<UiMode>('default')

  function setUiMode(mode: UiMode): void {
    uiMode.value = mode
  }

  // -- theme (persisted) --
  const theme = ref<Theme>('light')

  function applyTheme(t: Theme): void {
    theme.value = t
    if (typeof document !== 'undefined') {
      document.documentElement.dataset.theme = t
    }
  }

  function setTheme(t: Theme): void {
    applyTheme(t)
    try {
      localStorage.setItem(THEME_KEY, t)
    } catch {
      // SSR / private mode: silently no-op
    }
  }

  /**
   * Read persisted theme; fall back to prefers-color-scheme.
   * Attaches media-query listener only when no explicit user choice persisted.
   * Called from main.ts boot.
   */
  function initTheme(): void {
    let stored: Theme | null = null
    try {
      const v = localStorage.getItem(THEME_KEY)
      if (v === 'light' || v === 'dark') stored = v
    } catch {
      // no-op
    }

    if (stored) {
      applyTheme(stored)
      return
    }

    // No explicit user choice — use OS preference + listen for changes.
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mq = window.matchMedia('(prefers-color-scheme: dark)')
      applyTheme(mq.matches ? 'dark' : 'light')
      mq.addEventListener('change', (e) => {
        // Only auto-track OS theme while user has not made an explicit choice.
        const hasStored = (() => {
          try {
            return localStorage.getItem(THEME_KEY) !== null
          } catch {
            return false
          }
        })()
        if (!hasStored) applyTheme(e.matches ? 'dark' : 'light')
      })
    } else {
      applyTheme('light')
    }
  }

  return {
    uiMode,
    setUiMode,
    theme,
    setTheme,
    initTheme,
  }
})
