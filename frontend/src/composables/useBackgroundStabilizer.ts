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
// Input types that do NOT open the soft keyboard (so focusing them must not freeze
// the background). Everything else on <input> is text-entry (text/number/email/…).
const NON_TEXT_INPUT_TYPES = [
  'button',
  'submit',
  'reset',
  'checkbox',
  'radio',
  'file',
  'range',
  'color',
  'image',
  'hidden',
]

// True for a target that opens the soft keyboard on focus (text input / textarea /
// contenteditable) — the only focuses that should trigger the early bg-freeze.
function isTextEntry(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  if (target.tagName === 'TEXTAREA') return true
  if (target.isContentEditable) return true
  if (target.tagName === 'INPUT') {
    return !NON_TEXT_INPUT_TYPES.includes((target as HTMLInputElement).type)
  }
  return false
}

export function useBackgroundStabilizer(): void {
  const vv = typeof window !== 'undefined' ? window.visualViewport : null
  let rafId = 0
  let stopAfterEach: (() => void) | null = null

  // SP-3 — focus-driven early bg-freeze. The is-keyboard-open freeze (global.css)
  // only trips after the viewport shrinks past KEYBOARD_VIEWPORT_THRESHOLD (150px),
  // so the photo still slides during the keyboard's open-animation. Toggle a
  // `is-field-focused` class the instant a text field is focused — BEFORE the
  // keyboard animates — so `#app::before` is pinned for that whole window (see the
  // global.css rule). Only the bg-freeze engages early; is-keyboard-open (max-height
  // cap + mask-drop) stays on the 150px threshold, so there's no premature reflow.
  function onFocusIn(e: FocusEvent): void {
    if (isTextEntry(e.target)) document.documentElement.classList.add('is-field-focused')
  }
  function onFocusOut(): void {
    // Blur clears it; moving between two fields drops it for a frame then re-adds on
    // the next focusin — harmless (the keyboard stays open, so the is-keyboard-open
    // freeze covers the gap, and at rest transform:none == translateY(0) anyway).
    document.documentElement.classList.remove('is-field-focused')
  }

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
    // Focus listeners run regardless of visualViewport support (harmless without it —
    // no keyboard ⇒ no shift ⇒ transform:none == translateY(0)).
    document.addEventListener('focusin', onFocusIn)
    document.addEventListener('focusout', onFocusOut)
    if (!vv) return
    vv.addEventListener('resize', schedule)
    vv.addEventListener('scroll', schedule)
    setShift()
    // Clear stale shift / fog state the instant the route changes, so the next
    // screen's first frames don't inherit the previous screen's keyboard state.
    stopAfterEach = router.afterEach(() => resetKeyboardViewportState())
  })

  onBeforeUnmount(() => {
    document.removeEventListener('focusin', onFocusIn)
    document.removeEventListener('focusout', onFocusOut)
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
