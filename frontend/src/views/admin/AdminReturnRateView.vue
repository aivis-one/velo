<!--
  VELO Frontend -- AdminReturnRateView (Admin DS, 2026-06-14, operator SVG "4 Return rate")

  Drill-in from the dashboard Engagement "Return rate" row. Hero rate + totals +
  top loyal users.

  STUB (operator decision В): no admin metrics API yet -> full DS layout with honest
  empty states ("—" / "Данных пока нет"). Roadmap for Zod:
  GET /admin/metrics/return (return rate, totals, top loyal users).
-->

<template>
  <div class="admin-detail">
    <header class="admin-detail__top">
      <VBackButton @click="router.back()" />
      <span class="admin-detail__title">Return rate</span>
    </header>

    <VMetricHero :value="returnRate" label="Возвращаются повторно">
      <template #icon><IconRepeat :size="28" /></template>
    </VMetricHero>

    <div class="admin-detail__stats2">
      <VStatCard :value="totalUsers" label="Всего пользователей" />
      <VStatCard :value="returning" label="Повторно" />
    </div>

    <h3 class="admin-detail__section">Топ лояльных юзеров</h3>
    <template v-if="loyalUsers.length">
      <VListRow v-for="u in loyalUsers" :key="u.id" :title="u.title" :subtitle="u.subtitle" />
    </template>
    <VCard v-else><p class="admin-detail__empty">Данных пока нет</p></VCard>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VBackButton, VMetricHero, VStatCard, VCard, VListRow } from '@/components/ui'
import { IconRepeat } from '@/components/icons'

const router = useRouter()

// Stub data -> Zod (roadmap). Honest empty state (В) until the API exists.
const returnRate = '—'
const totalUsers = '—'
const returning = '—'
const loyalUsers: { id: string; title: string; subtitle: string }[] = []
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
