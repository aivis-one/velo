<!--
  VELO Frontend -- EditPracticeView (Phase F6.2 + F6.3, fixed W-2..W-9)

  Edit an existing practice and trigger state machine transitions.
  Protected by masterStatusGuard. Rendered inside MasterShell.

  Load order:
    1. Try masterStore.practices cache (instant if already loaded)
    2. Fallback: GET /api/v1/practices/:id

  Editable fields (draft / scheduled only -- completed/cancelled are readonly):
    title, description, what_to_prepare, contraindications,
    scheduled_at (date+time), duration_minutes,
    timezone, max_participants, is_free, price_cents, zoom_link

  State machine action buttons (below form):
    draft      -> "Опубликовать"  PATCH status=scheduled
                  "Удалить"       DELETE  (soft-delete, draft only)
    scheduled  -> "Начать эфир"   PATCH status=live
                  "Отменить"      POST /cancel (+ confirm dialog)
    live       -> "Завершить"     POST /finalize (+ confirm dialog)
                  "Отменить"      POST /cancel   (+ confirm dialog)
    completed / cancelled / deleted -> readonly info banner

  After any successful mutation:
    - refreshMyPractices() to invalidate cache
    - navigate back to master-practices

  Fixes:
    W-2: DURATION_OPTIONS / TIMEZONE_OPTIONS imported from @/utils/practiceOptions
    W-3: anyLoading computed = saving || transitioning || cancelling || deleting.
         All action buttons and Save use :disabled="anyLoading" -- prevents
         concurrent save + publish / save + cancel / etc.
    W-5: confirm dialog overlay click blocked while confirmDialog.loading is true
    W-6: priceCents uses eurStringToCents() -- no float arithmetic.
         populateForm uses centsToEurString() -- no float precision issues.
    W-8: date input has :min="todayDate" to prevent setting past dates
    W-9: commission calc uses COMMISSION_RATE from @/utils/commission
-->

