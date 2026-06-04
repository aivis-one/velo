import { ref, onMounted, onBeforeUnmount } from 'vue'

/**
 * Reactive "is the on-screen keyboard open" flag, derived from visualViewport.
 *
 * When the soft keyboard opens, the visual viewport height shrinks well below
 * the layout viewport (window.innerHeight). We treat a shrink larger than
 * `threshold` px as "keyboard open".
 *
 * Used to hide the floating bottom tab bar while typing, so it does not ride up
 * and overlap a focused input (e.g. BookingConfirmedView's "запрос мастеру").
 * The same visualViewport approach is used by DiaryComposer for field sizing.
 *
 * No-ops gracefully where visualViewport is unavailable (flag stays false).
 */
export function useKeyboardOpen(threshold = 150) {
  const keyboardOpen = ref(false)
  const vv = typeof window !== 'undefined' ? window.visualViewport : null

  function update(): void {
    if (!vv) return
    keyboardOpen.value = window.innerHeight - vv.height > threshold
  }

  onMounted(() => {
    if (!vv) return
    vv.addEventListener('resize', update)
    update()
  })

  onBeforeUnmount(() => {
    vv?.removeEventListener('resize', update)
  })

  return { keyboardOpen }
}
