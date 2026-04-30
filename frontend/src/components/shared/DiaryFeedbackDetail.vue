<!--
  VELO Frontend -- DiaryFeedbackDetail (NEW-3)

  Read-only feedback detail screen. Extracted from DiaryView.vue.

  Emits:
    back  — back button clicked
-->

<template>
  <div class="diary-detail">
    <header class="diary-detail__header">
      <button
        class="diary-detail__back"
        aria-label="Назад"
        @click="emit('back')"
      >
        ←
      </button>
      <h1 class="diary-detail__title">
        Feedback
      </h1>
      <span class="diary-detail__spacer" />
    </header>

    <div class="diary-detail__body">
      <div class="diary-detail__date">
        {{ formatFullDate(item.created_at) }}
      </div>
      <h2 class="diary-detail__heading">
        {{ RATING_EMOJI[item.rating] }} Feedback: {{ RATING_LABEL[item.rating] }}
      </h2>
      <div
        v-if="item.comment"
        class="diary-detail__content"
      >
        {{ item.comment }}
      </div>
      <div class="diary-detail__context">
        📌 После практики
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RATING_EMOJI, RATING_LABEL } from '@/utils/displayHelpers'
import type { FeedbackResponse } from '@/api/types'

defineProps<{ item: FeedbackResponse }>()
const emit = defineEmits<{ back: [] }>()

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
  background: var(--surface-steel-alpha-15);
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
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.diary-detail__spacer {
  width: 36px;
}

.diary-detail__body {
  padding: var(--space-6) var(--space-4);
}

.diary-detail__date {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.diary-detail__heading {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-4);
  line-height: 1.3;
}

.diary-detail__content {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--text-primary);
  line-height: 1.7;
  white-space: pre-wrap;
  margin-bottom: var(--space-4);
}

.diary-detail__context {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-muted);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-subtle);
}
</style>