<template>
  <div class="edit-practice">
    <VHeader
      title="Редактировать"
      show-back
      @back="router.push({ name: 'master-practices' })"
    />

    <!-- Loading -->
    <div v-if="loading" class="edit-practice__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error / not found -->
    <div v-else-if="!practice" class="edit-practice__content">
      <VEmptyState icon="⚠️" title="Практика не найдена">
        <VButton size="sm" variant="outline" @click="router.push({ name: 'master-practices' })">
          Назад
        </VButton>
      </VEmptyState>
    </div>

    <template v-else>
      <!-- ================================================================
           READONLY BANNER for terminal statuses
           ================================================================ -->
      <div v-if="isTerminal" class="edit-practice__readonly-banner">
        <VBadge :variant="statusVariant(practice.status)">
          {{ statusLabel(practice.status) }}
        </VBadge>
        <span class="edit-practice__readonly-text">Редактирование недоступно</span>
      </div>

      <div class="edit-practice__content">
        <!-- ================================================================
             FORM (editable for draft / scheduled only)
             ================================================================ -->
        <fieldset :disabled="isTerminal || saving" class="edit-practice__fieldset">

          <div class="edit-practice__section">
            <div class="edit-practice__section-title">📝 ОСНОВНОЕ</div>
            <VInput
              v-model="form.title"
              label="Название *"
              :error="errors.title"
            />
            <!-- practice_type is immutable after creation -->
            <div class="edit-practice__field">
              <label class="edit-practice__label">Тип практики</label>
              <span class="edit-practice__readonly-value">
                {{ practiceTypeLabel(practice.practice_type) }}
              </span>
            </div>

            <VSelect
              v-model="form.direction"
              label="Направление *"
              :options="DIRECTION_OPTIONS"
              @update:modelValue="onDirectionChange"
            />

            <VSelect
              v-model="form.difficulty"
              label="Сложность *"
              :options="DIFFICULTY_OPTIONS"
            />

            <VSelect
              v-if="styleOptionsForForm.length > 0"
              v-model="form.style"
              label="Вид практики"
              :options="styleSelectOptions"
            />
          </div>

          <div class="edit-practice__section">
            <div class="edit-practice__section-title">📅 РАСПИСАНИЕ</div>

            <!-- W-8: min attribute prevents setting past dates -->
            <VInput
              v-model="form.date"
              label="Дата"
              type="date"
              :min="todayDate"
              :disabled="isTerminal"
            />

            <VInput
              v-model="form.time"
              label="Время"
              type="time"
              :disabled="isTerminal"
            />

            <VSelect
              v-model="form.duration_minutes"
              label="Длительность"
              :options="DURATION_OPTIONS"
            />

            <VSelect
              v-model="form.timezone"
              label="Часовой пояс"
              :options="TIMEZONE_OPTIONS"
            />
          </div>

          <div class="edit-practice__section">
            <div class="edit-practice__section-title">👥 УЧАСТНИКИ</div>
            <VInput
              v-model="form.max_participants_raw"
              label="Максимум (пусто = без ограничений)"
              type="number"
              :error="errors.max_participants"
            />
          </div>

          <div class="edit-practice__section">
            <div class="edit-practice__section-title">💰 ЦЕНА</div>
            <VSegment
              :model-value="form.is_free ? 'free' : 'paid'"
              :options="PAYMENT_OPTIONS"
              @update:model-value="form.is_free = $event === 'free'"
            />
            <template v-if="!form.is_free">
              <VInput
                v-model="form.price_eur_raw"
                label="Цена (EUR)"
                type="number"
                :error="errors.price_cents"
              />
              <!-- W-9: commission calc via COMMISSION_RATE constant -->
              <VCard v-if="priceCents > 0" class="edit-practice__price-calc" padding="none">
                <div class="edit-practice__price-row">
                  <span>Комиссия {{ commissionPct }}%</span>
                  <span>{{ formatMoney(Math.round(priceCents * COMMISSION_RATE), 'EUR') }}</span>
                </div>
                <div class="edit-practice__price-row edit-practice__price-row--total">
                  <span>Вы получите</span>
                  <span>{{ formatMoney(Math.round(priceCents * (1 - COMMISSION_RATE)), 'EUR') }}</span>
                </div>
              </VCard>
            </template>
          </div>

          <div class="edit-practice__section">
            <div class="edit-practice__section-title">📝 ОПИСАНИЕ</div>
            <VTextarea
              v-model="form.description"
              label="Описание"
              :rows="4"
            />
            <VTextarea
              v-model="form.what_to_prepare"
              label="Что подготовить"
              placeholder="Коврик, удобная одежда, вода..."
              :rows="2"
            />
            <VTextarea
              v-model="form.contraindications"
              label="Противопоказания"
              placeholder="Беременность, заболевания позвоночника..."
              :rows="2"
            />
          </div>

          <div class="edit-practice__section">
            <div class="edit-practice__section-title">🔗 ПОДКЛЮЧЕНИЕ</div>
            <VInput
              v-model="form.zoom_link"
              label="Zoom ссылка"
              type="url"
              :error="errors.zoom_link"
            />
          </div>

          <!-- Save button (not shown for terminal statuses) -->
          <!-- W-3: :disabled="anyLoading" prevents Save while action is running -->
          <VButton
            v-if="!isTerminal"
            variant="secondary"
            block
            :loading="saving"
            :disabled="anyLoading"
            @click="save"
          >
            Сохранить изменения
          </VButton>
        </fieldset>

        <!-- ================================================================
             STATE MACHINE ACTIONS
             W-3: all buttons :disabled="anyLoading" -- prevents concurrent
             save + publish / save + cancel / save + delete etc.
             ================================================================ -->
        <div v-if="!isTerminal" class="edit-practice__actions">
          <div class="edit-practice__section-title">⚡ ДЕЙСТВИЯ</div>

          <!-- draft -> scheduled -->
          <VButton
            v-if="practice.status === 'draft'"
            variant="primary"
            block
            :loading="transitioning"
            :disabled="anyLoading"
            @click="publish"
          >
            ▶️ Опубликовать практику
          </VButton>

          <!-- scheduled -> live -->
          <VButton
            v-if="practice.status === 'scheduled'"
            variant="primary"
            block
            :loading="transitioning"
            :disabled="anyLoading"
            @click="startLive"
          >
            🎬 Начать эфир
          </VButton>

          <!-- live -> completed (finalize) -->
          <VButton
            v-if="practice.status === 'live'"
            variant="primary"
            block
            :loading="transitioning"
            :disabled="anyLoading"
            @click="confirmFinalize"
          >
            ✅ Завершить практику
          </VButton>

          <!-- scheduled / live -> attendance -->
          <VButton
            v-if="practice.status === 'live' || practice.status === 'scheduled'"
            variant="outline"
            block
            :disabled="anyLoading"
            @click="router.push({ name: 'master-attendance', params: { id: practice.id } })"
          >
            👥 Посещаемость
          </VButton>

          <!-- draft -> deleted -->
          <VButton
            v-if="practice.status === 'draft'"
            variant="danger"
            block
            :loading="deleting"
            :disabled="anyLoading"
            @click="confirmDelete"
          >
            🗑 Удалить черновик
          </VButton>

          <!-- scheduled / live -> cancelled -->
          <VButton
            v-if="practice.status === 'scheduled' || practice.status === 'live'"
            variant="danger"
            block
            :loading="cancelling"
            :disabled="anyLoading"
            @click="confirmCancel"
          >
            ❌ Отменить практику
          </VButton>
        </div>

        <!-- Attendance link for completed -->
        <div v-if="practice.status === 'completed'" class="edit-practice__actions">
          <VButton
            variant="outline"
            block
            @click="router.push({ name: 'master-attendance', params: { id: practice.id } })"
          >
            👥 Посещаемость
          </VButton>
        </div>
      </div>

      <!-- W-5: cancel/overlay blocked while confirmDialog.loading is true (VConfirmDialog) -->
      <VConfirmDialog
        :open="confirmDialog.visible"
        :message="confirmDialog.message"
        :confirm-label="confirmDialog.confirmLabel"
        :danger="confirmDialog.danger"
        :loading="confirmDialog.loading"
        @confirm="confirmDialog.onConfirm"
        @cancel="confirmDialog.visible = false"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { DateTime } from 'luxon'
