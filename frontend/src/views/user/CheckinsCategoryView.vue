<!--
  VELO Frontend — CheckinsCategoryView (S2-S3 SPEEDRUN MEGA-2 §C39)

  Category-filtered Diary route: only check-ins.
  Reuses SpineDivider + DiaryEntryBubble/Flat with shared layout key.
-->

<template>
  <div class="cat">
    <header class="cat__header">
      <h1 class="cat__title">
        Check-ins
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
      Check-ins пока нет
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
            kind="checkin"
            :title="row.title"
            :preview="row.preview"
          />
        </div>
      </section>
    </div>

    <DiaryComposer @expand="toast.info('Composer открыть из главного дневника')" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { IconDots } from '@/components/icons'
import SpineDivider from '@/components/shared/SpineDivider.vue'
import DiaryEntryBubble from '@/components/shared/DiaryEntryBubble.vue'
import DiaryEntryFlat from '@/components/shared/DiaryEntryFlat.vue'
import DiaryComposer from '@/components/shared/DiaryComposer.vue'
import type { CheckinResponse } from '@/api/types'

interface Row {
  key: string
  title: string
  preview: string
  created_at: string
}
interface Group {
  iso: string
  label: string
  items: Row[]
}

const LAYOUT_KEY = 'velo:diary-layout'
const layout = ref<'timeline' | 'list'>('timeline')
const loading = ref(false)
const diary = useDiaryStore()
const toast = useToast()

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

const grouped = computed<Group[]>(() => {
  const rows: Row[] = (diary.checkins as CheckinResponse[]).map((c) => ({
    key: `c-${c.id}`,
    title: 'Check-in',
    preview: c.comment ?? `Настроение: ${c.mood}`,
    created_at: c.created_at,
  }))
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
    await diary.fetchCheckins()
  } catch {
    toast.error('Не удалось загрузить check-ins')
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
