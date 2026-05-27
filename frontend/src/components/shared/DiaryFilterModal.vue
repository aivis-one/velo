<!--
  VELO Frontend -- DiaryFilterModal (Diary redesign, Batch 2a; screen 42)

  Category filter for the unified diary feed, opened from the "..." menu.
  Chips map 1:1 onto DiaryFeedCategory (backend `category` query values):
    Все       -> no categories (empty array)
    Дневник   -> entries
    Сонник    -> dreams
    Feedbacks -> feedbacks
    Check-ins -> checkins
    Практики  -> practices

  "Все" is mutually exclusive with the others: tapping it clears the
  selection; tapping any category clears "Все" and toggles that category
  (multi-select). An empty selection IS "Все".

  Date-range filtering (screen 43) is a separate piece (Batch 2b) and is not
  part of this modal yet.

  Works on a local DRAFT; nothing is applied until "Применить" (-> emits
  `apply` with the category array). "Сбросить" clears to "Все".

  Usage:
    <DiaryFilterModal
      :open="showFilter"
      :categories="feedFilters.categories ?? []"
      @apply="onApplyFilter"
      @close="showFilter = false"
    />
-->

<template>
  <VModal :open="open" @close="$emit('close')">
    <div class="diary-filter">
      <h2 class="diary-filter__heading">Фильтр</h2>

      <section class="diary-filter__group">
        <div class="diary-filter__chips">
          <!-- "Все" -- active when nothing else is selected. -->
          <button
            type="button"
            class="diary-filter__chip"
            :class="{ 'diary-filter__chip--on': draft.length === 0 }"
            @click="selectAll"
          >
            Все
          </button>
          <button
            v-for="opt in CATEGORY_CHIPS"
            :key="opt.value"
            type="button"
            class="diary-filter__chip"
            :class="{ 'diary-filter__chip--on': draft.includes(opt.value) }"
            @click="toggle(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </section>

      <div class="diary-filter__actions">
        <VButton variant="secondary" block @click="onReset">Сбросить</VButton>
        <VButton variant="primary" block @click="onApply">Применить</VButton>
      </div>
    </div>
  </VModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { VModal, VButton } from '@/components/ui'
import type { DiaryFeedCategory } from '@/api/types'

const props = defineProps<{
  open: boolean
  categories: DiaryFeedCategory[]
}>()

const emit = defineEmits<{
  apply: [categories: DiaryFeedCategory[]]
  close: []
}>()

// Chip option list (label + value). Labels match the design (screen 42);
// "Все" is rendered separately above (it is the empty selection).
const CATEGORY_CHIPS: { value: DiaryFeedCategory; label: string }[] = [
  { value: 'entries', label: 'Дневник' },
  { value: 'dreams', label: 'Сонник' },
  { value: 'feedbacks', label: 'Feedbacks' },
  { value: 'checkins', label: 'Check-ins' },
  { value: 'practices', label: 'Практики' },
]

// Local draft -- the working copy until "Применить".
const draft = ref<DiaryFeedCategory[]>([])

/** Sync the draft from incoming categories whenever the modal opens. */
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) draft.value = [...props.categories]
  },
  { immediate: true },
)

function selectAll(): void {
  // "Все" == empty selection.
  draft.value = []
}

function toggle(value: DiaryFeedCategory): void {
  const idx = draft.value.indexOf(value)
  if (idx === -1) draft.value = [...draft.value, value]
  else draft.value = draft.value.filter((c) => c !== value)
}

function onApply(): void {
  emit('apply', [...draft.value])
  emit('close')
}

function onReset(): void {
  draft.value = []
}
</script>

<style scoped>
.diary-filter {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.diary-filter__heading {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0;
}

.diary-filter__group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.diary-filter__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.diary-filter__chip {
  padding: var(--space-2) var(--space-4);
  border: 1px solid #ffffff;
  background: var(--velo-glass-blue-15);
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.diary-filter__chip:hover {
  opacity: 0.85;
}

.diary-filter__chip--on {
  background: var(--velo-primary);
  border-color: var(--velo-primary);
  color: #ffffff;
}

.diary-filter__actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-2);
}
</style>