import { useRoute, useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton, VInput, VTextarea, VSelect, VBadge, VLoader, VEmptyState, VCard, VSegment, VConfirmDialog } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useMasterStore } from '@/stores/master'
import {
  getPractice,
  updatePractice,
  deletePractice,
  cancelPractice,
  finalizePractice,
} from '@/api/practices'
import { formatMoney } from '@/utils/format'
import { ApiResponseError } from '@/api/client'
import {
  DURATION_OPTIONS,
  TIMEZONE_OPTIONS,
  DIRECTION_OPTIONS,
  DIFFICULTY_OPTIONS,
  stylesForDirection,
} from '@/utils/practiceOptions'
import { COMMISSION_RATE } from '@/utils/commission'
import { eurStringToCents, centsToEurString } from '@/utils/currency'
import type { PracticeResponse, PracticeType, PracticeStatus, PracticeDirection } from '@/api/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const masterStore = useMasterStore()

const practiceId = route.params.id as string

// -- Practice data --
const practice = ref<PracticeResponse | null>(null)
const loading = ref(false)

// -- Action loading states --
const saving = ref(false)
const transitioning = ref(false)
const cancelling = ref(false)
const deleting = ref(false)

// W-3: single guard covering all mutually exclusive actions.
// Every action button and the Save button use :disabled="anyLoading".
// Prevents concurrent save + publish, save + cancel, etc.
const anyLoading = computed(
  () => saving.value || transitioning.value || cancelling.value || deleting.value,
)

// -- Confirm dialog state --
const confirmDialog = reactive({
  visible: false,
  message: '',
  confirmLabel: 'Подтвердить',
  danger: false,
  loading: false,
  onConfirm: (): void => { /* filled per use */ },
})

