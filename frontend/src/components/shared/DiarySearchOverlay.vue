<!--
  VELO Frontend — DiarySearchOverlay (S2-S3 SPEEDRUN MEGA-2 §C38)

  Search modal: input + IconSearch action + history pills.
  Per BACKEND-COORDINATION § A.3 mock — search runs client-side over
  already-loaded entries via useDiaryStore.filteredEntries (driven by
  searchQuery). Toast lets the user know real backend search is pending.
-->

<template>
  <Teleport to="body">
    <div
      class="search"
      role="dialog"
      aria-modal="true"
    >
      <div
        class="search__backdrop"
        @click="$emit('close')"
      />
      <div class="search__panel">
        <header class="search__head">
          <div class="search__icon-wrap">
            <IconSearch :size="18" />
          </div>
          <h2 class="search__title">
            Поиск
          </h2>
          <button
            type="button"
            class="search__close"
            aria-label="Закрыть"
            @click="$emit('close')"
          >
            <IconClose :size="20" />
          </button>
        </header>

        <form
          class="search__form"
          @submit.prevent="runSearch"
        >
          <input
            v-model="local"
            type="search"
            class="search__input"
            placeholder="Искать..."
            autofocus
          >
          <button
            type="submit"
            class="search__action"
            aria-label="Искать"
          >
            <IconSearch :size="20" />
          </button>
        </form>

        <div
          v-if="diary.searchHistory.length > 0"
          class="search__history"
        >
          <div class="search__history-head">
            <span class="search__history-label">Недавно вы искали:</span>
            <button
              type="button"
              class="search__history-clear"
              @click="diary.clearSearchHistory()"
            >
              Очистить
            </button>
          </div>
          <button
            v-for="q in diary.searchHistory"
            :key="q"
            type="button"
            class="search__history-pill"
            @click="rerunSearch(q)"
          >
            <span>{{ q }}</span>
            <span
              class="search__history-arrow"
              aria-hidden="true"
            >↗</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDiaryStore } from '@/stores/diary'
import { useToast } from '@/composables/useToast'
import { IconSearch, IconClose } from '@/components/icons'

defineEmits<{ (e: 'close'): void }>()

const diary = useDiaryStore()
const toast = useToast()
const local = ref(diary.searchQuery)

function runSearch(): void {
  const q = local.value.trim()
  diary.setSearchQuery(q)
  if (q) {
    diary.pushSearchHistory(q)
    toast.info('Поиск временно недоступен — показаны локальные совпадения')
  }
}

function rerunSearch(q: string): void {
  local.value = q
  runSearch()
}
</script>

<style scoped>
.search {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: flex-start;
  justify-content: stretch;
}

.search__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
}

.search__panel {
  position: relative;
  background: var(--surface-default);
  border-bottom-left-radius: var(--radius-lg);
  border-bottom-right-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.search__head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.search__icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--surface-steel-alpha-15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}

.search__title {
  flex: 1 1 auto;
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.search__close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search__form {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.search__input {
  flex: 1 1 auto;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
}

.search__action {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--steel-button);
  color: white;
  border: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search__history {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.search__history-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.search__history-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.search__history-clear {
  background: transparent;
  border: 0;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  cursor: pointer;
}

.search__history-pill {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.search__history-arrow {
  color: var(--text-secondary);
}
</style>
