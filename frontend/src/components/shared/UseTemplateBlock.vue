<!--
  VELO Frontend -- UseTemplateBlock (CreatePracticeView «Использовать шаблон»)

  Collapsible block at the top of the create-practice form: pick one of the
  master's own past practices as a template to prefill the form.

  Three states:
    - Collapsed (default): the «Вы создавали ранее…» pill + chevron.
    - Expanded, no practices: muted «Данных пока нет…» card (empty state).
    - Expanded, has practices: the master's practices (newest-first) as reused
      PracticeListCard rows. Max 3 visible -> scroll; 1-2 -> the box shrinks
      to fit (max-height, not a fixed height).

  Reuse-first: the rows ARE PracticeListCard (icon via practiceIconFor + title +
  date/time); the subtitle slot shows the participant count. Selecting a row
  emits `select` and collapses the block; the parent does the prefill.

  Data source = masterStore.practices (real). No backend dependency.
-->

<template>
  <div class="use-template">
    <button
      type="button"
      class="use-template__head"
      :class="{ 'use-template__head--open': open }"
      :aria-expanded="open"
      @click="open = !open"
    >
      <span class="use-template__head-text">Вы создавали ранее…</span>
      <svg class="use-template__chev" viewBox="0 0 16 10" fill="none" aria-hidden="true">
        <path d="M2 2L8 8L14 2" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
      </svg>
    </button>

    <!-- Empty: master has no practices yet. -->
    <div v-if="open && practices.length === 0" class="use-template__empty">
      Данных пока нет — создайте первую практику
    </div>

    <!-- List: reuse PracticeListCard rows; max 3 tall then scroll. -->
    <div v-else-if="open" class="use-template__list">
      <PracticeListCard
        v-for="p in practices"
        :key="p.id"
        :practice="p"
        :when="cardDate(p)"
        :when-time="cardTime(p)"
        @click="select(p)"
      >
        <template #subtitle>
          <span class="use-template__participants">
            <IconGroup :size="15" />
            {{ formatParticipants(p.current_participants, p.max_participants) }}
          </span>
        </template>
      </PracticeListCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PracticeListCard from '@/components/shared/PracticeListCard.vue'
import { IconGroup } from '@/components/icons'
import { formatShortDate, formatTime, formatParticipants } from '@/utils/format'
import type { PracticeResponse } from '@/api/types'

defineProps<{
  /** The master's own practices (newest-first), used as templates. */
  practices: PracticeResponse[]
}>()

const emit = defineEmits<{ select: [practice: PracticeResponse] }>()

const open = ref(false)

function cardDate(p: PracticeResponse): string {
  return formatShortDate(p.scheduled_at, p.timezone)
}
function cardTime(p: PracticeResponse): string {
  return formatTime(p.scheduled_at, p.timezone)
}

function select(p: PracticeResponse): void {
  emit('select', p)
  open.value = false
}
</script>

<style scoped>
.use-template {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Trigger pill (collapsed look; SVG: white plate ~h48, rx15). Height is
   token-padding-driven (13*2 + ~22 line ≈ 48) — no magic px / no 48 token. */
.use-template__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: var(--velo-card-padding-y) var(--space-4);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  cursor: pointer;
}

.use-template__head-text {
  letter-spacing: 0.02em;
}

.use-template__chev {
  width: 16px;
  height: 10px;
  flex-shrink: 0;
  color: var(--velo-text-primary);
  transition: transform var(--transition-base);
}

.use-template__head--open .use-template__chev {
  transform: rotate(180deg);
}

/* Empty-state card (SVG: muted, centered). */
.use-template__empty {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  text-align: center;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

/* List: at most 3 cards tall, then scroll; shorter lists shrink (max-height). */
.use-template__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-height: calc(var(--velo-card-height-list) * 3 + var(--space-2) * 2);
  overflow-y: auto;
}

.use-template__participants {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}
</style>
