<!--
  VELO Frontend -- DiaryComposer (Diary redesign)

  Bottom composer for the diary feed. Creates a diary entry via the store; the
  target entry_type ('note' for Дневник, 'dream' for Сонник) is decided by the
  parent from the active filter and passed in as `entryType`.

  Behaviour:
  - Idle: a borderless "rail" field (translucent white outline + soft glow,
    matches the floating-glass chrome). Left: keyboard-collapse button (⌄);
    right: mic (stub) + send.
  - Compose (field focused): the parent dims the feed; here the field LIFTS to
    its own full-width row above the buttons, text turns white, and the ⌄ button
    inverts to white (mirrors the top white back-pill). Emits `composingChange`
    so the parent can toggle its dim scrim.
  - Collapsed with a draft: when blurred with unsent text, the field shows the
    START of that text + ellipsis (single line) instead of the placeholder, so
    the frame does not stay expanded. Tapping it re-opens compose.
  - Enter inserts a newline (send is the ↑ button only).
  - The unsent draft is mirrored to localStorage (keyed by entryType) on every
    keystroke, so it survives keyboard collapse / accidental navigation on iOS.

  Emits `created` after a successful entry so the parent can react.
-->

<template>
  <div class="composer" :class="{ 'composer--composing': composing }">
    <button
      type="button"
      class="composer__btn composer__btn--kb"
      aria-label="Свернуть клавиатуру"
      :disabled="submitting"
      @mousedown.prevent
      @click="toggleKeyboard"
    >
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" class="composer__kb-glyph">
        <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <div class="composer__field" @click="openCompose">
      <textarea
        v-show="!showPreview"
        ref="inputEl"
        v-model="text"
        class="composer__input"
        :placeholder="placeholder"
        rows="1"
        :maxlength="MAX_LEN"
        :disabled="submitting"
        @input="autogrow"
        @focus="onFocus"
        @blur="onBlur"
      />
      <span v-if="showPreview" class="composer__preview">{{ previewText }}</span>
    </div>

    <div class="composer__actions">
      <button
        type="button"
        class="composer__btn composer__btn--mic"
        aria-label="Голосовой ввод"
        :disabled="submitting"
        @pointerdown.prevent
        @click="onMic"
      >
        <IconMic :size="20" />
      </button>
      <button
        type="button"
        class="composer__btn composer__btn--send"
        aria-label="Отправить"
        :disabled="!canSend || submitting"
        @pointerdown.prevent
        @click="onSend"
      >
        <IconSend :size="20" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onBeforeUnmount } from 'vue'
import { IconMic, IconSend } from '@/components/icons'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'

const MAX_LEN = 10000

const props = withDefaults(
  defineProps<{
    /** Target diary entry type, decided by the parent from the active filter. */
    entryType?: 'note' | 'dream'
  }>(),
  { entryType: 'note' },
)

const emit = defineEmits<{
  created: []
  /** Field focused / blurred -- the parent toggles its dim scrim. */
  composingChange: [composing: boolean]
}>()

const diaryStore = useDiaryStore()
const toast = useToast()

const text = ref('')
const submitting = ref(false)
const composing = ref(false)
const inputEl = ref<HTMLTextAreaElement | null>(null)

const placeholder = computed(() =>
  props.entryType === 'dream' ? 'Запишите сон...' : 'Начните писать...',
)
const canSend = computed(() => text.value.trim().length > 0)

// Collapsed-with-draft preview: when not composing but there is unsent text,
// show its start (+ CSS ellipsis) instead of the empty placeholder.
const showPreview = computed(() => !composing.value && text.value.trim().length > 0)
const previewText = computed(() => text.value.replace(/\s*\n\s*/g, ' ').trim())

// -- Draft persistence (localStorage, keyed by target) -----------------------
// Survives keyboard collapse / navigation (iOS loses in-memory state); cleared
// on a successful send.
const draftKey = computed(() => `velo:diary:draft:${props.entryType}`)

function loadDraft(): void {
  try {
    text.value = localStorage.getItem(draftKey.value) ?? ''
  } catch {
    text.value = ''
  }
  void nextTick(autogrow)
}

watch(text, (val) => {
  try {
    if (val) localStorage.setItem(draftKey.value, val)
    else localStorage.removeItem(draftKey.value)
  } catch {
    /* storage unavailable (private mode / quota) -- ignore, draft is best-effort */
  }
})

// Switching Дневник <-> Сонник swaps to that target's own draft.
watch(() => props.entryType, loadDraft)

// Recompute the grow cap when the visual viewport changes (iOS keyboard show /
// hide), since the visible height drives how tall the field may grow.
function onViewportResize(): void {
  if (composing.value) autogrow()
}

onMounted(() => {
  loadDraft()
  window.visualViewport?.addEventListener('resize', onViewportResize)
})

onBeforeUnmount(() => {
  window.visualViewport?.removeEventListener('resize', onViewportResize)
})

// -- Compose focus state -----------------------------------------------------

function setComposing(on: boolean): void {
  if (composing.value === on) return
  composing.value = on
  emit('composingChange', on)
  // The grow cap depends on compose mode -- recompute once the class applies.
  void nextTick(autogrow)
}

function onFocus(): void {
  setComposing(true)
}

