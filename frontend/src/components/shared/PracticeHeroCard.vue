<!--
  VELO Frontend -- PracticeHeroCard (shared)

  Hero card used at the top of practice/booking detail screens
  (Figma 15 / 18 / dashboard):
    - Practice icon in a teal circle
    - Title
    - Meta row: date, duration, optional participants
    - Optional #badge slot (e.g. "Оплачено", "LIVE" -- screen 15)

  Props cover all three cases:
    - Catalog (15, not booked):  participants shown, no badge
    - Booked (15):               no participants, "Оплачено" badge via slot
    - Booking detail (18):       no participants, no badge

  The outer margin is left to the parent -- this is just the card.
-->

<template>
  <div class="hero-card">
    <div class="hero-card__icon">
      <IconMeditation :size="26" />
    </div>
    <h1 class="hero-card__title">{{ title }}</h1>
    <div class="hero-card__meta">
      <span class="hero-card__meta-item">
        <IconCalendar :size="14" /> {{ date }}
      </span>
      <span class="hero-card__meta-item">
        <IconClock :size="14" /> {{ duration }}
      </span>
      <span v-if="participants" class="hero-card__meta-item">
        <IconGroup :size="14" /> {{ participants }}
      </span>
      <slot name="badge" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { IconMeditation, IconCalendar, IconClock, IconGroup } from '@/components/icons'

withDefaults(
  defineProps<{
    title: string
    date: string
    duration: string
    /** Optional "N / M" participants string. Omit to hide (booked / detail). */
    participants?: string | null
  }>(),
  {
    participants: null,
  },
)
</script>

<style scoped>
.hero-card {
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-5) var(--space-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-2);
}

.hero-card__icon {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
  margin-bottom: var(--space-1);
}

.hero-card__title {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.hero-card__meta {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--space-3);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.hero-card__meta-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
}
</style>
