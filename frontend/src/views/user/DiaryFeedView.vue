<!--
  VELO Frontend -- DiaryFeedView (Diary redesign, screen 40)

  The diary screen. Renders the unified feed as the alternating thread
  (DiaryTimeline), with a frosted composer pinned at the bottom and a header
  ("Дневник" + "..." menu stub). Replaces the old tab-based DiaryView.

  Pagination: cursor-based infinite scroll. An IntersectionObserver sentinel
  at the bottom calls loadMoreFeed() when it scrolls into view (the project's
  other lists use a "show more" button, but the diary is a chat-like timeline
  where auto-load reads more naturally -- agreed deviation).

  Tap handling (this iteration = Variant A): editable cards (note/dream) show
  a "coming soon" toast; everything else is a no-op. The composer creates
  notes. When Variant B lands, only the tap handler here changes.
-->

<template>
  <div class="diary-feed">
    <!-- Header -->
    <header class="diary-feed__header">
      <div class="diary-feed__title-wrap">
        <h1 class="diary-feed__title">{{ feedTitle }}</h1>
        <button
          v-if="filterActive"
          type="button"
          class="diary-feed__filter-clear"
          aria-label="Сбросить фильтр"
          @click="clearFilter"
        >
          <IconClose :size="16" />
        </button>
      </div>
      <div class="diary-feed__menu-wrap">
        <button
          type="button"
          class="diary-feed__menu"
          aria-label="Меню"
          @click="menuOpen = !menuOpen"
        >
          <IconDots :size="20" />
        </button>
        <div v-if="menuOpen" class="diary-feed__menu-pop" role="menu">
          <button
            type="button"
            class="diary-feed__menu-item"
            @click="openFilter"
          >
            Фильтр
          </button>
          <button
            type="button"
            class="diary-feed__menu-item"
            @click="openSearch"
          >
            Поиск
          </button>
        </div>
      </div>
    </header>

    <!-- Feed body: the ONLY scrolling area, between fixed header and composer -->
    <div ref="scrollEl" class="diary-feed__body">
      <!-- Initial loading -->
      <div v-if="initialLoading" class="diary-feed__state">
        <VLoader size="lg" />
      </div>

      <!-- Error (only when nothing loaded yet) -->
      <VEmptyState
        v-else-if="feedError && items.length === 0"
        icon="⚠️"
        title="Не удалось загрузить дневник"
        description="Проверьте соединение и попробуйте ещё раз"
      >
        <template #action>
          <VButton variant="primary" @click="reload">Повторить</VButton>
        </template>
      </VEmptyState>

      <!-- Empty -->
      <VEmptyState
        v-else-if="items.length === 0"
        icon="📔"
        title="Дневник пуст"
        description="Здесь появятся ваши записи, практики, check-ins и отзывы"
      />

      <!-- Thread (chat-mode: oldest at top, newest at bottom) -->
      <template v-else>
        <!-- Infinite-scroll sentinel + "loading older" indicator sit ABOVE the
             thread: history is loaded by scrolling UP. -->
        <div ref="sentinelEl" class="diary-feed__sentinel" />
        <div v-if="loadingMore" class="diary-feed__state diary-feed__state--more">
          <VLoader />
        </div>

        <!-- Wrapper pins a short feed to the bottom (margin-top:auto) so few
             entries sit next to the composer, chat-style. -->
        <div class="diary-feed__thread">
          <DiaryTimeline :items="items" :timezone="timezone" @tap="onTap" />
        </div>
      </template>
    </div>

    <!-- Undo bar: shown after deleting an entry (Figma screen 58) -->
    <div v-if="deletedEntryId" class="diary-feed__undo">
      <span class="diary-feed__undo-text">Запись удалена</span>
      <button
        type="button"
        class="diary-feed__undo-btn"
        :disabled="undoing"
        @click="onUndoDelete"
      >
        Отменить
      </button>
    </div>

    <!-- Composer -->
    <div class="diary-feed__composer">
      <DiaryComposer @created="onComposerCreated" />
    </div>

    <!-- Category filter (screen 42), opened from the "..." menu -->
    <DiaryFilterModal
      :open="showFilter"
      :categories="activeCategories"
      :date-from="feedFilters.date_from"
      :date-to="feedFilters.date_to"
      :timezone="timezone"
      @apply="onApplyFilter"
      @close="showFilter = false"
    />

    <!-- Text search (screen 44), opened from the "..." menu -->
    <DiarySearchModal
      :open="showSearch"
      :initial="feedFilters.search ?? ''"
      @search="onApplySearch"
      @close="showSearch = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import { IconDots, IconClose } from '@/components/icons'
