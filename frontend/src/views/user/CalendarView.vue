<!--
  VELO Frontend -- CalendarView (Phase F3.1)

  Full practice catalog with:
    - Filter chips: practice type (all, live, series, one_on_one, replay)
    - Practices grouped by date sections ("Сегодня", "Завтра", "28 февраля")
    - "Load more" button (usePagination via store)

  Data shared with Dashboard via usePracticesStore.
  Changing filter chips calls store.applyFilters() which triggers
  auto-refresh (watcher on filters reactive object).
-->

<template>
  <div class="calendar">
    <!-- Filter chips -->
    <div class="calendar__filters">
      <button
        v-for="chip in typeChips"
        :key="chip.value"
        class="calendar__chip"
        :class="{ 'calendar__chip--active': activeType === chip.value }"
        @click="onTypeFilter(chip.value)"
      >
        {{ chip.label }}
      </button>
    </div>

    <!-- Loading (initial) -->
    <div v-if="store.loading && store.practices.length === 0" class="calendar__loader">
      <VLoader />
    </div>

    <!-- Error -->
    <VEmptyState
      v-else-if="store.error && store.practices.length === 0"
      icon="⚠️"
      title="Не удалось загрузить"
      :description="store.error"
    >
      <VButton size="sm" @click="store.refreshPractices()">Повторить</VButton>
    </VEmptyState>

    <!-- Empty -->
    <VEmptyState
      v-else-if="!store.loading && store.practices.length === 0"
      icon="📅"
      title="Нет практик"
      description="Попробуйте другие фильтры или загляните позже"
    />

    <!-- Grouped practices -->
    <div v-else class="calendar__list">
      <template v-for="(group, idx) in groupedPractices" :key="idx">
        <h3 class="calendar__date-header">{{ group.label }}</h3>
        <PracticeCard
          v-for="practice in group.items"
          :key="practice.id"
          :practice="practice"
          @click="goToDetail"
        />
      </template>

      <!-- Load more -->
      <div v-if="store.hasMore" class="calendar__load-more">
        <VButton
          variant="secondary"
          :loading="store.loading"
          block
          @click="store.loadMore()"
        >
          Показать ещё
        </VButton>
      </div>

      <!-- Inline loading indicator when fetching next page -->
      <div v-if="store.loading && store.practices.length > 0" class="calendar__loader">
        <VLoader size="sm" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePracticesStore } from '@/stores/practices'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import PracticeCard from '@/components/shared/PracticeCard.vue'
import { formatDateShort } from '@/utils/format'
import type { PracticeResponse, PracticeType } from '@/api/types'

const router = useRouter()
const store = usePracticesStore()

// -- Filter chip config --
interface TypeChip {
  value: PracticeType | 'all'
  label: string
}

const typeChips: TypeChip[] = [
  { value: 'all', label: 'Все' },
  { value: 'live', label: '🧘 Live' },
  { value: 'series', label: '🔄 Серии' },
  { value: 'one_on_one', label: '👤 Личные' },
  { value: 'replay', label: '📹 Записи' },
]

const activeType = computed<PracticeType | 'all'>(
  () => store.filters.practice_type ?? 'all',
)

function onTypeFilter(value: PracticeType | 'all'): void {
  store.applyFilters({
    practice_type: value === 'all' ? undefined : value,
  })
}

// -- Group practices by date --
interface DateGroup {
  label: string
  dateKey: string
  items: PracticeResponse[]
}

/**
 * Extract YYYY-MM-DD string in the practice's timezone for grouping.
 */
function dateKey(practice: PracticeResponse): string {
  const date = new Date(practice.scheduled_at)
  return new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: practice.timezone,
  }).format(date)
}

const groupedPractices = computed<DateGroup[]>(() => {
  const map = new Map<string, DateGroup>()

  for (const p of store.practices) {
    const key = dateKey(p)
    if (!map.has(key)) {
      map.set(key, {
        label: formatDateShort(p.scheduled_at, p.timezone),
        dateKey: key,
        items: [],
      })
    }
    map.get(key)!.items.push(p)
  }

  return Array.from(map.values())
})

function goToDetail(id: string): void {
  router.push({ name: 'practice-detail', params: { id } })
}

onMounted(() => {
  store.fetchPractices()
})
</script>

<style scoped>
.calendar__filters {
  display: flex;
  gap: var(--space-2);
  overflow-x: auto;
  padding-bottom: var(--space-3);
  margin-bottom: var(--space-4);
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.calendar__filters::-webkit-scrollbar {
  display: none;
}

.calendar__chip {
  padding: var(--space-2) var(--space-4);
  border: 1px solid #ffffff;
  background: var(--velo-glass-blue-15);
  border-radius: 100px;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  flex-shrink: 0;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.calendar__chip:hover {
  opacity: 0.8;
}

.calendar__chip--active {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: white;
}

.calendar__date-header {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: var(--space-4) 0 var(--space-3);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.calendar__date-header:first-child {
  margin-top: 0;
}

.calendar__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.calendar__load-more {
  margin-top: var(--space-4);
}

.calendar__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}
</style>
