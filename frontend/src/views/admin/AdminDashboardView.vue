<!--
  VELO Frontend -- AdminDashboardView (Phase F8.1, updated F8-fix W-4)

  Admin dashboard: 4 stat cards + alert banner when pending_verifications > 0.
  W-4: replaced hardcoded hex colors with CSS semantic tint variables.

  Data: GET /api/v1/admin/stats
-->

<template>
  <div class="admin-dashboard">
    <VHeader title="Панель управления" />

    <div class="admin-dashboard__content">
      <!-- Loading -->
      <div v-if="loading" class="admin-dashboard__loader">
        <VLoader size="lg" />
      </div>

      <template v-else-if="stats">
        <!-- Alert banner: pending verifications -->
        <div
          v-if="stats.pending_verifications > 0"
          class="admin-dashboard__alert"
          @click="router.push({ name: 'admin-masters' })"
        >
          <span class="admin-dashboard__alert-icon">⚠️</span>
          <div class="admin-dashboard__alert-body">
            <div class="admin-dashboard__alert-title">
              {{ stats.pending_verifications }} заявк{{ pendingSuffix }} на верификацию
            </div>
            <div class="admin-dashboard__alert-sub">Нажмите, чтобы перейти</div>
          </div>
          <span class="admin-dashboard__alert-arrow">→</span>
        </div>

        <!-- Stats grid -->
        <div class="admin-dashboard__grid">
          <VStatCard
            :value="stats.users_count"
            label="пользователей"
            icon="👥"
          />
          <VStatCard
            :value="stats.masters_count"
            label="мастеров"
            icon="🧘"
          />
          <VStatCard
            :value="stats.practices_count"
            label="практик"
            icon="📅"
          />
          <VStatCard
            :value="stats.pending_verifications"
            label="ожидают верификации"
            icon="🕐"
            :clickable="stats.pending_verifications > 0"
            @click="stats.pending_verifications > 0 && router.push({ name: 'admin-masters' })"
          />
        </div>

        <!-- Quick actions -->
        <div class="admin-dashboard__section-title">Быстрые действия</div>
        <div class="admin-dashboard__actions">
          <div
            class="admin-dashboard__action-card"
            @click="router.push({ name: 'admin-masters' })"
          >
            <span class="admin-dashboard__action-icon">👥</span>
            <div class="admin-dashboard__action-label">Мастера</div>
          </div>
          <div
            class="admin-dashboard__action-card"
            @click="router.push({ name: 'admin-reports' })"
          >
            <span class="admin-dashboard__action-icon">⚠️</span>
            <div class="admin-dashboard__action-label">Жалобы</div>
          </div>
          <div
            class="admin-dashboard__action-card"
            @click="router.push({ name: 'admin-consistency' })"
          >
            <span class="admin-dashboard__action-icon">🔍</span>
            <div class="admin-dashboard__action-label">Семафоры</div>
          </div>
        </div>
      </template>

      <!-- Error state -->
      <VEmptyState
        v-else
        icon="⚠️"
        title="Не удалось загрузить статистику"
        description="Проверьте соединение и попробуйте ещё раз"
      >
        <template #action>
          <VButton variant="primary" @click="loadStats">Повторить</VButton>
        </template>
      </VEmptyState>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VStatCard, VLoader, VEmptyState, VButton } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { getAdminStats } from '@/api/admin'
import type { AdminStatsResponse } from '@/api/admin'
import { ApiResponseError } from '@/api/client'

const router = useRouter()
const toast = useToast()

const stats = ref<AdminStatsResponse | null>(null)
const loading = ref(false)

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

/* -- Alert banner -- */
.admin-dashboard__alert {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-warning-bg);
  border: 1px solid var(--velo-warning-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.admin-dashboard__alert:hover {
  background: var(--velo-warning-bg-hover);
}

.admin-dashboard__alert-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.admin-dashboard__alert-body {
  flex: 1;
}

.admin-dashboard__alert-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--velo-warning-text);
}

.admin-dashboard__alert-sub {
  font-size: var(--text-xs);
  color: var(--velo-warning-text-light);
  margin-top: 2px;
}

.admin-dashboard__alert-arrow {
  color: var(--velo-warning-text);
  font-weight: 600;
  flex-shrink: 0;
}

/* -- Stats grid -- */
.admin-dashboard__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

/* -- Quick actions -- */
.admin-dashboard__section-title {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--velo-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.admin-dashboard__actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.admin-dashboard__action-card {
  background: var(--velo-bg-card);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-2);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  transition: all var(--transition-base);
}

.admin-dashboard__action-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.admin-dashboard__action-icon {
  font-size: 24px;
}

.admin-dashboard__action-label {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--velo-text-secondary);
  text-align: center;
}

/* -- Loader -- */
.admin-dashboard__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}
</style>
