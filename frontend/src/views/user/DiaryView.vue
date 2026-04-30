<!--
  VELO Frontend — DiaryView (S2-S3 SPEEDRUN MEGA-2 §C36 — refresh)

  Root diary tab. Mixed entries (check-ins / feedbacks / journal / dream)
  rendered in chronological order with two layout modes:
    - timeline: SpineDivider date headers + DiaryEntryBubble cards
    - list:     date sub-headers + DiaryEntryFlat cards

  Layout state persisted in localStorage 'velo:diary-layout'.

  ••• menu opens layout toggle, filter overlay (C37), search overlay (C38).
  Composer pill at bottom — tap → expand modal (C40).

  Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="diary">
    <header class="diary__header">
      <h1 class="diary__title">
        Дневник
      </h1>
      <button
        type="button"
        class="diary__menu-btn"
        aria-label="Меню"
        @click="menuOpen = !menuOpen"
      >
        <IconDots :size="22" />
      </button>
      <div
        v-if="menuOpen"
        class="diary__menu"
        @click.self="menuOpen = false"
      >
        <button
          type="button"
          class="diary__menu-item"
          @click="openFilter"
        >
          <IconFilter :size="18" />
          <span>Фильтр</span>
        </button>
        <button
          type="button"
          class="diary__menu-item"
          @click="openSearch"
        >
          <IconSearch :size="18" />
          <span>Поиск</span>
        </button>
        <button
          type="button"
          class="diary__menu-item"
          @click="toggleLayout"
        >
          <IconDots :size="18" />
          <span>Вид: {{ layout === 'timeline' ? 'timeline' : 'list' }}</span>
        </button>
      </div>
    </header>

    <div
      v-if="loading"
      class="diary__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="grouped.length === 0"
      class="diary__empty"
    >
      Пока нет записей
    </div>
    <div
      v-else
      class="diary__body"
    >
      <section
        v-for="g in grouped"
        :key="g.iso"
        class="diary__group"
      >
        <SpineDivider
          v-if="layout === 'timeline'"
          :date="g.label"
        />
        <h3
          v-else
          class="diary__date-head"
        >
          {{ g.label }}
        </h3>
        <div class="diary__items">
          <component
            :is="layout === 'timeline' ? DiaryEntryBubble : DiaryEntryFlat"
            v-for="row in g.items"
            :key="row.key"
            :kind="row.kind"
            :title="row.title"
            :preview="row.preview"
            @click="openItem(row)"
          />
        </div>
      </section>
    </div>

    <DiaryComposer @expand="composerOpen = true" />

    <DiaryFilterOverlay
      v-if="filterOpen"
      @close="filterOpen = false"
    />

    <DiarySearchOverlay
      v-if="searchOpen"
      @close="searchOpen = false"
    />

    <DiaryComposerExpanded
      v-if="composerOpen"
      @close="composerOpen = false"
      @saved="onSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { IconDots, IconFilter, IconSearch } from '@/components/icons'
import SpineDivider from '@/components/shared/SpineDivider.vue'
import DiaryEntryBubble from '@/components/shared/DiaryEntryBubble.vue'
import DiaryEntryFlat from '@/components/shared/DiaryEntryFlat.vue'
import DiaryComposer from '@/components/shared/DiaryComposer.vue'
import DiaryFilterOverlay from '@/components/shared/DiaryFilterOverlay.vue'
import DiarySearchOverlay from '@/components/shared/DiarySearchOverlay.vue'
import DiaryComposerExpanded from '@/components/shared/DiaryComposerExpanded.vue'
import type {
  CheckinResponse,
  FeedbackResponse,
  DiaryEntryResponse,
} from '@/api/types'

type Kind = 'checkin' | 'feedback' | 'journal' | 'dream' | 'insight'

interface Row {
  key: string
  kind: Kind
  title: string
  preview: string
  created_at: string
  ref:
    | { type: 'checkin'; data: CheckinResponse }
    | { type: 'feedback'; data: FeedbackResponse }
    | { type: 'entry'; data: DiaryEntryResponse }
}

interface Group {
  iso: string
  label: string
  items: Row[]
}

const diaryStore = useDiaryStore()
const toast = useToast()
const router = useRouter()

