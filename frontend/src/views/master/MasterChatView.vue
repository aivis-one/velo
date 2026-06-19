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
.chat {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.chat__thread {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4) 0 var(--space-6);
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

.chat__compose {
  position: sticky;
  bottom: 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) 0;
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
