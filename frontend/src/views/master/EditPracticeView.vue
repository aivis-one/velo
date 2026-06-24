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
    live       -> "Отменить"      POST /cancel   (+ confirm dialog)
                  (manual "Завершить" removed — completion is auto-by-duration,
                   pending backend; there is no live->finalize button here)
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
    <!-- Back always returns to the practice screen; that screen decides where to
         go next (dashboard or practices, depending on origin) — operator 2026-06-17. -->
    <!-- solid: opaque plate so the form scrolling under the floating header
         doesn't ghost through the transparent title (same A1 fix as reviews). -->
    <VHeader
      title="Редактировать"
      show-back
      solid
      @back="router.push({ name: 'master-practice-detail', params: { id: practiceId } })"
    />

    <!-- Loading -->
    <div v-if="loading" class="edit-practice__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error / not found -->
    <div v-else-if="!practice" class="edit-practice__content">
      <VEmptyState icon="warning" title="Практика не найдена">
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
        <VBadge
          v-if="masterPracticeBadge(practice.status)"
          :variant="masterPracticeBadge(practice.status)!.variant"
        >
          {{ masterPracticeBadge(practice.status)!.label }}
        </VBadge>
        <span class="edit-practice__readonly-text">Редактирование недоступно</span>
      </div>

      <div class="edit-practice__content" @click="dismissKeyboardOnBlank">
        <!-- ================================================================
             FORM (editable for draft / scheduled only)
             ================================================================ -->
        <fieldset :disabled="isTerminal || saving" class="edit-practice__fieldset">
          <!-- Реш. В (2026-06-12): поля по SVG Edit (label-above, белая плашка),
               БЕЗ секций-заголовков. Намеренно опущены направление/уровень/вид/
               таймзона/цена — они задаются на создании и блокируются после (хранятся
               в form, уходят на submit неизменными, данные не теряем). Дата и Zoom
               возвращены по логике (см. комментарии ниже). -->
          <VInput v-model="form.title" label="Название" :error="errors.title" />

          <!-- Дата — DS-пикер (реш. В: возвращена по логике — перенос практики
               норм. операция; нативный type=date заменён на брендовый пикер). -->
          <div class="edit-practice__field">
            <label class="edit-practice__field-label">Дата</label>
            <button
              type="button"
              class="edit-practice__picker"
              :class="{ 'edit-practice__picker--empty': !form.date }"
              @click="showDate = true"
            >
              {{ form.date ? dateDisplay : 'Выберите дату' }}
            </button>
          </div>

          <!-- Время — DS-пикер (24ч, шаг 5 мин). -->
          <div class="edit-practice__field">
            <label class="edit-practice__field-label">Время</label>
            <button
              type="button"
              class="edit-practice__picker"
              :class="{ 'edit-practice__picker--empty': !form.time }"
              @click="showTime = true"
            >
              {{ form.time || 'Выберите время' }}
            </button>
          </div>

          <VSelect
            v-model="form.duration_minutes"
            label="Длительность"
            :options="DURATION_OPTIONS"
          />

          <VInput
            v-model="form.max_participants_raw"
            label="Максимум мест"
            type="number"
            :error="errors.max_participants"
          />

          <VTextarea v-model="form.description" label="Описание" :rows="4" autogrow />

          <VTextarea
            v-model="form.contraindications"
            label="Противопоказания"
            placeholder="Беременность, сердечно-сосудистые заболевания"
            :rows="2"
            autogrow
          />

          <VTextarea
            v-model="form.what_to_prepare"
            label="Что подготовить"
            placeholder="Коврик, плед, вода"
            :rows="3"
            autogrow
          />

          <!-- Zoom (реш. В: сохранена по ЛОГИКЕ — авто-ссылки-бэка ещё нет, и Edit
               сейчас единственное место задать ссылку подключения; в SVG её нет). -->
          <VInput
            v-model="form.zoom_link"
            label="Zoom ссылка"
            type="url"
            :error="errors.zoom_link"
          />

          <!-- W-3: :disabled="anyLoading" prevents Save while an action runs. -->
          <VButton
            v-if="!isTerminal"
            variant="primary"
            block
            :loading="saving"
            :disabled="anyLoading"
            @click="save"
          >
            Сохранить
          </VButton>
        </fieldset>

        <!-- ================================================================
             STATE MACHINE ACTIONS
             Q2=А (2026-06-12): лайфсайкл-переходы СОХРАНЕНЫ ВРЕМЕННО (в SVG Edit
             их нет) — пока хаб Practice-detail (WI-B) их не заберёт. Выкинуть
             сейчас = оставить мастера без публикации/завершения вовсе (в макете
             хаба их тоже нет). При сборке WI-B этот блок мигрирует туда.
             W-3: all buttons :disabled="anyLoading" -- prevents concurrent
             save + publish / save + cancel / save + delete etc.
             ================================================================ -->
        <div v-if="!isTerminal" class="edit-practice__actions">
          <div class="edit-practice__section-title">Действия</div>

          <!-- draft -> scheduled -->
          <VButton
            v-if="practice.status === 'draft'"
            variant="primary"
            block
            :loading="transitioning"
            :disabled="anyLoading"
            @click="publish"
          >
            Опубликовать практику
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
            Начать эфир
          </VButton>

          <!-- «Завершить практику» + «Посещаемость» removed (operator 2026-06-17):
               finalize is non-obvious behind the edit form; a practice is meant to
               complete automatically by its duration (unless cancelled) once the
               backend implements it — see the Zod note. Attendance/check-ins stay
               reachable from the dashboard «Check-ins» and the practice screen. -->

          <!-- draft -> deleted -->
          <VButton
            v-if="practice.status === 'draft'"
            variant="danger"
            block
            :loading="deleting"
            :disabled="anyLoading"
            @click="confirmDelete"
          >
            Удалить черновик
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
            Отменить практику
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

      <!-- Branded cancel-practice modal (replaces the generic confirm for cancel;
           operator SVG «Abolish the practice»). cancelPractice = real refund;
           series-scope radio inside is captured-only (→ Zod). -->
      <CancelPracticeDialog
        :open="cancelModalOpen"
        :practice="practice"
        :loading="cancelling"
        @confirm="cancel"
        @cancel="cancelModalOpen = false"
      />

      <!-- Date/time picker sheets (teleport to body; open on field tap). -->
      <DatePickerSheet
        :open="showDate"
        :model-value="form.date"
        :min="todayDate"
        @update:model-value="form.date = $event"
        @close="showDate = false"
      />
      <TimePickerSheet
        :open="showTime"
        :model-value="form.time"
        @update:model-value="form.time = $event"
        @close="showTime = false"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { DateTime } from 'luxon'