// W-9: human-readable commission percentage for template
const commissionPct = Math.round(COMMISSION_RATE * 100)

const PAYMENT_OPTIONS = [
  { value: 'free', label: 'Бесплатно' },
  { value: 'paid', label: 'Платно' },
]

// W-8: computed so todayDate is never stale after midnight
const todayDate = computed(() => new Date().toISOString().split('T')[0])

// -- Form state (populated from practice on load) --
const form = reactive({
  title: '',
  direction: 'meditation',
  difficulty: 'beginner',
  style: '',
  date: '',
  time: '',
  duration_minutes: '60',
  timezone: 'Europe/Moscow',
  max_participants_raw: '',
  is_free: false,
  price_eur_raw: '',
  description: '',
  what_to_prepare: '',
  contraindications: '',
  zoom_link: '',
})

const errors = reactive({
  title: '',
  max_participants: '',
  price_cents: '',
  zoom_link: '',
})

// -- Derived --
const isTerminal = computed((): boolean =>
  practice.value?.status === 'completed' ||
  practice.value?.status === 'cancelled' ||
  practice.value?.status === 'deleted',
)

// W-6: use eurStringToCents() -- avoids parseFloat(raw) * 100 float precision trap.
const priceCents = computed((): number => eurStringToCents(form.price_eur_raw))

// -- Label helpers --
const PRACTICE_TYPE_LABELS: Record<PracticeType, string> = {
  live: 'Живая группа',
  series: 'Серия занятий',
  one_on_one: 'Индивидуально',
  replay: 'Запись',
}
function practiceTypeLabel(t: PracticeType): string {
  return PRACTICE_TYPE_LABELS[t] ?? t
}

const STATUS_LABELS: Record<PracticeStatus, string> = {
  draft: 'Черновик',
  scheduled: 'Запланирована',
  live: 'В эфире',
  completed: 'Завершена',
  cancelled: 'Отменена',
  deleted: 'Удалена',
}
function statusLabel(s: PracticeStatus): string {
  return STATUS_LABELS[s] ?? s
}

// Direction-conditional style options (mirror of CreatePracticeView).
const styleOptionsForForm = computed(() =>
  stylesForDirection(form.direction as PracticeDirection),
)
const styleSelectOptions = computed(() => [
  { value: '', label: 'Без вида' },
  ...styleOptionsForForm.value,
])

/** Reset style when direction changes — the previous value is likely
 *  invalid for the new direction. */
function onDirectionChange(): void {
  form.style = ''
}

function statusVariant(s: PracticeStatus): 'success' | 'warning' | 'error' | 'info' {
  switch (s) {
    case 'live':      return 'success'
    case 'scheduled': return 'info'
    case 'draft':     return 'warning'
    case 'completed': return 'info'
    default:          return 'error'
  }
}

// -- Populate form from practice --
function populateForm(p: PracticeResponse): void {
  form.title = p.title
  // Taxonomy (data.taxonomy on the backend). Older practices created before
  // the Calendar iteration may have null facets -> fall back to defaults so
  // the selects always show a valid option.
  form.direction = p.direction ?? 'meditation'
  form.difficulty = p.difficulty ?? 'beginner'
  form.style = p.style ?? ''
  // Render the stored UTC instant as wall-clock date + time in the practice's
  // OWN timezone (the one the master created it in), so the form shows the
  // same values the master originally entered -- not the editor's browser tz.
  const scheduledDt = DateTime.fromISO(p.scheduled_at, { zone: 'utc' }).setZone(
    p.timezone,
  )
  form.date = scheduledDt.toFormat('yyyy-MM-dd')
  form.time = scheduledDt.toFormat('HH:mm')
  form.duration_minutes = String(p.duration_minutes)
  form.timezone = p.timezone
  form.max_participants_raw = p.max_participants != null ? String(p.max_participants) : ''
  form.is_free = p.is_free
  // W-6: centsToEurString uses integer division + toFixed(2), no float multiplication.
  form.price_eur_raw = p.is_free ? '' : centsToEurString(p.price_cents)
  form.description = p.description ?? ''
  form.what_to_prepare = p.what_to_prepare ?? ''
  form.contraindications = p.contraindications ?? ''
  form.zoom_link = p.zoom_link ?? ''
}

