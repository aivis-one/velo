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
      <h1 class="diary-feed__title">Дневник</h1>
      <button
        type="button"
        class="diary-feed__menu"
        aria-label="Меню"
        @click="onMenu"
      >
        <IconDots :size="20" />
      </button>
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

    <!-- Composer -->
    <div class="diary-feed__composer">
      <DiaryComposer @created="onComposerCreated" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import { IconDots } from '@/components/icons'
import DiaryTimeline from '@/components/shared/DiaryTimeline.vue'
import DiaryComposer from '@/components/shared/DiaryComposer.vue'
import { useDiaryStore } from '@/stores/diary'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import type { DiaryFeedItem } from '@/api/types'

const diaryStore = useDiaryStore()
const authStore = useAuthStore()
const toast = useToast()

const { feedItems, feedLoading, feedError, feedHasMore } = storeToRefs(diaryStore)

const items = computed<DiaryFeedItem[]>(() => feedItems.value)
const timezone = computed(() => authStore.user?.timezone ?? 'UTC')

// Loading split: first page (full-screen loader) vs subsequent pages (inline).
const initialLoading = computed(
  () => feedLoading.value && items.value.length === 0,
)
const loadingMore = computed(
  () => feedLoading.value && items.value.length > 0,
)

// -- Tap handling (Variant A) ------------------------------------------------

function onTap(payload: { item: DiaryFeedItem; editable: boolean }): void {
  if (payload.editable) {
    // note/dream -- inline editor arrives in Variant B.
    toast.info('Функция временно недоступна')
  }
  // All other cards: no-op in this iteration.
}

function onMenu(): void {
  // Filter / search menu lands in a later sub-step (1b-3).
  toast.info('Функция временно недоступна')
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

/* -- Composer (fixed row, always above the tab bar) -- */
.diary-feed__composer {
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  padding: var(--space-3) var(--space-8) var(--space-4);
}
</style>
