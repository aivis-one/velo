/**
 * VELO Frontend -- Floating header island (G-1)
 *
 * Lets a screen's <VHeader> float as an island ABOVE the scrollable, fog-masked
 * content instead of scrolling inside it. The header lives in the DOM inside the
 * view (which is rendered into MobileLayout's masked __main), so a CSS mask alone
 * cannot exempt it -- it gets eaten by the fog. The fix: VHeader teleports itself
 * into an island layer that MobileLayout renders OUTSIDE __main, and registers
 * its presence so MobileLayout can add top clearance under the island.
 *
 * Provider  -> MobileLayout (and any layout that hosts a `.<host>__island` layer)
 * Consumer  -> VHeader
 *
 * When no provider is up the tree (shell-less screens like master/apply,
 * master/pending, and the admin layout which has no rail/fog), the consumer
 * reports `floating = false` and VHeader renders inline exactly as before.
 */
import {
  inject,
  provide,
  ref,
  onMounted,
  onUnmounted,
  type Ref,
  type InjectionKey,
} from 'vue'

interface FloatingHeaderApi {
  /** Number of mounted headers (normally 0 or 1 -- one route at a time). */
  count: Ref<number>
  register(): void
  unregister(): void
}

const KEY: InjectionKey<FloatingHeaderApi> = Symbol('velo-floating-header')

/**
 * Called by the layout (MobileLayout). Returns a reactive count of mounted
 * floating headers; the layout adds top clearance while it is > 0.
 */
export function provideFloatingHeader(): Ref<number> {
  const count = ref(0)
  provide(KEY, {
    count,
    register() {
      count.value++
    },
    unregister() {
      count.value = Math.max(0, count.value - 1)
    },
  })
  return count
}

/**
 * Called by VHeader. Registers presence while mounted and returns whether a
 * floating island host exists (true -> teleport into it; false -> render inline).
 */
export function useFloatingHeader(): boolean {
  const api = inject(KEY, null)
  if (!api) return false
  onMounted(() => api.register())
  onUnmounted(() => api.unregister())
  return true
}
