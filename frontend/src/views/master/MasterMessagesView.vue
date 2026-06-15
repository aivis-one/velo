<!--
  VELO Frontend -- MasterMessagesView (messages list, 2026-06-13)

  Master ↔ participant conversations. Route /master/messages, built to the
  «2 Messages» design. STUB: no messaging backend yet → the list is hardcoded
  sample data and opening a thread toasts nothing (navigates to the equally-stub
  chat). -> Zod: conversations + unread-count API (roadmap Screen 14).
-->

<template>
  <div class="messages">
    <VHeader title="Сообщения" show-back @back="router.back()" />

    <div class="messages__list">
      <button
        v-for="c in conversations"
        :key="c.id"
        type="button"
        class="messages__row"
        @click="openChat(c.id)"
      >
        <VAvatar :name="c.name" size="md" class="messages__avatar" />
        <div class="messages__body">
          <div class="messages__top">
            <span class="messages__name">{{ c.name }}</span>
            <span class="messages__time">{{ c.time }}</span>
          </div>
          <div class="messages__bottom">
            <span class="messages__preview">{{ c.preview }}</span>
            <span v-if="c.unread" class="messages__badge">{{ c.unread }}</span>
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VAvatar } from '@/components/ui'

const router = useRouter()

// STUB sample (no messaging backend) -> Zod.
const conversations = [
  {
    id: '1',
    name: 'Мария К.',
    preview: 'Спасибо за практику! Чувствую себя…',
    time: '5 мин',
    unread: 1,
  },
  { id: '2', name: 'Анна П.', preview: 'Подскажите, как правильно…', time: '1 час', unread: 1 },
  { id: '3', name: 'Дмитрий С.', preview: 'Понял, спасибо!', time: 'Вт', unread: 0 },
  { id: '4', name: 'Поддержка VELΘ', preview: 'Ваш запрос обработан…', time: '19.01', unread: 0 },
]

function openChat(id: string): void {
  router.push({ name: 'master-chat', params: { id } })
}
</script>

<style scoped>
.messages {
  display: flex;
  flex-direction: column;
}

.messages__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4) 0;
}

.messages__row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  text-align: left;
  font-family: var(--font-body);
  transition: opacity var(--transition-fast);
}

.messages__row:active {
  opacity: 0.85;
}

.messages__avatar {
  flex-shrink: 0;
}

.messages__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.messages__top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-2);
}

.messages__name {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.messages__time {
  flex-shrink: 0;
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

.messages__bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.messages__preview {
  flex: 1;
  min-width: 0;
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.messages__badge {
  flex-shrink: 0;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: var(--radius-full);
  background: var(--velo-error);
  color: white;
  font-size: var(--text-xs);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
