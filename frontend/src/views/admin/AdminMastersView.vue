<!--
  VELO Frontend -- AdminMastersView (Phase F8.2, updated F8-fix S-4)

  List of pending master applications.
  Click on a card -> AdminMasterReviewView with master data in router state.

  S-4: added separate `error` ref; on fetch failure shows VEmptyState with
  retry button instead of silently showing empty "Все заявки обработаны".
-->

<template>
  <div class="admin-masters">
    <VHeader title="Заявки мастеров" />

    <div class="admin-masters__content">
      <!-- Loading: initial -->
      <div
        v-if="loading"
        class="admin-masters__loader"
      >
        <VLoader size="lg" />
      </div>

      <!-- Fetch error -->
      <VEmptyState
        v-else-if="error"
        icon="⚠️"
        title="Не удалось загрузить заявки"
        description="Проверьте соединение и попробуйте ещё раз"
      >
        <template #action>
          <VButton
            variant="primary"
            @click="loadInitial"
          >
            Повторить
          </VButton>
        </template>
      </VEmptyState>

      <!-- Empty state (genuine) -->
      <VEmptyState
        v-else-if="items.length === 0"
        icon="✅"
        title="Новых заявок нет"
        description="Все заявки обработаны"
      />

      <template v-else>
        <!-- Count -->
        <div class="admin-masters__count">
          Ожидают верификации: <strong>{{ total }}</strong>
        </div>

        <!-- List -->
        <div class="admin-masters__list">
          <div
            v-for="item in items"
            :key="item.id"
            class="admin-masters__card"
            role="button"
            tabindex="0"
            @click="openReview(item)"
            @keydown.enter.space.prevent="openReview(item)"
          >
            <VAvatar
              :name="masterDisplayName(item)"
              :url="item.avatar_url ?? undefined"
              size="md"
            />
            <div class="admin-masters__card-body">
              <div class="admin-masters__card-name">
                {{ masterDisplayName(item) }}
              </div>
              <div class="admin-masters__card-meta">
                <VBadge :variant="masterStatusVariant(item.master_status)">
                  {{ masterStatusLabel(item.master_status) }}
                </VBadge>
              </div>
            </div>
            <span class="admin-masters__card-arrow">→</span>
          </div>
        </div>

        <!-- Load more -->
        <div
          v-if="hasMore"
          class="admin-masters__load-more"
        >
          <VButton
            variant="outline"
            block
            :loading="loadingMore"
            @click="loadMore"
          >
            Показать ещё
          </VButton>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VAvatar, VBadge, VButton, VLoader, VEmptyState } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { getPendingMasters } from '@/api/admin'
import type { AdminMasterListItem } from '@/api/admin'
import { ApiResponseError } from '@/api/client'
import {
  masterDisplayName,
  masterStatusVariant,
  masterStatusLabel,
} from '@/utils/adminHelpers'

const LIMIT = 20

const router = useRouter()
const toast = useToast()

const items = ref<AdminMasterListItem[]>([])
const total = ref(0)
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(false)
// S-4: separate error state so retry button is shown instead of empty state.
const error = ref(false)

async function loadInitial(): Promise<void> {
  loading.value = true
  error.value = false
  try {
    const res = await getPendingMasters(LIMIT, 0)
    items.value = res.items
    total.value = res.total
    hasMore.value = res.items.length < res.total
  } catch (e) {
    error.value = true
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки заявок'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

async function loadMore(): Promise<void> {
  loadingMore.value = true
  try {
    const res = await getPendingMasters(LIMIT, items.value.length)
    items.value.push(...res.items)
    hasMore.value = items.value.length < res.total
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки'
    toast.error(msg)
  } finally {
    loadingMore.value = false
  }
}

function openReview(item: AdminMasterListItem): void {
  router.push({
    name: 'admin-master-review',
    params: { id: item.id },
    state: { master: JSON.parse(JSON.stringify(item)) },
  })
}

onMounted(loadInitial)
</script>

<style scoped>
.admin-masters {
  min-height: 100dvh;
}

.admin-masters__content {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.admin-masters__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

.admin-masters__count {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.admin-masters__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.admin-masters__card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.admin-masters__card:active {
  opacity: 0.8;
}

.admin-masters__card-body {
  flex: 1;
  min-width: 0;
}

.admin-masters__card-name {
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.admin-masters__card-meta {
  margin-top: var(--space-1);
}

.admin-masters__card-arrow {
  color: var(--text-muted);
  flex-shrink: 0;
}

.admin-masters__load-more {
  padding-top: var(--space-2);
}
</style>
