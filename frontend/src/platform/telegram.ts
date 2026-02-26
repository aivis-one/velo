// =============================================================================
// VELO Frontend -- Telegram Platform (Phase F1.1)
// =============================================================================
//
// Real implementation that wraps the Telegram WebApp SDK.
// SDK is loaded via CDN <script> in index.html -- window.Telegram.WebApp
// is available by the time this code runs.
//
// Only instantiated when initData is present (user came from Telegram bot).
// =============================================================================

import type { Platform } from './types'

/** Telegram WebApp SDK object (loaded from CDN script in index.html). */
const webApp = window.Telegram!.WebApp

/** Active BackButton callback reference (for cleanup on hide). */
let _backButtonCallback: (() => void) | null = null

export const telegramPlatform: Platform = {
  name: 'telegram',

  async init(): Promise<void> {
    // Tell Telegram the app is ready to be displayed.
    webApp.ready()

    // Expand to full viewport height (removes half-screen mode).
    webApp.expand()

    // Set header and background colors to match VELO design.
    // Uses Telegram's built-in theming -- respects dark/light mode.
    webApp.setHeaderColor('#334D6E')
    webApp.setBackgroundColor('#F8FAFC')
  },

  getInitData(): string | null {
    return webApp.initData || null
  },

  getTheme(): 'light' | 'dark' {
    return webApp.colorScheme || 'light'
  },

  hapticFeedback(style: 'light' | 'medium' | 'heavy'): void {
    try {
      webApp.HapticFeedback.impactOccurred(style)
    } catch {
      // Silently ignore -- older Telegram clients may not support this.
    }
  },

  showBackButton(callback: () => void): void {
    _backButtonCallback = callback
    webApp.BackButton.onClick(callback)
    webApp.BackButton.show()
  },

  hideBackButton(): void {
    if (_backButtonCallback) {
      webApp.BackButton.offClick(_backButtonCallback)
      _backButtonCallback = null
    }
    webApp.BackButton.hide()
  },

  close(): void {
    webApp.close()
  },
}
