// =============================================================================
// VELO Frontend -- useSafeArea Composable (@tma.js/sdk-vue) -- safe-area step 2
// =============================================================================
//
// Single source of truth for the Telegram content safe-area top inset, now
// backed by the official SDK signal instead of a hand-rolled window.Telegram
// event subscription.
//
// WHY THE SDK SIGNAL (and not a raw CSS var or manual onEvent):
//   The content safe-area inset arrives asynchronously, after first paint.
//   The vendored SDK wrote --tg-content-safe-area-inset-top via a raw
//   setProperty that did not trigger a style recompute in the Telegram iOS
//   WebView, so a CSS var() stayed at 0. @tma.js/sdk exposes the inset as a
//   reactive SIGNAL (viewport.contentSafeAreaInsetTop); useSignal() turns it
//   into a Vue ref that updates on every change, so any inline style bound to
//   it re-renders when the inset arrives -- which is what actually moves the
//   content.
//
// GUARDED: outside Telegram (standalone browser, unit tests in happy-dom) the
// viewport component is never mounted, so reading the signal is unsafe. We
// detect mount state and fall back to 0, keeping the standalone build and the
// test gate green.
//
// PATTERN: thin composable returning a readonly reactive value, consistent
// with useAuth / useToast.
// =============================================================================

import { computed, type ComputedRef } from 'vue'
import { viewport, useSignal } from '@tma.js/sdk-vue'

/**
 * Reactive Telegram content safe-area top inset, in pixels.
 *
 * "Content" safe area is the room Telegram reserves for its own controls
 * (Close / menu) in fullscreen. Device-verified: 46px in fullscreen, 0 inside
 * a chat. Bind it to an inline style so the padding re-renders reactively:
 *   :style="{ paddingTop: contentSafeTop + 'px' }"
 */
export function useSafeArea(): { contentSafeTop: ComputedRef<number> } {
  // viewport.contentSafeAreaInsetTop is a signal; useSignal gives a Vue ref
  // that tracks it. When the viewport isn't mounted (standalone / tests),
  // reading the signal could throw, so guard with isMounted and default to 0.
  const isMounted = useSignal(viewport.isMounted)
  const rawTop = useSignal(viewport.contentSafeAreaInsetTop)

  const contentSafeTop = computed<number>(() => {
    if (!isMounted.value) return 0
    const top = rawTop.value
    return typeof top === 'number' && Number.isFinite(top) ? top : 0
  })

  return { contentSafeTop }
}
