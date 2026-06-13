<!--
  VELO Frontend -- AdminPracticesView (Admin DS, 2026-06-14, operator SVG "2 Practices")

  Global practices list (all platform practices, across masters). Reached from the
  dashboard «Практик» stat card. Header (back + count badge) + VSegment filter
  (Все / Предстоящие / Прошедшие) + practice cards.

  STUB (operator Q2=А — honest skeleton): there is no admin practices API yet -> the
  list is empty ("Данных пока нет"); the header count + the «Все» badge show the
  real total from /admin/stats (practices_count). The card design (direction icon +
  master + date/duration/capacity + status) is built and ready for data. Roadmap for
  Zod: GET /admin/practices (filters upcoming/past, counts, capacity + status).
-->

<template>
  <div class="admin-list">
    <header class="admin-list__top">
      <VBackButton @click="router.back()" />
      <span class="admin-list__title">Практики</span>
      <span class="admin-list__count">{{ headerCount }}</span>
    </header>

    <VSegment v-model="filter" :options="segOptions" />

    <div v-if="practices.length" class="admin-list__items">
      <div v-for="p in practices" :key="p.id" class="pcard">
        <div class="pcard__top">
          <span class="pcard__icon"><component :is="iconFor(p)" :size="46" /></span>
          <div class="pcard__head">
            <h4 class="pcard__title">{{ p.title }}</h4>
            <p class="pcard__master">
              <span class="pcard__pic">{{ masterInitial(p) }}</span>
              <span class="pcard__master-name">{{ p.master_name }}</span>
            </p>
          </div>
        </div>

        <div class="pcard__meta">
          <span class="pcard__cell"><IconCalendar :size="14" />{{ p.when_label }}</span>
          <span class="pcard__cell"><IconClock :size="14" />{{ p.duration_label }}</span>
          <span class="pcard__cell" :class="{ 'pcard__cell--full': p.booked >= p.capacity }">
            <IconGroup :size="14" />{{ p.booked }}/{{ p.capacity }}
          </span>
        </div>

        <div class="pcard__badge">
          <VBadge :variant="p.status === 'past' ? 'muted' : 'blue'">
            {{ p.status === 'past' ? 'Завершена' : 'Скоро' }}
          </VBadge>
        </div>
      </div>
    </div>

    <VCard v-else>
      <p class="admin-list__empty">Данных пока нет</p>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VBackButton, VSegment, VBadge, VCard } from '@/components/ui'
import type { SegmentOption } from '@/components/ui/VSegment.vue'
import { IconCalendar, IconClock, IconGroup } from '@/components/icons'
import { practiceIconFor } from '@/utils/displayHelpers'
import { useAdminStore } from '@/stores/admin'

interface AdminPractice {
  id: string
  title: string
  direction?: string | null
  master_name: string
  /** Pre-formatted "Завтра, 07:00" / "22 янв, 07:00". */
  when_label: string
  /** Pre-formatted "45 мин". */
  duration_label: string
  booked: number
  capacity: number
  status: 'upcoming' | 'past'
}

const router = useRouter()
const adminStore = useAdminStore()

// Filter scopes the future API query (Zod). Visual-only until /admin/practices.
const filter = ref('all')

// Stub list -> Zod. Honest skeleton (Q2=А): empty until the API exists.
const practices = ref<AdminPractice[]>([])

// Real aggregate from /admin/stats (loaded by AdminShell). Header + «Все» badge.
const totalCount = computed<number | null>(() => adminStore.stats?.practices_count ?? null)
const headerCount = computed<string>(() =>
  totalCount.value !== null ? String(totalCount.value) : '—',
)

const segOptions = computed<SegmentOption[]>(() => [
  { value: 'all', label: 'Все', badge: totalCount.value ?? undefined },
  { value: 'upcoming', label: 'Предстоящие' },
  { value: 'past', label: 'Прошедшие' },
])

// Direction icon (carries its own circle ring) — same canon as PracticeListCard.
function iconFor(p: AdminPractice): ReturnType<typeof practiceIconFor> {
  return practiceIconFor({ direction: p.direction, title: p.title })
}

function masterInitial(p: AdminPractice): string {
  return (p.master_name.trim().charAt(0) || 'М').toUpperCase()
}
</script>

<style scoped>
.admin-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* -- Header: back + title + real-total count badge -- */
.admin-list__top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 44px;
}

.admin-list__title {
  flex: 1;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.admin-list__count {
  min-width: 48px;
  height: 36px;
  padding: 0 12px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  background: var(--velo-primary);
  color: var(--velo-white);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-body);
  font-size: var(--text-base);
  letter-spacing: 0.02em;
}

.admin-list__items {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.admin-list__empty {
  margin: 0;
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  padding: var(--space-4) var(--space-2);
}

/* -- Practice card -- */
.pcard {
  width: 100%;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
  font-family: var(--font-body);
}

.pcard__top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.pcard__icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--velo-text-primary);
}

.pcard__head {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.pcard__title {
  margin: 0;
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pcard__master {
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.pcard__pic {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--velo-blue-300);
  color: var(--velo-white);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-8);
  letter-spacing: 0.02em;
}

.pcard__master-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pcard__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) 18px;
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.pcard__cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.pcard__cell--full {
  color: var(--velo-pink-500);
}

.pcard__badge {
  display: flex;
}
</style>
