<!--
  VELO Frontend — DiaryEntryBubble (S2-S3 SPEEDRUN MEGA-2 §C36)

  Timeline-mode bubble: mood circle on left + chat-bubble card on right.
  Used by DiaryView timeline layout for mixed entries (check-ins, feedbacks,
  diary entries, dream entries).

  kind = which icon component renders inside the left circle.
-->

<template>
  <button
    type="button"
    class="bubble"
    @click="$emit('click')"
  >
    <span
      class="bubble__icon"
      :class="`bubble__icon--${kind}`"
    >
      <component
        :is="iconComp"
        :size="20"
      />
    </span>
    <span class="bubble__card">
      <span class="bubble__title">{{ title }}</span>
      <span class="bubble__preview">{{ preview }}</span>
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import {
  IconFeedback,
  IconBookFeather,
  IconBookDream,
  IconBrain,
} from '@/components/icons'

type Kind = 'checkin' | 'feedback' | 'journal' | 'dream' | 'insight'

const props = defineProps<{
  kind: Kind
  title: string
  preview: string
}>()

defineEmits<{ (e: 'click'): void }>()

const iconComp = computed<Component>(() => {
  switch (props.kind) {
    case 'checkin':
      return IconBrain
    case 'feedback':
      return IconFeedback
    case 'dream':
      return IconBookDream
    case 'insight':
      return IconBrain
    default:
      return IconBookFeather
  }
})
</script>

<style scoped>
.bubble {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  width: 100%;
  padding: 0;
  background: transparent;
  border: 0;
  cursor: pointer;
  text-align: left;
}

.bubble__icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--surface-steel-alpha-15);
  color: var(--text-primary);
  border: 1px solid var(--text-primary);
}

.bubble__icon--checkin {
  background: var(--steel-button);
  color: white;
  border-color: var(--steel-button);
}

.bubble__icon--feedback {
  background: var(--warm-deep);
  color: white;
  border-color: var(--warm-deep);
}

.bubble__card {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--surface-default);
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  border: 1px solid var(--text-primary);
}

.bubble__title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  font-weight: 500;
}

.bubble__preview {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
