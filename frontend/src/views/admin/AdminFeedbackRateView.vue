<!--
  VELO Frontend -- AdminFeedbackRateView (Admin DS, 2026-06-14, operator SVG "3 Feedback rate")

  Drill-in from the dashboard Engagement "Feedback rate" row. Hero rate + totals +
  rating distribution (Огонь / Хорошо / Есть вопросы).

  STUB (operator decision В): no admin metrics API yet -> full DS layout with honest
  empty states (labels + icons render, values "—"). Roadmap for Zod:
  GET /admin/metrics/feedback (leave-rate, visited/left totals, rating distribution).
-->

<template>
  <div class="admin-detail">
    <header class="admin-detail__top">
      <VBackButton @click="router.back()" />
      <span class="admin-detail__title">Feedback rate</span>
    </header>

    <VMetricHero :value="leaveRate" label="Оставляют отзыв">
      <template #icon><IconFeedback :size="28" /></template>
    </VMetricHero>

    <div class="admin-detail__stats2">
      <VStatCard :value="visited" label="Посетили" />
      <VStatCard :value="leftReview" label="Оставили отзыв" />
    </div>

    <h3 class="admin-detail__section">Распределение оценок</h3>
    <VCard class="admin-detail__rating">
      <VRatingBar
        label="Огонь!"
        :value="fireRate"
        bar-color="var(--velo-peach-300)"
        icon-color="var(--velo-peach-500)"
      >
        <template #icon><IconRatingFire :size="22" /></template>
      </VRatingBar>
      <VRatingBar
        label="Хорошо"
        :value="goodRate"
        bar-color="var(--velo-pink-300)"
        icon-color="var(--velo-pink-500)"
      >
        <template #icon><IconRatingGood :size="22" /></template>
      </VRatingBar>
      <VRatingBar
        label="Есть вопросы"
        :value="questionRate"
        bar-color="var(--velo-blue-400)"
        icon-color="var(--velo-blue-400)"
      >
        <template #icon><IconRatingConfused :size="22" /></template>
      </VRatingBar>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VBackButton, VMetricHero, VStatCard, VCard, VRatingBar } from '@/components/ui'
import {
  IconFeedback,
  IconRatingFire,
  IconRatingGood,
  IconRatingConfused,
} from '@/components/icons'

const router = useRouter()

// Stub data -> Zod (roadmap). Honest empty state (В): labels/icons render, "—".
const leaveRate = '—'
const visited = '—'
const leftReview = '—'
const fireRate: number | null = null
const goodRate: number | null = null
const questionRate: number | null = null
</script>

<style scoped>
.admin-detail {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.admin-detail__top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 44px;
}
.admin-detail__title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}
.admin-detail__stats2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}
.admin-detail__section {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 2px 0 0;
}
.admin-detail__rating {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}
</style>
