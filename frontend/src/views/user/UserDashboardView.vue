<!--
  VELO Frontend -- UserDashboardView (Phase F3.1)

  Main user screen. Shows:
    - Greeting with user's first name
    - "Upcoming practices" section (first 5 from catalog)
    - "All practices" link → /user/calendar

  Reuses PracticeCard for items, VEmptyState when catalog is empty.
  Data comes from usePracticesStore (shared with CalendarView).
-->

<template>
  <div class="dashboard">
    <!-- Greeting -->
    <div class="dashboard__greeting">
      <p class="dashboard__greeting-text">{{ greetingText }}</p>
      <h2 class="dashboard__greeting-name">{{ userName }} 👋</h2>
    </div>

    <!-- Upcoming practices -->
    <section class="dashboard__section">
      <div class="dashboard__section-header">
        <h3 class="dashboard__section-title">Ближайшие практики</h3>
        <button
          v-if="upcomingPractices.length > 0"
          class="dashboard__link"
          @click="router.push({ name: 'user-calendar' })"
        >
          Все →
        </button>
      </div>

      <!-- Loading -->
      <div v-if="store.loading && upcomingPractices.length === 0" class="dashboard__loader">
        <VLoader />
      </div>

      <!-- Error -->
      <VEmptyState
        v-else-if="store.error"
        icon="⚠️"
        title="Не удалось загрузить"
        :description="store.error"
      >
        <VButton size="sm" @click="store.refreshPractices()">Повторить</VButton>
      </VEmptyState>

      <!-- Empty -->
      <VEmptyState
        v-else-if="!store.loading && upcomingPractices.length === 0"
        icon="📅"
        title="Пока нет практик"
        description="Практики появятся здесь, когда мастера их опубликуют"
      />

      <!-- Practice cards -->
      <div v-else class="dashboard__practices">
        <PracticeCard
          v-for="practice in upcomingPractices"
          :key="practice.id"
          :practice="practice"
          @click="goToDetail"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePracticesStore } from '@/stores/practices'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import PracticeCard from '@/components/shared/PracticeCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const store = usePracticesStore()

// -- Max cards shown on dashboard --
const DASHBOARD_LIMIT = 5

const userName = computed(() => authStore.user?.first_name ?? 'Друг')

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return 'Доброй ночи,'
  if (hour < 12) return 'Доброе утро,'
  if (hour < 18) return 'Добрый день,'
  return 'Добрый вечер,'
})

const upcomingPractices = computed(() =>
  store.practices.slice(0, DASHBOARD_LIMIT),
)

function goToDetail(id: string): void {
  router.push({ name: 'practice-detail', params: { id } })
}

onMounted(() => {
  store.fetchPractices()
})
</script>

<style scoped>
.dashboard__greeting {
  margin-bottom: var(--space-6);
}

.dashboard__greeting-text {
  font-size: 14px;
  color: var(--velo-text-secondary);
  margin: 0 0 var(--space-1);
}

.dashboard__greeting-name {
  font-family: var(--font-heading);
  font-size: 26px;
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0;
}

.dashboard__section {
  margin-bottom: var(--space-6);
}

.dashboard__section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.dashboard__section-title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0;
}

.dashboard__link {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-primary);
  cursor: pointer;
  transition: opacity 0.2s;
}

.dashboard__link:hover {
  opacity: 0.7;
}

.dashboard__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

.dashboard__practices {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
</style>
