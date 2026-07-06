<!--
  VELO Frontend -- AdminMastersView (Admin DS rebuild 2026-06-14, operator SVGs "1 Masters" all/under-review/verified)

  The «Мастера» tab (admin-masters). Rebuilt to the operator design: header (back +
  count badge) + VSegment filter (Все / На проверке / Верифицированы) + master cards.
  A fog-feed tab screen (mandala background, the admin tab bar stays). Tapping a card
  opens the master review (admin-master-review) where verify / reject live.

  DATA IS REAL: GET /admin/masters/list (all masters) -> avatar + name + status badge;
  the 3 filter counts are derived client-side from the fetched list. (The list is
  small; very large lists would need server-side filtering -> Zod.)

  STUB «—» (operator honest-skeleton В): the rich card fields — directions, Практик /
  Учеников, К выводу (payout), Опыт, Заявка (applied-at) — are NOT in the masters
  endpoint, so they render «—» until Zod extends it. The card structure is built so
  those values drop in when the endpoint grows. Roadmap: extend GET /admin/masters/list.
-->

<template>
  <div class="admin-list">
    <header class="admin-list__top">
      <VBackButton @click="router.back()" />
      <span class="admin-list__title">Мастера</span>
      <span class="admin-list__count">{{ headerCount }}</span>
    </header>

    <VSegment v-model="filter" :options="segOptions" />

    <!-- Batch-INVITE (№258): entry to the one-time invite link screen. -->
    <VButton variant="secondary" block @click="router.push({ name: 'admin-master-invite' })">
      Пригласить мастера
    </VButton>

    <!-- Loading -->
    <div v-if="loading" class="admin-list__loader"><VLoader size="lg" /></div>

    <!-- Fetch error -->
    <VEmptyState
      v-else-if="error"
      icon="warning"
      title="Не удалось загрузить мастеров"
      description="Проверьте соединение и попробуйте ещё раз"
    >
      <template #action><VButton variant="primary" @click="load">Повторить</VButton></template>
    </VEmptyState>

    <!-- List -->
    <div v-else-if="filtered.length" class="admin-list__items">
      <button v-for="m in filtered" :key="m.id" type="button" class="mcard" @click="openReview(m)">
        <div class="mcard__head">
          <VAvatar :name="nameOf(m)" :url="m.avatar_url ?? undefined" size="md" />
          <div class="mcard__id">
            <span class="mcard__name">{{ nameOf(m) }}</span>
            <VBadge :variant="masterStatusVariant(m.master_status)" class="mcard__badge">
              <component :is="badgeIcon(m.master_status)" :size="14" />
              {{ badgeLabel(m.master_status) }}
            </VBadge>
          </div>
        </div>

        <!-- Rich meta -> Zod (honest «—» until the endpoint carries it). -->
        <div class="mcard__meta">
          <p v-if="m.master_status === 'verified'" class="mcard__line">Практик: — • Учеников: —</p>
          <p v-else class="mcard__line">Опыт: —</p>
        </div>

        <div class="mcard__foot">
          <template v-if="m.master_status === 'verified'">
            <span class="mcard__foot-key">К выводу:</span>
            <span class="mcard__foot-val">—</span>
          </template>
          <span v-else class="mcard__foot-key">Заявка: —</span>
        </div>
      </button>
    </div>

    <!-- Empty (filter has no masters) -->
    <VCard v-else
      ><p class="admin-list__empty">{{ emptyText }}</p></VCard
    >
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Component } from 'vue'
import { useRouter } from 'vue-router'
import {
  VBackButton,
  VSegment,
  VAvatar,
  VBadge,
  VCard,
  VLoader,
  VEmptyState,
  VButton,
} from '@/components/ui'
import type { SegmentOption } from '@/components/ui/VSegment.vue'
import { IconCheck, IconPending, IconClose } from '@/components/icons'
import { getMastersList } from '@/api/admin'
import type { AdminMasterListItem } from '@/api/admin'
import { masterDisplayName, masterStatusVariant } from '@/utils/adminHelpers'
import { ApiResponseError } from '@/api/client'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()

const filter = ref('all')
const masters = ref<AdminMasterListItem[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref(false)

function nameOf(m: AdminMasterListItem): string {
  return masterDisplayName(m)
}

// Filter counts derived from the fetched list (list is small). «Все» uses the API
// total so the header stays correct even if a cap is hit.
const pendingCount = computed<number>(
  () => masters.value.filter((m) => m.master_status === 'pending').length,
)
const verifiedCount = computed<number>(
  () => masters.value.filter((m) => m.master_status === 'verified').length,
)

const headerCount = computed<string>(() => (total.value ? String(total.value) : '—'))

const segOptions = computed<SegmentOption[]>(() => [
  { value: 'all', label: 'Все', badge: total.value || undefined },
  { value: 'pending', label: 'На проверке', badge: pendingCount.value || undefined },
  { value: 'verified', label: 'Верифицированы', badge: verifiedCount.value || undefined },
])

const filtered = computed<AdminMasterListItem[]>(() => {
  if (filter.value === 'pending') return masters.value.filter((m) => m.master_status === 'pending')
  if (filter.value === 'verified')
    return masters.value.filter((m) => m.master_status === 'verified')
  return masters.value
})

const emptyText = computed<string>(() => {
  if (filter.value === 'pending') return 'Нет мастеров на проверке'
  if (filter.value === 'verified') return 'Нет верифицированных мастеров'
  return 'Мастеров пока нет'
})

// Status badge labels match the operator SVG (the shared helper uses shorter ones).
function badgeLabel(status: string): string {
  if (status === 'verified') return 'Верифицирован'
  if (status === 'pending') return 'Ожидает верификации'
  if (status === 'rejected') return 'Отклонён'
  return status
}

function badgeIcon(status: string): Component {
  if (status === 'verified') return IconCheck
  if (status === 'pending') return IconPending
  return IconClose
}

async function load(): Promise<void> {
  loading.value = true
  error.value = false
  try {
    // Fetch all masters once; filter + count client-side (the list is small).
    // Limit is clamped to the backend page cap (le=100 on /admin/masters/list);
    // 200 was 422-rejected. Alpha: 100 is enough — add pagination when the
    // master count approaches 100 (operator ruling, ПРОМТ №289).
    const res = await getMastersList(undefined, 100, 0)
    masters.value = res.items
    total.value = res.total
  } catch (e) {
    error.value = true
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки мастеров'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

function openReview(m: AdminMasterListItem): void {
  router.push({
    name: 'admin-master-review',
    params: { id: m.id },
    state: { master: JSON.parse(JSON.stringify(m)) },
  })
}

onMounted(load)
</script>

<style scoped>
.admin-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* -- Header: back + title + count badge -- */
.admin-list__top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: var(--velo-size-44);
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
  padding: 0 var(--velo-inset-12);
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

.admin-list__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

.admin-list__items {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.admin-list__empty {
  margin: 0;
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  padding: var(--space-4) var(--space-2);
}

/* -- Master card -- */
.mcard {
  width: 100%;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  text-align: left;
  cursor: pointer;
  font-family: var(--font-body);
  transition: opacity var(--transition-fast);
}

.mcard:active {
  opacity: 0.85;
}

.mcard__head {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.mcard__id {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  align-items: flex-start;
}

.mcard__name {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.mcard__badge :deep(svg) {
  flex-shrink: 0;
}

.mcard__meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.mcard__line {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: 0.02em;
}

.mcard__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  padding-top: var(--space-3);
  border-top: 1px solid var(--velo-border-light);
}

.mcard__foot-key,
.mcard__foot-val {
  font-size: var(--text-xs);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}
</style>
