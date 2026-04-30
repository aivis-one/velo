<!--
  VELO Frontend — EntriesCategoryView (S2-S3 SPEEDRUN MEGA-2 §C39)

  Combined Дневник + Сонник view with type-filter chip header.
  Uses useDiaryStore.filteredEntries (typeFilter aware).
-->

<template>
  <div class="cat">
    <header class="cat__header">
      <h1 class="cat__title">
        Дневник • Сонник
      </h1>
      <button
        type="button"
        class="cat__btn"
        aria-label="Сменить вид"
        @click="toggleLayout"
      >
        <IconDots :size="20" />
      </button>
    </header>

    <div class="cat__chips">
      <button
        v-for="opt in TYPE_OPTIONS"
        :key="opt.value"
        type="button"
        class="cat__chip"
        :class="{ 'cat__chip--active': diary.typeFilter === opt.value }"
        @click="diary.typeFilter = opt.value"
      >
        {{ opt.label }}
      </button>
    </div>

    <div
      v-if="loading"
      class="cat__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="grouped.length === 0"
      class="cat__empty"
    >
      Записей пока нет
    </div>
    <div
      v-else
      class="cat__body"
    >
      <section
        v-for="g in grouped"
        :key="g.iso"
      >
        <SpineDivider
          v-if="layout === 'timeline'"
          :date="g.label"
        />
        <h3
          v-else
          class="cat__date-head"
        >
          {{ g.label }}
        </h3>
        <div class="cat__items">
          <component
            :is="layout === 'timeline' ? DiaryEntryBubble : DiaryEntryFlat"
            v-for="row in g.items"
            :key="row.key"
            :kind="row.kind"
            :title="row.title"
            :preview="row.preview"
            @click="router.push(`/user/diary/entry/${row.id}`)"
          />
        </div>
      </section>
    </div>

    <DiaryComposer @expand="composerOpen = true" />

    <DiaryComposerExpanded
      v-if="composerOpen"
      @close="composerOpen = false"
      @saved="composerOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { IconDots } from '@/components/icons'
import SpineDivider from '@/components/shared/SpineDivider.vue'
import DiaryEntryBubble from '@/components/shared/DiaryEntryBubble.vue'
import DiaryEntryFlat from '@/components/shared/DiaryEntryFlat.vue'
import DiaryComposer from '@/components/shared/DiaryComposer.vue'
import DiaryComposerExpanded from '@/components/shared/DiaryComposerExpanded.vue'
import type { DiaryEntryResponse } from '@/api/types'

type Kind = 'journal' | 'dream' | 'insight'

interface Row {
  key: string
  id: string
  kind: Kind
  title: string
  preview: string
  created_at: string
}
interface Group {
  iso: string
  label: string
  items: Row[]
}

const TYPE_OPTIONS = [
  { value: 'all', label: 'Все' },
  { value: 'journal', label: 'Дневник' },
  { value: 'dream', label: 'Сонник' },
] as const

const LAYOUT_KEY = 'velo:diary-layout'
const layout = ref<'timeline' | 'list'>('timeline')
const loading = ref(false)
const composerOpen = ref(false)
const diary = useDiaryStore()
const toast = useToast()
const router = useRouter()

watch(layout, (v) => {
  try {
    localStorage.setItem(LAYOUT_KEY, v)
  } catch {
    /* ignore */
  }
})

function toggleLayout(): void {
  layout.value = layout.value === 'timeline' ? 'list' : 'timeline'
}

function entryKind(e: DiaryEntryResponse): Kind {
  const t = (e as DiaryEntryResponse & { type?: string }).type
  if (t === 'dream') return 'dream'
  if (t === 'insight') return 'insight'
  return 'journal'
}

const grouped = computed<Group[]>(() => {
  const rows: Row[] = (diary.filteredEntries as DiaryEntryResponse[]).map(
    (e) => ({
      key: `e-${e.id}`,
      id: e.id,
      kind: entryKind(e),
      title: e.title ?? 'Запись',
      preview: e.content ?? '',
      created_at: e.created_at,
    }),
  )
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
    out.push({ iso, label: humanDate(iso), items: map.get(iso)! })
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

onMounted(async () => {
  try {
    const stored = localStorage.getItem(LAYOUT_KEY)
    if (stored === 'list' || stored === 'timeline') layout.value = stored
  } catch {
    /* ignore */
  }
  loading.value = true
  try {
    await diary.fetchEntries()
  } catch {
    toast.error('Не удалось загрузить записи')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.cat {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-4) 0;
  min-height: 100%;
}
.cat__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.cat__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}
.cat__btn {
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
.cat__chips {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}
.cat__chip {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
}
.cat__chip--active {
  background: var(--steel-button);
  color: white;
  border-color: var(--steel-button);
}
.cat__loader,
.cat__empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}
.cat__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  flex: 1 1 auto;
}
.cat__date-head {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  margin: var(--space-2) 0;
  color: var(--text-primary);
  font-weight: 400;
}
.cat__items {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
