<!--
  VELO Frontend -- MasterChatView (chat thread; honesty-cleanup 2026-07-12)

  Route /master/messages/:id, only ever reached from MasterMessagesView's
  conversation list (grep-confirmed: no other entry point in the app). Now that
  the list is an honest empty-state (no fake conversations), this thread is
  unreachable via normal navigation but the route still resolves on a direct/deep
  link -- so it renders the same honest empty-state rather than a fabricated peer
  + message thread. HONEST STUB: no messaging backend. -> Zod.
  Tab bar hidden (detail screen, route meta.hideTabBar).
-->

<template>
  <div class="chat">
    <VHeader title="Сообщения" show-back @back="router.back()" />
    <VEmptyState title="Переписки пока недоступны" description="Функция в разработке">
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
/* Fill-mode screen (MasterShell routes master-chat into MobileLayout `fill` mode,
   which zeroes the shared rail) -- re-add rail padding and centre the empty-state
   vertically, mirroring how the old thread container supplied its own rail. */
.chat {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 var(--velo-rail-pad-x);
}
</style>