// -- Load practice --
onMounted(async () => {
  const cached = masterStore.practices.find((p) => p.id === practiceId)
  if (cached) {
    practice.value = cached
    populateForm(cached)
    return
  }
  loading.value = true
  try {
    const p = await getPractice(practiceId)
    practice.value = p
    populateForm(p)
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось загрузить практику')
  } finally {
    loading.value = false
  }
})

// -- Validate --
function validate(): boolean {
  let ok = true
  errors.title = ''
  errors.max_participants = ''
  errors.price_cents = ''
  errors.zoom_link = ''

  if (!form.title.trim()) {
    errors.title = 'Введите название'
    ok = false
  }
  if (form.max_participants_raw) {
    const n = parseInt(form.max_participants_raw, 10)
    if (isNaN(n) || n < 1) {
      errors.max_participants = 'Введите положительное число или оставьте пустым'
      ok = false
    }
  }
  if (!form.is_free && priceCents.value < 100) {
    errors.price_cents = 'Минимальная цена — €1,00'
    ok = false
  }
  if (form.zoom_link && !form.zoom_link.startsWith('https://')) {
    errors.zoom_link = 'Ссылка должна начинаться с https://'
    ok = false
  }
  return ok
}

// -- Save --
async function save(): Promise<void> {
  if (!validate() || saving.value) return
  saving.value = true
  try {
    // Convert the wall-clock date + time back to a UTC instant in the
    // selected timezone (mirrors CreatePracticeView). undefined when either
    // field is empty so we don't send a bad scheduled_at.
    let scheduledAt: string | undefined
    if (form.date && form.time) {
      const dt = DateTime.fromISO(`${form.date}T${form.time}`, {
        zone: form.timezone,
      })
      if (!dt.isValid) {
        toast.error('Некорректные дата или время')
        saving.value = false
        return
      }
      scheduledAt = dt.toUTC().toISO() ?? undefined
    }

    const updated = await updatePractice(practiceId, {
      title: form.title.trim(),
      direction: form.direction,
      difficulty: form.difficulty,
      style: form.style.trim() || null,
      description: form.description.trim() || null,
      what_to_prepare: form.what_to_prepare.trim() || null,
      contraindications: form.contraindications.trim() || null,
      scheduled_at: scheduledAt ?? null,
      duration_minutes: parseInt(form.duration_minutes, 10),
      timezone: form.timezone,
      max_participants: form.max_participants_raw
        ? parseInt(form.max_participants_raw, 10)
        : null,
      zoom_link: form.zoom_link.trim() || null,
      is_free: form.is_free,
      price_cents: form.is_free ? 0 : priceCents.value,
    })
    practice.value = updated
    toast.success('Сохранено')
    await masterStore.refreshMyPractices()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Ошибка сохранения')
  } finally {
    saving.value = false
  }
}

// -- Publish: draft -> scheduled --
async function publish(): Promise<void> {
  if (anyLoading.value) return
  transitioning.value = true
  try {
    const updated = await updatePractice(practiceId, { status: 'scheduled' })
    practice.value = updated
    toast.success('Практика опубликована!')
    await masterStore.refreshMyPractices()
    router.push({ name: 'master-practices' })
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось опубликовать')
  } finally {
    transitioning.value = false
  }
}

// -- Start live: scheduled -> live --
async function startLive(): Promise<void> {
  if (anyLoading.value) return
  transitioning.value = true
  try {
    const updated = await updatePractice(practiceId, { status: 'live' })
    practice.value = updated
    toast.success('Эфир начат!')
    await masterStore.refreshMyPractices()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось начать эфир')
  } finally {
    transitioning.value = false
  }
}

