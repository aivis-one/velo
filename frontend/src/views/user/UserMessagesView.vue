<!--
  VELO Frontend -- UserMessagesView (user messaging entry, 2026-06-30)

  User ↔ master conversations, reached from Profile ▸ «Аккаунт» ▸ «Сообщения».
  Route: /user/profile/messages (name: 'user-messages').

  HONEST STUB: there is no messaging backend yet (no conversations / thread / send
  endpoints — recorded in VELO-Backend-Tasks.md «Messaging»). This screen renders
  an honest empty-state — NEVER fake threads. It is the swap point for the real
  conversations list when the API + its design land (F1=А, operator 2026-06-30).
-->

<template>
  <div class="user-messages">
    <VHeader title="Сообщения" show-back @back="router.back()" />
    <VEmptyState
      title="Здесь появятся ваши переписки с мастерами"
      description="Функция в разработке"
    >
      <template #icon><IconMessages :size="48" /></template>
    </VEmptyState>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VEmptyState } from '@/components/ui'
import { IconMessages } from '@/components/icons'

const router = useRouter()
</script>

<style scoped>
.user-messages {
  display: flex;
  flex-direction: column;
}
</style>
