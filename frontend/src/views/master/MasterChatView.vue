<!--
  VELO Frontend -- MasterChatView (chat thread, 2026-06-13)

  Route /master/messages/:id, built to the «3 Chat» design. STUB: no messaging
  backend → hardcoded sample thread; sending toasts «недоступно». -> Zod.
  Tab bar hidden (detail screen, route meta.hideTabBar).
-->

<template>
  <div class="chat">
    <VHeader :title="peerName" show-back @back="router.back()" />

    <div class="chat__thread">
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="chat__msg"
        :class="m.out ? 'chat__msg--out' : 'chat__msg--in'"
      >
        <p class="chat__text">{{ m.text }}</p>
        <span class="chat__time">{{ m.time }}</span>
      </div>
    </div>

    <div class="chat__compose">
      <input v-model="draft" type="text" class="chat__input" placeholder="Написать сообщение…" />
      <button
        type="button"
        class="chat__send"
        :disabled="!draft.trim()"
        aria-label="Отправить"
        @click="onSend"
      >
        <IconSend :size="20" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { IconSend } from '@/components/icons'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()
const draft = ref('')

// STUB peer + thread (no messaging backend) -> Zod.
const peerName = 'Мария К.'
const messages = [
  { out: false, text: 'Здравствуйте! Спасибо за практику! Чувствую себя отлично.', time: '10:30' },
  { out: true, text: 'Рад, что вам понравилось! Буду ждать вас на следующей 🙏', time: '10:35' },
  {
    out: false,
    text: 'Обязательно приду! А можно записать дыхательное упражнение, которое мы делали в начале?',
    time: '10:40',
  },
]

function onSend(): void {
  toast.info('Сообщения пока недоступны')
}
</script>

<style scoped>
/* Fill-mode chat layout (MC-2, №242): the shell puts master-chat in MobileLayout
   `fill` mode (overflow:hidden, no rail, no shared fog), so the view owns its scroll,
   its rail, its top fog and a truly-pinned composer — mirroring the diary
   (DiaryFeedView `.diary-feed` / `__body` / `__composer`). */
.chat {
  position: relative;
  height: 100%;
  min-height: 0;
}

/* Keyboard-safe composer (M2, ПРОМТ №273): fill mode opts OUT of the shared
   keyboard shrink (global.css targets `.mobile-layout__main:not(--fill)`), so
   .chat kept its full pre-keyboard height and the absolute composer stayed at the
   old bottom — mid-screen, under the keyboard. Constrain .chat to the visible
   viewport (--velo-vvh, published by useBackgroundStabilizer) while the keyboard
   is open so the composer pins just above it. Reads the existing signal only —
   no new global machinery. */
html.is-keyboard-open .chat {
  height: var(--velo-vvh);
}

/* Internal-scroll thread: an absolute layer under the floating header + the pinned
   composer. Its own top/bottom fog mask (the MC-1 header-overlap fix, now view-side)
   dissolves the thread under the floating title on scroll and behind the composer.
   The clearances (header ~header-height top, composer bottom) + the inline mask
   mirror DiaryFeedView's `__body`; the rail is re-added here because fill mode zeroes
   MobileLayout's rail. */
.chat__thread {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: 92px var(--velo-rail-pad-x) 84px;
  scrollbar-width: none;
  -ms-overflow-style: none;
  -webkit-mask-image: linear-gradient(
    to bottom,
    transparent 0,
    transparent 44px,
    #000 92px,
    #000 calc(100% - 84px),
    transparent calc(100% - 40px),
    transparent 100%
  );
  mask-image: linear-gradient(
    to bottom,
    transparent 0,
    transparent 44px,
    #000 92px,
    #000 calc(100% - 84px),
    transparent calc(100% - 40px),
    transparent 100%
  );
}

.chat__thread::-webkit-scrollbar {
  display: none;
}

.chat__msg {
  max-width: 80%;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
}

.chat__msg--in {
  align-self: flex-start;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
}

.chat__msg--out {
  align-self: flex-end;
  background: var(--velo-primary);
}

.chat__text {
  margin: 0;
  font-size: var(--text-sm);
  line-height: 1.45;
}

.chat__msg--in .chat__text {
  color: var(--velo-text-primary);
}

.chat__msg--out .chat__text {
  color: var(--velo-white);
}

.chat__time {
  display: block;
  margin-top: var(--space-1);
  font-size: var(--text-xs);
}

.chat__msg--in .chat__time {
  color: var(--velo-text-muted);
}

.chat__msg--out .chat__time {
  color: var(--velo-white);
  opacity: 0.7;
}

/* Composer PINNED to the bottom (was position:sticky, which floated mid-thread when
   the stub thread was short — MC-2). An absolute layer over the faded thread bottom;
   the thread's bottom mask dissolves messages behind it, so no backing is needed. */
.chat__compose {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--velo-rail-pad-x);
}

.chat__input {
  flex: 1;
  height: var(--velo-size-50);
  padding: 0 var(--space-4);
  border-radius: var(--radius-full);
  border: 1px solid var(--velo-glass-border);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  /* Opaque white plate (was 1% glass) so the blue text the master types stays
     readable instead of bleeding into the bubble behind it (operator 2026-06-19). */
  background: var(--velo-bg-card-solid);
}

.chat__input::placeholder {
  color: var(--velo-text-muted);
}

.chat__send {
  flex-shrink: 0;
  width: var(--velo-size-44);
  height: var(--velo-size-44);
  border-radius: var(--radius-full);
  border: none;
  background: var(--velo-primary);
  color: var(--velo-white);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.chat__send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
