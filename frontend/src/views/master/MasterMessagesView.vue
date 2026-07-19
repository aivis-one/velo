<!--
  VELO Frontend -- MasterMessagesView (messages list, 2026-06-13; honesty-cleanup 2026-07-12)

  Master <-> participant conversations. Route /master/messages, built to the
  «2 Messages» design. HONEST STUB: no messaging backend yet (no conversations /
  thread / send endpoints) -> renders an honest empty-state, mirroring
  UserMessagesView.vue. NEVER fake threads. -> Zod: conversations + unread-count
  API (roadmap Screen 14).
-->

<template>
  <div class="messages">
    <VHeader title="Сообщения" show-back @back="router.back()" />
    <VEmptyState title="Здесь появятся переписки с учениками" description="Функция в разработке">
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
.messages {
  display: flex;
  flex-direction: column;
}
</style>
