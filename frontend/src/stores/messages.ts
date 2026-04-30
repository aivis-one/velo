// =============================================================================
// VELO Frontend — Messages Store (S2-S3 SPEEDRUN MEGA-2 §C49)
//
// Mock-only store fronting MOCK_CONVERSATIONS / MOCK_THREADS.
// Real backend (Inbox endpoints + WebSocket) deferred per
// BACKEND-COORDINATION § A.7. Send-button currently fires toast.info per spec.
// =============================================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  MOCK_CONVERSATIONS,
  MOCK_THREADS,
  type Conversation,
  type ConversationMessage,
} from '@/utils/mockMessagesData'
import { useToast } from '@/composables/useToast'

export const useMessagesStore = defineStore('messages', () => {
  const conversations = ref<Conversation[]>(
    JSON.parse(JSON.stringify(MOCK_CONVERSATIONS)),
  )
  const activeConversationId = ref<string | null>(null)
  const threads = ref<Record<string, ConversationMessage[]>>(
    JSON.parse(JSON.stringify(MOCK_THREADS)),
  )

  const totalUnread = computed(() =>
    conversations.value.reduce((sum, c) => sum + c.unread_count, 0),
  )

  const activeMessages = computed<ConversationMessage[]>(() =>
    activeConversationId.value
      ? threads.value[activeConversationId.value] ?? []
      : [],
  )

  const activeConversation = computed<Conversation | null>(
    () =>
      conversations.value.find((c) => c.id === activeConversationId.value) ??
      null,
  )

  function setActiveConversation(id: string): void {
    activeConversationId.value = id
    // Mock mark-read
    const conv = conversations.value.find((c) => c.id === id)
    if (conv) {
      conv.unread_count = 0
      conv.last_message.is_unread = false
    }
  }

  function clearActiveConversation(): void {
    activeConversationId.value = null
  }

  function sendMessage(_text: string): void {
    const toast = useToast()
    toast.info('Сообщения скоро будут доступны')
  }

  return {
    conversations,
    activeConversationId,
    threads,
    totalUnread,
    activeMessages,
    activeConversation,
    setActiveConversation,
    clearActiveConversation,
    sendMessage,
  }
})
