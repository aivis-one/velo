<!--
  VELO Frontend -- TEMPORARY bg-bug diagnostic HUD (ПРОМТ №380/381-AMEND/382/383,
  throwaway TEST-only build). Deletable in one step: remove this file + the
  `<BgDebugHud />` mount in App.vue.

  Purpose: a SINGLE screenshot taken with the keyboard open must reveal
  everything -- so every metric is shown as BASE (latched once at mount, while
  the keyboard is closed) / LIVE (refreshed continuously) / Δ (LIVE - BASE).
  A nonzero Δ on vv.top or a negative #app.top is PAN; a shrinking #app.height
  with #app.top staying 0 is RESIZE. Diagnosis locked (№383): it's neither --
  the ROOT itself is force-scrolled to reveal a focused input, dragging
  #app.top negative while #app.height stays frozen. `bg.top`/`bg.height`
  (added №383) measure the NEW `#app-bg` fixed layer that replaced
  `#app::before` -- proof-of-fix is `bg.top` staying ~0 (Δ 0) while `app.top`
  is still allowed to move.

  LIVE is driven by a 200ms poll, not just event listeners: a native Android
  pan may fire no JS event at all (no resize, no scroll, no visualViewport
  event) -- an event-only HUD would freeze mid-gesture and mislead whoever
  reads the screenshot. The poll is the source of truth for "what does the
  screen show right now"; listeners only make it react a beat faster.

  ALWAYS-ON (ПРОМТ №382): a `?bgdebug=1` query gate is unreachable in a real
  Telegram Mini App (bot-fixed URL, startapp payload lands in
  tgWebAppStartParam, not location.search) -- renders unconditionally until
  the device read is done, then this whole component + its App.vue wiring
  gets reverted.
