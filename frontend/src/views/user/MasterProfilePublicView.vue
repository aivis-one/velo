<!--
  VELO Frontend — MasterProfilePublicView (S2-S3 SPEEDRUN MEGA-2 §C51)

  DEGRADED v1: no public GET /masters/{id} endpoint (Code anomaly #2).
  Falls back to deriving master metadata from PracticeSummary on
  recent practices. Stats hidden; bio/methods placeholder. Logged
  as BACKLOG #99 (added at MEGA-2 close).
-->

<template>
  <div class="mp">
    <header class="mp__header">
      <button
        type="button"
        class="mp__back"
        aria-label="Назад"
        @click="router.back()"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="mp__title">
        Мастер
      </h1>
    </header>

    <div
      v-if="loading"
      class="mp__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="!derived"
      class="mp__empty"
    >
      Информация о мастере временно недоступна.
    </div>
    <div
      v-else
      class="mp__body"
    >
      <article class="mp__hero">
        <span class="mp__avatar">
          <img
            v-if="derived.avatar_url"
            :src="derived.avatar_url"
            :alt="derived.name"
          >
          <IconProfile
            v-else
            :size="36"
          />
        </span>
        <h2 class="mp__name">
          {{ derived.name }}
        </h2>
        <div class="mp__chips">
          <span class="mp__chip">Верифицирован</span>
        </div>
        <p class="mp__bio">
          Информация о мастере временно ограничена. Полный профиль появится после расширения backend.
        </p>
      </article>

      <!--
        Stats deferred per BACKEND § Master public stats — see BACKLOG #99
        on backend MasterPublicResponse with practice_count + review_count.
      -->

      <section
        v-if="upcoming.length"
        class="mp__section"
      >
        <h3 class="mp__sub">
          Ближайшие практики
        </h3>
        <RouterLink
          v-for="p in upcoming"
          :key="p.id"
          :to="`/user/practices/${p.id}`"
          class="mp__practice"
        >
          <span class="mp__practice-title">{{ p.title }}</span>
          <span class="mp__practice-time">{{ humanTime(p.scheduled_at) }}</span>
        </RouterLink>
      </section>

      <button
        type="button"
        class="mp__ask"
        @click="onAsk"
      >
        Задать вопрос
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { IconArrowBack, IconProfile } from '@/components/icons'
import { getPractices } from '@/api/practices'
import { useToast } from '@/composables/useToast'
import type { PracticeResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const loading = ref(false)
const upcoming = ref<PracticeResponse[]>([])

const derived = computed<{
  name: string
  avatar_url: string | null
} | null>(() => {
  if (upcoming.value.length === 0) return null
  const first = upcoming.value[0]!
  return {
    name: first.master_name ?? 'Мастер',
    avatar_url: (first as PracticeResponse & { master_avatar_url?: string })
      .master_avatar_url ?? null,
  }
})

function humanTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function onAsk(): void {
  toast.info('Сообщения скоро будут доступны')
}

onMounted(async () => {
  const id = route.params.id
  if (typeof id !== 'string') return
  loading.value = true
  try {
    const data = await getPractices({ master_id: id }, 3, 0)
    upcoming.value = data.items
  } catch {
    upcoming.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.mp {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
}

.mp__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.mp__back {
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

.mp__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.mp__loader,
.mp__empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.mp__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.mp__hero {
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  text-align: center;
}

.mp__avatar {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: var(--surface-steel-alpha-15);
  border: 1px solid var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: var(--text-primary);
}

.mp__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mp__name {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.mp__chips {
  display: flex;
  gap: var(--space-2);
}

.mp__chip {
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: var(--mint-primary, var(--surface-steel-alpha-15));
  color: white;
  font-size: var(--text-xs);
}

.mp__bio {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.mp__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.mp__sub {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.mp__practice {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--text-primary);
  font-family: var(--font-body);
}

.mp__practice-title {
  font-size: var(--text-base);
  font-weight: 500;
}

.mp__practice-time {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.mp__ask {
  margin-top: var(--space-3);
  padding: var(--space-3);
  background: var(--steel-button);
  color: white;
  border: 0;
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 500;
  cursor: pointer;
}
</style>
