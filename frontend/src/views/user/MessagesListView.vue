<!--
  VELO Frontend — MessagesListView (S2-S3 SPEEDRUN MEGA-2 §C49)
-->

<template>
  <div class="msgs">
    <header class="msgs__header">
      <button
        type="button"
        class="msgs__back"
        aria-label="Назад"
        @click="router.back()"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="msgs__title">
        Сообщения
      </h1>
    </header>

    <div
      v-if="messages.conversations.length === 0"
      class="msgs__empty"
    >
      Нет активных бесед.
    </div>
    <div
      v-else
      class="msgs__list"
    >
      <ConversationListItem
        v-for="c in messages.conversations"
        :key="c.id"
        :conversation="c"
        @click="open(c.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useMessagesStore } from '@/stores/messages'
import { IconArrowBack } from '@/components/icons'
import ConversationListItem from '@/components/shared/ConversationListItem.vue'

const router = useRouter()
const messages = useMessagesStore()

function open(id: string): void {
  messages.setActiveConversation(id)
  router.push(`/user/messages/${id}`)
}
</script>

<style scoped>
.msgs {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  min-height: 100%;
}

.msgs__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.msgs__back {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.msgs__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.msgs__empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.msgs__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
