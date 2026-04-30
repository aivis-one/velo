<!--
  VELO Frontend — ConversationListItem (S2-S3 SPEEDRUN MEGA-2 §C49)
-->

<template>
  <button
    type="button"
    class="conv"
    @click="$emit('click')"
  >
    <span
      v-if="conversation.counterparty.avatar_url"
      class="conv__avatar"
    >
      <img
        :src="conversation.counterparty.avatar_url"
        :alt="conversation.counterparty.name"
      >
    </span>
    <span
      v-else
      class="conv__avatar conv__avatar--mono"
      aria-hidden="true"
    >
      VΘ
    </span>
    <span class="conv__body">
      <span class="conv__head">
        <span class="conv__name">{{ conversation.counterparty.name }}</span>
        <span class="conv__time">{{ humanTime(conversation.last_message.created_at) }}</span>
      </span>
      <span class="conv__preview">{{ conversation.last_message.text }}</span>
    </span>
    <span
      v-if="conversation.unread_count > 0"
      class="conv__badge"
    >
      {{ conversation.unread_count }}
    </span>
  </button>
</template>

<script setup lang="ts">
import type { Conversation } from '@/utils/mockMessagesData'

defineProps<{ conversation: Conversation }>()
defineEmits<{ (e: 'click'): void }>()

function humanTime(iso: string): string {
  try {
    const d = new Date(iso)
    const now = new Date()
    const today = now.toISOString().slice(0, 10)
    if (iso.slice(0, 10) === today) {
      return d.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
      })
    }
    const yesterday = new Date(now)
    yesterday.setDate(yesterday.getDate() - 1)
    if (iso.slice(0, 10) === yesterday.toISOString().slice(0, 10)) {
      return 'Вчера'
    }
    return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
  } catch {
    return ''
  }
}
</script>

<style scoped>
.conv {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.conv__avatar {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-steel-alpha-15);
  border: 1px solid var(--text-primary);
}

.conv__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.conv__avatar--mono {
  font-family: var(--font-heading);
  font-size: 18px;
  color: var(--text-primary);
}

.conv__body {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.conv__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.conv__name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv__time {
  flex-shrink: 0;
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.conv__preview {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv__badge {
  flex-shrink: 0;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  border-radius: var(--radius-full);
  background: var(--pink-primary, var(--text-primary));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: 600;
}
</style>
