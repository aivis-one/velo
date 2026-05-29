<!--
  VELO Frontend -- FormShell (WARNING-9)

  Shared full-screen form shell used by CheckinView and FeedbackView.
  Extracts ~200 lines of identical CSS and layout structure.

  Layout:
    - Success screen (v-if submitted)
    - Form screen:
        - VHeader with back button
        - Practice info (emoji + name + meta)
        - Question (title + subtitle)
        - #selection slot  ← mood buttons / rating buttons
        - Comment textarea (v-model)
        - Actions (submit + optional skip)

  Slots:
    #selection          — mood or rating buttons
    #success-actions    — buttons shown on success screen
    #success-icon       -- success screen icon (defaults to successIcon emoji)
    #practice-meta      — meta line below practice name (date / "Завершена")

  Props:
    backLabel           — VHeader back label
    practice            — PracticeResponse | null
    practiceLoading     — boolean
    questionTitle       — main question text
    questionSubtitle    — subtitle below question
    comment             — v-model for textarea
    submitting          — loading state for submit button
    submitDisabled      — disable submit button
    submitLabel         — submit button text
    showSkip            — show "Пропустить" ghost button
    submitted           — show success screen instead of form
    successIcon         — emoji shown on success screen
    successTitle        — title on success screen
    successText         — body text on success screen

  Emits:
    back                — back button clicked
    submit              — submit button clicked
    skip                — skip button clicked
    update:comment      — textarea v-model
-->

<template>
  <!-- ===== SUCCESS SCREEN ===== -->
  <div v-if="submitted" class="form-shell-success">
    <div class="form-shell-success__icon">
      <slot name="success-icon">{{ successIcon }}</slot>
    </div>
    <h1 class="form-shell-success__title">{{ successTitle }}</h1>
    <p class="form-shell-success__text">{{ successText }}</p>
    <div class="form-shell-success__actions">
      <slot name="success-actions" />
    </div>
  </div>

  <!-- ===== FORM SCREEN ===== -->
  <div v-else class="form-shell">
    <!-- Header -->
    <VHeader show-back :back-label="backLabel" @back="emit('back')" />

    <div class="form-shell__body">
      <!-- Practice info — общий PracticeHeroCard в form-варианте (F-3). -->
      <PracticeHeroCard
        v-if="practice"
        variant="form"
        :title="practice.title"
        :direction="practice.direction"
      >
        <template #meta>
          <slot name="practice-meta">
            <span class="form-shell__practice-meta-cell">
              с {{ practice.master_name ?? 'Мастером' }}
            </span>
          </slot>
        </template>
      </PracticeHeroCard>
      <div v-else-if="practiceLoading" class="form-shell__loader">
        <VLoader />
      </div>

      <!-- Question -->
      <div class="form-shell__question">
        <h3>{{ questionTitle }}</h3>
        <p>{{ questionSubtitle }}</p>
      </div>

      <!-- Selection slot (mood buttons / rating buttons) -->
      <div class="form-shell__selection">
        <slot name="selection" />
      </div>

      <!-- Comment textarea -->
      <div class="form-shell__comment">
        <textarea
          :value="comment"
          class="form-shell__textarea"
          placeholder="Добавьте комментарий..."
          maxlength="1000"
          rows="3"
          @input="emit('update:comment', ($event.target as HTMLTextAreaElement).value)"
        />
      </div>

      <!-- Actions -->
      <div class="form-shell__actions">
        <VButton
          variant="primary"
          size="lg"
          block
          :disabled="submitDisabled"
          :loading="submitting"
          @click="emit('submit')"
        >
          {{ submitLabel }}
        </VButton>
        <p
          v-if="submitDisabled && disabledHint"
          class="form-shell__disabled-hint"
        >
          {{ disabledHint }}
        </p>
        <VButton v-if="showSkip" variant="ghost" block @click="emit('skip')">
          Пропустить
        </VButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { VButton, VLoader } from '@/components/ui'
import { VHeader } from '@/components/layout'
import PracticeHeroCard from '@/components/shared/PracticeHeroCard.vue'
import type { PracticeResponse } from '@/api/types'

defineProps<{
  backLabel: string
  practice: PracticeResponse | null
  practiceLoading: boolean
  questionTitle: string
  questionSubtitle: string
  comment: string
  submitting: boolean
  submitDisabled: boolean
  /** Helper text shown right under the submit button when submitDisabled is true
   * (e.g. "Чек-ин закрыт — практика уже началась"). */
  disabledHint?: string
  submitLabel: string
  showSkip?: boolean
  submitted: boolean
  successIcon: string
  successTitle: string
  successText: string
}>()

const emit = defineEmits<{
  back: []
  submit: []
  skip: []
  'update:comment': [value: string]
}>()
</script>

<style scoped>
/* ===== Success screen ===== */
.form-shell-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: var(--space-6);
  text-align: center;
  background: #ffffff;
}

.form-shell-success__icon {
  font-size: var(--size-success-icon);
  margin-bottom: var(--space-6);
}

.form-shell-success__title {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-3);
}

.form-shell-success__text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-8);
  max-width: 280px;
}

.form-shell-success__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  width: 100%;
  max-width: 320px;
}

/* ===== Form screen ===== */
.form-shell {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.form-shell__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  /* Horizontal screen-padding теперь раздаётся MobileLayout-ом (--velo-screen-padding).
   * Здесь добавляем только vertical, чтобы не было двойного отступа по бокам. */
  padding: var(--space-6) 0;
  gap: var(--space-6);
}

/* Meta-cell для слота #practice-meta (контент от CheckinView / FeedbackView).
 * Layout самой practice-карточки (паддинги, иконка, заголовок, грид-meta) теперь
 * приходит из общего PracticeHeroCard variant="form" (F-3). Здесь остаётся только
 * стиль ячейки: дублируем scoped + :slotted, чтобы класс работал и для дефолтного
 * содержимого слота (FormShell scope), и для override от вьюх (parent scope). */
.form-shell__practice-meta-cell,
:slotted(.form-shell__practice-meta-cell) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
}

.form-shell__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-4) 0;
}

/* Question — паддинги и gap по Figma 2266:728 (карточка 336x87) */
.form-shell__question {
  text-align: center;
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: 20px var(--space-4) 22px;
}

.form-shell__question h3 {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: 13px;
}

.form-shell__question p {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

/* Selection slot wrapper */
.form-shell__selection {
  display: flex;
  justify-content: center;
}

/* Comment */
.form-shell__textarea {
  width: 100%;
  min-height: 129px;
  padding: var(--space-4);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  resize: none;
  background: var(--velo-bg-card-solid);
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
}

.form-shell__textarea::placeholder {
  color: var(--velo-text-muted);
  font-size: var(--text-base);
}

.form-shell__textarea:focus {
  outline: none;
  border-color: var(--velo-border-input-focus);
}

/* Actions */
.form-shell__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-top: auto;
}

.form-shell__disabled-hint {
  text-align: center;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin: calc(-1 * var(--space-2)) 0 0;
}
</style>
