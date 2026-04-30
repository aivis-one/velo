<!--
  VELO Frontend -- MasterCardSummary (S2 P08 C26 + C28 + C29; S3 C51)

  Compact master row: avatar + name + verified chip + method chips +
  "Подробнее →" link. Used inside PracticeDetail / Booked / BookingDetail.
-->

<template>
  <div class="mcs">
    <div class="mcs__avatar">
      <IconProfile :size="32" />
    </div>
    <div class="mcs__body">
      <div class="mcs__title-row">
        <span class="mcs__name">{{ name }}</span>
        <span
          v-if="verified"
          class="mcs__chip mcs__chip--mint"
        >Верифицирован</span>
      </div>
      <div
        v-if="methods && methods.length"
        class="mcs__methods"
      >
        <span
          v-for="m in methods"
          :key="m"
          class="mcs__method"
        >{{ m }}</span>
      </div>
    </div>
    <RouterLink
      v-if="masterId"
      :to="`/user/master/${masterId}`"
      class="mcs__link"
      aria-label="Подробнее"
    >
      <IconArrowForward :size="20" />
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import { IconProfile, IconArrowForward } from '@/components/icons'

defineProps<{
  name: string
  masterId?: string | null
  methods?: string[]
  verified?: boolean
}>()
</script>

<style scoped>
.mcs {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.mcs__avatar {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  background: var(--surface-default);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.mcs__body {
  flex: 1;
  min-width: 0;
}

.mcs__title-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-bottom: var(--space-1);
}

.mcs__name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  font-weight: 400;
}

.mcs__chip {
  font-size: var(--text-xs);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-family: var(--font-body);
}

.mcs__chip--mint {
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
  color: var(--text-primary);
}

.mcs__methods {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.mcs__method {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.mcs__link {
  flex-shrink: 0;
  color: var(--text-primary);
  text-decoration: none;
  display: inline-flex;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
}

.mcs__link:hover {
  background: var(--surface-default);
}
</style>
