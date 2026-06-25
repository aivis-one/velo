<!--
  VELO Frontend -- MasterStudentProfileView (Master DS, 2026-06-11)

  "Профиль ученика" — one student's card: hero, stats, recent check-ins,
  feedbacks, and a "Написать сообщение" action. Rendered inside MasterShell.

  LIVE (E5): getStudent(id) → GET /api/v1/masters/me/students/{id} →
  StudentDetailResponse { name, avatar_url, practices_count, hours,
  satisfaction_pct, recent_checkins[], feedbacks[] }. Reuses the real MoodAvatar
  (diary mood faces) for check-ins. The "Написать сообщение" action is still a
  STUB (E4 messaging pending backend).
-->

<template>
  <div class="profile">
    <VHeader title="Профиль ученика" show-back @back="router.back()" />

    <div class="profile__content">
      <!-- Loading -->
      <div v-if="loading" class="profile__state">
        <VLoader size="lg" />
      </div>

      <!-- Error -->
      <VEmptyState
        v-else-if="error"
        icon="warning"
        title="Не удалось загрузить профиль"
        :description="error"
      >
        <VButton size="sm" variant="outline" @click="load">Повторить</VButton>
      </VEmptyState>

      <template v-else>
        <!-- Hero (name comes from the list nav — see script note) -->
        <div class="profile__hero">
          <VAvatar :name="name" :url="avatarUrl" size="xl" class="profile__hero-ava" />
          <div class="profile__hero-name">{{ name }}</div>
        </div>

        <!-- Stats (% card removed — ПРОМТ №157; two cards widen under the hero) -->
        <div class="profile__stats">
          <VStatCard :value="practicesCount" label="Практик" />
          <VStatCard :value="hours" label="Часов" />
        </div>

        <!-- Recent check-ins (cap 3; rest behind «посмотреть еще» — ПРОМТ №157) -->
        <h2 class="velo-section-title">Последние check-ins</h2>
        <div v-if="checkinRows.length === 0" class="profile__empty">Пока нет check-ins</div>
        <div v-for="(ci, i) in visibleCheckins" :key="`ci-${i}`" class="profile__ci">
          <MoodAvatar :mood="ci.mood" :size="46" />
          <div class="profile__ci-body">
            <div class="profile__ci-text">{{ ci.comment || moodLabelFromScore(ci.mood) }}</div>
            <div class="profile__ci-date">{{ ci.date }}</div>
          </div>
        </div>
        <VShowMore
          v-if="!ciExpanded && hiddenCheckins > 0"
          label="посмотреть еще"
          @click="ciExpanded = true"
        />

        <!-- Feedbacks (cap 3; rest behind «посмотреть еще» — ПРОМТ №157) -->
        <h2 class="velo-section-title">Feedbacks</h2>
        <div v-if="feedbackRows.length === 0" class="profile__empty">Пока нет отзывов</div>
        <div v-for="(fb, i) in visibleFeedbacks" :key="`fb-${i}`" class="profile__fb">
          <span class="profile__fb-ic" :style="{ color: fb.color }">
            <component :is="fb.icon" :size="30" />
          </span>
          <div class="profile__fb-body">
            <div class="profile__fb-row">
              <span class="profile__fb-title">{{ fb.label }}</span>
              <span class="profile__fb-date">{{ fb.date }}</span>
            </div>
            <div v-if="fb.comment" class="profile__fb-text">{{ fb.comment }}</div>
          </div>
        </div>
        <VShowMore
          v-if="!fbExpanded && hiddenFeedbacks > 0"
          label="посмотреть еще"
          @click="fbExpanded = true"
        />

        <!-- Action (stub — E4 messaging not delivered) -->
        <VButton variant="primary" block class="profile__cta" @click="msgOpen = true">
          Написать сообщение
        </VButton>
      </template>
    </div>

    <SendMessageModal :open="msgOpen" :name="name" @close="msgOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VAvatar, VStatCard, VButton, VLoader, VEmptyState } from '@/components/ui'
