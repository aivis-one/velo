// =============================================================================
// VELO Frontend -- useSafeArea Composable (safe-area step 0)
// =============================================================================
//
// Single source of truth for the Telegram content safe-area top inset.
//
// WHY THIS EXISTS (and why a plain CSS var() was not enough):
//   The Telegram SDK writes --tg-content-safe-area-inset-top onto :root via
//   element.style.setProperty AFTER the first paint (it arrives on the async
//   contentSafeAreaChanged event). In the Telegram iOS WebView, a stylesheet
//   rule reading that CSS variable through var() does NOT reliably recompute
//   when the variable changes later -- so a layout whose padding-top is
//   `var(--tg-content-safe-area-inset-top)` stays at the fallback 0px even
//   once the real inset (46px in fullscreen) has been pushed. Reading the
//   value in JS and exposing it as a reactive Vue ref forces Vue to re-render
//   the bound inline style, which DOES update the rendered padding.
//
//   Device-verified: with this reactive ref the dashboard content starts at
//   the inset offset on first open, with no manual refresh.
//
// PATTERN: module-level ref shared across all useSafeArea() calls, matching
// the singleton-composable style already used by useAuth / useToast.
// =============================================================================

import { ref, readonly, onMounted, onUnmounted } from 'vue'

/** Minimal shape of the bits of the Telegram WebApp SDK we read here. */
interface TelegramWebAppLike {
  contentSafeAreaInset?: { top?: number; bottom?: number; left?: number; right?: number }
  safeAreaInset?: { top?: number; bottom?: number; left?: number; right?: number }
  onEvent?: (event: string, callback: () => void) => void
  offEvent?: (event: string, callback: () => void) => void
}

function getWebApp(): TelegramWebAppLike | null {
  return (window as unknown as { Telegram?: { WebApp?: TelegramWebAppLike } }).Telegram?.WebApp ?? null
}

/**
 * Content safe-area top inset in pixels.
 *
 * "Content" safe area is the space Telegram reserves for its own controls
 * (Close / menu) when the Mini App is opened fullscreen. In fullscreen it is
 * 46px on the tested device; launched inside a chat it is 0 (Telegram draws
 * its own header). This is the value to push content down by.
 */
const contentSafeTop = ref<number>(readInset())

/** How many live consumers are mounted -- so we subscribe once and clean up. */
let _refCount = 0

/** Telegram event names that affect the safe area (SDK uses camelCase). */
const SAFE_AREA_EVENTS = ['contentSafeAreaChanged', 'safeAreaChanged', 'viewportChanged'] as const

function readInset(): number {
  const wa = getWebApp()
  const top = wa?.contentSafeAreaInset?.top
  return typeof top === 'number' ? top : 0
}

function refresh(): void {
  contentSafeTop.value = readInset()
}

/**
 * Reactive access to the Telegram content safe-area top inset.
 *
 * Returns a readonly ref (px). Components bind it to an inline style, e.g.
 *   :style="{ paddingTop: contentSafeTop + 'px' }"
 * so the padding re-renders when the inset arrives/changes.
 */
export function useSafeArea() {
  onMounted(() => {
    _refCount += 1
    // Read once now (covers the case where the inset is already present), then
    // keep it in sync with Telegram's async events.
    refresh()
    const wa = getWebApp()
    if (wa?.onEvent) {
      for (const evt of SAFE_AREA_EVENTS) {
        wa.onEvent(evt, refresh)
      }
    }
  })

  onUnmounted(() => {
    _refCount -= 1
    if (_refCount <= 0) {
      _refCount = 0
      const wa = getWebApp()
      if (wa?.offEvent) {
        for (const evt of SAFE_AREA_EVENTS) {
          wa.offEvent(evt, refresh)
        }
      }
    }
  })

  return {
    /** Content safe-area top inset in px (reactive, readonly). */
    contentSafeTop: readonly(contentSafeTop),
  }
}
