// =============================================================================
// VELO Frontend -- useSafeArea Composable (@tma.js/sdk-vue)
// =============================================================================
//
// Single source of truth for the top safe-area offset the app content must
// leave clear in fullscreen, backed by the official SDK viewport signals.
//
// WHY THE SUM OF TWO INSETS (device-verified):
//   Telegram exposes two top insets, and the buttons (Close / menu) sit ABOVE
//   the system status-bar area, so the content must clear BOTH:
//     - safeAreaInset.top        = system area (status bar / notch), e.g. 44px
//     - contentSafeAreaInset.top = Telegram's own controls strip, e.g. 46px
//   Taking only contentSafeAreaInset (46) pushed content out from under the
//   status bar but NOT from under the Close button. The full clearance is the
//   SUM: 44 + 46 = 90px in fullscreen. Out of fullscreen (launched from a
//   chat) both are 0, so the sum is 0 and Telegram draws its own header --
//   exactly what we want, no extra padding.
//
//   These numbers were read live on device via the diagnostic panel:
//     fullscreen: safeAreaInset.top=44, contentSafeAreaInset.top=46
//     in-chat:    both 0
//
// WHY SIGNALS (not a CSS var): the insets arrive asynchronously after first
// paint; the vendored SDK's raw setProperty did not trigger a style recompute
// in the Telegram iOS WebView, so a CSS var() stayed at 0. useSignal() turns
// each SDK signal into a Vue ref, so an inline style bound to the value
// re-renders when the inset arrives -- which is what moves the content.
//
// GUARDED: outside Telegram (standalone, unit tests) the viewport is never
// mounted; we fall back to 0 to keep the standalone build and test gate green.
// =============================================================================

import { computed, type ComputedRef } from 'vue'
import { viewport, useSignal } from '@tma.js/sdk-vue'

function toNum(v: unknown): number {
  return typeof v === 'number' && Number.isFinite(v) ? v : 0
}

/**
 * Reactive top safe-area offset, in pixels: the full clearance the content
 * needs below Telegram's controls in fullscreen (system area + controls strip).
 *
 * Bind to an inline style so the padding re-renders reactively:
 *   :style="{ paddingTop: contentSafeTop + 'px' }"
 */
export function useSafeArea(): { contentSafeTop: ComputedRef<number> } {
  const isMounted = useSignal(viewport.isMounted)
  const safeTop = useSignal(viewport.safeAreaInsetTop)
  const contentTop = useSignal(viewport.contentSafeAreaInsetTop)

  const contentSafeTop = computed<number>(() => {
    if (!isMounted.value) return 0
    // Full top clearance = system safe area + Telegram controls strip.
    return toNum(safeTop.value) + toNum(contentTop.value)
  })

  return { contentSafeTop }
}
