<!--
  VELO Frontend -- AdminDashboardView (Phase F8.1; refreshed S4 P15 C68)

  Admin dashboard: 4 StatCards row + Callout(amber) when pending_verifications > 0
  + Quick actions row.

  Data: GET /api/v1/admin/stats → AdminStatsResponse {users_count,
        masters_count, practices_count, pending_verifications}

  Path Y MEDIUM (#047). No emojis (#048): icon-component pattern via Callout
  + ProfileMenuItem-style quick actions.
-->

<template>
  <div class="admin-dashboard">
    <VHeader title="Панель управления" />

    <div class="admin-dashboard__content">
      <!-- Loading -->
      <div
        v-if="loading"
        class="admin-dashboard__loader"
      >
        <VLoader size="lg" />
      </div>

      <template v-else-if="stats">
        <!-- Greeting -->
        <header class="admin-dashboard__greet">
          <p class="admin-dashboard__greet-time">
            {{ greetingPrefix }}
          </p>
          <h1 class="admin-dashboard__greet-name">
            {{ adminName }}
          </h1>
        </header>

        <!-- Alert: pending verifications -->
        <Callout
          v-if="stats.pending_verifications > 0"
          variant="amber"
          :icon="IconWarning"
          title="Заявки на верификацию"
        >
          <button
            type="button"
            class="admin-dashboard__alert-link"
            @click="router.push({ name: 'admin-masters' })"
          >
            {{ stats.pending_verifications }} заявк{{ pendingSuffix }} ждут проверки. Перейти →
          </button>
        </Callout>

        <!-- StatCards row -->
        <div class="admin-dashboard__grid">
          <StatCard
            :value="stats.users_count"
            label="Пользователи"
          />
          <StatCard
            :value="stats.masters_count"
            label="Мастера"
          />
          <StatCard
            :value="stats.practices_count"
            label="Практики"
          />
          <StatCard
            :value="stats.pending_verifications"
            label="На проверке"
          />
        </div>

        <!-- Quick actions -->
        <h3 class="admin-dashboard__section-title">
          Быстрые действия
        </h3>
        <div class="admin-dashboard__actions">
          <ProfileMenuItem
            :icon="IconGroup"
            label="Мастера"
            to="/admin/masters"
          />
          <ProfileMenuItem
            :icon="IconWarning"
            label="Жалобы"
            to="/admin/reports"
          />
          <ProfileMenuItem
            :icon="IconCheck"
            label="Сверка"
            to="/admin/consistency"
          />
        </div>
      </template>

      <!-- Error state -->
      <VEmptyState
        v-else
        title="Не удалось загрузить статистику"
        description="Проверьте соединение и попробуйте ещё раз"
      >
        <template #action>
          <VButton
            variant="primary"
            @click="loadStats"
          >
            Повторить
          </VButton>
        </template>
      </VEmptyState>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VLoader, VEmptyState, VButton } from '@/components/ui'
import {
  IconWarning,
  IconGroup,
  IconCheck,
} from '@/components/icons'
import StatCard from '@/components/shared/StatCard.vue'
import Callout from '@/components/shared/Callout.vue'
import ProfileMenuItem from '@/components/shared/ProfileMenuItem.vue'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { getAdminStats } from '@/api/admin'
import type { AdminStatsResponse } from '@/api/admin'
import { ApiResponseError } from '@/api/client'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const stats = ref<AdminStatsResponse | null>(null)
const loading = ref(false)

const adminName = computed(() => {
  const u = authStore.user
  if (!u) return 'Администратор'
  const parts = [u.first_name, u.last_name].filter(Boolean)
  return parts.length > 0 ? parts.join(' ') : 'Администратор'
})

const greetingPrefix = computed((): string => {
  const h = new Date().getHours()
  if (h < 5) return 'Доброй ночи,'
  if (h < 12) return 'Доброе утро,'
  if (h < 18) return 'Добрый день,'
  return 'Добрый вечер,'
})

// Russian suffix for "заявк(а/и/...)" based on count
const pendingSuffix = computed(() => {
  const n = stats.value?.pending_verifications ?? 0
  if (n % 10 === 1 && n % 100 !== 11) return 'а'
  if (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) return 'и'
  return ''
})

async function loadStats(): Promise<void> {
  loading.value = true
  try {
    stats.value = await getAdminStats()
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки статистики'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<style scoped>
.admin-dashboard {
  min-height: 100dvh;
}

.admin-dashboard__content {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.admin-dashboard__greet {
  margin-bottom: var(--space-1);
}

.admin-dashboard__greet-time {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.admin-dashboard__greet-name {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

/* Alert link inside Callout slot */
.admin-dashboard__alert-link {
  background: transparent;
  border: 0;
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  cursor: pointer;
  text-align: left;
  padding: 0;
}

/* Stats grid */
.admin-dashboard__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

/* Quick actions */
.admin-dashboard__section-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin: 0;
  font-weight: 400;
}

.admin-dashboard__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

/* Loader */
.admin-dashboard__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}
</style>
