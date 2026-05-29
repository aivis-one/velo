<!--
  VELO Frontend -- DiaryList (Diary redesign, screen 40 "list")

  Flat-column rendering of the unified feed: the SAME DiaryFeedCard cards as
  the thread, just stacked in a plain vertical column (no central axis, no
  left/right alternation). Paired with DiaryTimeline via the view toggle in
  DiaryFeedView ("..." menu).

  Order (chat-mode, identical to DiaryTimeline): oldest at the TOP, newest at
  the BOTTOM, so the freshest entry sits next to the composer and toggling
  between list/map never reshuffles the vertical order. props.items is not
  mutated (reverse() runs on a shallow copy).
-->

<template>
  <div class="diary-list">
    <DiaryFeedCard
      v-for="item in ordered"
      :key="item.id"
      :item="item"
      :timezone="timezone"
      @tap="(p) => emit('tap', p)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DiaryFeedCard from '@/components/shared/DiaryFeedCard.vue'
import type { DiaryFeedItem } from '@/api/types'

const props = defineProps<{
  items: DiaryFeedItem[]
  timezone?: string
}>()

const emit = defineEmits<{
  tap: [payload: { item: DiaryFeedItem; editable: boolean }]
}>()

const ordered = computed<DiaryFeedItem[]>(() => [...props.items].reverse())
</script>

<style scoped>
.diary-list {
  display: flex;
  flex-direction: column;
  /* Figma diary-list.svg: межкарточный gap 10px. Нет точного токена (4/8/14…) —
     берём ближайший --space-2 (8px); единый источник для отступа списка. */
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-3) 0;
}
</style>
