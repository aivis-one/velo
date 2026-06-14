<!--
  VELO Frontend -- AdminMasterReviewView (Admin DS rebuild 2026-06-14, operator SVGs
  "2 Master's request" ×5)

  Master-application review (admin). Reached by tapping a card in the «Мастера» tab
  (admin-master-review); the master is handed via router state, with getMasterById as
  fallback. Rebuilt to the operator design, replacing the F8.2 layout:
    profile (avatar photo / IconIdCard glyph) → «Информация» (Направление/Вид editable,
    Опыт/Язык/О себе read) → «Документы» (verified file rows) → «История заявок»
    (accordion) → sticky footer Отклонить / Одобрить.

  DATA. Real: name · avatar · status · verify (verifyMaster) / reject (rejectMaster —
  reason collected in a DS bottom-sheet, operator fork п.1=А 2026-06-14).
  STUB «—»/empty (honest skeleton, operator В): direction · type · experience · language ·
  bio · documents · history · email are NOT in AdminMasterListItem, so they render «—» /
  empty until Zod extends GET /admin/masters/:id. Editing Направление/Вид has no save
  endpoint → «ОК» toasts «недоступно» (build-full-design-now). Roadmap (Zod): extend the
  master-detail endpoint (profile fields + documents[] + submission history + email) +
  an admin edit-master-fields endpoint.

  Footer only for master_status==='pending'; processed applications show a note. After
  verify/reject → router.push({ name: 'admin-masters' }) (S-1/S-2: fresh list mount).
-->

<template>
  <div class="mreview">
    <header class="mreview__top">
      <VBackButton @click="router.back()" />
      <span class="mreview__title">Заявка мастера</span>
    </header>

    <div v-if="loading" class="mreview__loader"><VLoader size="lg" /></div>

    <template v-else-if="master">
      <!-- Profile -->
      <VCard class="mreview__profile" padding="none">
        <img
          v-if="master.avatar_url"
          :src="master.avatar_url"
          :alt="displayName"
          class="mreview__photo"
        />
        <span v-else class="mreview__glyph"><IconIdCard :size="104" /></span>
        <div class="mreview__name">{{ displayName }}</div>
        <div class="mreview__email">{{ email }}</div>
      </VCard>

      <!-- Информация -->
      <div class="mreview__seclabel">Информация</div>
      <VCard class="mreview__info" padding="none">
        <!-- Направление (editable stub) -->
        <div class="mreview__row">
          <div class="mreview__k">Направление</div>
          <div v-if="editing === 'direction'" class="mreview__edit">
            <VInput v-model="directionDraft" />
            <button type="button" class="mreview__ok" @click="saveEdit">ОК</button>
          </div>
          <template v-else>
            <div class="mreview__v">{{ direction }}</div>
            <button
              type="button"
              class="mreview__pen"
              aria-label="Изменить направление"
              @click="startEdit('direction')"
            >
              <IconEdit :size="22" />
            </button>
          </template>
        </div>

        <!-- Вид (editable stub) -->
        <div class="mreview__row">
          <div class="mreview__k">Вид</div>
          <div v-if="editing === 'kind'" class="mreview__edit">
            <VInput v-model="kindDraft" />
            <button type="button" class="mreview__ok" @click="saveEdit">ОК</button>
          </div>
          <template v-else>
            <div class="mreview__v">{{ kind }}</div>
            <button
              type="button"
              class="mreview__pen"
              aria-label="Изменить вид"
              @click="startEdit('kind')"
            >
              <IconEdit :size="22" />
            </button>
          </template>
        </div>

        <div class="mreview__row">
          <div class="mreview__k">Опыт</div>
          <div class="mreview__v">{{ experience }}</div>
        </div>
        <div class="mreview__row">
          <div class="mreview__k">Язык практик</div>
          <div class="mreview__v">{{ language }}</div>
        </div>
        <div class="mreview__row">
          <div class="mreview__k">О себе</div>
          <div class="mreview__v mreview__v--bio">{{ bio }}</div>
        </div>
      </VCard>

      <!-- Документы -->
      <div class="mreview__seclabel">Документы</div>
      <VCard v-if="documents.length" class="mreview__docs" padding="none">
        <div v-for="d in documents" :key="d.name" class="mreview__doc">
          <span class="mreview__doc-chk">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.9" />
              <path
                d="M7.5 12.5l3 3L17 9"
                stroke="currentColor"
                stroke-width="1.9"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>
          <span class="mreview__doc-name">{{ d.name }}</span>
          <button
            type="button"
            class="mreview__doc-eye"
            aria-label="Посмотреть документ"
            @click="viewDoc"
          >
            <IconView :size="22" />
          </button>
        </div>
      </VCard>
      <VCard v-else><p class="mreview__empty">Документы не приложены</p></VCard>

      <!-- История заявок -->
      <VCard class="mreview__hist" padding="none">
        <button
          type="button"
          class="mreview__acc"
          :aria-expanded="historyOpen"
          @click="historyOpen = !historyOpen"
        >
          <span class="mreview__acc-ic"><IconClock :size="20" /></span>
          <span class="mreview__acc-t">История заявок</span>
          <svg
            class="mreview__acc-ch"
            :class="{ 'mreview__acc-ch--open': historyOpen }"
            width="20"
            height="12"
            viewBox="0 0 24 14"
            fill="none"
          >
            <path
              d="M2 2l10 10L22 2"
              stroke="currentColor"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
        <div v-if="historyOpen" class="mreview__acc-body">
          <div v-for="(h, i) in history" :key="i" class="mreview__hist-entry">
            <div class="mreview__hist-when">{{ h.when }}</div>
            <div class="mreview__hist-title">{{ h.title }}</div>
            <div v-if="h.comment" class="mreview__hist-q">«{{ h.comment }}»</div>
          </div>
          <p v-if="!history.length" class="mreview__first">Заявка подаётся впервые.</p>
        </div>
      </VCard>

      <!-- Actions -->
      <div v-if="isPending" class="mreview__foot">
        <VButton variant="ghost" :disabled="anyLoading" @click="openReject">Отклонить</VButton>
        <VButton variant="primary" :loading="verifying" :disabled="anyLoading" @click="onVerify">
          Одобрить
        </VButton>
      </div>
      <VCard v-else class="mreview__processed">
        Заявка уже обработана — статус: <strong>{{ statusLabel }}</strong>
      </VCard>
    </template>

    <!-- Not found -->
    <VEmptyState
      v-else
      icon="notfound"
      title="Заявка не найдена"
      description="Возможно, она была удалена или уже обработана"
    />

    <!-- Reject reason (bottom-sheet, fork п.1=А) -->
    <VBottomSheet
      :open="showReject"
      title="Причина отказа"
      save-label="Отклонить заявку"
      @save="onReject"
      @close="closeReject"
    >
      <VTextarea
        v-model="rejectReason"
        placeholder="Укажите причину отклонения заявки"
        :rows="3"
        :error="rejectError"
      />
    </VBottomSheet>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  VBackButton,
  VCard,
  VInput,
  VTextarea,
  VButton,
  VLoader,
  VEmptyState,
  VBottomSheet,
} from '@/components/ui'
import { IconIdCard, IconEdit, IconView, IconClock } from '@/components/icons'
import { useToast } from '@/composables/useToast'
import { getMasterById, verifyMaster, rejectMaster } from '@/api/admin'
import type { AdminMasterListItem } from '@/api/admin'
import { ApiResponseError } from '@/api/client'
import { masterDisplayName, masterStatusLabel } from '@/utils/adminHelpers'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const masterId = route.params.id as string

