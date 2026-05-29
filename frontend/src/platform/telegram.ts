// =============================================================================
// VELO Frontend -- Telegram Platform (Phase F1.1, fixed 10.1, updated TD-F01)
// =============================================================================
//
// FIX 10.1: WebApp accessed lazily via getter, not at module level.
// If CDN is blocked (VPN, proxy, downtime), standalone mode still works.
//
// TD-F01: added getStartParam() -- reads WebApp.initDataUnsafe.start_param
// for deep link handling (open_practice__{uuid}).
//
// TEMP DIAGNOSTIC: prints whether the MobileLayout padding-top actually
// resolved on device. Decides "variable never reached CSS" vs "padding applied
// but content still on top". Remove this block once read.
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

// =============================================================================
// TEMP DIAGNOSTIC -- remove after reading the values from the client's screen.
// =============================================================================
function showLayoutDiagnostic(): void {
  const panel = document.createElement('div')
  panel.id = 'velo-layout-diagnostic'
  panel.style.cssText = [
    'position:fixed',
    'top:0',
    'left:0',
    'right:0',
    'z-index:99999',
    'background:rgba(0,0,0,0.85)',
    'color:#0f0',
    'font:12px/1.5 monospace',
    'padding:8px 10px',
    'white-space:pre',
    'pointer-events:none',
  ].join(';')
  document.body.appendChild(panel)

  const render = (): void => {
    const root = getComputedStyle(document.documentElement)
    const wa = window.Telegram?.WebApp as unknown as Record<string, unknown>

    // The actual element we patched. If it isn't found, the dashboard is not
    // rendered through MobileLayout (would explain why padding does nothing).
    const ml = document.querySelector('.mobile-layout') as HTMLElement | null
    const mlStyle = ml ? getComputedStyle(ml) : null

    const lines = [
      `--tg-content-safe-top (root): ${root.getPropertyValue('--tg-content-safe-area-inset-top').trim() || '(empty)'}`,
      `isFullscreen: ${String(wa?.isFullscreen ?? '(unknown)')}`,
      `.mobile-layout found: ${ml ? 'YES' : 'NO'}`,
      `.mobile-layout padding-top: ${mlStyle?.paddingTop ?? '(n/a)'}`,
      `.mobile-layout box-sizing: ${mlStyle?.boxSizing ?? '(n/a)'}`,
      `.mobile-layout top (rect): ${ml ? Math.round(ml.getBoundingClientRect().top) : '(n/a)'}`,
      `first child top (rect): ${
        ml?.firstElementChild
          ? Math.round((ml.firstElementChild as HTMLElement).getBoundingClientRect().top)
          : '(n/a)'
      }`,
    ]
    panel.textContent = lines.join('\n')
  }

  render()
  const events = ['safe_area_changed', 'content_safe_area_changed', 'viewport_changed', 'fullscreen_changed']
  for (const evt of events) {
    try {
      ;(
        window.Telegram?.WebApp as unknown as {
          onEvent?: (e: string, cb: () => void) => void
        }
      ).onEvent?.(evt, render)
    } catch {
      // ignore
    }
  }
  for (const delay of [200, 500, 1000, 2000, 3000]) {
    setTimeout(render, delay)
  }
}

export const telegramPlatform: Platform = {
  name: 'telegram',

  async init(): Promise<void> {
    const webApp = getWebApp()
    webApp.ready()
    webApp.expand()
    webApp.setHeaderColor('#334D6E')
    webApp.setBackgroundColor('#F8FAFC')

    // TEMP DIAGNOSTIC -- remove after reading values from the client's screen.
    showLayoutDiagnostic()
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

  openLink(url: string): void {
    // Telegram opens external links in the system browser.
    getWebApp().openLink(url)
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
