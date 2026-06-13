<!--
  VELO Frontend -- AdminPracticeDetailView (Admin DS, 2026-06-14, operator SVGs "3 Practice details" upcoming/past)

  Admin oversight of a single practice (read-only). Reached by tapping a card in the
  admin practices list (admin-practice-detail), which hands the practice via router
  state. Hero (PracticeHeroCard, #meta = master + date) + 2 VStatCard + roster.

  Two variants by practice.status:
    - upcoming: stats Записалось / Свободно; section «Записались (N/M)».
    - past: stats Записалось / Пришли; «Присутствовали» (teal check) + «Не пришли»
      (rose cross).

  STUB (operator Q2=А — honest skeleton): the hero + the «Записалось»/«Свободно» stats
  come from the handed practice; the per-person roster and the attendance count have
  no API yet -> empty («Данных пока нет») / «—». Roadmap for Zod: GET
  /admin/practices/:id (detail + roster + attendance).
-->

<template>
  <div class="admin-detail">
    <header class="admin-detail__top">
      <VBackButton @click="router.back()" />
      <span class="admin-detail__title">Детали практики</span>
    </header>

    <template v-if="practice">
      <PracticeHeroCard :title="practice.title" :direction="practice.direction ?? null">
        <template #meta>
          <span class="admin-detail__hero-cell">
            <span class="admin-detail__pic">{{ masterInitial }}</span>
            {{ practice.master_name }}
          </span>
          <span class="admin-detail__hero-cell">
            <IconCalendar :size="14" /> {{ practice.when_label }}
          </span>
        </template>
      </PracticeHeroCard>

      <div class="admin-detail__stats2">
        <VStatCard :value="bookedLabel" label="Записалось" />
        <VStatCard v-if="isPast" :value="attendedLabel" label="Пришли" />
        <VStatCard v-else :value="freeLabel" label="Свободно" />
      </div>

      <!-- Upcoming: who registered -->
      <template v-if="!isPast">
        <h3 class="admin-detail__section">
          Записались ({{ practice.booked }}/{{ practice.capacity }})
        </h3>
        <template v-if="registered.length">
          <div class="admin-detail__items">
            <VListRow v-for="r in registered" :key="r.id" :title="r.name" :subtitle="r.sub">
              <template #lead>
                <span class="admin-detail__avatar"><IconProfile :size="22" /></span>
              </template>
            </VListRow>
          </div>
          <div class="admin-detail__more">
            <VButton variant="outline" @click="stub"
              >Показать всех ({{ registered.length }})</VButton
            >
          </div>
        </template>
        <VCard v-else><p class="admin-detail__empty">Данных пока нет</p></VCard>
      </template>

      <!-- Past: who attended / who didn't -->
      <template v-else>
        <h3 class="admin-detail__section">Присутствовали ({{ present.length }})</h3>
        <template v-if="present.length">
          <div class="admin-detail__items">
            <VListRow v-for="r in present" :key="r.id" :title="r.name" :subtitle="r.sub">
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
          <div class="admin-detail__more">
            <VButton variant="outline" @click="stub">Показать всех ({{ present.length }})</VButton>
          </div>
        </template>
        <VCard v-else><p class="admin-detail__empty">Данных пока нет</p></VCard>

        <h3 class="admin-detail__section">Не пришли ({{ absent.length }})</h3>
        <div v-if="absent.length" class="admin-detail__items">
          <VListRow v-for="r in absent" :key="r.id" :title="r.name" :subtitle="r.sub">
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VBackButton, VStatCard, VCard, VButton, VListRow } from '@/components/ui'
import PracticeHeroCard from '@/components/shared/PracticeHeroCard.vue'
import { IconCalendar, IconProfile, IconCheck, IconClose } from '@/components/icons'
import { useToast } from '@/composables/useToast'

interface DetailPractice {
  id: string
  title: string
  direction?: string | null
  master_name: string
  when_label: string
  booked: number
  capacity: number
  status: 'upcoming' | 'past'
}

interface RosterPerson {
  id: string
  name: string
  sub: string
  avatar_url?: string
}

const router = useRouter()
const toast = useToast()

// The practice is handed over via router state by the practices list (no detail API
// yet). Direct navigation without state -> "Практика недоступна".
const practice = ref<DetailPractice | null>(
  (history.state as { practice?: DetailPractice }).practice ?? null,
)

const isPast = computed<boolean>(() => practice.value?.status === 'past')

const masterInitial = computed<string>(() =>
  (practice.value?.master_name.trim().charAt(0) || 'М').toUpperCase(),
)

const bookedLabel = computed<string>(() => String(practice.value?.booked ?? '—'))
const freeLabel = computed<string>(() => {
  const p = practice.value
  return p ? String(Math.max(0, p.capacity - p.booked)) : '—'
})
// «Пришли» (attended) has no source without the roster API -> honest «—».
const attendedLabel = computed<string>(() => '—')

// Roster -> Zod. Honest skeleton (Q2=А): empty until GET /admin/practices/:id.
const registered = ref<RosterPerson[]>([])
const present = ref<RosterPerson[]>([])
const absent = ref<RosterPerson[]>([])

// Inert until the roster API lands (the «Показать всех» button only shows with data).
function stub(): void {
  toast.info('Раздел пока недоступен')
}
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

.admin-detail__more {
  display: flex;
  justify-content: center;
  padding-top: var(--space-1);
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