const master = ref<AdminMasterListItem | null>(null)
const loading = ref(false)
const verifying = ref(false)
const rejecting = ref(false)

// Inline edit (stub — no save endpoint yet, see header note → Zod).
const editing = ref<'direction' | 'kind' | null>(null)
const directionDraft = ref('')
const kindDraft = ref('')

// Reject reason sheet.
const showReject = ref(false)
const rejectReason = ref('')
const rejectError = ref('')

// History accordion.
const historyOpen = ref(false)

// Honest skeleton (operator В): rich fields are not on AdminMasterListItem → «—» /
// empty until Zod extends the endpoint. Sample data lives in the design preview only.
const PLACEHOLDER = '—'
const displayName = computed<string>(() => (master.value ? masterDisplayName(master.value) : ''))
const email = computed<string>(() => PLACEHOLDER)
const direction = computed<string>(() => PLACEHOLDER)
const kind = computed<string>(() => PLACEHOLDER)
const experience = computed<string>(() => PLACEHOLDER)
const language = computed<string>(() => PLACEHOLDER)
const bio = computed<string>(() => PLACEHOLDER)
const documents = ref<{ name: string }[]>([])
const history = ref<{ when: string; title: string; comment?: string }[]>([])

const isPending = computed<boolean>(() => master.value?.master_status === 'pending')
const statusLabel = computed<string>(() =>
  master.value ? masterStatusLabel(master.value.master_status) : '',
)
const anyLoading = computed<boolean>(() => verifying.value || rejecting.value)

async function loadMaster(): Promise<void> {
  // Handed via router state by the list (our `history` ref shadows the global
  // History, so reach it through window.history.state).
  const handed = (window.history.state as { master?: AdminMasterListItem }).master
  if (handed && handed.id === masterId) {
    master.value = handed
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

function startEdit(field: 'direction' | 'kind'): void {
  editing.value = field
  if (field === 'direction') directionDraft.value = direction.value
  else kindDraft.value = kind.value
}

// Stub: admin editing of master profile fields has no backend yet → Zod.
function saveEdit(): void {
  editing.value = null
  toast.info('Редактирование пока недоступно')
}

// Stub: document viewing has no backend yet → Zod (documents are empty until then).
function viewDoc(): void {
  toast.info('Просмотр документа пока недоступен')
}

function openReject(): void {
  rejectReason.value = ''
  rejectError.value = ''
  showReject.value = true
}

function closeReject(): void {
  showReject.value = false
}

async function onVerify(): Promise<void> {
  if (anyLoading.value) return
  verifying.value = true
  try {
    await verifyMaster(masterId)
    toast.success('Мастер верифицирован')
    // S-1/S-2: push to the list (fresh mount) instead of back().
    router.push({ name: 'admin-masters' })
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка верификации'
    toast.error(msg)
  } finally {
    verifying.value = false
  }
}

async function onReject(): Promise<void> {
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
    showReject.value = false
    // S-1/S-2: push to the list (fresh mount) instead of back().
    router.push({ name: 'admin-masters' })
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Ошибка при отклонении'
    toast.error(msg)
  } finally {
    rejecting.value = false
  }
}

onMounted(loadMaster)
</script>

<style scoped>
.mreview {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.mreview__top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 44px;
}

.mreview__title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.mreview__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

/* -- Profile -- */
.mreview__profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-5) var(--space-4);
}