import DiaryTimeline from '@/components/shared/DiaryTimeline.vue'
import DiaryComposer from '@/components/shared/DiaryComposer.vue'
import DiaryFilterModal from '@/components/shared/DiaryFilterModal.vue'
import DiarySearchModal from '@/components/shared/DiarySearchModal.vue'
import { useDiaryStore } from '@/stores/diary'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import type { DiaryFeedItem, DiaryFeedCategory } from '@/api/types'

const router = useRouter()
const route = useRoute()
const diaryStore = useDiaryStore()
const authStore = useAuthStore()
const toast = useToast()

const { feedItems, feedLoading, feedError, feedHasMore, feedFilters } =
  storeToRefs(diaryStore)

const items = computed<DiaryFeedItem[]>(() => feedItems.value)
const timezone = computed(() => authStore.user?.timezone ?? 'UTC')

// Loading split: first page (full-screen loader) vs subsequent pages (inline).
const initialLoading = computed(
  () => feedLoading.value && items.value.length === 0,
)
const loadingMore = computed(
  () => feedLoading.value && items.value.length > 0,
)

// -- Tap handling ------------------------------------------------------------

function onTap(payload: { item: DiaryFeedItem; editable: boolean }): void {
  const item = payload.item
  if (payload.editable) {
    // note/dream -- open the full entry screen (view/edit/delete). The card's
    // source_id is the DiaryEntry id.
    void router.push({
      name: 'user-diary-entry',
      params: { id: item.source_id },
    })
    return
  }

  // Read-only detail for check-in / feedback (source_id is the row id).
  if (item.kind === 'checkin' || item.kind === 'feedback') {
    void router.push({
      name: 'user-diary-detail',
      params: { type: item.kind, id: item.source_id },
    })
    return
  }

  // Practice outcome -> existing practice detail page (source_id is the
  // practice id, per project_practice_outcome).
  if (item.kind === 'practice_outcome') {
    void router.push({
      name: 'practice-detail',
      params: { id: item.source_id },
    })
    return
  }

  // Banner kinds (booking_confirmed/cancelled/rescheduled) are not tappable.
}

// -- "..." menu + filter / search modals (screens 42 / 43 / 44) --------------

const menuOpen = ref(false)
const showFilter = ref(false)
const showSearch = ref(false)

// Current categories from the store, used to seed the filter modal's draft.
const activeCategories = computed<DiaryFeedCategory[]>(
  () => feedFilters.value.categories ?? [],
)

function openFilter(): void {
  menuOpen.value = false
  showFilter.value = true
}

function openSearch(): void {
  menuOpen.value = false
  showSearch.value = true
}

async function onApplyFilter(payload: {
  categories: DiaryFeedCategory[]
  date_from?: string
  date_to?: string
}): Promise<void> {
  // setFeedFilters resets the feed to the first page with the new filter set.
  await diaryStore.setFeedFilters({
    categories: payload.categories,
    date_from: payload.date_from,
    date_to: payload.date_to,
  })
  await nextTick()
  // Chat-mode: jump to the newest matching entry (bottom) after refiltering.
  scrollToBottom()
}

async function onApplySearch(query: string): Promise<void> {
  // runFeedSearch trims; an empty string clears the search. Both reload the
  // feed from the first page.
  await diaryStore.runFeedSearch(query)
  await nextTick()
  scrollToBottom()
}

// -- Active-filter header + reset (minimal indicator) ------------------------
//
// When a filter is active the header shows it and offers a one-tap reset
// (the cross), so the user is never confused about whether the feed is
// filtered. The title is swapped to the category name ONLY when exactly one
// category is selected (screens "Check-ins" / "Feedbacks" / "Сонник" ...);
// otherwise it stays "Дневник" but the cross still appears.