// -- Confirm finalize --
function confirmFinalize(): void {
  confirmDialog.message = 'Завершить практику? Посещаемость будет зафиксирована.'
  confirmDialog.confirmLabel = 'Завершить'
  confirmDialog.danger = false
  confirmDialog.visible = true
  confirmDialog.onConfirm = finalize
}

// -- Finalize: live -> completed --
async function finalize(): Promise<void> {
  if (confirmDialog.loading) return
  confirmDialog.loading = true
  try {
    const updated = await finalizePractice(practiceId)
    practice.value = updated
    confirmDialog.visible = false
    toast.success('Практика завершена!')
    await masterStore.refreshMyPractices()
    router.push({ name: 'master-attendance', params: { id: practiceId } })
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось завершить')
  } finally {
    confirmDialog.loading = false
  }
}

// -- Confirm cancel --
function confirmCancel(): void {
  confirmDialog.message = 'Отменить практику? Все участники получат полный возврат средств.'
  confirmDialog.confirmLabel = 'Отменить практику'
  confirmDialog.danger = true
  confirmDialog.visible = true
  confirmDialog.onConfirm = cancel
}

// -- Cancel: scheduled/live -> cancelled --
async function cancel(): Promise<void> {
  if (confirmDialog.loading) return
  confirmDialog.loading = true
  try {
    const updated = await cancelPractice(practiceId)
    practice.value = updated
    confirmDialog.visible = false
    toast.success('Практика отменена, возвраты выполнены')
    await masterStore.refreshMyPractices()
    router.push({ name: 'master-practices' })
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось отменить')
  } finally {
    confirmDialog.loading = false
  }
}

// -- Confirm delete --
function confirmDelete(): void {
  confirmDialog.message = 'Удалить черновик? Это действие нельзя отменить.'
  confirmDialog.confirmLabel = 'Удалить'
  confirmDialog.danger = true
  confirmDialog.visible = true
  confirmDialog.onConfirm = remove
}

// -- Delete: draft -> deleted (soft) --
async function remove(): Promise<void> {
  if (confirmDialog.loading) return
  confirmDialog.loading = true
  try {
    await deletePractice(practiceId)
    confirmDialog.visible = false
    toast.success('Черновик удалён')
    await masterStore.refreshMyPractices()
    router.push({ name: 'master-practices' })
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось удалить')
  } finally {
    confirmDialog.loading = false
  }
}
</script>

<style scoped>
.edit-practice {
  min-height: 100%;
  background: transparent;
  display: flex;
  flex-direction: column;
}

.edit-practice__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-12) 0;
}

/* -- Readonly banner -- */
.edit-practice__readonly-banner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--velo-glass-blue-15);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.edit-practice__readonly-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-muted);
}

/* -- Content -- */
.edit-practice__content {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* -- Fieldset reset -- */
.edit-practice__fieldset {
  border: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.edit-practice__fieldset:disabled {
  opacity: 0.6;
  pointer-events: none;
}

/* -- Section -- */
.edit-practice__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.edit-practice__section-title {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  padding-bottom: var(--space-1);
  border-bottom: 1px solid var(--velo-border-light);
}

/* -- Readonly value (practice_type) -- */
.edit-practice__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.edit-practice__label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.edit-practice__readonly-value {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-muted);
  padding: 10px var(--space-3);
  background: var(--velo-glass-blue-15);
  border: 2px solid transparent;
  border-radius: var(--velo-radius-badge);
}

/* -- Price calc -- */
.edit-practice__price-calc {
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.edit-practice__price-row {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.edit-practice__price-row--total {
  font-weight: 400;
  color: var(--velo-text-primary);
  padding-top: var(--space-2);
  border-top: 1px solid var(--velo-border-light);
}

/* -- Actions section -- */
.edit-practice__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding-top: var(--space-2);
  border-top: 1px solid var(--velo-border-light);
}

/* (confirm dialog now provided by <VConfirmDialog>) */
</style>
