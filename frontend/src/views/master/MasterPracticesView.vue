<!--
  VELO Frontend -- MasterPracticesView (Phase F6.2)

  Master's own practice list. Protected by masterStatusGuard.
  Rendered inside MasterShell (with tab bar).

  Tabs:
    - "Предстоящие" -- draft + scheduled + live (sorted asc by scheduled_at)
    - "Прошедшие"   -- completed + cancelled    (sorted desc by scheduled_at)

  Data source: masterStore.practices (populated by fetchMyPractices).
  Lazy-load on mount; force-refresh after returning from create/edit.

  Each card:
    - Type emoji, title, date/time, duration
    - Participants count + price
    - Status badge
    - "Явка" button (completed only) -> master-attendance

  "+" header button -> master-practice-new
  Tap card -> master-practice-edit
-->

<template>
  <div class="master-practices">
    <!-- Header -->
    <VHeader title="Практики" :badge="masterStore.practicesTotal || undefined">
      <template #action>
        <button class="master-practices__add-btn" aria-label="Создать практику" @click="router.push({ name: 'master-practice-new' })">
          +
        </button>
      </template>
    </VHeader>

    <!-- Tabs -->
    <div class="master-practices__tabs">
      <VSegment
        :model-value="activeTab"
        :options="tabOptions"
        @update:model-value="activeTab = $event as 'upcoming' | 'past'"
      />
    </div>

    <!-- Loading -->
    <div v-if="masterStore.practicesLoading && masterStore.practices.length === 0" class="master-practices__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error -->
    <div v-else-if="masterStore.practicesError" class="master-practices__content">
      <VEmptyState
        icon="warning"
        title="Не удалось загрузить практики"
        :description="masterStore.practicesError"
      >
        <VButton size="sm" variant="outline" @click="masterStore.refreshMyPractices()">
          Повторить
        </VButton>
      </VEmptyState>
    </div>

    <!-- List -->
    <div v-else class="master-practices__content">
      <!-- Upcoming tab -->
      <template v-if="activeTab === 'upcoming'">
        <template v-if="upcomingPractices.length > 0">
          <div
            v-for="practice in upcomingPractices"
            :key="practice.id"
            class="master-practices__card"
            @click="router.push({ name: 'master-practice-edit', params: { id: practice.id } })"
          >
            <PracticeListCard
              :practice="practice"
              :clickable="false"
              :when="formatShortDate(practice.scheduled_at, practice.timezone)"
              :duration="formatDuration(practice.duration_minutes)"
            >
              <template #subtitle>
                <span class="master-practices__details">
                  <span><IconGroup :size="14" :style="{ verticalAlign: 'middle' }" /> {{ formatParticipants(practice.current_participants, practice.max_participants) }}</span>
                  <span>{{ formatMoney(practice.price_cents, practice.currency) }}</span>
                </span>
              </template>
              <template v-if="masterPracticeBadge(practice.status)" #badge>
                <VBadge :variant="masterPracticeBadge(practice.status)!.variant">{{ masterPracticeBadge(practice.status)!.label }}</VBadge>
              </template>
            </PracticeListCard>
          </div>
        </template>
        <VEmptyState
          v-else
          icon="calendar"
          title="Нет предстоящих практик"
          description="Создайте первую практику"
        >
          <VButton
            size="sm"
            variant="outline"
            @click="router.push({ name: 'master-practice-new' })"
          >
            Создать
          </VButton>
        </VEmptyState>
      </template>

      <!-- Past tab -->
      <template v-else>
        <template v-if="pastPractices.length > 0">
          <div
            v-for="practice in pastPractices"
            :key="practice.id"
            class="master-practices__card"
            @click="router.push({ name: 'master-practice-edit', params: { id: practice.id } })"
          >
            <PracticeListCard
              :practice="practice"
              :clickable="false"
              :when="formatShortDate(practice.scheduled_at, practice.timezone)"
              :duration="formatDuration(practice.duration_minutes)"
            >
              <template #subtitle>
                <span class="master-practices__details">
                  <span><IconGroup :size="14" :style="{ verticalAlign: 'middle' }" /> {{ formatParticipants(practice.current_participants, practice.max_participants) }}</span>
                  <span>{{ formatMoney(practice.price_cents, practice.currency) }}</span>
                </span>
              </template>
              <template v-if="masterPracticeBadge(practice.status)" #badge>
                <VBadge :variant="masterPracticeBadge(practice.status)!.variant">{{ masterPracticeBadge(practice.status)!.label }}</VBadge>
              </template>
              <!-- Attendance button for completed practices -->
              <template v-if="practice.status === 'completed'" #action>
                <VButton
                  size="sm"
                  variant="outline"
                  @click.stop="router.push({ name: 'master-attendance', params: { id: practice.id } })"
                >
                  Явка
                </VButton>
              </template>
            </PracticeListCard>
          </div>
        </template>
        <VEmptyState
          v-else
          icon="list"
          title="Нет прошедших практик"
          description="Здесь появятся завершённые и отменённые практики"
        />
      </template>

      <!-- Load more -->
      <div v-if="masterStore.practicesHasMore" class="master-practices__load-more">
        <VButton
          variant="ghost"
          block
          :loading="masterStore.practicesLoading"
          @click="masterStore.loadMorePractices()"
        >
          Показать ещё
        </VButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton, VLoader, VEmptyState, VSegment, VBadge } from '@/components/ui'
