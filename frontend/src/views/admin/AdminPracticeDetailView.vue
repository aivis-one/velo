<!--
  VELO Frontend -- AdminPracticeDetailView (Admin DS, 2026-06-14, operator SVGs "3 Practice details" upcoming/past)

  Admin oversight of a single practice (read-only). Reached by tapping a card in the
  admin practices list (admin-practice-detail); the detail re-fetches by route id.
  Hero (PracticeHeroCard, #meta = master + date) + 2 VStatCard + roster.

  Two variants by practice.status ("upcoming" / "past"):
    - upcoming: stats Записалось / Свободно; section «Записались (N/M)».
    - past: stats Записалось / Пришли; «Присутствовали» (teal check) + «Не пришли»
      (rose cross).

  WIRED (E9, 2026-06-16): GET /api/v1/admin/practices/:id provides the hero fields,
  booked/capacity/attended counts and the full non-cancelled roster (loading/error
  states). Past practices bucket the roster by booking status (attended / no_show).
-->

<template>
  <div class="admin-detail">
    <header class="admin-detail__top">
      <VBackButton @click="router.back()" />
      <span class="admin-detail__title">Детали практики</span>
    </header>

    <div v-if="loading" class="admin-detail__loader"><VLoader size="lg" /></div>

    <VEmptyState
      v-else-if="error"
      icon="warning"
      title="Не удалось загрузить практику"
      :description="error"
    >
      <VButton size="sm" variant="outline" @click="load">Повторить</VButton>
    </VEmptyState>

    <template v-else-if="practice">
      <PracticeHeroCard :title="practice.title" :direction="practice.direction">
        <template #meta>
          <span class="admin-detail__hero-cell">
            <span class="admin-detail__pic">{{ masterInitial }}</span>
            {{ practice.master_name }}
          </span>
          <span class="admin-detail__hero-cell"> <IconCalendar :size="14" /> {{ whenLabel }} </span>
        </template>
      </PracticeHeroCard>

      <div class="admin-detail__stats2">
        <VStatCard :value="bookedLabel" label="Записалось" />
        <VStatCard v-if="isPast" :value="attendedLabel" label="Пришли" />
        <VStatCard v-else :value="freeLabel" label="Свободно" />
      </div>

      <!-- Upcoming: who registered -->
      <template v-if="!isPast">
        <h3 class="admin-detail__section">Записались ({{ practice.booked }}/{{ capacityText }})</h3>
        <div v-if="registered.length" class="admin-detail__items">
          <VListRow v-for="r in registered" :key="r.user_id" :title="r.name">
            <template #lead>
              <span class="admin-detail__avatar"><IconProfile :size="22" /></span>
            </template>
          </VListRow>
        </div>
        <VCard v-else><p class="admin-detail__empty">Данных пока нет</p></VCard>
      </template>

      <!-- Past: who attended / who didn't -->
      <template v-else>
        <h3 class="admin-detail__section">Присутствовали ({{ present.length }})</h3>
        <div v-if="present.length" class="admin-detail__items">
          <VListRow v-for="r in present" :key="r.user_id" :title="r.name">
            <template #lead>
              <span class="admin-detail__avatar"><IconProfile :size="22" /></span>
            </template>
            <template #trailing>
              <span class="admin-detail__mark admin-detail__mark--ok"
                ><IconCheck :size="24"
              /></span>
            </template>
          </VListRow>
        </div>
        <VCard v-else><p class="admin-detail__empty">Данных пока нет</p></VCard>

        <h3 class="admin-detail__section">Не пришли ({{ absent.length }})</h3>
        <div v-if="absent.length" class="admin-detail__items">
          <VListRow v-for="r in absent" :key="r.user_id" :title="r.name">
            <template #lead>
              <span class="admin-detail__avatar"><IconProfile :size="22" /></span>
            </template>
            <template #trailing>
              <span class="admin-detail__mark admin-detail__mark--no"
                ><IconClose :size="22"
              /></span>
            </template>
          </VListRow>
        </div>
        <VCard v-else><p class="admin-detail__empty">Нет данных</p></VCard>
      </template>
    </template>

    <VCard v-else>
      <p class="admin-detail__empty">Практика недоступна</p>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  VBackButton,
  VStatCard,
  VCard,
  VButton,
  VListRow,
  VLoader,
  VEmptyState,
} from '@/components/ui'
import PracticeHeroCard from '@/components/shared/PracticeHeroCard.vue'
import { IconCalendar, IconProfile, IconCheck, IconClose } from '@/components/icons'
import { getAdminPracticeDetail } from '@/api/admin'
import { ApiResponseError } from '@/api/client'
import { formatDateShort } from '@/utils/format'
import type { AdminPracticeDetailResponse, AdminRosterEntry } from '@/api/types'

const route = useRoute()
const router = useRouter()
const practiceId = route.params.id as string

const practice = ref<AdminPracticeDetailResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const isPast = computed<boolean>(() => practice.value?.status === 'past')

const masterInitial = computed<string>(() =>
  (practice.value?.master_name.trim().charAt(0) || 'М').toUpperCase(),
)

const whenLabel = computed<string>(() =>
  practice.value ? formatDateShort(practice.value.scheduled_at) : '',
)

const bookedLabel = computed<string>(() => String(practice.value?.booked ?? '—'))
const attendedLabel = computed<string>(() => String(practice.value?.attended ?? '—'))
const capacityText = computed<string>(() => {
  const c = practice.value?.capacity
  return c != null ? String(c) : '∞'
})
const freeLabel = computed<string>(() => {
  const p = practice.value
  if (!p) return '—'
  return p.capacity != null ? String(Math.max(0, p.capacity - p.booked)) : '∞'
})

// Roster from the detail response. Past practices bucket by booking status.
const roster = computed<AdminRosterEntry[]>(() => practice.value?.roster ?? [])
const registered = computed<AdminRosterEntry[]>(() => roster.value)
const present = computed<AdminRosterEntry[]>(() =>
  roster.value.filter((r) => r.status === 'attended'),
)
const absent = computed<AdminRosterEntry[]>(() =>
  roster.value.filter((r) => r.status !== 'attended'),
)

async function load(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    practice.value = await getAdminPracticeDetail(practiceId)
  } catch (e) {
    error.value = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

onMounted(load)
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

/* Hero #meta cells (master + date), centred by PracticeHeroCard. */
.admin-detail__hero-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.admin-detail__pic {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--velo-text-primary);
  color: var(--velo-white);
  font-size: var(--text-8);
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

.admin-detail__items {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.admin-detail__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-6) 0;
}

.admin-detail__empty {
  margin: 0;
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  padding: var(--space-4) var(--space-2);
}

.admin-detail__avatar {
  width: 41px;
  height: 41px;
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--velo-blue-300);
  color: var(--velo-white);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.admin-detail__mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.admin-detail__mark--ok {
  color: var(--velo-teal-600);
}

.admin-detail__mark--no {
  color: var(--velo-pink-500);
}
</style>
