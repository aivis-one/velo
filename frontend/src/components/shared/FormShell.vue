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
      <!-- Practice info -->
      <div v-if="practice" class="form-shell__practice">
        <span class="form-shell__practice-icon">
          <IconMeditation :size="26" />
        </span>
        <h2 class="form-shell__practice-name">{{ practice.title }}</h2>
        <p class="form-shell__practice-meta">
          <slot name="practice-meta">
            с {{ practice.master_name ?? 'Мастером' }}
          </slot>
        </p>
      </div>
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
import { IconMeditation } from '@/components/icons'
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
  background: var(--velo-glass-teal-30);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.form-shell-success__icon {
  font-size: var(--size-success-icon);
  margin-bottom: var(--space-6);
}

.form-shell-success__title {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-success-text);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-3);
}

.form-shell-success__text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-success-text);
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
  padding: var(--space-6) var(--space-4);
  gap: var(--space-6);
}

/* Practice info */
.form-shell__practice {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.form-shell__practice-icon {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
  margin-bottom: var(--space-2);
}

.form-shell__practice-name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-2);
}

.form-shell__practice-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.form-shell__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-4) 0;
}

/* Question */
.form-shell__question {
  text-align: center;
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.form-shell__question h3 {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-bottom: var(--space-1);
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
</style>
