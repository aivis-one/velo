// =============================================================================
// VELO Frontend -- useSafeArea Composable (@tma.js/sdk-vue)
// =============================================================================
//
// Single source of truth for the top safe-area offset the app content must
// leave clear in fullscreen, backed by the official SDK viewport signals.
//
// FORMULA (device-tuned):
//   offset = safeAreaInset.top + contentSafeAreaInset.top - OVERLAP
//   where OVERLAP (20px) compensates for the fact that the system status-bar
//   area and Telegram's controls strip partially overlap; adding the two raw
//   insets (44 + 46 = 90) pushed the content a bit too low, leaving a gap
//   below the buttons. 90 - 20 = 70 sits the content just under the controls.
//
//   Guarded so the offset never goes negative: out of fullscreen (launched
//   from a chat) both insets are 0, the sum is 0, and we return 0 -- we do NOT
//   subtract OVERLAP there, otherwise the content would slide UP under
//   Telegram's own header. The subtraction only applies when there is a real
//   inset to trim (fullscreen).
//
//   Device-verified via the diagnostic panel:
//     fullscreen: safeAreaInset.top=44, contentSafeAreaInset.top=46 -> 70px
//     in-chat:    both 0 -> 0px
//
// WHY SIGNALS (not a CSS var): insets arrive asynchronously after first paint;
// the vendored SDK's raw setProperty did not trigger a style recompute in the
// Telegram iOS WebView, so a CSS var() stayed at 0. useSignal() turns each SDK
// signal into a Vue ref, so an inline style bound to the value re-renders when
// the inset arrives -- which is what moves the content.
//
// GUARDED: outside Telegram (standalone, unit tests) the viewport is never
// mounted; we fall back to 0 to keep the standalone build and test gate green.
// =============================================================================

import { computed, type ComputedRef } from 'vue'
import { viewport, useSignal } from '@tma.js/sdk-vue'

/** Overlap (px) between the status-bar area and Telegram's controls strip. */
const OVERLAP_PX = 20

function toNum(v: unknown): number {
  return typeof v === 'number' && Number.isFinite(v) ? v : 0
}

/**
 * Reactive top safe-area offset, in pixels: the clearance the content needs
 * below Telegram's controls in fullscreen, with the overlap trimmed.
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
    const sum = toNum(safeTop.value) + toNum(contentTop.value)
    // Only trim the overlap when there's a real inset (fullscreen). Out of
    // fullscreen sum is 0 -> return 0, never negative.
    return sum > 0 ? Math.max(sum - OVERLAP_PX, 0) : 0
  })

  return { contentSafeTop }
}
