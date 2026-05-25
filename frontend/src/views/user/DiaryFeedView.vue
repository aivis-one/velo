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

    <!-- Scrollable feed body -->
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

      <!-- Thread -->
      <template v-else>
        <DiaryTimeline :items="items" :timezone="timezone" @tap="onTap" />

        <!-- Infinite-scroll sentinel + loading more indicator -->
        <div ref="sentinelEl" class="diary-feed__sentinel" />
        <div v-if="loadingMore" class="diary-feed__state diary-feed__state--more">
          <VLoader />
        </div>
      </template>
    </div>

    <!-- Composer -->
    <div class="diary-feed__composer">
      <DiaryComposer />
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
  setupObserver()
})

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
        void diaryStore.loadMoreFeed()
      }
    },
    { root: scrollEl.value, rootMargin: '120px' },
  )
  observer.observe(sentinelEl.value)
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
.diary-feed {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

/* -- Header -- */
.diary-feed__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-8) var(--space-3);
  flex-shrink: 0;
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

/* -- Body (scroll area) -- */
.diary-feed__body {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-8) var(--space-5);
  /* room so the last cards clear the pinned composer */
  padding-bottom: 90px;
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

/* -- Composer (pinned bottom) -- */
.diary-feed__composer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  padding: var(--space-3) var(--space-8) var(--space-5);
  pointer-events: none;
}

.diary-feed__composer > * {
  pointer-events: auto;
}
</style>
