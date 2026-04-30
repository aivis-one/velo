<!--
  VELO Frontend — ThreadView (S2-S3 SPEEDRUN MEGA-2 §C49)

  Single conversation thread. Bubbles + ThreadComposer at bottom.
  Send button currently fires toast.info via store.
-->

<template>
  <div class="thread">
    <header class="thread__header">
      <button
        type="button"
        class="thread__back"
        aria-label="Назад"
        @click="router.back()"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="thread__title">
        {{ conversation?.counterparty.name ?? 'Чат' }}
      </h1>
    </header>

    <div class="thread__messages">
      <ChatBubble
        v-for="m in messagesList"
        :key="m.id"
        :message="m"
        :is-me="m.sender_id === 'me'"
      />
    </div>

    <ThreadComposer @send="onSend" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { IconArrowBack } from '@/components/icons'
import ChatBubble from '@/components/shared/ChatBubble.vue'
import ThreadComposer from '@/components/shared/ThreadComposer.vue'
import { useMessagesStore } from '@/stores/messages'

const route = useRoute()
const router = useRouter()
const messages = useMessagesStore()

const conversation = computed(() => messages.activeConversation)
const messagesList = computed(() => messages.activeMessages)

function applyRoute(id: string): void {
  messages.setActiveConversation(id)
}

watch(
  () => route.params.conversationId,
  (id) => {
    if (typeof id === 'string') applyRoute(id)
  },
)

function onSend(text: string): void {
  messages.sendMessage(text)
}

onMounted(() => {
  const id = route.params.conversationId
  if (typeof id === 'string') applyRoute(id)
})
</script>

<style scoped>
.thread {
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-height: 100%;
}

.thread__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  border-bottom: 1px solid var(--text-primary);
}

.thread__back {
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

.thread__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.thread__messages {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  overflow-y: auto;
}
</style>