function onBlur(): void {
  setComposing(false)
}

// Open compose from a tap on the (possibly collapsed-preview) field: show the
// textarea first, then focus it (a display:none textarea can't be focused).
function openCompose(): void {
  if (composing.value) return
  setComposing(true)
  void nextTick(() => inputEl.value?.focus())
}

// Keyboard button: toggles. Tap when idle -> open + focus; tap when composing
// -> blur (collapses the keyboard, keeps the draft). On iOS blur() dismisses the
// keyboard; on Android it mirrors the system behaviour harmlessly.
function toggleKeyboard(): void {
  if (composing.value) inputEl.value?.blur()
  else openCompose()
}

// Grow the textarea with content, then scroll internally past the cap. In
// compose mode the field grows UP until its top is ~20% from the screen top
// (so a long entry can fill most of the screen); collapsed it stays small.
function autogrow(): void {
  const el = inputEl.value
  if (!el) return
  // Use the VISUAL viewport height (excludes the on-screen keyboard on iOS), so
  // the field grows only within the area still visible above the keyboard rather
  // than expanding behind it.
  // -96 clears the composer chrome; -80 extra is the top gap so the field stops
  // short of the header buttons instead of colliding with them.
  const vh = window.visualViewport?.height ?? window.innerHeight
  const cap = composing.value ? Math.max(120, Math.round(vh * 0.8) - 176) : 120
  el.style.maxHeight = `${cap}px`
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, cap)}px`
}

function onMic(): void {
  // Voice input is not implemented yet -- visual stub.
  toast.info('Функция временно недоступна')
}

async function onSend(): Promise<void> {
  if (!canSend.value || submitting.value) return
  submitting.value = true
  try {
    const result = await diaryStore.createEntry({
      content: text.value.trim(),
      entry_type: props.entryType,
    })
    if (result.ok) {
      text.value = '' // watch() clears the stored draft
      await nextTick()
      autogrow()
      emit('created')
    } else {
      toast.error(result.error)
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* Transparent flex container -- the field + buttons float on it; nothing opaque
   here so the feed shows through the gaps between them. */
.composer {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
}

/* The "rail" field: borderless, translucent white outline + soft glow (matches
   the floating-glass chrome). No solid fill -- keeps the airy look. */
.composer__field {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  min-height: 50px;
  padding: var(--space-2) var(--space-4);
  box-sizing: border-box;
  border: 1.26px solid rgba(255, 255, 255, 0.6);
  border-radius: var(--radius-full);
  box-shadow: 0 0 14px 2px rgba(255, 255, 255, 0.4);
  cursor: text;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    background var(--transition-fast);
}

.composer__input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: var(--text-16);
  letter-spacing: 0.32px;
  line-height: 1.3;
  color: var(--velo-text-primary);
  max-height: 120px;
  overflow-y: auto;
  transition: color var(--transition-fast);
}

.composer__input::placeholder {
  color: var(--velo-text-primary);
  opacity: 0.6;
}

/* Collapsed-with-draft single-line preview (start of text + ellipsis). */
.composer__preview {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: var(--font-body);
  font-size: var(--text-16);
  letter-spacing: 0.32px;
  color: var(--velo-text-primary);
  opacity: 0.85;
}

.composer__actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex-shrink: 0;
}

/* SOLID round buttons (kb, mic, send) -- #627A9C, no glass; icon stays readable
   on any backdrop. 44px circles (Figma Group 2545). */
.composer__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  background: var(--velo-nav-active-bg);
  color: var(--velo-white);
  transition:
    opacity var(--transition-fast),
    background var(--transition-fast),
    color var(--transition-fast);
}

.composer__kb-glyph {
  width: 22px;
  height: 22px;
  transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.composer__btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.composer__btn:not(:disabled):hover {
  opacity: 0.85;
}

/* -- Compose mode: field lifts to a full-width row ABOVE the buttons; the kb
   button inverts to white (mirrors the top white back-pill); text turns white
   on the parent's dim scrim. -- */
.composer--composing {
  flex-wrap: wrap;
  row-gap: var(--space-3);
  align-items: center;
}

.composer--composing .composer__field {
  order: -1;
  flex: 0 0 100%;
  width: 100%;
  min-height: 54px;
  align-items: flex-start;
  padding: 13px 18px;
  /* Blue outline + slightly whitened glass (matches the write-mode frost);
     NO dark, NO white inversion. */
  border-color: var(--velo-nav-active-bg);
  box-shadow: none;
  background: rgba(255, 255, 255, 0.55);
  -webkit-backdrop-filter: blur(var(--velo-write-blur));
  backdrop-filter: blur(var(--velo-write-blur));
  border-radius: 20px;
}

.composer--composing .composer__input {
  color: var(--velo-text-primary);
}

.composer--composing .composer__input::placeholder {
  color: var(--velo-text-primary);
  opacity: 0.55;
}

/* keep mic/send on the right of the second row; the kb button stays left */
.composer--composing .composer__actions {
  margin-left: auto;
}

/* kb button keeps its blue circle; the chevron rotates UP while writing (a state
   cue, mirrors the "..." dots animation). No colour inversion. */
.composer--composing .composer__btn--kb .composer__kb-glyph {
  transform: rotate(180deg);
}
</style>
