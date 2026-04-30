<!--
  VELO Frontend — ThreadComposer (S2-S3 SPEEDRUN MEGA-2 §C49)

  Distinct from DiaryComposer per D2 — input + IconArrowUp only, no mic,
  no expand modal. Emits 'send' with the trimmed text.
-->

<template>
  <form
    class="tc"
    @submit.prevent="onSend"
  >
    <input
      v-model="local"
      type="text"
      class="tc__input"
      placeholder="Написать сообщение..."
    >
    <button
      type="submit"
      class="tc__send"
      :disabled="!local.trim()"
      aria-label="Отправить"
    >
      <IconArrowUp :size="20" />
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { IconArrowUp } from '@/components/icons'

const emit = defineEmits<{ (e: 'send', text: string): void }>()

const local = ref('')

function onSend(): void {
  const t = local.value.trim()
  if (!t) return
  emit('send', t)
  local.value = ''
}
</script>

<style scoped>
.tc {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border-top: 1px solid var(--text-primary);
}

.tc__input {
  flex: 1 1 auto;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
}

.tc__send {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--steel-button);
  color: white;
  border: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tc__send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
