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
// TEMP DIAGNOSTIC: measures both .welcome and .mobile-layout (padding-top,
// box-sizing, geometry) so we can see, on the Welcome screen specifically,
// whether the padding applied (and where the first child actually sits).
// Remove this block once read.
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
function showDiagnostic(): void {
  const panel = document.createElement('div')
  panel.id = 'velo-diagnostic'
  panel.style.cssText = [
    'position:fixed',
    'top:0',
    'left:0',
    'right:0',
    'z-index:99999',
    'background:rgba(0,0,0,0.85)',
    'color:#0f0',
    'font:11px/1.45 monospace',
    'padding:8px 10px',
    'white-space:pre',
    'pointer-events:none',
  ].join(';')
  document.body.appendChild(panel)

  const measure = (sel: string): string => {
    const el = document.querySelector(sel) as HTMLElement | null
    if (!el) return `${sel}: NOT FOUND`
    const s = getComputedStyle(el)
    const rectTop = Math.round(el.getBoundingClientRect().top)
    const childTop = el.firstElementChild
      ? Math.round((el.firstElementChild as HTMLElement).getBoundingClientRect().top)
      : NaN
    const justify = s.justifyContent
    return [
      `${sel}: FOUND`,
      `  padding-top: ${s.paddingTop}`,
      `  box-sizing:  ${s.boxSizing}`,
      `  justify:     ${justify}`,
      `  rect.top:    ${rectTop}`,
      `  child.top:   ${Number.isNaN(childTop) ? '(none)' : childTop}`,
    ].join('\n')
  }

  const render = (): void => {
    const root = getComputedStyle(document.documentElement)
    const wa = window.Telegram?.WebApp as unknown as Record<string, unknown>
    const lines = [
      `--tg-content-safe-top (root): ${root.getPropertyValue('--tg-content-safe-area-inset-top').trim() || '(empty)'}`,
      `isFullscreen: ${String(wa?.isFullscreen ?? '(unknown)')}`,
      measure('.welcome'),
      measure('.mobile-layout'),
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
    showDiagnostic()
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