const CATEGORY_TITLE: Record<DiaryFeedCategory, string> = {
  entries: 'Дневник',
  dreams: 'Сонник',
  feedbacks: 'Feedbacks',
  checkins: 'Check-ins',
  practices: 'Практики',
}

// Any filter axis active = categories and/or date range and/or search.
const filterActive = computed(
  () =>
    activeCategories.value.length > 0 ||
    feedFilters.value.date_from !== undefined ||
    feedFilters.value.date_to !== undefined ||
    (feedFilters.value.search ?? '') !== '',
)

const feedTitle = computed(() => {
  const cats = activeCategories.value
  const only = cats.length === 1 ? cats[0] : undefined
  if (only !== undefined) return CATEGORY_TITLE[only]
  return 'Дневник'
})

async function clearFilter(): Promise<void> {
  // Full reset: categories + date range + search (clearFeedFilters reloads
  // the feed from the first page).
  await diaryStore.clearFeedFilters()
  await nextTick()
  scrollToBottom()
}

// -- Undo bar (after deleting an entry on EntryView) -------------------------
//
// EntryView soft-deletes then navigates back here with ?deleted=<entryId>.
// We surface an "Запись удалена / Отменить" bar (Figma screen 58); tapping
// Отменить restores the entry. The bar auto-dismisses after a few seconds.

const UNDO_DURATION_MS = 6000
const deletedEntryId = ref<string | null>(null)
const undoing = ref(false)
let undoTimer: ReturnType<typeof setTimeout> | null = null

function clearUndoTimer(): void {
  if (undoTimer) {
    clearTimeout(undoTimer)
    undoTimer = null
  }
}

function dismissUndo(): void {
  clearUndoTimer()
  deletedEntryId.value = null
}

// Strip the ?deleted param without adding a history entry.
function stripDeletedQuery(): void {
  if (route.query.deleted !== undefined) {
    const query = { ...route.query }
    delete query.deleted
    void router.replace({ query })
  }
}

watch(
  () => route.query.deleted,
  (val) => {
    const id = Array.isArray(val) ? val[0] : val
    if (!id) return
    deletedEntryId.value = id
    stripDeletedQuery()
    clearUndoTimer()
    undoTimer = setTimeout(dismissUndo, UNDO_DURATION_MS)
  },
  { immediate: true },
)

async function onUndoDelete(): Promise<void> {
  const id = deletedEntryId.value
  if (!id || undoing.value) return
  undoing.value = true
  const result = await diaryStore.restoreEntry(id)
  undoing.value = false
  dismissUndo()
  if (result.ok) {
    await nextTick()
    scrollToBottom()
  } else {
    toast.error(result.error)
  }
}

// -- Data load ---------------------------------------------------------------

async function reload(): Promise<void> {
  await diaryStore.refreshFeed()
}

onMounted(async () => {
  await diaryStore.fetchFeed()
  await nextTick()
  // Chat-mode: open pinned to the newest entry (bottom). Do this BEFORE
  // attaching the observer so the top sentinel (now out of view) does not
  // immediately fire and load an older page.
  scrollToBottom()
  await nextTick()
  setupObserver()
})

// -- Scroll helpers (chat-mode) ----------------------------------------------

function scrollToBottom(): void {
  const el = scrollEl.value
  if (el) el.scrollTop = el.scrollHeight
}

// Composer just created a note: the store refreshed the feed to the newest
// page, so jump to the bottom to reveal it.
async function onComposerCreated(): Promise<void> {
  await nextTick()
  scrollToBottom()
}

// -- Infinite scroll ---------------------------------------------------------

const scrollEl = ref<HTMLElement | null>(null)
const sentinelEl = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null

function setupObserver(): void {
  if (observer || !sentinelEl.value) return
  observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (
        entry?.isIntersecting &&
        feedHasMore.value &&
        !feedLoading.value
      ) {
        void onLoadMore()
      }
    },
    { root: scrollEl.value, rootMargin: '120px' },
  )
  observer.observe(sentinelEl.value)
}

