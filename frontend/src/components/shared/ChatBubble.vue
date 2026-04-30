<!--
  VELO Frontend — ChatBubble (S2-S3 SPEEDRUN MEGA-2 §C49)

  Outgoing (right-aligned, ink-soft fill, white text) vs incoming
  (left-aligned, white surface, ink text).
-->

<template>
  <div
    class="bubble-row"
    :class="{ 'bubble-row--mine': isMe }"
  >
    <div
      class="bubble"
      :class="{ 'bubble--mine': isMe }"
    >
      <p class="bubble__text">
        {{ message.text }}
      </p>
      <span class="bubble__time">{{ humanTime(message.created_at) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ConversationMessage } from '@/utils/mockMessagesData'

defineProps<{
  message: ConversationMessage
  isMe: boolean
}>()

function humanTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
}
</script>

<style scoped>
.bubble-row {
  display: flex;
  justify-content: flex-start;
}

.bubble-row--mine {
  justify-content: flex-end;
}

.bubble {
  max-width: 75%;
  padding: var(--space-2) var(--space-3);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: var(--text-primary);
}

.bubble--mine {
  background: var(--steel-button);
  color: white;
  border-color: var(--steel-button);
}

.bubble__text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  margin: 0;
  white-space: pre-wrap;
}

.bubble__time {
  font-size: var(--text-xs);
  opacity: 0.7;
  align-self: flex-end;
}
</style>
