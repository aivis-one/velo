<!--
  VELO Frontend — DiaryEntryFlat (S2-S3 SPEEDRUN MEGA-2 §C36)

  List-mode flat card: icon + title + preview, full-width.
  Used by DiaryView list layout (no timeline spine).
-->

<template>
  <button
    type="button"
    class="flat"
    @click="$emit('click')"
  >
    <span
      class="flat__icon"
      :class="`flat__icon--${kind}`"
    >
      <component
        :is="iconComp"
        :size="22"
      />
    </span>
    <span class="flat__body">
      <span class="flat__title">{{ title }}</span>
      <span class="flat__preview">{{ preview }}</span>
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
.flat {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  text-align: left;
  font-family: var(--font-body);
}

.flat__icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-steel-alpha-15);
  color: var(--text-primary);
  border: 1px solid var(--text-primary);
}

.flat__icon--checkin {
  background: var(--steel-button);
  color: white;
  border-color: var(--steel-button);
}

.flat__icon--feedback {
  background: var(--warm-deep);
  color: white;
  border-color: var(--warm-deep);
}

.flat__body {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.flat__title {
  font-size: var(--text-base);
  color: var(--text-primary);
  font-weight: 500;
}

.flat__preview {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
