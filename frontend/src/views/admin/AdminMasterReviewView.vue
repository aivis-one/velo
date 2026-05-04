<!--
  VELO Frontend -- AdminMasterReviewView (Phase F8.2 fixed S-1/S-2; refreshed S4 P15 C70)

  Review a master application: show available data + verify / reject actions.

  S-1/S-2: after verify/reject use router.push({ name: 'admin-masters' })
  instead of router.back(). This guarantees a fresh mount of AdminMastersView
  and a fresh loadInitial() call -- no stale pending count shown.

  Path Y MEDIUM (#047). No emojis (#048): IconCheck/IconClose icons; Callout
  amber for missing application-data placeholder.

  DEGRADED v1: AdminMasterListItem type only exposes id/telegram_id/role/
  is_active/master_status/name/avatar — no bio/methods/experience/certifications.
  Backend extension queued (BACKLOG #104 candidate). Renders available fields
  with Callout note for missing application content.
-->

<template>
  <div class="review">
    <VHeader
      title="Заявка мастера"
      :show-back="true"
      @back="router.back()"
    />

    <div class="review__content">
      <!-- Loading fallback -->
      <div
        v-if="loading"
        class="review__loader"
      >
        <VLoader size="lg" />
      </div>

      <template v-else-if="master">
        <!-- Profile card -->
        <div class="review__profile">
          <VAvatar
            :name="masterDisplayName(master)"
            :url="master.avatar_url ?? undefined"
            size="xl"
          />
          <div class="review__profile-info">
            <div class="review__profile-name">
              {{ masterDisplayName(master) }}
            </div>
            <VBadge :variant="masterStatusVariant(master.master_status)">
              {{ masterStatusLabel(master.master_status) }}
            </VBadge>
          </div>
        </div>

        <!-- Meta info -->
        <div class="review__section">
          <div class="review__section-title">
            Информация
          </div>
          <div class="review__meta-list">
            <div class="review__meta-row">
              <span class="review__meta-key">Telegram ID</span>
              <span class="review__meta-val">{{ master.telegram_id ?? '—' }}</span>
            </div>
            <div class="review__meta-row">
              <span class="review__meta-key">Роль</span>
              <span class="review__meta-val">{{ master.role }}</span>
            </div>
            <div class="review__meta-row">
              <span class="review__meta-key">Статус аккаунта</span>
              <span class="review__meta-val">
                {{ master.is_active ? 'Активен' : 'Заблокирован' }}
              </span>
            </div>
            <div class="review__meta-row">
              <span class="review__meta-key">Статус заявки</span>
              <span class="review__meta-val">
                {{ masterStatusLabel(master.master_status) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Note: limited data placeholder (BACKLOG #104) -->
        <Callout
          variant="amber"
          :icon="IconQuestion"
          title="Расширенные данные заявки"
        >
          Биография, методы, опыт и сертификаты пока недоступны в admin-API.
          Расширение бэкенда поставлено в очередь.
        </Callout>

        <!-- Actions: only for pending applications -->
        <template v-if="master.master_status === 'pending'">
          <VButton
            variant="primary"
            block
            :loading="verifying"
            :disabled="anyLoading"
            @click="confirmVerify = true"
          >
            Верифицировать
          </VButton>

          <div
            v-if="!showRejectForm"
            class="review__reject-toggle"
          >
            <VButton
              variant="danger"
              block
              :disabled="anyLoading"
              @click="showRejectForm = true"
            >
              Отклонить
            </VButton>
          </div>

          <div
            v-else
            class="review__reject-form"
          >
            <VTextarea
              v-model="rejectReason"
              label="Причина отказа *"
              placeholder="Укажите причину отклонения заявки"
              :rows="3"
              :error="rejectError"
            />
            <div class="review__reject-actions">
              <VButton
                variant="danger"
                :loading="rejecting"
                :disabled="anyLoading"
                @click="onReject"
              >
                Подтвердить отказ
              </VButton>
              <VButton
                variant="ghost"
                :disabled="anyLoading"
                @click="cancelReject"
              >
                Отмена
              </VButton>
            </div>
          </div>
        </template>

        <!-- Already processed -->
        <div
          v-else
          class="review__processed"
        >
          Заявка уже обработана — статус:
          <strong>{{ masterStatusLabel(master.master_status) }}</strong>
        </div>
      </template>

      <!-- Not found -->
      <VEmptyState
        v-else
        title="Заявка не найдена"
        description="Возможно, она была удалена или уже обработана"
      />
    </div>

    <!-- Verify confirm modal -->
    <ConfirmModal
      v-model:visible="confirmVerify"
      :loading="verifying"
      title="Подтвердить мастера"
      message="Действие необратимо. Мастер получит роль MASTER и сможет публиковать практики."
      confirm-label="Верифицировать"
      @confirm="onVerify"
      @cancel="confirmVerify = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import {
  VAvatar,
  VBadge,
  VButton,
  VTextarea,
  VLoader,
  VEmptyState,
} from '@/components/ui'
import { IconQuestion } from '@/components/icons'
import Callout from '@/components/shared/Callout.vue'
import ConfirmModal from '@/components/shared/ConfirmModal.vue'
import { useToast } from '@/composables/useToast'
import { getMasterById, verifyMaster, rejectMaster } from '@/api/admin'
import type { AdminMasterListItem } from '@/api/admin'
import { ApiResponseError } from '@/api/client'
import {
  masterDisplayName,
  masterStatusVariant,
  masterStatusLabel,
} from '@/utils/adminHelpers'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const masterId = route.params.id as string

const master = ref<AdminMasterListItem | null>(null)
const loading = ref(false)
const verifying = ref(false)
const rejecting = ref(false)
const showRejectForm = ref(false)
const rejectReason = ref('')
const rejectError = ref('')
const confirmVerify = ref(false)

const anyLoading = computed(() => verifying.value || rejecting.value)

async function loadMaster(): Promise<void> {
  const stateData = (history.state as { master?: AdminMasterListItem }).master
  if (stateData && stateData.id === masterId) {
    master.value = stateData
    return
  }
  loading.value = true
  try {
    master.value = await getMasterById(masterId)
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка загрузки данных'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

async function onVerify(): Promise<void> {
  if (verifying.value) return
  verifying.value = true
  try {
    await verifyMaster(masterId)
    toast.success('Мастер верифицирован')
    confirmVerify.value = false
    // S-1/S-2: push to list instead of back() -- guarantees fresh loadInitial().
    router.push({ name: 'admin-masters' })
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка верификации'
    toast.error(msg)
  } finally {
    verifying.value = false
  }
}

async function onReject(): Promise<void> {
  // W-6: guard before validation.
  if (rejecting.value) return
  rejectError.value = ''
  if (!rejectReason.value.trim()) {
    rejectError.value = 'Укажите причину отказа'
    return
  }
  rejecting.value = true
  try {
    await rejectMaster(masterId, rejectReason.value.trim())
    toast.success('Заявка отклонена')
    // S-1/S-2: push to list instead of back() -- guarantees fresh loadInitial().
    router.push({ name: 'admin-masters' })
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка при отклонении'
    toast.error(msg)
  } finally {
    rejecting.value = false
  }
}

function cancelReject(): void {
  showRejectForm.value = false
  rejectReason.value = ''
  rejectError.value = ''
}

onMounted(loadMaster)
</script>

<style scoped>
.review {
  min-height: 100dvh;
}

.review__content {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.review__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

.review__profile {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.review__profile-name {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.review__section-title {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}

.review__meta-list {
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.review__meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.review__meta-row:last-child {
  border-bottom: none;
}

.review__meta-key {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.review__meta-val {
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--text-primary);
}

.review__reject-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.review__reject-actions {
  display: flex;
  gap: var(--space-2);
}

.review__processed {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--text-muted);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border-radius: var(--radius-lg);
}
</style>
