<!--
  VELO Frontend -- MasterPublicView (Calendar iteration, S-4)

  Public master profile shown to users who tap "Подробнее" on a practice's
  master card (frame 4). Figma node 541:2065:
    - Hero card: avatar, name, "✓ Верифицирован" badge + "N лет опыта" pill, bio
    - Two stat cards: practices_count "Практик" / reviews_count "Отзывов"
    - "Методы" accordion (method chips)
    - "Ближайшие практики": upcoming practices by this master (reuses
      getPractices with master_id -- no new endpoint, no dedicated store)
    - "Задать вопрос" button -> ask-master flow (frame 6, not built yet:
      toast placeholder, V2)

  Backend: GET /api/v1/masters/:id (MasterPublicResponse). Only verified
  masters resolve; 404 otherwise -> shown as an empty state.

  Route: /user/masters/:id  (name: user-master-public)
-->

<template>
  <div class="master-public">
    <VHeader title="Мастер" show-back @back="router.back()" />

    <!-- Loading -->
    <div v-if="loading" class="master-public__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error / not found -->
    <VEmptyState
      v-else-if="error || !profile"
      icon="⚠️"
      title="Мастер не найден"
      :description="error ?? 'Профиль недоступен'"
    >
      <VButton size="sm" @click="router.back()">Назад</VButton>
    </VEmptyState>

    <!-- Content -->
    <div v-else class="master-public__content">
      <!-- Hero -->
      <div class="master-public__hero">
        <div class="master-public__avatar">
          <img
            v-if="profile.avatar_url"
            :src="profile.avatar_url"
            :alt="displayName"
            class="master-public__avatar-img"
          />
          <IconMeditation v-else :size="44" />
        </div>

        <h1 class="master-public__name">{{ displayName }}</h1>

        <div class="master-public__pills">
          <span class="master-public__pill master-public__pill--verified">
            <IconCheck :size="14" /> Верифицирован
          </span>
          <span
            v-if="profile.experience_years != null"
            class="master-public__pill"
          >
            {{ profile.experience_years }} {{ pluralYears(profile.experience_years) }} опыта
          </span>
        </div>

        <p v-if="profile.bio" class="master-public__bio">{{ profile.bio }}</p>
      </div>

      <!-- Stats -->
      <div class="master-public__stats">
        <div class="master-public__stat">
          <div class="master-public__stat-value">{{ profile.practices_count }}</div>
          <div class="master-public__stat-label">{{ pluralPractices(profile.practices_count) }}</div>
        </div>
        <div class="master-public__stat">
          <div class="master-public__stat-value">{{ profile.reviews_count }}</div>
          <div class="master-public__stat-label">{{ pluralReviews(profile.reviews_count) }}</div>
        </div>
      </div>

      <!-- Methods accordion -->
      <VAccordion v-if="profile.methods?.length" title="Методы">
        <div class="master-public__chips">
          <VTag
            v-for="(method, i) in (profile.methods || [])"
            :key="method"
            :variant="TAG_VARIANTS[i % TAG_VARIANTS.length]"
          >
            {{ method }}
          </VTag>
        </div>
      </VAccordion>

      <!-- Upcoming practices -->
      <section v-if="upcoming.length" class="master-public__section">
        <h3 class="master-public__section-title">Ближайшие практики</h3>
        <div class="master-public__practices">
          <PracticeCard
            v-for="p in upcoming"
            :key="p.id"
            :practice="p"
            @click="goToPractice"
          />
        </div>
      </section>

      <!-- Ask a question (frame 6 -- not built yet) -->
      <div class="master-public__actions">
        <VButton variant="primary" size="lg" block @click="onAsk">
          Задать вопрос
        </VButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VLoader, VEmptyState, VButton, VAccordion, VTag } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { IconMeditation, IconCheck } from '@/components/icons'
import PracticeCard from '@/components/shared/PracticeCard.vue'
import { getPublicMaster } from '@/api/masters'
import { getPractices } from '@/api/practices'
import { extractApiError } from '@/composables/useApiError'
import { useToast } from '@/composables/useToast'
import type { MasterPublicResponse, PracticeResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const profile = ref<MasterPublicResponse | null>(null)
const upcoming = ref<PracticeResponse[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const masterId = computed(() => String(route.params.id))

const displayName = computed(() => profile.value?.display_name ?? 'Мастер')

// Method tags cycle through three tints (same as MasterCard).
const TAG_VARIANTS = ['blue', 'pink', 'sand'] as const

// -- Russian pluralization helpers --
function plural(n: number, one: string, few: string, many: string): string {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod100 >= 11 && mod100 <= 14) return many
  if (mod10 === 1) return one
  if (mod10 >= 2 && mod10 <= 4) return few
  return many
}
function pluralYears(n: number): string {
  return plural(n, 'год', 'года', 'лет')
}
function pluralPractices(n: number): string {
  return plural(n, 'Практика', 'Практики', 'Практик')
}
function pluralReviews(n: number): string {
  return plural(n, 'Отзыв', 'Отзыва', 'Отзывов')
}

function goToPractice(id: string): void {
  router.push({ name: 'practice-detail', params: { id } })
}

function onAsk(): void {
  // Ask-master flow (Figma frame 6) is a separate iteration with its own
  // backend endpoint. Placeholder until then (V2).
  toast.info('Вопрос мастеру -- скоро')
}

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    profile.value = await getPublicMaster(masterId.value)
    // Upcoming practices by this master: reuse the public feed with a
    // master_id filter + scheduled status. One small page is enough.
    try {
      const res = await getPractices(
        { master_id: masterId.value, status: 'scheduled', sort_by: 'scheduled_at', sort_order: 'asc' },
        10,
        0,
      )
      upcoming.value = res.items
    } catch {
      // Non-fatal: the profile still renders without the upcoming list.
      upcoming.value = []
    }
  } catch (e) {
    error.value = extractApiError(e, 'Не удалось загрузить профиль мастера')
    profile.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.master-public {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.master-public__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

.master-public__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

/* Hero */
.master-public__hero {
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

.master-public__avatar {
  width: 96px;
  height: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
  overflow: hidden;
}

.master-public__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-full);
}

.master-public__name {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0;
}

.master-public__pills {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.master-public__pill {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.master-public__pill--verified {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}

.master-public__bio {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.6;
  margin: var(--space-1) 0 0;
}

/* Stats */
.master-public__stats {
  display: flex;
  gap: var(--space-3);
}

.master-public__stat {
  flex: 1;
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
}

.master-public__stat-value {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--velo-text-primary);
}

.master-public__stat-label {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

/* Sections */
.master-public__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.master-public__section-title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-2);
}

.master-public__practices {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.master-public__actions {
  margin-top: var(--space-2);
}
</style>
