<!--
  VELO Frontend -- VHeader Component (Phase F2.1)

  Sticky top header. Matches mockup .header styles.
  Back button integrates with platform.showBackButton() in Telegram.

  Usage:
    <VHeader title="Дашборд" />
    <VHeader title="Практика" show-back @back="router.back()">
      <template #action>
        <VButton size="sm" variant="ghost">⚙️</VButton>
      </template>
    </VHeader>
-->

<template>
  <header class="v-header">
    <div class="v-header__left">
      <button v-if="showBack" class="v-header__back" @click="$emit('back')">
        ←
      </button>
      <h1 class="v-header__title">{{ title }}</h1>
      <span v-if="badge" class="v-header__badge">{{ badge }}</span>
    </div>
    <div v-if="$slots.action" class="v-header__right">
      <slot name="action" />
    </div>
  </header>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    showBack?: boolean
    badge?: string | number
  }>(),
  {
    showBack: false,
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
  background: rgba(255, 255, 255, 0.70);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  min-height: 56px;
}

.v-header__left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.v-header__back {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  font-size: 18px;
  color: var(--velo-text-primary);
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
  flex-shrink: 0;
}

.v-header__back:hover {
  background: var(--velo-bg-subtle);
}

.v-header__title {
  font-family: var(--font-heading);
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
  font-weight: 600;
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
