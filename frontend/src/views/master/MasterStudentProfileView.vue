<!--
  VELO Frontend -- MasterStudentProfileView (Master DS, 2026-06-11)

  "Профиль ученика" — one student's card: hero, stats, recent check-ins,
  feedbacks, and a "Написать сообщение" action. Rendered inside MasterShell.

  STUB: no per-student aggregation backend (practices/hours/satisfaction, the
  student's check-ins across practices, their feedbacks). Placeholder data below;
  documents the contract for Zod (roadmap: Agent-Velo/master-ds-zod-roadmap.md).
  Reuses the real MoodAvatar (diary mood faces) for check-ins.
-->

<template>
  <div class="profile">
    <VHeader title="Профиль ученика" show-back @back="router.back()" />

    <div class="profile__content">
      <!-- Hero -->
      <div class="profile__hero">
        <VAvatar :name="student.name" size="xl" class="profile__hero-ava" />
        <div class="profile__hero-name">{{ student.name }}</div>
      </div>

      <!-- Stats -->
      <div class="profile__stats">
        <VStatCard :value="student.practices_count" label="Практик" />
        <VStatCard :value="student.hours" label="Часов" />
        <div class="profile__stat">
          <div class="profile__stat-value">{{ student.satisfaction_pct }}%</div>
          <div class="profile__stat-icons">
            <IconHeart :size="15" class="profile__ic-heart" />
            <IconRatingFire :size="15" class="profile__ic-fire" />
          </div>
        </div>
      </div>

      <!-- Recent check-ins -->
      <h3 class="profile__section-title">Последние check-ins</h3>
      <div
        v-for="(ci, i) in checkins"
        :key="i"
        class="profile__ci"
      >
        <MoodAvatar :mood="ci.mood" :size="46" />
        <div class="profile__ci-body">
          <div class="profile__ci-text">{{ ci.comment || moodLabelFromScore(ci.mood) }}</div>
          <div class="profile__ci-date">{{ ci.date }}</div>
        </div>
      </div>

      <!-- Feedbacks -->
      <h3 class="profile__section-title">Feedbacks</h3>
      <div
        v-for="(fb, i) in feedbacks"
        :key="`fb-${i}`"
        class="profile__fb"
      >
        <span class="profile__fb-ic"><IconRatingFire :size="30" /></span>
        <div class="profile__fb-body">
          <div class="profile__fb-row">
            <span class="profile__fb-title">{{ fb.title }}</span>
            <span class="profile__fb-date">{{ fb.date }}</span>
          </div>
          <div class="profile__fb-text">{{ fb.comment }}</div>
        </div>
      </div>

      <!-- Action -->
      <VButton variant="primary" block class="profile__cta" @click="msgOpen = true">
        Написать сообщение
      </VButton>
    </div>

    <SendMessageModal :open="msgOpen" :name="student.name" @close="msgOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VAvatar, VStatCard, VButton } from '@/components/ui'
import { IconHeart, IconRatingFire } from '@/components/icons'
import MoodAvatar from '@/components/shared/MoodAvatar.vue'
import SendMessageModal from '@/components/shared/SendMessageModal.vue'
import { moodLabelFromScore } from '@/utils/displayHelpers'

const router = useRouter()

// -- STUB data (no per-student aggregation backend → roadmap for Zod). --
const student = ref({
  name: 'Мария К.',
  practices_count: 12,
  hours: '9,5',
  satisfaction_pct: 85,
})
const checkins = ref<Array<{ mood: number; date: string; comment: string }>>([
  { mood: 9, date: '22 янв', comment: 'Выспалась, готова к практике' },
  { mood: 6, date: '20 янв', comment: '' },
])
const feedbacks = ref<Array<{ title: string; date: string; comment: string }>>([
  { title: 'Огонь!', date: '22 янв', comment: 'Лучшая практика за месяц!' },
])

const msgOpen = ref(false)
</script>

<style scoped>
.profile {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.profile__content {
  flex: 1;
  /* F-5 rail sync: ride MobileLayout's 24px rail (no local h-padding). */
  padding: var(--space-4) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* -- Hero -- */
.profile__hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-5) var(--space-4);
}

.profile__hero-ava {
  width: 100px;
  height: 100px;
  font-size: var(--text-xl);
}

.profile__hero-name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

/* -- Stats (VStatCard ×2 + a custom % card matching its look) -- */
.profile__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.profile__stat {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-2);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 9px;
  text-align: center;
}

.profile__stat-value {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  color: var(--velo-text-primary);
  line-height: 1.1;
  letter-spacing: 0.64px;
}

.profile__stat-icons {
  display: inline-flex;
  gap: var(--space-1);
}

.profile__ic-heart { color: var(--velo-pink-500); }
.profile__ic-fire { color: var(--velo-peach-500); }

/* -- Section title -- */
.profile__section-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: var(--space-1) 0 0;
}

/* -- Check-in card -- */
.profile__ci {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
}

.profile__ci-body { flex: 1; min-width: 0; }

.profile__ci-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
}

.profile__ci-date {
  font-family: var(--font-body);
  font-size: var(--text-12);
  color: var(--velo-text-secondary);
  margin-top: 2px;
}

/* -- Feedback card -- */
.profile__fb {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: 13px var(--space-4);
}

.profile__fb-ic {
  flex-shrink: 0;
  color: var(--velo-peach-500);
  display: flex;
  align-items: center;
}

.profile__fb-body { flex: 1; min-width: 0; }

.profile__fb-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: var(--space-2);
}

.profile__fb-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.profile__fb-date {
  font-family: var(--font-body);
  font-size: var(--text-12);
  color: var(--velo-text-secondary);
  flex-shrink: 0;
}

.profile__fb-text {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin-top: 3px;
}

.profile__cta {
  margin-top: var(--space-2);
}
</style>
