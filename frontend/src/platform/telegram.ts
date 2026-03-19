// =============================================================================
// VELO Frontend -- Telegram Platform (Phase F1.1, fixed 10.1, updated TD-F01)
// =============================================================================
//
// FIX 10.1: WebApp accessed lazily via getter, not at module level.
// If CDN is blocked (VPN, proxy, downtime), standalone mode still works.
//
// TD-F01: added getStartParam() -- reads WebApp.initDataUnsafe.start_param
// for deep link handling (open_practice__{uuid}).
// =============================================================================

import type { Platform } from './types'

/** Lazy accessor -- avoids crash if SDK didn't load. */
function getWebApp(): TelegramWebApp {
  const wa = window.Telegram?.WebApp
  if (!wa) {
    throw new Error('Telegram WebApp SDK not available')
  }
  return wa
}

/** Active BackButton callback reference (for cleanup on hide). */
let _backButtonCallback: (() => void) | null = null

export const telegramPlatform: Platform = {
  name: 'telegram',

  async init(): Promise<void> {
    const webApp = getWebApp()
    webApp.ready()
    webApp.expand()
    webApp.setHeaderColor('#334D6E')
    webApp.setBackgroundColor('#F8FAFC')
  },

  getInitData(): string | null {
    return getWebApp().initData || null
  },

  getStartParam(): string | null {
    // start_param is set when the bot link contains startapp=... query.
    // Example: https://t.me/bot?startapp=open_practice__<uuid>
    return getWebApp().initDataUnsafe?.start_param ?? null
  },

  getTheme(): 'light' | 'dark' {
    return getWebApp().colorScheme || 'light'
  },

  hapticFeedback(style: 'light' | 'medium' | 'heavy'): void {
    try {
      getWebApp().HapticFeedback.impactOccurred(style)
    } catch {
      // Silently ignore -- older clients or missing SDK.
    }
  },

  showBackButton(callback: () => void): void {
    const webApp = getWebApp()
    _backButtonCallback = callback
    webApp.BackButton.onClick(callback)
    webApp.BackButton.show()
  },

  hideBackButton(): void {
    if (_backButtonCallback) {
      getWebApp().BackButton.offClick(_backButtonCallback)
      _backButtonCallback = null
    }
    getWebApp().BackButton.hide()
  },

  close(): void {
    getWebApp().close()
  },
}
