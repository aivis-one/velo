<!--
  VELO Frontend -- VEmptyState Component (Phase F2.1; F-9 icons 2026-06)

  Empty state placeholder. Matches mockup .empty-state styles.

  The `icon` prop takes a SEMANTIC KEY (not an emoji) — the DS picks the glyph:
    warning | notfound | calendar | list | group | success | empty
  Usage:
    <VEmptyState icon="calendar" title="Нет практик" description="Создайте первую практику" />
    <VEmptyState icon="warning" title="Ошибка">
      <VButton size="sm" @click="reload">Обновить</VButton>
    </VEmptyState>

  Custom icon via slot (any DS icon component, overrides the key):
    <VEmptyState title="Нет практик">
      <template #icon><IconClock :size="48" /></template>
    </VEmptyState>
-->

<template>
  <div class="v-empty">
    <span class="v-empty__icon">
      <slot name="icon"><component :is="resolvedIcon" v-if="resolvedIcon" :size="48" /></slot>
    </span>
    <p class="v-empty__title">{{ title }}</p>
    <p v-if="description" class="v-empty__desc">{{ description }}</p>
    <div v-if="$slots.default" class="v-empty__action">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import {
  IconWarning,
  IconCalendar,
  IconList,
  IconGroup,
  IconSuccess,
  IconFile,
} from '@/components/icons'

const props = withDefaults(
  defineProps<{
    /** Semantic key -> DS glyph (see ICON_MAP). Not an emoji. */
    icon?: string
    title: string
    description?: string
  }>(),
  {
    icon: 'empty',
    description: '',
  },
)

const ICON_MAP: Record<string, Component> = {
  warning: IconWarning,
  notfound: IconWarning,
  calendar: IconCalendar,
  list: IconList,
  group: IconGroup,
  success: IconSuccess,
  empty: IconFile,
}

const resolvedIcon = computed<Component | null>(() => ICON_MAP[props.icon] ?? null)
</script>

<style scoped>
.v-empty {
  text-align: center;
  padding: var(--space-8) var(--space-4);
}

.v-empty__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  line-height: 1;
  margin-bottom: var(--space-3);
  /* Vector DS icon (resolved from the semantic key) inherits this as currentColor. */
  color: var(--velo-text-muted);
}

.v-empty__title {
  font-size: var(--text-base);
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-1);
}

.v-empty__desc {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  line-height: 1.5;
}

.v-empty__action {
  margin-top: var(--space-4);
}
</style>
