<!--
  VELO Frontend -- VHeader Component (Phase F2.1, updated back-button design)

  Sticky top header. Matches mockup .header styles.

  Two back-button modes (per Figma DS, 2026-05-28):
    1. With separate title -> arrow-only compact pill (63×35), title sits next to it.
       Example: PracticeDetailView ("Моя практика" / "Практика").
    2. Without title -> arrow + backLabel inside the pill (e.g. "← Check-in").
       Example: CheckinView / FeedbackView.

  Usage:
    <VHeader title="Дашборд" />                            -- title only
    <VHeader title="Моя практика" show-back @back="..." /> -- mode 1: arrow-only
    <VHeader show-back back-label="Check-in" @back="..." />-- mode 2: arrow + text
-->

<template>
  <header class="v-header">
    <div class="v-header__left">
      <VBackButton
        v-if="showBack"
        :aria-label="title ? 'Назад' : backLabel"
        @click="$emit('back')"
      />
      <h1 v-if="title" class="v-header__title">{{ title }}</h1>
      <span v-if="badge" class="v-header__badge">{{ badge }}</span>
    </div>
    <div v-if="$slots.action" class="v-header__right">
      <slot name="action" />
    </div>
  </header>
</template>

<script setup lang="ts">
import { VBackButton } from '@/components/ui'

withDefaults(
  defineProps<{
    title?: string
    showBack?: boolean
    backLabel?: string
    badge?: string | number
  }>(),
  {
    title: '',
    showBack: false,
    backLabel: 'Назад',
    badge: undefined,
  },
)

defineEmits<{
  back: []
}>()
</script>

<style scoped>
.v-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky, 200);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  background: transparent;
  min-height: 56px;
}

.v-header__left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.v-header__title {
  font-family: var(--font-body);
  font-size: 18px;
  font-weight: 400;
  color: var(--velo-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.v-header__badge {
  background: var(--velo-primary);
  color: white;
  font-size: var(--text-xs);
  font-weight: 400;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.v-header__right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}
</style>
