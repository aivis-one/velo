// =============================================================================
// VELO Frontend -- Platform Interface (Phase F1.1)
// =============================================================================
//
// Contract that both Telegram and Standalone implementations follow.
// Components use `platform.*` without knowing which environment they're in.
//
// Telegram: real SDK calls (initData, haptic, back button, etc.)
// Standalone: safe no-ops (browser, PWA from Home Screen)
// =============================================================================

export interface Platform {
  /** Which environment we're running in. */
  readonly name: 'telegram' | 'standalone'

  /**
   * Initialize the platform.
   * Telegram: calls WebApp.ready(), expand(), sets header color.
   * Standalone: no-op.
   */
  init(): Promise<void>

  /**
   * Get Telegram initData for authentication.
   * Telegram: signed query string from WebApp.initData.
   * Standalone: null (no Telegram auth available).
   */
  getInitData(): string | null

  /**
   * Get current color scheme.
   * Telegram: reads WebApp.colorScheme.
   * Standalone: always 'light' (dark theme is out of MVP scope).
   */
  getTheme(): 'light' | 'dark'

  /**
   * Trigger haptic feedback.
   * Telegram: WebApp.HapticFeedback.impactOccurred(style).
   * Standalone: no-op (browser has no haptics).
   */
  hapticFeedback(style: 'light' | 'medium' | 'heavy'): void

  /**
   * Show the native back button (top-left in Telegram).
   * Telegram: WebApp.BackButton.show() + onClick handler.
   * Standalone: no-op (browser has its own back).
   */
  showBackButton(callback: () => void): void

  /**
   * Hide the native back button.
   * Telegram: WebApp.BackButton.hide() + remove handler.
   * Standalone: no-op.
   */
  hideBackButton(): void

  /**
   * Close the WebApp.
   * Telegram: WebApp.close() -- returns user to chat.
   * Standalone: no-op (can't close a browser tab programmatically).
   */
  close(): void
}