-->
<template>
  <div class="bg-debug-hud">
    <div class="bg-debug-hud__title">BG DEBUG HUD</div>
    <div class="bg-debug-hud__row bg-debug-hud__row--head">
      <span class="bg-debug-hud__label"></span>
      <span class="bg-debug-hud__base">BASE</span>
      <span class="bg-debug-hud__live">LIVE</span>
      <span class="bg-debug-hud__delta">&Delta;</span>
    </div>
    <div
      v-for="m in metrics"
      :key="m.key"
      class="bg-debug-hud__row"
      :class="{ 'bg-debug-hud__row--highlight': m.highlight }"
    >
      <span class="bg-debug-hud__label">{{ m.label }}</span>
      <span class="bg-debug-hud__base">{{ base[m.key] }}</span>
      <span class="bg-debug-hud__live">{{ live[m.key] }}</span>
      <span class="bg-debug-hud__delta">{{ delta(m) }}</span>
    </div>
    <div class="bg-debug-hud__row">
      <span class="bg-debug-hud__label">kbd-open</span>
      <span class="bg-debug-hud__live" style="grid-column: span 3">{{ isKeyboardOpen }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { viewport } from '@tma.js/sdk-vue'

interface TelegramWebAppViewportShape {
  viewportHeight?: number
  viewportStableHeight?: number
  isExpanded?: boolean
}

interface Metric {
  key: string
  label: string
  numeric: boolean
  highlight?: boolean
  read: () => string | number
}

function readTelegramWebApp(): TelegramWebAppViewportShape | null {
  const wa = (window as unknown as { Telegram?: { WebApp?: TelegramWebAppViewportShape } })
    .Telegram?.WebApp
  return wa ?? null
}

function readSdkViewport(): { height?: number; stableHeight?: number } | null {
  // @tma.js/sdk-vue viewport is a Computed signal -- callable directly for a
  // one-off synchronous read (useSignal() is only needed for Vue reactivity).
  // Guarded: throws if the component was never mounted (isTelegramSdkReady
  // false, e.g. standalone browser).
  try {
    if (!viewport.isMounted()) return null
    return { height: viewport.height(), stableHeight: viewport.stableHeight() }
  } catch {
    return null
  }
}

function appRect(): DOMRect | null {
  return document.getElementById('app')?.getBoundingClientRect() ?? null
}

function bgRect(): DOMRect | null {
  // ПРОМТ №383: the new body-level fixed layer (index.html #app-bg). If it's
  // fixed correctly, this should read top≈0/height≈frozen on every poll tick,
  // completely independent of #app's own rect (which the root's forced
  // focus-scroll still legitimately moves).
  return document.getElementById('app-bg')?.getBoundingClientRect() ?? null
}

// One read() per metric -- BASE latches these once at mount, LIVE reruns them
// on every poll tick. Numeric metrics get a Δ column; non-numeric (n/a guards,
// booleans-as-string) don't.
const metrics: Metric[] = [
  { key: 'innerH', label: 'innerHeight', numeric: true, read: () => window.innerHeight },
  {
    key: 'clientH',
    label: 'docEl.clientH',
    numeric: true,
    read: () => document.documentElement.clientHeight,
  },
  { key: 'vvH', label: 'vv.height', numeric: true, read: () => window.visualViewport?.height ?? 0 },
  {
    key: 'vvTop',
    label: 'vv.offsetTop',
    numeric: true,
    highlight: true,
    read: () => window.visualViewport?.offsetTop ?? 0,
  },
  {
    key: 'vvPageTop',
    label: 'vv.pageTop',
    numeric: true,
    read: () => window.visualViewport?.pageTop ?? 0,
  },
  {
    key: 'frozenVh',
    label: 'frozen-vh',
    numeric: false,
    read: () =>
      document.documentElement.style.getPropertyValue('--velo-frozen-vh') || 'unset',
  },
  {
    key: 'tgVh',
    label: 'tg.vpHeight',
    numeric: false,
    read: () => {
      const v = readTelegramWebApp()?.viewportHeight
      return v != null ? v : 'n/a'
    },
  },
  {
    key: 'tgStable',
    label: 'tg.vpStable',
    numeric: false,
    read: () => {
      const v = readTelegramWebApp()?.viewportStableHeight
      return v != null ? v : 'n/a'
    },
  },
  {
    key: 'tgExpanded',
    label: 'tg.isExpanded',
    numeric: false,
    read: () => {
      const v = readTelegramWebApp()?.isExpanded
      return v != null ? String(v) : 'n/a'
    },
  },
  {
    key: 'sdkH',
    label: 'sdk.height',
    numeric: false,
    read: () => {
      const v = readSdkViewport()?.height
      return v != null ? v : 'n/a'
    },
  },
  {
    key: 'sdkStable',
    label: 'sdk.stable',
    numeric: false,
    read: () => {
      const v = readSdkViewport()?.stableHeight
      return v != null ? v : 'n/a'
    },
  },
  {
    key: 'appTop',
    label: 'app.top',
    numeric: true,
    highlight: true,
    read: () => Math.round(appRect()?.top ?? 0),
  },
  {
    key: 'appH',
    label: 'app.height',
    numeric: true,
    highlight: true,
    read: () => Math.round(appRect()?.height ?? 0),
  },
  {
    key: 'bgTop',
    label: 'bg.top',
    numeric: true,
    highlight: true,
    read: () => Math.round(bgRect()?.top ?? 0),
  },
  {
    key: 'bgH',
    label: 'bg.height',
    numeric: true,
    highlight: true,
    read: () => Math.round(bgRect()?.height ?? 0),
  },
]

const base: Record<string, string | number> = reactive({})
const live: Record<string, string | number> = reactive({})
const isKeyboardOpen = ref(false)

function delta(m: Metric): string {
  if (!m.numeric) return ''
  const b = base[m.key]
  const l = live[m.key]
  if (typeof b !== 'number' || typeof l !== 'number') return ''
  const d = l - b
  return d === 0 ? '0' : d > 0 ? `+${d}` : `${d}`
}

function captureBase(): void {
  for (const m of metrics) base[m.key] = m.read()
}

function refreshLive(): void {
  for (const m of metrics) live[m.key] = m.read()
  isKeyboardOpen.value = document.documentElement.classList.contains('is-keyboard-open')
}

let pollId = 0

onMounted(() => {
  // Capture BASE immediately -- assumes mount happens keyboard-closed, same
  // assumption freezeAppHeight() already relies on.
  captureBase()
  refreshLive()

  // POLL is the source of truth (catches a pan that fires zero JS events);
  // listeners just shave latency off the next poll tick for a snappier read.
  pollId = window.setInterval(refreshLive, 200)
  window.addEventListener('resize', refreshLive)
  window.addEventListener('focusin', refreshLive)
  window.visualViewport?.addEventListener('resize', refreshLive)
  window.visualViewport?.addEventListener('scroll', refreshLive)
})

onBeforeUnmount(() => {
  window.clearInterval(pollId)
  window.removeEventListener('resize', refreshLive)
  window.removeEventListener('focusin', refreshLive)
  window.visualViewport?.removeEventListener('resize', refreshLive)
  window.visualViewport?.removeEventListener('scroll', refreshLive)
})
</script>

<style scoped>
.bg-debug-hud {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 999999;
  background: #000;
  color: #0f0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  padding: 6px 8px 8px;
  pointer-events: none;
}

.bg-debug-hud__title {
  color: #ff0;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 2px;
}

.bg-debug-hud__row {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 0.8fr);
  column-gap: 6px;
}

.bg-debug-hud__row--head {
  color: #888;
  font-weight: bold;
}

.bg-debug-hud__row--highlight .bg-debug-hud__label,
.bg-debug-hud__row--highlight .bg-debug-hud__live,
.bg-debug-hud__row--highlight .bg-debug-hud__delta {
  color: #0ff;
  font-weight: bold;
}

.bg-debug-hud__base {
  color: #ccc;
}

.bg-debug-hud__delta {
  color: #f66;
  font-weight: bold;
}
</style>
