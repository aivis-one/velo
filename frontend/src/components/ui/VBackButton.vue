<!--
  VELO Frontend -- VBackButton (unified design-system back button)

  ONE back button for every screen: a white pill, 63x40, fully rounded, with a
  single mirrored arrow glyph (icon-only, no text). Navigation stays in the
  caller -- this component only emits `click`; wire it to router.back() or a
  custom handler at the call site.

  Usage:
    <VBackButton @click="router.back()" />
    <VBackButton aria-label="Выйти из дневника" @click="exitDiary" />
-->

<template>
  <button type="button" class="v-back" :aria-label="ariaLabel" @click="$emit('click')">
    <IconArrowRight :size="18" class="v-back__arrow" />
  </button>
</template>

<script setup lang="ts">
import { IconArrowRight } from '@/components/icons'

withDefaults(
  defineProps<{
    /** Accessible label; navigation is the caller's, this is just the control. */
    ariaLabel?: string
  }>(),
  { ariaLabel: 'Назад' },
)

defineEmits<{ click: [] }>()
</script>

<style scoped>
.v-back {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 63px;
  height: 40px;
  flex-shrink: 0;
  border: none;
  border-radius: var(--radius-full);
  background: var(--velo-bg-card-solid);
  color: var(--velo-text-primary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.v-back:hover,
.v-back:active {
  opacity: 0.85;
}

/* The only arrow glyph is a right arrow -- mirror it to point back. */
.v-back__arrow {
  transform: scaleX(-1);
}
</style>
