<!--
  VELO Frontend -- DiaryEntryDetail (NEW-3)

  Diary entry detail screen with edit action. Extracted from DiaryView.vue.

  Emits:
    back  — back button clicked
    edit  — edit button clicked
-->

<template>
  <div class="diary-detail">
    <header class="diary-detail__header">
      <button class="diary-detail__back" aria-label="Назад" @click="emit('back')">←</button>
      <h1 class="diary-detail__title">Запись</h1>
      <button class="diary-detail__action" aria-label="Редактировать" @click="emit('edit')">✏️</button>
    </header>

    <div class="diary-detail__body">
      <div class="diary-detail__date">{{ formatFullDate(item.created_at) }}</div>
      <h2 class="diary-detail__heading">{{ item.title || 'Без названия' }}</h2>
      <div class="diary-detail__content">{{ item.content }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DiaryEntryResponse } from '@/api/types'

defineProps<{ item: DiaryEntryResponse }>()
const emit = defineEmits<{ back: []; edit: [] }>()

function formatFullDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit',
  })
}
</script>

<style scoped>
.diary-detail {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.diary-detail__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
}

.diary-detail__back {
  width: 36px;
  height: 36px;
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  background: var(--velo-bg-card);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  font-size: var(--text-lg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity var(--transition-fast);
  flex-shrink: 0;
}

.diary-detail__back:hover {
  opacity: 0.8;
}

.diary-detail__title {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.diary-detail__action {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  transition: opacity var(--transition-fast);
}

.diary-detail__action:hover {
  opacity: 0.7;
}

.diary-detail__body {
  padding: var(--space-6) var(--space-4);
}

.diary-detail__date {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-2);
}

.diary-detail__heading {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-4);
  line-height: 1.3;
}

.diary-detail__content {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  line-height: 1.7;
  white-space: pre-wrap;
}
</style>
