<!--
  VELO Frontend -- SendMessageModal (Master DS, 2026-06-11)

  "Написать сообщение" sheet, reused on the student screens (list / profile /
  summary). STUB: master↔participant messaging has no backend yet — "Отправить"
  shows a toast and closes (roadmap for Zod). Visual contract: recipient chip +
  message textarea + Отмена / Отправить.
-->

<template>
  <VModal :open="open" :show-close="false" @close="$emit('close')">
    <div class="send-msg">
      <div class="send-msg__chip">
        <VAvatar :name="name" size="md" />
        <span class="send-msg__name">{{ name }}</span>
      </div>
      <VTextarea v-model="text" placeholder="Сообщение…" :rows="5" />
      <div class="send-msg__actions">
        <VButton variant="danger" block @click="$emit('close')">Отмена</VButton>
        <VButton variant="primary" block @click="onSend">Отправить</VButton>
      </div>
    </div>
  </VModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { VModal, VAvatar, VTextarea, VButton } from '@/components/ui'
import { useToast } from '@/composables/useToast'

const props = defineProps<{ open: boolean; name: string }>()
defineEmits<{ close: [] }>()

const toast = useToast()
const text = ref('')

// Reset the field each time the sheet opens.
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) text.value = ''
  },
)

function onSend(): void {
  // Messaging backend not built yet (roadmap for Zod).
  toast.info('Сообщения пока недоступны')
}
</script>

<style scoped>
.send-msg {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.send-msg__chip {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-glass-blue-15);
  border-radius: 10px;
  padding: 10px var(--space-4);
}

.send-msg__name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.send-msg__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

/* VTextarea owns a bottom margin; drop it so the modal's gap controls spacing. */
.send-msg :deep(.v-textarea) {
  margin-bottom: 0;
}

/* The textarea rests with a transparent border (white plate) — invisible on the
   white modal. Give it a visible frame here so the input area reads clearly
   (design «3 Students» message sheet). */
.send-msg :deep(.v-textarea__field) {
  border-color: var(--velo-border);
}
</style>
