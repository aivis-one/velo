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
// TEMP DIAGNOSTIC: an on-screen overlay prints live safe-area / viewport /
// 100dvh values so the client can screenshot them on a real device. This whole
// block (showViewportDiagnostic + its call in init) is throwaway -- remove it
// once we have the numbers. Goal of THIS measurement: find out whether 100dvh
// equals the Telegram viewport height on iOS, which decides the height system.
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
//
// Renders a fixed panel at the top showing everything needed to design the
// height system: the real pixel height of a `height:100dvh` probe element,
// window.innerHeight, Telegram's reported viewportHeight, the safe-area insets,
// and the launch mode. Re-reads on every Telegram resize/safe-area event,
// because Telegram pushes those asynchronously AFTER init() (a one-shot read
// would capture stale zeros).
//
function showViewportDiagnostic(): void {
  // A real element sized to 100dvh, measured in px. This is the only reliable
  // way to learn what 100dvh actually resolves to inside the Telegram WebView.
  const probe = document.createElement('div')
  probe.style.cssText =
    'position:absolute;top:0;left:0;width:1px;height:100dvh;pointer-events:none;visibility:hidden;'
  document.body.appendChild(probe)

  const panel = document.createElement('div')
  panel.id = 'velo-viewport-diagnostic'
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
    // Raw WebApp fields not present on our typed interface.
    const wa = window.Telegram?.WebApp as unknown as Record<string, unknown>
    const probeH = Math.round(probe.getBoundingClientRect().height)
    const lines = [
      `100dvh probe (px):     ${probeH}`,
      `window.innerHeight:    ${window.innerHeight}`,
      `viewportHeight (TG):   ${String(wa?.viewportHeight ?? '(unknown)')}`,
      `viewportStableHeight:  ${String(wa?.viewportStableHeight ?? '(unknown)')}`,
      `--tg-safe-area-top:    ${root.getPropertyValue('--tg-safe-area-inset-top').trim() || '(empty)'}`,
      `--tg-content-safe-top: ${root.getPropertyValue('--tg-content-safe-area-inset-top').trim() || '(empty)'}`,
      `platform:     ${String(wa?.platform ?? '(unknown)')}`,
      `version:      ${String(wa?.version ?? '(unknown)')}`,
      `isExpanded:   ${String(wa?.isExpanded ?? '(unknown)')}`,
      `isFullscreen: ${String(wa?.isFullscreen ?? '(unknown)')}`,
    ]
    panel.textContent = lines.join('\n')
  }

  render()

  // Telegram pushes safe-area / viewport data asynchronously after init().
  // Re-render whenever it changes so the client screenshots real numbers.
  const events = [
    'safe_area_changed',
    'content_safe_area_changed',
    'viewport_changed',
    'fullscreen_changed',
    'theme_changed',
  ]
  for (const evt of events) {
    try {
      ;(
        window.Telegram?.WebApp as unknown as {
          onEvent?: (e: string, cb: () => void) => void
        }
      ).onEvent?.(evt, render)
    } catch {
      // Ignore -- older client without this event.
    }
  }
  // Belt-and-suspenders: also re-read a few times in case events are missed.
  for (const delay of [100, 300, 600, 1000, 2000]) {
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
    showViewportDiagnostic()
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