import { IconRatingFire, IconRatingGood, IconRatingConfused } from '@/components/icons'
import MoodAvatar from '@/components/shared/MoodAvatar.vue'
import SendMessageModal from '@/components/shared/SendMessageModal.vue'
import VShowMore from '@/components/shared/VShowMore.vue'
import {
  moodLabelFromScore,
  ratingLabelFromScore,
  ratingZoneFromScore,
  RATING_ICON_COLOR,
} from '@/utils/displayHelpers'
import { formatShortDate } from '@/utils/format'
import { getStudent } from '@/api/masters'
import type { StudentDetailResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()

// Identity comes from StudentDetailResponse (name/avatar_url, E5). The list
// still forwards ?name= for an instant pre-fetch render; «Ученик» is only a
// last-resort fallback (e.g. before the fetch resolves on a direct deep-link),
// never the unconditional placeholder.
const name = computed((): string => {
  const q = route.query.name
  return detail.value?.name || (typeof q === 'string' && q) || 'Ученик'
})
const avatarUrl = computed((): string => detail.value?.avatar_url ?? '')

// -- Per-student aggregate (E5: GET /masters/me/students/{id}). --
const detail = ref<StudentDetailResponse | null>(null)
const loading = ref(true)
const error = ref('')

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    detail.value = await getStudent(String(route.params.id))
  } catch {
    error.value = 'Попробуйте ещё раз'
  } finally {
    loading.value = false
  }
}
onMounted(load)

const practicesCount = computed((): number => detail.value?.practices_count ?? 0)
const hours = computed((): number => detail.value?.hours ?? 0)

const ICON_BY_ZONE: Record<'confused' | 'good' | 'fire', Component> = {
  confused: IconRatingConfused,
  good: IconRatingGood,
  fire: IconRatingFire,
}

const checkinRows = computed(() =>
  (detail.value?.recent_checkins ?? []).map((ci) => ({
    mood: ci.mood,
    comment: ci.comment ?? '',
    date: formatShortDate(ci.created_at),
  })),
)

const feedbackRows = computed(() =>
  (detail.value?.feedbacks ?? []).map((fb) => {
    const zone = ratingZoneFromScore(fb.rating)
    return {
      label: ratingLabelFromScore(fb.rating),
      icon: ICON_BY_ZONE[zone],
      color: RATING_ICON_COLOR[zone],
      comment: fb.comment ?? '',
      date: formatShortDate(fb.created_at),
    }
  }),
)

// Show the 3 most recent of each; the rest hide behind a «посмотреть еще» pill
// until tapped (operator, ПРОМТ №157). Client-side expand of the already-loaded
// (backend-capped) set — no pagination.
const PREVIEW_CAP = 3
const ciExpanded = ref(false)
const fbExpanded = ref(false)
const visibleCheckins = computed(() =>
  ciExpanded.value ? checkinRows.value : checkinRows.value.slice(0, PREVIEW_CAP),
)
const visibleFeedbacks = computed(() =>
  fbExpanded.value ? feedbackRows.value : feedbackRows.value.slice(0, PREVIEW_CAP),
)
const hiddenCheckins = computed((): number => Math.max(0, checkinRows.value.length - PREVIEW_CAP))
const hiddenFeedbacks = computed((): number => Math.max(0, feedbackRows.value.length - PREVIEW_CAP))

// "Написать сообщение" — stub (E4 messaging not delivered).
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

.profile__state {
  display: flex;
  justify-content: center;
  padding: var(--space-6) 0;
}

.profile__empty {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
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

/* -- Stats (VStatCard ×2: practices + hours) -- */
.profile__stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

/* -- Section title -- */

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

.profile__ci-body {
  flex: 1;
  min-width: 0;
}

.profile__ci-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
}

.profile__ci-date {
  font-family: var(--font-body);
  font-size: var(--text-12);
  color: var(--velo-text-secondary);
  margin-top: var(--velo-gap-2);
}

/* -- Feedback card -- */
.profile__fb {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--velo-card-padding-y) var(--space-4);
}

.profile__fb-ic {
  flex-shrink: 0;
  color: var(--velo-peach-500);
  display: flex;
  align-items: center;
}

.profile__fb-body {
  flex: 1;
  min-width: 0;
}

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
  margin-top: var(--velo-gap-3);
}

.profile__cta {
  margin-top: var(--space-2);
}
</style>
