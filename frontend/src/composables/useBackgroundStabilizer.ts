import { onMounted, onBeforeUnmount } from 'vue'
import router from '@/router'
import { KEYBOARD_VIEWPORT_THRESHOLD } from '@/utils/constants'
import { resetKeyboardViewportState } from '@/utils/keyboardViewportState'

/**
 * App-root visual-viewport publisher. Mounted ONCE from App.vue (the
 * always-mounted root); the single visualViewport listener for CSS state.
 * Two jobs, both off the same rAF-throttled handler (no second listener stack):
 *
 *  1. "Dancing background" fix — on iOS / Telegram webview, focusing an input
 *     shrinks the visual viewport and shifts the layout viewport; the fixed bg
 *     layer (#app::before) then drifts. We write the viewport's offsetTop into
 *     `--velo-bg-shift` (on #app) that the bg layer translates by, so it tracks
 *     the visible area. At rest offsetTop is 0 -> `0px` -> translateY(0px) -> inert.
 *
 *  2. Keyboard-aware layout — publishes the visual-viewport HEIGHT as `--velo-vvh`
 *     and toggles the `is-keyboard-open` class, BOTH on :root (documentElement)
 *     so teleported modals (under <body>, outside #app) inherit them too. The
 *     gated rules in global.css cap the scroll container / modal to `--velo-vvh`
 *     ONLY while that class is present (#2/#6/#7). At rest the class is absent ->
 *     the rules are inert -> layout is byte-identical. Threshold is shared with
 *     useKeyboardOpen (KEYBOARD_VIEWPORT_THRESHOLD) so the two never drift.
 *
 * Writes are rAF-throttled (one style write per frame). No-ops where
 * visualViewport is absent (SSR / desktop -> class never added).
 *
 * Also resets the above state SYNCHRONOUSLY on every route change (a single
 * router.afterEach, registered once from this app-root composable) so a freshly
 * navigated screen never inherits the previous screen's shift / fog geometry
 * (the between-screens "fog lag", KB #4 item 6). If the keyboard is genuinely
 * still open, the next visualViewport event re-syncs truth on the following frame.
 */
export function useBackgroundStabilizer(): void {
  const vv = typeof window !== 'undefined' ? window.visualViewport : null
  let rafId = 0
  let stopAfterEach: (() => void) | null = null

  function setShift(): void {
    rafId = 0
    if (!vv) return
    const el = document.getElementById('app')
    if (el) el.style.setProperty('--velo-bg-shift', `${vv.offsetTop}px`)
    // Keyboard-aware layout state, published on :root so teleported modals
    // inherit it. See global.css `html.is-keyboard-open`.
    const root = document.documentElement
    root.style.setProperty('--velo-vvh', `${vv.height}px`)
    root.classList.toggle(
      'is-keyboard-open',
      window.innerHeight - vv.height > KEYBOARD_VIEWPORT_THRESHOLD,
    )
  }

  function schedule(): void {
    if (rafId) return
    rafId = window.requestAnimationFrame(setShift)
  }

  onMounted(() => {
    if (!vv) return
    vv.addEventListener('resize', schedule)
    vv.addEventListener('scroll', schedule)
    setShift()
    // Clear stale shift / fog state the instant the route changes, so the next
    // screen's first frames don't inherit the previous screen's keyboard state.
    stopAfterEach = router.afterEach(() => resetKeyboardViewportState())
  })

  onBeforeUnmount(() => {
    if (rafId) {
      window.cancelAnimationFrame(rafId)
      rafId = 0
    }
    vv?.removeEventListener('resize', schedule)
    vv?.removeEventListener('scroll', schedule)
    stopAfterEach?.()
    stopAfterEach = null
    resetKeyboardViewportState()
  })
}
