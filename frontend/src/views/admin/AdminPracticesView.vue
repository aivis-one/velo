<!--
  VELO Frontend -- AdminPracticesView (Admin DS, 2026-06-14, operator SVGs "2 Practices" + upcoming/past)

  Global practices list (all platform practices, across masters). Reached from the
  dashboard «Практик» stat card. Header (back + count badge) + VSegment filter
  (Все / Предстоящие / Прошедшие) + PracticeListCard rows. Tapping a card opens the
  admin practice detail (admin-practice-detail), handing the practice via router state.

  Card = the canonical PracticeListCard (operator reconciliation п.1=А): direction
  icon + title + master (+verified) + bottom meta (date under the icon · duration ·
  capacity in the #badge slot, rose when full). No status badge — capacity took its
  slot in the newer SVGs.

  STUB (operator Q2=А — honest skeleton): no admin practices API yet -> the list is
  empty ("Данных пока нет"); the header count + the «Все» badge show the real total
  from /admin/stats (practices_count). Roadmap for Zod: GET /admin/practices (filters
  upcoming/past, counts, capacity + status) + GET /admin/practices/:id (detail).
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
      <PracticeListCard
        v-for="p in practices"
        :key="p.id"
        :practice="p"
        :when="p.when_label"
        :duration="p.duration_label"
        @click="openDetail(p)"
      >
        <template #badge>
          <span class="admin-cap" :class="{ 'admin-cap--full': p.booked >= p.capacity }">
            <IconGroup :size="14" />{{ p.booked }}/{{ p.capacity }}
          </span>
        </template>
      </PracticeListCard>
    </div>

    <VCard v-else>
      <p class="admin-list__empty">Данных пока нет</p>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VBackButton, VSegment, VCard } from '@/components/ui'
import type { SegmentOption } from '@/components/ui/VSegment.vue'
import PracticeListCard from '@/components/shared/PracticeListCard.vue'
import { IconGroup } from '@/components/icons'
import { useAdminStore } from '@/stores/admin'

interface AdminPractice {
  id: string
  title: string
  direction?: string | null
  master_name: string
  when_label: string
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

// Tap a card -> admin practice detail; hand the practice via router state (the list
// API isn't wired yet, so the detail reads what it was given).
function openDetail(p: AdminPractice): void {
  router.push({
    name: 'admin-practice-detail',
    params: { id: p.id },
    state: { practice: JSON.parse(JSON.stringify(p)) },
  })
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

/* Capacity cell in the PracticeListCard #badge slot (rose when full). */
.admin-cap {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.admin-cap--full {
  color: var(--velo-pink-500);
}
</style>
