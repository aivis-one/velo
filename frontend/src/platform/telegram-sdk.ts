// =============================================================================
// VELO Frontend -- Telegram SDK bootstrap (@tma.js/sdk) -- safe-area step 1
// =============================================================================
//
// Initializes @tma.js/sdk and binds the viewport CSS variables + safe-area
// insets, so the rest of the app can read a RELIABLE, reactive content
// safe-area inset (the whole reason the previous CSS-var approach failed: the
// vendored SDK wrote --tg-content-safe-area-inset-top with a raw setProperty
// that did not trigger a style recompute in the Telegram iOS WebView).
//
// This module runs IN PARALLEL with the existing window.Telegram.WebApp
// platform layer (platform/telegram.ts) during the migration. Nothing here
// touches the old layer, auth, or the tests yet -- it only adds the SDK.
//
// GUARDED: the SDK throws when the app is not launched from Telegram
// (standalone browser, PWA, unit tests in happy-dom). We detect the Telegram
// environment first and swallow any error, so the standalone build and the
// test gate stay green.
//
// CSS variables produced by bindCssVars() (default --tg- prefix):
//   --tg-viewport-height, --tg-viewport-width, --tg-viewport-stable-height
// Safe-area insets are exposed as signals (viewport.contentSafeAreaInsetTop(),
// etc.) and consumed reactively via useSafeArea() (see composables).
// =============================================================================

import { init, viewport } from '@tma.js/sdk-vue'

/** True when running inside a real Telegram client (launch params present). */
function isTelegramEnv(): boolean {
  // The vendored SDK still injects window.Telegram.WebApp; a non-empty initData
  // is the reliable "launched from Telegram" signal (same check the platform
  // layer uses). In standalone/tests this is absent -> we skip SDK init.
  const wa = (window as unknown as { Telegram?: { WebApp?: { initData?: string } } })
    .Telegram?.WebApp
  return !!wa?.initData
}

/** Whether the SDK was successfully initialized this session. */
let _initialized = false

/**
 * Best-effort Telegram SDK initialization. Called once from main.ts before
 * the Vue app is created. Safe to call outside Telegram (no-op) and safe to
 * call more than once (guarded by _initialized).
 */
export function initTelegramSdk(): void {
  if (_initialized) return
  if (!isTelegramEnv()) return

  try {
    // Configure the SDK's global dependencies. Without this, viewport.* throws.
    init()

    // Mount the viewport component (async) and bind its CSS variables once
    // ready. We do not await in main.ts -- the inset is consumed reactively via
    // signals, so it updates the bound CSS vars / refs as soon as it arrives.
    void mountViewport()

    _initialized = true
  } catch {
    // Outside Telegram or unsupported client -- standalone/tests fall through.
  }
}

/** Mount viewport, bind CSS vars, request fullscreen (all best-effort). */
async function mountViewport(): Promise<void> {
  try {
    if (viewport.mount.isAvailable()) {
      await viewport.mount()
    }
    // Expose --tg-viewport-* CSS variables (height / width / stable-height).
    if (viewport.bindCssVars.isAvailable()) {
      viewport.bindCssVars()
    }
    // Fullscreen is a product requirement for VELO. Request it once mounted.
    if (viewport.requestFullscreen.isAvailable()) {
      await viewport.requestFullscreen()
    }
  } catch {
    // Viewport not supported on this client/version -- safe-area falls back to 0.
  }
}

/** True if the SDK was initialized (for diagnostics / guards). */
export function isTelegramSdkReady(): boolean {
  return _initialized
}
