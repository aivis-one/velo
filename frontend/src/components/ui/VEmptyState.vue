<!--
  VELO Frontend -- VEmptyState Component (Phase F2.1)

  Empty state placeholder. Matches mockup .empty-state styles.

  Usage:
    <VEmptyState icon="📅" title="Нет практик" description="Создайте первую практику" />
    <VEmptyState icon="📭" title="Пусто">
      <VButton size="sm" @click="reload">Обновить</VButton>
    </VEmptyState>

  Custom icon via slot (e.g. a DS icon component instead of an emoji):
    <VEmptyState title="Нет практик">
      <template #icon><IconClock :size="48" /></template>
    </VEmptyState>
-->

<template>
  <div class="v-empty">
    <span class="v-empty__icon">
      <slot name="icon">{{ icon }}</slot>
    </span>
    <p class="v-empty__title">{{ title }}</p>
    <p v-if="description" class="v-empty__desc">{{ description }}</p>
    <div v-if="$slots.default" class="v-empty__action">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    icon?: string
    title: string
    description?: string
  }>(),
  {
    icon: '📭',
    description: '',
  },
)
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
}

.v-empty__title {
  font-size: var(--text-base);
  font-weight: 400;
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