.mreview__photo {
  width: 104px;
  height: 104px;
  border-radius: 14px;
  object-fit: cover;
  margin-bottom: var(--space-2);
}

.mreview__glyph {
  display: flex;
  color: var(--velo-blue-200);
  margin-bottom: var(--space-2);
}

.mreview__name {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.mreview__email {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: 0.02em;
}

/* -- Section label -- */
.mreview__seclabel {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 2px 2px -6px;
}

/* -- Информация -- */
.mreview__info {
  padding: var(--space-1) 18px;
}

.mreview__row {
  position: relative;
  padding: var(--space-3) 0;
}

.mreview__row + .mreview__row {
  border-top: 1px solid var(--velo-border);
}

.mreview__k {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: 0.02em;
}

.mreview__v {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-top: 3px;
}

.mreview__v--bio {
  line-height: 1.35;
}

.mreview__pen {
  position: absolute;
  top: var(--space-3);
  right: 0;
  display: flex;
  padding: 0;
  background: none;
  border: none;
  color: var(--velo-primary);
  cursor: pointer;
}

.mreview__edit {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-1);
}

.mreview__edit :deep(.v-input) {
  flex: 1;
  min-width: 0;
  margin-bottom: 0;
}

.mreview__ok {
  flex-shrink: 0;
  width: 60px;
  height: 41px;
  border-radius: 5px;
  background: var(--velo-primary);
  color: var(--velo-white);
  border: none;
  font-family: var(--font-body);
  font-size: var(--text-lg);
  letter-spacing: 0.02em;
  cursor: pointer;
}

/* -- Документы -- */
.mreview__docs {
  display: flex;
  flex-direction: column;
  gap: 11px;
  padding: var(--space-3) 15px;
}

.mreview__doc {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 44px;
  padding: 0 14px;
  border-radius: 9px;
  background: var(--velo-glass-teal-30);
  border: 1px solid var(--velo-teal-400);
  color: var(--velo-teal-700);
}

.mreview__doc-chk {
  display: flex;
  flex-shrink: 0;
}

.mreview__doc-name {
  flex: 1;
  min-width: 0;
  font-size: var(--text-base);
  letter-spacing: 0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mreview__doc-eye {
  display: flex;
  flex-shrink: 0;
  padding: 0;
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
}

.mreview__empty {
  margin: 0;
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  padding: var(--space-3) var(--space-2);
}

/* -- История заявок (accordion) -- */
.mreview__hist {
  overflow: hidden;
}

.mreview__acc {
  display: flex;
  align-items: center;
  gap: 21px;
  width: 100%;
  padding: 15px 18px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
}

.mreview__acc-ic {
  display: flex;
  flex-shrink: 0;
  color: var(--velo-text-primary);
}

.mreview__acc-t {
  flex: 1;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.mreview__acc-ch {
  flex-shrink: 0;
  color: var(--velo-text-primary);
  transition: transform var(--transition-fast);
}

.mreview__acc-ch--open {
  transform: rotate(180deg);
}

.mreview__acc-body {
  padding: 0 16px 16px;
}

.mreview__hist-entry {
  background: var(--velo-warning-bg);
  border-radius: var(--radius-md);
  padding: 18px 15px;
}

.mreview__hist-entry + .mreview__hist-entry {
  margin-top: var(--space-2);
}

.mreview__hist-when {
  font-size: var(--text-xs);
  color: var(--velo-peach-500);
  letter-spacing: 0.02em;
}

.mreview__hist-title {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin-top: var(--space-2);
}

.mreview__hist-q {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: 0.02em;
  margin-top: 6px;
  line-height: 1.35;
}

.mreview__first {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  letter-spacing: 0.02em;
}

/* -- Sticky action footer (pending only) -- */
.mreview__foot {
  position: sticky;
  bottom: 0;
  z-index: var(--z-sticky);
  display: flex;
  gap: 15px;
  margin-top: var(--space-1);
  padding: var(--space-3) 0;
  /* Soft scrim so the content fades under the floating glass buttons. */
  background: linear-gradient(to top, var(--velo-bg-start) 55%, transparent);
}

.mreview__foot :deep(.v-btn) {
  flex: 1;
}

/* -- Processed (non-pending) note -- */
.mreview__processed {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
}
</style>
