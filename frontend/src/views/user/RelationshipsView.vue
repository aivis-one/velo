<!--
  VELO Frontend — RelationshipsView (S2-S3 SPEEDRUN MEGA-2 §C45)

  Composite view: SpineDivider + RelationshipChain + entry context cards
  + AI commentary placeholder. Per BACKEND § A.8 mock — chain items derived
  client-side from the entry's mood + adjacent feedback/checkin (best-effort).
-->

<template>
  <div class="rel">
    <header class="rel__header">
      <button
        type="button"
        class="rel__back"
        aria-label="Назад"
        @click="router.back()"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="rel__title">
        Взаимосвязи
      </h1>
    </header>

    <SpineDivider :date="dateLabel" />

    <RelationshipChain :items="chainItems" />

    <article
      v-if="entry"
      class="rel__entry"
    >
      <p class="rel__entry-date">
        {{ humanDate(entry.created_at) }}
      </p>
      <h2
        v-if="entry.title"
        class="rel__entry-title"
      >
        {{ entry.title }}
      </h2>
      <p class="rel__entry-body">
        {{ entry.content }}
      </p>
    </article>

    <AICommentaryCard
      title="Связь между состоянием и практикой"
      body="Похоже, после вечерних практик ваше настроение улучшалось чаще. Попробуйте чаще включать их в свой график."
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  IconArrowBack,
  IconFeedback,
  IconBookFeather,
  IconBookDream,
  IconBrain,
} from '@/components/icons'
import SpineDivider from '@/components/shared/SpineDivider.vue'
import RelationshipChain from '@/components/shared/RelationshipChain.vue'
import AICommentaryCard from '@/components/shared/AICommentaryCard.vue'
import { useDiaryStore } from '@/stores/diary'

type Kind = 'mood' | 'flame' | 'feather' | 'dream' | 'neutral'

const route = useRoute()
const router = useRouter()
const diary = useDiaryStore()

const entry = computed(() => diary.selectedEntry)

const dateLabel = computed(() => {
  if (!entry.value) return ''
  return humanDate(entry.value.created_at)
})

const chainItems = computed<Array<{ icon: Component; kind: Kind }>>(() => {
  // Static placeholder per BACKEND § A.8 mock — chain doesn't have a real
  // backend signal yet; render a representative 3-icon chain.
  return [
    { icon: IconBrain, kind: 'mood' },
    { icon: IconFeedback, kind: 'flame' },
    { icon: entry.value ? entryIcon() : IconBookFeather, kind: 'feather' },
  ]
})

function entryIcon(): Component {
  if (!entry.value) return IconBookFeather
  const t = (entry.value as typeof entry.value & { type?: string }).type
  if (t === 'dream') return IconBookDream
  return IconBookFeather
}

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
  const id = route.params.id
  if (typeof id === 'string') {
    await diary.fetchEntry(id)
  }
})
</script>

<style scoped>
.rel {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  min-height: 100%;
}

.rel__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.rel__back {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rel__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.rel__entry {
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.rel__entry-date {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin: 0;
}

.rel__entry-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.rel__entry-body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  margin: 0;
  white-space: pre-wrap;
}
</style>
