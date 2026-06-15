<!--
  VELO Frontend -- AdminCheckinRateView (Admin DS, 2026-06-14, operator SVG "2 Check-in rate")

  Drill-in from the dashboard Engagement "Check-in rate" row. Hero rate + totals +
  weekly bar chart + low-check-in practices.

  STUB (operator decision В): no admin metrics API yet -> full DS layout with honest
  empty states ("—" / empty chart / "Данных пока нет"). Roadmap for Zod:
  GET /admin/metrics/check-in (avg rate, totals, weekly series, low-check-in list).
-->

<template>
  <div class="admin-detail">
    <header class="admin-detail__top">
      <VBackButton @click="router.back()" />
      <span class="admin-detail__title">Check-in rate</span>
    </header>

    <VMetricHero :value="avgRate" label="Средний check-in rate">
      <template #icon><IconCheck :size="30" /></template>
    </VMetricHero>

    <div class="admin-detail__stats2">
      <VStatCard :value="totalRecords" label="Всего записей" />
      <VStatCard :value="checkedIn" label="Отметились" />
    </div>

    <VBarChart :bars="weekBars" />

    <h3 class="admin-detail__section">Низкий check-in (практики)</h3>
    <template v-if="lowPractices.length">
      <VListRow v-for="p in lowPractices" :key="p.id" :title="p.title" :subtitle="p.subtitle" />
    </template>
    <VCard v-else><p class="admin-detail__empty">Данных пока нет</p></VCard>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VBackButton, VMetricHero, VStatCard, VBarChart, VCard, VListRow } from '@/components/ui'
import { IconCheck } from '@/components/icons'

const router = useRouter()

// Stub data -> Zod (roadmap). Honest empty state (В) until the API exists.
const avgRate = '—'
const totalRecords = '—'
const checkedIn = '—'
const weekBars: { label: string; value: number }[] = []
const lowPractices: { id: string; title: string; subtitle: string }[] = []
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
.admin-detail__empty {
  margin: 0;
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  padding: var(--space-1) var(--space-2);
}
</style>