import { useRoute, useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import {
  VButton,
  VInput,
  VTextarea,
  VSelect,
  VBadge,
  VLoader,
  VEmptyState,
  VConfirmDialog,
} from '@/components/ui'
import DatePickerSheet from '@/components/shared/DatePickerSheet.vue'
import TimePickerSheet from '@/components/shared/TimePickerSheet.vue'
import CancelPracticeDialog from '@/components/shared/CancelPracticeDialog.vue'
import { useToast } from '@/composables/useToast'
import { useMasterStore } from '@/stores/master'
import { getPractice, updatePractice, deletePractice, cancelPractice } from '@/api/practices'
import { formatShortDate } from '@/utils/format'
import { masterPracticeBadge } from '@/utils/practiceStatus'
import { ApiResponseError } from '@/api/client'
import { DURATION_OPTIONS } from '@/utils/practiceOptions'
import { eurStringToCents, centsToEurString } from '@/utils/currency'
import type { PracticeResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const masterStore = useMasterStore()

const practiceId = route.params.id as string

// Tap a blank area of the form to dismiss the soft keyboard (number/text inputs
// like «Максимум мест» have no «Готово» key) — operator 2026-06-17.
function dismissKeyboardOnBlank(e: MouseEvent): void {
  const t = e.target as HTMLElement
  if (!t.closest('input, textarea, select, button, [role="button"], a, label')) {
    ;(document.activeElement as HTMLElement | null)?.blur()
  }
}

// -- Practice data --
const practice = ref<PracticeResponse | null>(null)
const loading = ref(false)

// -- Action loading states --
const saving = ref(false)
const transitioning = ref(false)
const cancelling = ref(false)
const deleting = ref(false)

// Date/time picker sheets + branded cancel modal (Q1=В / Q3=А, 2026-06-12).
const showDate = ref(false)
const showTime = ref(false)
const cancelModalOpen = ref(false)

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
  onConfirm: (): void => {
    /* filled per use */
  },
})

