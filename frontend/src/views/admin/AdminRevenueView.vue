<!--
  VELO Frontend -- AdminRevenueView (Admin DS, 2026-06-14, operator SVG "1 Revenue")

  Drill-in from the dashboard "Баланс по мастерам" link. Monthly platform revenue +
  commission + payout + per-master earnings.

  STUB (operator decision А): admin revenue is financial -> NO mocked figures until
  Zod wires the API. Empty state until then (roadmap for Zod: GET /admin/revenue ->
  monthly revenue, commission, payout, per-master earnings + payouts). The full
  card/list design is approved on the .tmp preview; built when real data exists.
-->

<template>
  <div class="admin-detail">
    <header class="admin-detail__top">
      <VBackButton @click="router.back()" />
      <span class="admin-detail__title">Выручка</span>
    </header>

    <VCard>
      <p class="admin-detail__empty">Данные появятся после подключения аналитики</p>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VBackButton, VCard } from '@/components/ui'

const router = useRouter()
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
.admin-detail__empty {
  margin: 0;
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  padding: var(--space-4) var(--space-2);
}
</style>
