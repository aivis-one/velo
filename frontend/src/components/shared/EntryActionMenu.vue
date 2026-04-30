<!--
  VELO Frontend — EntryActionMenu (S2-S3 SPEEDRUN MEGA-2 §C43)

  Floating right-rail action stack: ••• reveals/hides Edit + Trash buttons.
  Used on DiaryEntryView and RelationshipsView.
-->

<template>
  <div class="actions">
    <button
      type="button"
      class="actions__btn actions__btn--menu"
      :class="{ 'actions__btn--open': open }"
      aria-label="Меню"
      @click="open = !open"
    >
      <IconDots :size="20" />
    </button>
    <button
      v-if="open"
      type="button"
      class="actions__btn actions__btn--edit"
      aria-label="Редактировать"
      @click="onEdit"
    >
      <IconEdit :size="20" />
    </button>
    <button
      v-if="open"
      type="button"
      class="actions__btn actions__btn--delete"
      aria-label="Удалить"
      @click="onDelete"
    >
      <IconTrash :size="20" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { IconDots, IconEdit, IconTrash } from '@/components/icons'

const emit = defineEmits<{
  (e: 'edit'): void
  (e: 'delete'): void
}>()

const open = ref(false)

function onEdit(): void {
  open.value = false
  emit('edit')
}
function onDelete(): void {
  open.value = false
  emit('delete')
}
</script>

<style scoped>
.actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  position: fixed;
  right: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  z-index: 90;
}

.actions__btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.actions__btn--menu {
  background: var(--surface-default);
}

.actions__btn--menu.actions__btn--open {
  background: var(--steel-button);
  color: white;
  border-color: var(--steel-button);
}

.actions__btn--edit {
  background: var(--steel-button);
  color: white;
  border-color: var(--steel-button);
}

.actions__btn--delete {
  background: var(--pink-primary, var(--text-primary));
  color: white;
  border-color: var(--pink-primary, var(--text-primary));
}
</style>