import { IconGroup } from '@/components/icons'
import { useMasterStore } from '@/stores/master'
import PracticeListCard from '@/components/shared/PracticeListCard.vue'
import { formatShortDate, formatDuration, formatMoney, formatParticipants } from '@/utils/format'
import { masterPracticeBadge } from '@/utils/practiceStatus'
import type { PracticeResponse } from '@/api/types'

const router = useRouter()
const masterStore = useMasterStore()

const activeTab = ref<'upcoming' | 'past'>('upcoming')

// -- Upcoming: draft + scheduled + live, sorted ascending --
const upcomingPractices = computed((): PracticeResponse[] =>
  masterStore.practices
    .filter((p) => p.status === 'draft' || p.status === 'scheduled' || p.status === 'live')
    .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime()),
)

// -- Past: completed + cancelled, sorted descending (newest first) --
const pastPractices = computed((): PracticeResponse[] =>
  masterStore.practices
    .filter((p) => p.status === 'completed' || p.status === 'cancelled')
    .sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime()),
)

const tabOptions = computed(() => [
  { value: 'upcoming', label: 'Предстоящие', badge: upcomingPractices.value.length || undefined },
  { value: 'past', label: 'Прошедшие', badge: pastPractices.value.length || undefined },
])

// Status badge → shared masterPracticeBadge (only draft/completed/cancelled get
// a badge; scheduled/live/deleted → null = no badge).

onMounted(async () => {
  await masterStore.fetchMyPractices()
})
</script>

<style scoped>
.master-practices {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

/* -- "+" add button in header -- */
.master-practices__add-btn {
  width: 32px;
  height: 32px;
  font-size: 22px;
  font-weight: 400;
  color: var(--velo-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-xl);
  background: var(--velo-glass-blue-15);
  transition: opacity var(--transition-fast);
}

.master-practices__add-btn:hover {
  opacity: 0.9;
}

/* -- Tabs -- */
.master-practices__tabs {
  /* F-5 rail sync: ride MobileLayout's 24px rail (no local h-padding). */
  padding: var(--space-3) 0;
  background: transparent;
}

/* (tab buttons + count badge now provided by <VSegment>) */

/* -- Content -- */
.master-practices__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-12) 0;
}

.master-practices__content {
  flex: 1;
  /* F-5 rail sync: ride MobileLayout's 24px rail (no local h-padding). */
  padding: var(--space-3) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.master-practices__card {
  cursor: pointer;
}

/* Subtitle override for master's own practice: participants · price */
.master-practices__details {
  display: flex;
  gap: var(--space-3);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

.master-practices__load-more {
  padding-top: var(--space-2);
}
</style>
