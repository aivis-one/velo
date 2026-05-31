<!--
  VELO Frontend -- DiaryComposer (Diary redesign)

  Bottom "pill" composer for the diary feed. Creates a note (entry_type=note)
  via the store. The mic button is a visual stub in this iteration (tapping
  shows a "coming soon" toast); dream entries have no UI input yet (created
  via backend only). Search is not handled here.

  Visual: frosted pill (glass-blue bg, backdrop-blur, white border, white glow
  shadow) matching Figma screen 40. Mic + send sit at the right; the send
  button is enabled only when there is non-empty text.

  Emits `created` after a successful note creation so the parent can react
  (the store already refreshes the feed; this is just a hook).
-->

<template>
  <div class="composer">
    <textarea
      ref="inputEl"
      v-model="text"
      class="composer__input"
      :placeholder="placeholder"
      rows="1"
      :maxlength="MAX_LEN"
      :disabled="submitting"
      @input="autogrow"
      @keydown="onKeydown"
    />

    <div class="composer__actions">
      <button
        type="button"
        class="composer__btn composer__btn--mic"
        aria-label="Голосовой ввод"
        :disabled="submitting"
        @click="onMic"
      >
        <IconMic :size="20" />
      </button>
      <button
        type="button"
        class="composer__btn composer__btn--send"
        aria-label="Отправить"
        :disabled="!canSend || submitting"
        @click="onSend"
      >
        <IconSend :size="20" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { IconMic, IconSend } from '@/components/icons'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'

const MAX_LEN = 10000
const placeholder = 'Начните писать...'

const diaryStore = useDiaryStore()
const toast = useToast()

const emit = defineEmits<{ created: [] }>()

const text = ref('')
const submitting = ref(false)
const inputEl = ref<HTMLTextAreaElement | null>(null)

const canSend = computed(() => text.value.trim().length > 0)

// Grow the textarea with content up to a cap, then scroll internally.
function autogrow(): void {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 120)}px`
}

// Enter sends; Shift+Enter inserts a newline.
function onKeydown(e: KeyboardEvent): void {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    void onSend()
  }
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
      entry_type: 'note',
    })
    if (result.ok) {
      text.value = ''
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
/* Transparent flex container — the three islands float on it; nothing opaque
   here so the feed shows through the gaps between them. */
.composer {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  max-width: var(--velo-content-width);
}

/* Island 1: the glass input pill (the ONLY glass element in the composer). */
.composer__field {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  min-height: 50px;
  padding: var(--space-2) var(--space-4);
  box-sizing: border-box;
  background: var(--velo-glass-blue-15);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1.26px solid #ffffff;
  border-radius: var(--radius-full);
  box-shadow: var(--velo-shadow-glow);
}

.composer__input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: 16px;
  letter-spacing: 0.32px;
  line-height: 1.3;
  color: var(--velo-text-primary);
  max-height: 120px;
  overflow-y: auto;
}

.composer__input::placeholder {
  color: var(--velo-text-primary);
  opacity: 0.6;
}

.composer__actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex-shrink: 0;
}

/* Islands 2 & 3: SOLID round buttons (mic, send) — #627A9C, no glass; the icon
   stays readable on any backdrop. 44px circles (Figma Group 2545, r=20 ≈ 40-44). */
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
  color: #ffffff;
  transition: opacity var(--transition-fast);
}

.composer__btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.composer__btn:not(:disabled):hover {
  opacity: 0.85;
}
</style>