// W-8: computed so todayDate is never stale after midnight
const todayDate = computed(() => new Date().toISOString().split('T')[0])

// Friendly date for the picker trigger, e.g. "25 янв. 2026" (mirrors Create).
const dateDisplay = computed((): string =>
  form.date ? `${formatShortDate(`${form.date}T12:00:00`)} ${form.date.slice(0, 4)}` : '',
)

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
  zoom_link: '',
})

// -- Derived --
const isTerminal = computed(
  (): boolean =>
    practice.value?.status === 'completed' ||
    practice.value?.status === 'cancelled' ||
    practice.value?.status === 'deleted',
)

// W-6: use eurStringToCents() -- avoids parseFloat(raw) * 100 float precision trap.
const priceCents = computed((): number => eurStringToCents(form.price_eur_raw))

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
  const scheduledDt = DateTime.fromISO(p.scheduled_at, { zone: 'utc' }).setZone(p.timezone)
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
      max_participants: form.max_participants_raw ? parseInt(form.max_participants_raw, 10) : null,
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

// -- Confirm cancel: open the branded modal (CancelPracticeDialog). --
function confirmCancel(): void {
  cancelModalOpen.value = true
}

// -- Cancel: scheduled/live -> cancelled (full refund). Driven by the branded
//    modal; uses the `cancelling` flag (modal :loading). --
async function cancel(scope: 'this' | 'this_and_future'): Promise<void> {
  if (cancelling.value) return
  cancelling.value = true
  try {
    const updated = await cancelPractice(practiceId, scope)
    practice.value = updated
    cancelModalOpen.value = false
    toast.success('Практика отменена, возвраты выполнены')
    await masterStore.refreshMyPractices()
    router.push({ name: 'master-practices' })
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось отменить')
  } finally {
    cancelling.value = false
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
  font-size: var(--text-sm);  color: var(--velo-text-muted);
}

/* -- Content -- */
.edit-practice__content {
  flex: 1;
  /* F-5 rail sync: ride MobileLayout's 24px rail (no local h-padding).
     Top trimmed to sit closer to the header (operator 2026-06-17). */
  padding: var(--space-2) 0 var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* -- Fieldset reset -- (flat field list; spacing via each field's own
   margin-bottom, so gap is 0 to avoid double spacing). -- */
.edit-practice__fieldset {
  border: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.edit-practice__fieldset:disabled {
  opacity: 0.6;
  pointer-events: none;
}

.edit-practice__section-title {
  font-family: var(--font-body);
  font-size: var(--text-xs);  color: var(--velo-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  padding-bottom: var(--space-1);
  border-bottom: 1px solid var(--velo-border-light);
}

/* -- Date/time picker trigger field (mirrors the white VInput plate). -- */
.edit-practice__field {
  margin-bottom: var(--space-4);
}

.edit-practice__field-label {
  display: block;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  margin-bottom: var(--space-2);
}

.edit-practice__picker {
  display: flex;
  align-items: center;
  width: 100%;
  height: var(--velo-size-40);
  text-align: left;
  padding: 0 var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  background: var(--velo-bg-card-solid);
  border: 2px solid transparent;
  border-radius: var(--velo-radius-badge);
  cursor: pointer;
}

.edit-practice__picker--empty {
  color: var(--velo-text-muted);
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
