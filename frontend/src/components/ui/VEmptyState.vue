<!--
  VELO Frontend -- VEmptyState Component (Phase F2.1)

  Empty state placeholder. Matches mockup .empty-state styles.

  Usage:
    <VEmptyState title="Нет практик" description="Создайте первую практику" />
    <VEmptyState title="Пусто">
      <VButton size="sm" @click="reload">Обновить</VButton>
    </VEmptyState>

  Note (S3 #048): icon prop accepts text/emoji input but default is empty —
  master/admin views may still pass legacy emoji glyphs; user-scope views
  omit icon entirely.
-->

<template>
  <div class="v-empty">
    <span
      v-if="icon"
      class="v-empty__icon"
    >{{ icon }}</span>
    <p class="v-empty__title">
      {{ title }}
    </p>
    <p
      v-if="description"
      class="v-empty__desc"
    >
      {{ description }}
    </p>
    <div
      v-if="$slots.default"
      class="v-empty__action"
    >
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
    icon: '',
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
  display: block;
  font-size: 48px;
  margin-bottom: var(--space-3);
}

.v-empty__title {
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--text-secondary);
  margin-bottom: var(--space-1);
}

.v-empty__desc {
  font-size: var(--text-sm);
  color: var(--text-muted);
  line-height: 1.5;
}

.v-empty__action {
  margin-top: var(--space-4);
}
</style>
