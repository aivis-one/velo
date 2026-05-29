<!--
  VELO Frontend -- DiarySearchModal (Diary redesign, Batch 3; screen 44)

  Text search over the unified diary feed, opened from the "..." menu.
  Field + magnifier; below it a "Недавно вы искали" list of recent queries.

  On submit (Enter or the magnifier button) emits `search` with the trimmed
  query and records it in recents. An empty submit clears the search (the
  parent maps that to runFeedSearch('')). Tapping a recent runs it immediately.

  Recent queries persist in localStorage (this is the production app, not a
  Claude artifact -- localStorage is available here). Capped at MAX_RECENTS,
  most-recent-first, de-duplicated case-insensitively.

  Usage:
    <DiarySearchModal
      :open="showSearch"
      :initial="feedFilters.search ?? ''"
      @search="onApplySearch"
      @close="showSearch = false"
    />
-->

<template>
  <VModal :open="open" @close="$emit('close')">
    <div class="diary-search">
      <div class="diary-search__header">
        <span class="diary-search__header-icon" aria-hidden="true">
          <svg viewBox="0 0 20 20" fill="none">
            <circle cx="9" cy="9" r="5.5" stroke="currentColor" stroke-width="1.8" />
            <path
              d="M17 17l-4-4"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            />
          </svg>
        </span>
        <h2 class="diary-search__heading">Поиск</h2>
      </div>

      <!-- Search field + magnifier -->
      <div class="diary-search__field">
        <div class="diary-search__input">
          <VInput
            v-model="query"
            placeholder="Искать..."
            @keydown.enter="submit(query)"
          />
        </div>
        <button
          type="button"
          class="diary-search__go"
          aria-label="Искать"
          @click="submit(query)"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle
              cx="11" cy="11" r="7"
              stroke="currentColor" stroke-width="2"
            />
            <path
              d="M20 20l-3.5-3.5"
              stroke="currentColor" stroke-width="2" stroke-linecap="round"
            />
          </svg>
        </button>
      </div>

      <!-- Recent searches -->
      <section v-if="recents.length" class="diary-search__recent">
        <h3 class="diary-search__recent-label">Недавно вы искали:</h3>
        <button
          v-for="term in recents"
          :key="term"
          type="button"
          class="diary-search__recent-item"
          @click="submit(term)"
        >
          <span class="diary-search__recent-text">{{ term }}</span>
          <svg
            class="diary-search__recent-arrow"
            width="16" height="16" viewBox="0 0 24 24" fill="none"
          >
            <path
              d="M7 17L17 7M17 7H9M17 7v8"
              stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round"
            />
          </svg>
        </button>
      </section>
    </div>
  </VModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { VModal, VInput } from '@/components/ui'

const props = defineProps<{
  open: boolean
  initial?: string
}>()

const emit = defineEmits<{
  search: [query: string]
  close: []
}>()

const RECENTS_KEY = 'velo:diary:recent-searches'
const MAX_RECENTS = 6

const query = ref('')
const recents = ref<string[]>([])

function loadRecents(): void {
  try {
    const raw = localStorage.getItem(RECENTS_KEY)
    const parsed: unknown = raw ? JSON.parse(raw) : []
    recents.value = Array.isArray(parsed)
      ? parsed.filter((x): x is string => typeof x === 'string')
      : []
  } catch {
    // Corrupt / unavailable storage -- start empty, never throw.
    recents.value = []
  }
}

function saveRecents(): void {
  try {
    localStorage.setItem(RECENTS_KEY, JSON.stringify(recents.value))
  } catch {
    // Storage full / unavailable -- recents are best-effort, ignore.
  }
}

function recordRecent(term: string): void {
  const t = term.trim()
  if (!t) return
  // Case-insensitive de-dup, most-recent-first, capped.
  const lower = t.toLowerCase()
  const next = [t, ...recents.value.filter((r) => r.toLowerCase() !== lower)]
  recents.value = next.slice(0, MAX_RECENTS)
  saveRecents()
}

// Sync the field from the active search whenever the modal opens.
watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) return
    query.value = props.initial ?? ''
    loadRecents()
  },
  { immediate: true },
)

function submit(term: string): void {
  const trimmed = term.trim()
  query.value = trimmed
  if (trimmed) recordRecent(trimmed)
  // Empty submit clears the search (parent maps to runFeedSearch('')).
  emit('search', trimmed)
  emit('close')
}
</script>

<style scoped>
.diary-search {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.diary-search__header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.diary-search__header-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--velo-primary);
  color: #ffffff;
}

.diary-search__header-icon svg {
  width: 18px;
  height: 18px;
}

.diary-search__heading {
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0;
}

/* -- Field + magnifier -- */
.diary-search__field {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

/* VInput grows; the button keeps its size. */
.diary-search__input {
  flex: 1;
  min-width: 0;
}

.diary-search__go {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: var(--radius-full);
  background: var(--velo-primary);
  color: #ffffff;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.diary-search__go:hover {
  opacity: 0.9;
}

/* -- Recent searches -- */
.diary-search__recent {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.diary-search__recent-label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin: 0;
}

.diary-search__recent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border: 1px solid #ffffff;
  background: var(--velo-glass-blue-15);
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
  text-align: left;
}

.diary-search__recent-item:hover {
  opacity: 0.85;
}

.diary-search__recent-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diary-search__recent-arrow {
  flex-shrink: 0;
  color: var(--velo-text-secondary);
}
</style>
