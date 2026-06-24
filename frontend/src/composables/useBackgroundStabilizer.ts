import { onMounted, onBeforeUnmount } from 'vue'

/**
 * Keeps the fixed photo-background layer (#app::before) visually pinned while
 * the on-screen keyboard opens.
 *
 * On iOS / Telegram webview, focusing a text input shrinks the visual viewport
 * and shifts the layout viewport; a `position:fixed` element (the bg layer in
 * global.css) then drifts/jumps -- the "dancing background". We counter that by
 * writing the visual viewport's offsetTop into a CSS custom property
 * (`--velo-bg-shift`) that the bg layer translates by, so it tracks the visible
 * area instead of drifting.
 *
 * At rest offsetTop is 0 -> the var is `0px` -> translateY(0px) -> pixel-identity
 * with no keyboard open (inert, since the pseudo is fixed / z-index:-1 / no
 * pointer events). The writes are rAF-throttled so a burst of resize/scroll
 * events collapses to one style write per frame.
 *
 * Mounted ONCE from App.vue (the always-mounted root). Independent of
 * useKeyboardOpen (the tab-bar flag): this only writes the CSS var, never the
 * keyboardOpen ref. No-ops where visualViewport is absent (SSR / desktop).
 */
export function useBackgroundStabilizer(): void {
  const vv = typeof window !== 'undefined' ? window.visualViewport : null
  let rafId = 0

  function setShift(): void {
    rafId = 0
    if (!vv) return
    const el = document.getElementById('app')
    if (!el) return
    el.style.setProperty('--velo-bg-shift', `${vv.offsetTop}px`)
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
  })

  onBeforeUnmount(() => {
    if (rafId) {
      window.cancelAnimationFrame(rafId)
      rafId = 0
    }
    vv?.removeEventListener('resize', schedule)
    vv?.removeEventListener('scroll', schedule)
    const el = typeof document !== 'undefined' ? document.getElementById('app') : null
    el?.style.setProperty('--velo-bg-shift', '0px')
  })
}
