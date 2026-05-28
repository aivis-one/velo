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
      <button
        v-if="showBack"
        :class="['v-header__back', { 'v-header__back--icon': !!title }]"
        :aria-label="title ? 'Назад' : undefined"
        @click="$emit('back')"
      >
        <IconArrowRight :size="18" class="v-header__back-arrow" />
        <template v-if="!title">{{ backLabel }}</template>
      </button>
      <h1 v-if="title" class="v-header__title">{{ title }}</h1>
      <span v-if="badge" class="v-header__badge">{{ badge }}</span>
    </div>
    <div v-if="$slots.action" class="v-header__right">
      <slot name="action" />
    </div>
  </header>
</template>

<script setup lang="ts">
import { IconArrowRight } from '@/components/icons'

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

/* Pill-shaped back button — glassmorphism. With text by default. */
.v-header__back {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 36px;
  padding: 0 var(--space-4);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-primary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
  flex-shrink: 0;
  white-space: nowrap;
}

/* Arrow-only mode — compact pill 63×35, white background (per Figma 4816:132). */
.v-header__back--icon {
  width: 63px;
  height: 35px;
  padding: 0;
  justify-content: center;
  background: #ffffff;
  font-size: 18px;
  line-height: 1;
}

/* Mirror IconArrowRight to make it a back-arrow.
 * Same pattern as EntryView/DetailView (`.entry__back-glyph`). */
.v-header__back-arrow {
  transform: scaleX(-1);
  flex-shrink: 0;
}

.v-header__back:active {
  opacity: 0.7;
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
