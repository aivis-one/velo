<!--
  VELO Frontend -- VHeader Component (Phase F2.1, updated back-button design)

  Sticky top header. Matches mockup .header styles.
  Back button renders as a pill (← label) matching the glassmorphism design.

  Usage:
    <VHeader title="Дашборд" />
    <VHeader title="Практика" show-back @back="router.back()" />
    <VHeader title="" show-back back-label="Check-in" @back="onBack" />
-->

<template>
  <header class="v-header">
    <div class="v-header__left">
      <button
        v-if="showBack"
        class="v-header__back"
        @click="$emit('back')"
      >
        <IconArrowBack :size="16" />
        <span>{{ backLabel }}</span>
      </button>
      <h1
        v-if="title"
        class="v-header__title"
      >
        {{ title }}
      </h1>
      <span
        v-if="badge"
        class="v-header__badge"
      >{{ badge }}</span>
    </div>
    <div class="v-header__right">
      <slot name="action" />
      <button
        v-if="!hideThemeToggle"
        type="button"
        class="v-header__theme"
        :aria-label="ui.theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'"
        @click="ui.setTheme(ui.theme === 'dark' ? 'light' : 'dark')"
      >
        <IconTheme :size="20" />
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import { IconArrowBack, IconTheme } from '@/components/icons'

const ui = useUiStore()

withDefaults(
  defineProps<{
    title?: string
    showBack?: boolean
    backLabel?: string
    badge?: string | number
    hideThemeToggle?: boolean
  }>(),
  {
    title: '',
    showBack: false,
    backLabel: 'Назад',
    badge: undefined,
    hideThemeToggle: false,
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

/* Pill-shaped back button matching glassmorphism design */
.v-header__back {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 36px;
  padding: 0 var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-primary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
  flex-shrink: 0;
  white-space: nowrap;
}

.v-header__back:active {
  opacity: 0.7;
}

.v-header__title {
  font-family: var(--font-body);
  font-size: 18px;
  font-weight: 400;
  color: var(--steel-button);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.v-header__badge {
  background: var(--steel-button);
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

.v-header__theme {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: var(--radius-full);
  transition: opacity var(--transition-fast);
}

.v-header__theme:hover {
  opacity: 0.75;
}
</style>
