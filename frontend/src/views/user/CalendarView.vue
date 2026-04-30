<!--
  VELO Frontend -- CalendarView (S2 P07 C23 — refresh per skin 21)

  Week strip + day-grouped practice list. Filter overlay (C24) opens via
  "Выбрать практики" pill button.

  Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="cal">
    <header class="cal__header">
      <h1 class="cal__title">
        Календарь
      </h1>
    </header>

    <WeekStrip
      v-model:selected-iso="selectedIso"
      :practice-days="practiceDays"
    />

    <button
      type="button"
      class="cal__filter-cta"
      @click="filterOpen = true"
    >
      <span>Выбрать практики</span>
      <IconFilter :size="20" />
    </button>

    <div
      v-if="loading"
      class="cal__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="grouped.length === 0"
      class="cal__empty"
    >
      На выбранную дату практик нет
    </div>
    <div
      v-else
      class="cal__list"
    >
      <section
        v-for="g in grouped"
        :key="g.iso"
        class="cal__group"
      >
        <h3 class="cal__group-head">
          {{ g.label }}
        </h3>
        <div class="cal__group-cards">
          <RouterLink
            v-for="p in g.practices"
            :key="p.id"
            :to="`/user/practices/${p.id}`"
            class="cal__card"
          >
            <component
              :is="iconFor(p.practice_type)"
              class="cal__card-icon"
              :size="28"
            />
            <div class="cal__card-body">
              <h4>{{ p.title }}</h4>
              <p>с {{ p.master_name ?? 'Мастером' }}</p>
              <p>{{ formatTime(p.scheduled_at, p.timezone) }} · {{ formatDuration(p.duration_minutes) }}</p>
            </div>
          </RouterLink>
        </div>
      </section>
    </div>

    <CalendarFilterOverlay
      v-if="filterOpen"
      :initial="filters"
      @close="filterOpen = false"
      @apply="applyFilters"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { IconFilter } from '@/components/icons'
import WeekStrip from '@/components/shared/WeekStrip.vue'
import CalendarFilterOverlay from '@/components/shared/CalendarFilterOverlay.vue'
import { PRACTICE_TYPE_ICON } from '@/utils/displayHelpers'
import { formatTime, formatDuration } from '@/utils/format'
import { getPractices } from '@/api/practices'
import type { PracticeFilters, PracticeResponse } from '@/api/types'

interface Group {
  iso: string
  label: string
  practices: PracticeResponse[]
}

function todayIso(): string {
  const d = new Date()
  d.setHours(0, 0, 0, 0)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const selectedIso = ref(todayIso())
const filterOpen = ref(false)
const filters = ref<PracticeFilters>({})
const loading = ref(false)
const practices = ref<PracticeResponse[]>([])

const practiceDays = computed<Set<string>>(() => {
  const s = new Set<string>()
  for (const p of practices.value) {
    s.add(p.scheduled_at.slice(0, 10))
  }
  return s
})

const grouped = computed<Group[]>(() => {
  const today = todayIso()
  const tomorrow = (() => {
    const d = new Date(today)
    d.setDate(d.getDate() + 1)
    return d.toISOString().slice(0, 10)
  })()
  const map = new Map<string, PracticeResponse[]>()
  for (const p of practices.value) {
    const iso = p.scheduled_at.slice(0, 10)
    if (!map.has(iso)) map.set(iso, [])
    map.get(iso)!.push(p)
  }
  const out: Group[] = []
  for (const iso of Array.from(map.keys()).sort()) {
    const list = map.get(iso)!.slice().sort(
      (a, b) =>
        new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime(),
    )
    let label = iso
    if (iso === today) label = 'Сегодня'
    else if (iso === tomorrow) label = 'Завтра'
    else
      label = new Date(iso).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
      })
    out.push({ iso, label, practices: list })
  }
  return out
})

function iconFor(type: string) {
  return PRACTICE_TYPE_ICON[type] ?? PRACTICE_TYPE_ICON.live
}

function startOfWeek(iso: string): string {
  const d = new Date(iso)
  const dow = d.getDay()
  const diff = (dow + 6) % 7
  d.setDate(d.getDate() - diff)
  return d.toISOString().slice(0, 10)
}

function endOfWeek(iso: string): string {
  const d = new Date(startOfWeek(iso))
  d.setDate(d.getDate() + 6)
  return d.toISOString().slice(0, 10)
}

async function reload(): Promise<void> {
  loading.value = true
  try {
    const start = startOfWeek(selectedIso.value)
    const end = endOfWeek(selectedIso.value)
    const data = await getPractices(
      {
        ...filters.value,
        date_from: `${start}T00:00:00Z`,
        date_to: `${end}T23:59:59Z`,
      },
      50,
      0,
    )
    practices.value = data.items
  } catch {
    practices.value = []
  } finally {
    loading.value = false
  }
}

function applyFilters(next: PracticeFilters): void {
  filters.value = next
  filterOpen.value = false
  reload()
}

onMounted(() => {
  reload()
})

watch(selectedIso, () => {
  reload()
})
</script>

<style scoped>
.cal {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.cal__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.cal__filter-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: var(--steel-button);
  color: white;
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-base);
}

.cal__loader,
.cal__empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
  font-family: var(--font-body);
}

.cal__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.cal__group-head {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0 0 var(--space-2);
  font-weight: 400;
  color: var(--text-primary);
}

.cal__group-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.cal__card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--text-primary);
}

.cal__card:hover {
  background: var(--surface-default);
}

.cal__card-icon {
  flex-shrink: 0;
  color: var(--text-primary);
}

.cal__card-body h4 {
  font-family: var(--font-body);
  font-size: var(--text-base);
  margin: 0 0 2px;
  font-weight: 400;
}

.cal__card-body p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}
</style>
