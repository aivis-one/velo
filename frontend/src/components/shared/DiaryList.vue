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
    <template v-for="group in dayGroups" :key="group.dayKey">
      <!-- Day divider: разделяет записи разных дней (Сегодня/Вчера/«2 июня»).
           Возвращён по просьбе оператора 2026-06-04 — в списочном виде их не
           было (были только в thread). Стиль — простая строка с тонкими
           линиями (без тяжёлых орнаментов thread-вида). -->
      <div class="diary-list__divider">
        <span>{{ group.label }}</span>
      </div>
      <DiaryFeedCard
        v-for="item in group.items"
        :key="item.id"
        :item="item"
        :timezone="timezone"
        @tap="(p) => emit('tap', p)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DiaryFeedCard from '@/components/shared/DiaryFeedCard.vue'
import { dayKeyOf, dayLabelOf } from '@/utils/format'
import type { DiaryFeedItem } from '@/api/types'

const props = defineProps<{
  items: DiaryFeedItem[]
  timezone?: string
}>()

const emit = defineEmits<{
  tap: [payload: { item: DiaryFeedItem; editable: boolean }]
}>()

const tz = computed(() => props.timezone ?? 'UTC')

interface DayGroup {
  dayKey: string
  label: string
  items: DiaryFeedItem[]
}

// Chat-mode: лента приходит newest-first; рендерим хронологическую копию
// (oldest сверху, newest снизу), группируя по дню. props.items не мутируем.
const dayGroups = computed<DayGroup[]>(() => {
  const groups: DayGroup[] = []
  let current: DayGroup | null = null
  for (const item of [...props.items].reverse()) {
    const key = dayKeyOf(item.occurred_at, tz.value)
    if (!current || current.dayKey !== key) {
      current = { dayKey: key, label: dayLabelOf(item.occurred_at, tz.value), items: [] }
      groups.push(current)
    }
    current.items.push(item)
  }
  return groups
})
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

/* Разделитель дня: дата по центру + тонкие линии по бокам (токены DS). */
.diary-list__divider {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin: var(--space-1) var(--space-1) 0;
}

.diary-list__divider::before,
.diary-list__divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--velo-border-light);
}

.diary-list__divider span {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  white-space: nowrap;
}
</style>
