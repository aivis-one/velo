import { onMounted, onBeforeUnmount } from 'vue'
import router from '@/router'
import { KEYBOARD_VIEWPORT_THRESHOLD } from '@/utils/constants'
import { resetKeyboardViewportState } from '@/utils/keyboardViewportState'

/**
 * App-root keyboard-viewport publisher. Mounted ONCE from App.vue (the
 * always-mounted root); the single visualViewport listener for CSS state.
 *
 * The "dancing background" is fixed STRUCTURALLY now (batch K): #app::before is an
 * absolute child of #app's stable 100lvh box (global.css), so it no longer tracks
 * the visual viewport and there is nothing to counter-shift per frame. This
 * composable therefore no longer writes `--velo-bg-shift` or freezes any transform.
 *
 * Its one remaining job: keyboard-aware LAYOUT. It publishes the visual-viewport
 * HEIGHT as `--velo-vvh` and toggles `is-keyboard-open`, BOTH on :root
 * (documentElement) so teleported modals (under <body>, outside #app) inherit them.
 * The gated rules in global.css cap the scroll container / modal to `--velo-vvh`
 * ONLY while that class is present. At rest the class is absent → the rules are
 * inert → layout is byte-identical. Threshold is shared with useKeyboardOpen
 * (KEYBOARD_VIEWPORT_THRESHOLD) so the two never drift.
 *
 * Writes are rAF-throttled (one style write per frame). No-ops where
 * visualViewport is absent (SSR / desktop → class never added).
 *
 * K3f — on every route change it (1) blurs the active element so a focused field
 * releases and the keyboard dismisses on navigation, (2) resets the state, and
 * (3) opens a short SUPPRESSION window during which it will NOT re-assert
 * `is-keyboard-open` / `--velo-vvh`. Without it, a still-closing keyboard fires
 * more visualViewport resizes right after the reset and repaints keyboard-open
 * geometry (the max-height cap → a fog "line" band + reflow lag) onto the freshly
 * navigated screen.
 */
// K3f suppression window (ms): a soft keyboard animates shut over ~250ms; hold
// at-rest geometry a touch longer so no closing-keyboard frame re-caps the new screen.
const NAV_SUPPRESS_MS = 350

export function useBackgroundStabilizer(): void {
  const vv = typeof window !== 'undefined' ? window.visualViewport : null
  let rafId = 0
  let stopAfterEach: (() => void) | null = null
  // Timestamp (ms, epoch) until which keyboard-open geometry is suppressed after a
  // navigation. 0 = not suppressing.
  let suppressUntil = 0

  function setShift(): void {
    rafId = 0
    if (!vv) return
    const root = document.documentElement
    // K3f: while the post-navigation window is open, hold at-rest geometry so a
    // closing keyboard can't paint the cap onto the screen the user just opened.
    if (Date.now() < suppressUntil) {
      root.classList.remove('is-keyboard-open')
      root.style.setProperty('--velo-vvh', '')
      return
    }
    // Keyboard-aware layout state, published on :root so teleported modals inherit
    // it. See global.css `html.is-keyboard-open`.
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
    // K3f + the between-screens "fog lag": clear stale keyboard state the instant
    // the route changes, dismiss the keyboard, then suppress re-assertion while it
    // animates shut so the next screen never inherits keyboard-open geometry.
    stopAfterEach = router.afterEach(() => {
      ;(document.activeElement as HTMLElement | null)?.blur?.()
      resetKeyboardViewportState()
      suppressUntil = Date.now() + NAV_SUPPRESS_MS
      // Re-sync truth once the window closes (the keyboard may legitimately still
      // be open on the new screen — rare, but then this restores the cap).
      window.setTimeout(schedule, NAV_SUPPRESS_MS)
    })
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
