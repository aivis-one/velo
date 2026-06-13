<!--
  VELO Frontend -- AdminParticipantsView (Admin DS, 2026-06-14, operator SVG "1 Participants")

  Global participants list (all platform users). Reached from the dashboard
  «Участников» stat card. Header (back + count badge) + VSegment filter
  (Все / Новые / Активные) + participant rows + load-more.

  STUB (operator Q2=А — honest skeleton): there is no admin participants API yet
  -> the list is empty ("Данных пока нет"); the header count + the «Все» badge show
  the real total from /admin/stats (users_count). The row / avatar / message-button
  design is built and ready for data. Roadmap for Zod: GET /admin/participants
  (filters new/active, counts, joined + last-active labels) + admin->user messaging.
-->

<template>
  <div class="admin-list">
    <header class="admin-list__top">
      <VBackButton @click="router.back()" />
      <span class="admin-list__title">Участники</span>
      <span class="admin-list__count">{{ headerCount }}</span>
    </header>

    <VSegment v-model="filter" :options="segOptions" />

    <template v-if="participants.length">
      <div class="admin-list__items">
        <div v-for="p in participants" :key="p.id" class="prow">
          <span class="prow__avatar">
            <img v-if="p.avatar_url" :src="p.avatar_url" :alt="p.name" class="prow__avatar-img" />
            <IconProfile v-else :size="22" />
          </span>
          <span class="prow__text">
            <span class="prow__name">{{ p.name }}</span>
            <span class="prow__sub">{{ p.email }}</span>
            <span class="prow__meta">
              Практик: {{ p.practices_count
              }}<template v-if="p.joined_label"> • с {{ p.joined_label }}</template>
            </span>
            <span v-if="p.last_active_label" class="prow__meta"
              >Последняя: {{ p.last_active_label }}</span
            >
          </span>
          <button type="button" class="prow__msg" aria-label="Написать" @click="messageStub">
            <IconMessages :size="22" />
          </button>
        </div>
      </div>

      <div v-if="hasMore" class="admin-list__more">
        <VButton variant="outline" @click="loadMore">Показать ещё</VButton>
      </div>
    </template>

    <VCard v-else>
      <p class="admin-list__empty">Данных пока нет</p>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VBackButton, VSegment, VButton, VCard } from '@/components/ui'
import type { SegmentOption } from '@/components/ui/VSegment.vue'
import { IconProfile, IconMessages } from '@/components/icons'
import { useToast } from '@/composables/useToast'
import { useAdminStore } from '@/stores/admin'

interface AdminParticipant {
  id: string
  name: string
  email: string
  avatar_url?: string
  practices_count: number
  /** "Дек 2025" — omitted when unknown. */
  joined_label?: string
  /** "вчера" / "сегодня" — present in the Активные filter. */
  last_active_label?: string
}

const router = useRouter()
const toast = useToast()
const adminStore = useAdminStore()

// Filter scopes the future API query (Zod). Visual-only until /admin/participants.
const filter = ref('all')

// Stub list -> Zod. Honest skeleton (Q2=А): empty until the API exists.
const participants = ref<AdminParticipant[]>([])
const hasMore = ref(false)

// Real aggregate from /admin/stats (loaded by AdminShell). Header + «Все» badge.
const totalCount = computed<number | null>(() => adminStore.stats?.users_count ?? null)
const headerCount = computed<string>(() =>
  totalCount.value !== null ? String(totalCount.value) : '—',
)

const segOptions = computed<SegmentOption[]>(() => [
  { value: 'all', label: 'Все', badge: totalCount.value ?? undefined },
  { value: 'new', label: 'Новые' },
  { value: 'active', label: 'Активные' },
])

// No messaging endpoint yet -> stub toast (build-full-design). Roadmap: Zod.
function messageStub(): void {
  toast.info('Сообщения пока недоступны')
}

// No participants API yet -> inert until Zod wires pagination.
function loadMore(): void {
  toast.info('Раздел пока недоступен')
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

.admin-list__more {
  display: flex;
  justify-content: center;
  padding-top: var(--space-1);
}

.admin-list__empty {
  margin: 0;
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  padding: var(--space-4) var(--space-2);
}

/* -- Participant row -- */
.prow {
  width: 100%;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  text-align: left;
  font-family: var(--font-body);
}

.prow__avatar {
  width: 41px;
  height: 41px;
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--velo-blue-300);
  color: var(--velo-white);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.prow__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.prow__text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.prow__name {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prow__sub {
  font-size: var(--text-xs);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prow__meta {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: 0.02em;
}

.prow__msg {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  border: none;
  border-radius: var(--radius-full);
  background: var(--velo-primary);
  color: var(--velo-white);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.prow__msg:active {
  opacity: 0.85;
}
</style>
