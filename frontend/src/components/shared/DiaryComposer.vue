<!--
  VELO Frontend — DiaryComposer (S2-S3 SPEEDRUN MEGA-2 §C36)

  Collapsed pill bar with mic + send. Click on any of these elements
  emits 'expand' so the parent can open the C40 expanded modal.
-->

<template>
  <div class="composer">
    <button
      type="button"
      class="composer__pill"
      @click="$emit('expand')"
    >
      <span class="composer__placeholder">Начните писать...</span>
      <span class="composer__mic">
        <IconMic :size="20" />
      </span>
    </button>
    <button
      type="button"
      class="composer__send"
      aria-label="Открыть редактор"
      @click="$emit('expand')"
    >
      <IconArrowUp :size="20" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { IconMic, IconArrowUp } from '@/components/icons'

defineEmits<{ (e: 'expand'): void }>()
</script>

<style scoped>
.composer {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border-top: 1px solid var(--text-primary);
}

.composer__pill {
  flex: 1 1 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: var(--font-body);
}

.composer__placeholder {
  font-size: var(--text-base);
  color: var(--text-secondary);
}

.composer__mic {
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.composer__send {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--steel-button);
  color: white;
  border: 0;
  cursor: pointer;
}
</style>