const LAYOUT_KEY = 'velo:diary-layout'
const layout = ref<'timeline' | 'list'>('timeline')
const menuOpen = ref(false)
const filterOpen = ref(false)
const searchOpen = ref(false)
const composerOpen = ref(false)
const loading = ref(false)

watch(layout, (v) => {
  try {
    localStorage.setItem(LAYOUT_KEY, v)
  } catch {
    /* ignore */
  }
})

function toggleLayout(): void {
  layout.value = layout.value === 'timeline' ? 'list' : 'timeline'
  menuOpen.value = false
}

function openFilter(): void {
  menuOpen.value = false
  filterOpen.value = true
}

function openSearch(): void {
  menuOpen.value = false
  searchOpen.value = true
}

function entryKind(e: DiaryEntryResponse): Kind {
  const t = (e as DiaryEntryResponse & { type?: string }).type
  if (t === 'dream') return 'dream'
  if (t === 'insight') return 'insight'
  return 'journal'
}

const grouped = computed<Group[]>(() => {
  const rows: Row[] = []

  for (const c of diaryStore.checkins as CheckinResponse[]) {
    rows.push({
      key: `c-${c.id}`,
      kind: 'checkin',
      title: 'Check-in',
      preview: c.comment ?? `Настроение: ${c.mood}`,
      created_at: c.created_at,
      ref: { type: 'checkin', data: c },
    })
  }
  for (const f of diaryStore.feedbacks as FeedbackResponse[]) {
    rows.push({
      key: `f-${f.id}`,
      kind: 'feedback',
      title: 'Feedback',
      preview: f.comment ?? `Оценка: ${f.rating}`,
      created_at: f.created_at,
      ref: { type: 'feedback', data: f },
    })
  }
  for (const e of diaryStore.filteredEntries as DiaryEntryResponse[]) {
    rows.push({
      key: `e-${e.id}`,
      kind: entryKind(e),
      title: e.title ?? 'Запись',
      preview: e.content ?? '',
      created_at: e.created_at,
      ref: { type: 'entry', data: e },
    })
  }

  rows.sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )

  const map = new Map<string, Row[]>()
  for (const r of rows) {
    const iso = r.created_at.slice(0, 10)
    if (!map.has(iso)) map.set(iso, [])
    map.get(iso)!.push(r)
  }

  const out: Group[] = []
  for (const iso of Array.from(map.keys()).sort().reverse()) {
    out.push({
      iso,
      label: humanDate(iso),
      items: map.get(iso)!,
    })
  }
  return out
})

function humanDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
    })
  } catch {
    return iso
  }
}

function openItem(row: Row): void {
  if (row.ref.type === 'entry') {
    router.push(`/user/diary/entry/${row.ref.data.id}`)
  } else {
    // Checkins + feedbacks reuse entry detail layout via id-prefixed routing.
    // For v1 we keep them in-page (no detail nav); a stub toast is gentler than
    // a 404. Detail views for check-ins / feedbacks are out of MEGA-2 scope.
    toast.info('Откройте практику, чтобы увидеть подробности')
  }
}

function onSaved(): void {
  composerOpen.value = false
  toast.success('Запись сохранена')
}

onMounted(async () => {
  try {
    const stored = localStorage.getItem(LAYOUT_KEY)
    if (stored === 'list' || stored === 'timeline') {
      layout.value = stored
    }
  } catch {
    /* ignore */
  }
  loading.value = true
  try {
    await Promise.all([
      diaryStore.fetchEntries(),
      diaryStore.fetchCheckins(),
      diaryStore.fetchFeedbacks(),
    ])
  } catch {
    toast.error('Не удалось загрузить дневник')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.diary {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-4) 0;
  min-height: 100%;
  position: relative;
}

.diary__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.diary__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  margin: 0;
  color: var(--text-primary);
}

.diary__menu-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.diary__menu {
  position: absolute;
  top: 48px;
  right: 0;
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-2);
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 200px;
  z-index: 20;
}

.diary__menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: transparent;
  border: 0;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  text-align: left;
}

.diary__menu-item:hover {
  background: var(--surface-steel-alpha-15);
}

.diary__loader,
.diary__empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.diary__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  flex: 1 1 auto;
}

.diary__date-head {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  margin: var(--space-2) 0;
  color: var(--text-primary);
  font-weight: 400;
}

.diary__items {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