// Load an older page (triggered by scrolling UP to the top sentinel) and
// preserve the viewport: older cards are prepended at the top, so without
// compensation the content would jump. Measure height around the load and
// shift scrollTop by the delta.
async function onLoadMore(): Promise<void> {
  const el = scrollEl.value
  const prevHeight = el?.scrollHeight ?? 0
  const prevTop = el?.scrollTop ?? 0
  await diaryStore.loadMoreFeed()
  await nextTick()
  if (el) el.scrollTop = prevTop + (el.scrollHeight - prevHeight)
}

// The sentinel only exists once items render; re-attach when it appears.
watch(sentinelEl, (el) => {
  if (el && !observer) setupObserver()
})

onBeforeUnmount(() => {
  observer?.disconnect()
  observer = null
  clearUndoTimer()
})
</script>

<style scoped>
/* Chat-style layout. The parent (MobileLayout main in `fill` mode) is a flex
   column that hands us its full height with no scroll of its own. We fill that
   height and split it into three rows: fixed header, scrolling feed, fixed
   composer. Only the feed (.diary-feed__body) scrolls -- header and composer
   stay put, so the composer is always pinned just above the tab bar on both
   short and long feeds. The background stays continuous across all three rows
   (overlay look preserved: nothing opaque cuts the runes backdrop). */
.diary-feed {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* -- Header (fixed row) -- */
.diary-feed__header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-8) var(--space-3);
}

.diary-feed__title {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  letter-spacing: 0.36px;
  color: var(--velo-text-primary);
}

/* Title + active-filter reset cross. */
.diary-feed__title-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
}

.diary-feed__filter-clear {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  border: none;
  border-radius: var(--radius-full);
  background: var(--velo-glass-blue-15);
  color: var(--velo-text-secondary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.diary-feed__filter-clear:hover {
  opacity: 0.8;
}

.diary-feed__menu {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: var(--radius-full);
  background: var(--velo-nav-active-bg);
  color: #ffffff;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.diary-feed__menu:hover {
  opacity: 0.85;
}

/* "..." menu popover (Фильтр / Поиск) */
.diary-feed__menu-wrap {
  position: relative;
  flex-shrink: 0;
}

.diary-feed__menu-pop {
  position: absolute;
  top: calc(100% + var(--space-1));
  right: 0;
  z-index: var(--z-content);
  display: flex;
  flex-direction: column;
  min-width: 160px;
  padding: var(--space-1);
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-md);
  box-shadow: var(--velo-shadow-glow);
}

.diary-feed__menu-item {
  padding: var(--space-2) var(--space-3);
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  cursor: pointer;
  text-align: left;
  transition: background var(--transition-fast);
}

.diary-feed__menu-item:hover {
  background: var(--velo-glass-blue-15);
}

/* -- Body: the ONLY scrolling row -- */
.diary-feed__body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding: 0 var(--space-8);
  /* Chat-mode: a flex column so the thread wrapper can pin a short feed to the
     bottom (next to the composer). When the feed overflows, this has no effect
     and the area scrolls normally. */
  display: flex;
  flex-direction: column;
}

/* Pins a short feed to the bottom; a long one scrolls normally (margin-top
   collapses once content fills the column). */
.diary-feed__thread {
  margin-top: auto;
}

.diary-feed__state {
  display: flex;
  justify-content: center;
  padding: var(--space-10) 0;
}

.diary-feed__state--more {
  padding: var(--space-5) 0;
}

.diary-feed__sentinel {
  height: 1px;
}

/* -- Undo bar (delete confirmation, Figma screen 58) -- */
.diary-feed__undo {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin: 0 var(--space-8);
  padding: var(--space-3) var(--space-4);
  background: var(--velo-glass-blue-15);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-md);
}

.diary-feed__undo-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
}

.diary-feed__undo-btn {
  flex-shrink: 0;
  border: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--velo-teal-600);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.diary-feed__undo-btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.diary-feed__undo-btn:not(:disabled):hover {
  opacity: 0.8;
}

/* -- Composer (fixed row, always above the tab bar) -- */
.diary-feed__composer {
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  padding: var(--space-3) var(--space-8) var(--space-4);
}
</style>
