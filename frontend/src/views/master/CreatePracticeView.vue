<!--
  VELO Frontend -- CreatePracticeView (Phase F6.2, fixed W-2, W-6, W-7, W-9)

  Create a new practice. Protected by masterStatusGuard.
  Standalone within MasterShell (back button -> origin via router.back(); see onBack).

  Sections (matching mockup screen-practice-create):
    ОСНОВНОЕ    -- title (required), practice_type (required)
    РАСПИСАНИЕ  -- date, time (combined -> scheduled_at UTC), duration, timezone
    УЧАСТНИКИ   -- max_participants (null = unlimited)
    ЦЕНА        -- is_free toggle; if paid: price_cents
    ОПИСАНИЕ    -- description, what_to_prepare, contraindications (optional)
    ПОДКЛЮЧЕНИЕ -- zoom_link (optional)

  Submit: POST /api/v1/practices (status defaults to 'draft' in backend).
  On success -> show toast + navigate to master-practices + refreshMyPractices().

  Fixes:
    W-2: DURATION_OPTIONS / TIMEZONE_OPTIONS imported from @/utils/practiceOptions
    W-6: priceCents uses eurStringToCents() -- no parseFloat * 100 float trap
    W-7: todayDate is a computed ref -- not stale after midnight
    W-9: commission calc uses COMMISSION_RATE from @/utils/commission

  Timezone handling:
    The date + time inputs are wall-clock values in the timezone the master
    selects (form.timezone). They are converted to a UTC instant with luxon
    (DateTime.fromISO(..., { zone: form.timezone }).toUTC()), so the stored
    scheduled_at is the correct moment regardless of the master's browser
    timezone. Each viewer later sees it rendered in their own timezone.
    (Closes the earlier "F10" simplification that used browser-local time.)
-->

<template>
  <div class="create-practice">
    <!-- Header -->
    <!-- solid: opaque plate so the form scrolling under the floating header
         doesn't ghost through the transparent title (same A1 fix as reviews). -->
    <VHeader title="Новая практика" show-back solid @back="onBack" />

    <div class="create-practice__content" @click="dismissKeyboardOnBlank">
      <!-- Required-fields legend (DS banner, Phase-3). -->
      <div class="create-practice__legend">
        <IconRequired class="create-practice__legend-seal" :size="22" />
        <span>— поля, обязательные для заполнения</span>
      </div>

      <!-- ================================================================
           Использовать шаблон — prefill from one of the master's own past
           practices (newest-first). Reuses PracticeListCard rows. Date/time
           are NOT copied (a template must not schedule in the past).
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="velo-section-title">Использовать шаблон</h2>
        <UseTemplateBlock :practices="templatePractices" @select="applyTemplate" />
      </div>

      <!-- ================================================================
           Основное  (Q2=А: 3 поля — Направление / Вид=style / Уровень=difficulty;
           practice_type не показываем, выводим из «Повторения»)
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="velo-section-title">Основное</h2>

        <VInput v-model="form.title" placeholder="Название" :error="errors.title" required />

        <!-- Направление = дисциплина (meditation/yoga/…). Подпись = плейсхолдер. -->
        <VSelect
          v-model="form.direction"
          placeholder="Направление практики"
          :options="DIRECTION_OPTIONS"
          :error="errors.direction"
          required
          @update:modelValue="onDirectionChange"
        />

        <!-- Вид практики = style. Показываем только если у направления есть виды
             (Q4=А: без явного «Без вида», не выбрано = null, необязательное). -->
        <VSelect
          v-if="styleOptionsForForm.length > 0"
          v-model="form.style"
          placeholder="Вид практики"
          :options="styleOptionsForForm"
        />

        <!-- Уровень сложности = difficulty (локальные мужские лейблы, Q1=Б). -->
        <VSelect
          v-model="form.difficulty"
          placeholder="Уровень сложности"
          :options="DIFFICULTY_OPTIONS_CREATE"
          :error="errors.difficulty"
          required
        />
      </div>

      <!-- ================================================================
           Расписание
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="velo-section-title">Расписание</h2>

        <!-- Дата: открывает DatePickerSheet. Подпись = плейсхолдер внутри поля. -->
        <div class="create-practice__field">
          <div class="create-practice__field-row">
            <button
              type="button"
              class="create-practice__picker"
              :class="{
                'create-practice__picker--empty': !form.date,
                'create-practice__picker--error': !!errors.date,
              }"
              @click="showDate = true"
            >
              {{ form.date ? dateDisplay : 'Дата' }}
            </button>
            <span class="create-practice__seal" :class="{ 'create-practice__seal--done': !!form.date }">
              <IconRequired v-if="!form.date" :size="22" />
              <IconRequiredDone v-else :size="22" />
            </span>
          </div>
          <span v-if="errors.date" class="create-practice__field-error">{{ errors.date }}</span>
        </div>

        <!-- Время: открывает TimePickerSheet (24ч). Подпись = плейсхолдер. -->
        <div class="create-practice__field">
          <div class="create-practice__field-row">
            <button
              type="button"
              class="create-practice__picker"
              :class="{
                'create-practice__picker--empty': !form.time,
                'create-practice__picker--error': !!errors.time,
              }"
              @click="showTime = true"
            >
              {{ form.time || 'Время' }}
            </button>
            <span class="create-practice__seal" :class="{ 'create-practice__seal--done': !!form.time }">
              <IconRequired v-if="!form.time" :size="22" />
              <IconRequiredDone v-else :size="22" />
            </span>
          </div>
          <span v-if="errors.time" class="create-practice__field-error">{{ errors.time }}</span>
        </div>

        <VSelect
          v-model="form.duration_minutes"
          placeholder="Длительность"
          :options="DURATION_OPTIONS"
          :error="errors.duration_minutes"
          required
        />
        <!-- Часовой пояс убран: берётся из профиля мастера (form.timezone),
             расписание задаётся в его часовом поясе (operator 2026-06-18). -->
      </div>

      <!-- ================================================================
           Повторение  (Q1=А: полная секция — период + дни недели + «Завершить»
           + счётчик. РЕАЛЬНО только series/live из чекбокса-гейта; период/дни/
           условие/счётчик — captured-only (нет бэка), см. master-ds-zod-roadmap.
           Печати обязательности — Q2=В: на полях повтора, когда «регулярная» вкл.)
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="velo-section-title">Повторение</h2>

        <VCard class="create-practice__repeat" padding="none">
          <VCheckbox v-model="form.is_recurring" label="Сделать регулярной" />
        </VCard>

        <template v-if="form.is_recurring">
          <!-- Повтор: период (всегда выбрано → печать не нужна). -->
          <div class="create-practice__seal-row">
            <VCard class="create-practice__repeat create-practice__grow" padding="none">
              <div class="create-practice__repeat-title">Повтор:</div>
              <VRadioGroup v-model="form.recurrence" :options="RECURRENCE_OPTIONS" />
            </VCard>
            <span
              class="create-practice__seal-card"
              :class="{ 'create-practice__seal-card--done': !!form.recurrence }"
            >
              <IconRequired v-if="!form.recurrence" :size="22" />
              <IconRequiredDone v-else :size="22" />
            </span>
          </div>

          <!-- Дни недели (captured-only; DS-primitive VDayPicker, оставлен в
               карточке-обёртке чтобы держать ритм секции «Повторение»). -->
          <div class="create-practice__seal-row">
            <div class="create-practice__days create-practice__grow">
              <VDayPicker v-model="form.recurrence_days" aria-label="Дни недели для повтора" />
            </div>
            <span
              class="create-practice__seal-card"
              :class="{ 'create-practice__seal-card--done': form.recurrence_days.length > 0 }"
            >
              <IconRequired v-if="!form.recurrence_days.length" :size="22" />
              <IconRequiredDone v-else :size="22" />
            </span>
          </div>
          <span v-if="errors.recurrence_days" class="create-practice__field-error">{{
            errors.recurrence_days
          }}</span>

          <!-- Завершить -->
          <div class="create-practice__seal-row">
            <VCard class="create-practice__repeat create-practice__grow" padding="none">
              <div class="create-practice__repeat-title">Завершить:</div>
              <VRadioGroup v-model="form.recurrence_end" :options="RECURRENCE_END_OPTIONS" />

              <!-- Выбрать дату: тот же DatePickerSheet, дата окончания серии (#10). -->
              <button
                v-if="form.recurrence_end === 'until_date'"
                type="button"
                class="create-practice__picker create-practice__end-control"
                :class="{ 'create-practice__picker--empty': !form.recurrence_end_date }"
                @click="showEndDate = true"
              >
                {{ form.recurrence_end_date ? endDateDisplay : 'Дата окончания' }}
              </button>

              <!-- После числа повторений: ручной ввод количества (#11). -->
              <input
                v-else-if="form.recurrence_end === 'after_count'"
                v-model.number="form.recurrence_count"
                type="number"
                inputmode="numeric"
                min="1"
                class="create-practice__end-control create-practice__count-input"
                placeholder="Число повторений"
                @focus="scrollFieldIntoView"
              />
            </VCard>
            <span
              class="create-practice__seal-card"
              :class="{ 'create-practice__seal-card--done': !!form.recurrence_end }"
            >
              <IconRequired v-if="!form.recurrence_end" :size="22" />
              <IconRequiredDone v-else :size="22" />
            </span>
          </div>
          <span v-if="errors.recurrence_end_date" class="create-practice__field-error">{{
            errors.recurrence_end_date
          }}</span>
          <span v-if="errors.recurrence_count" class="create-practice__field-error">{{
            errors.recurrence_count
          }}</span>
        </template>
      </div>

      <!-- ================================================================
           Участники  (опционально → без печати; имя поля = плейсхолдер)
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="velo-section-title">Участники</h2>

        <VInput
          v-model="form.max_participants_raw"
          type="number"
          placeholder="Максимум мест"
          :error="errors.max_participants"
        />
      </div>

      <!-- ================================================================
           Оплата  (платная опция убрана — пока только «Бесплатно», operator
           2026-06-18 Q2=А; «Платно» + цену вернём одной строкой при надобности)
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="velo-section-title">Оплата</h2>

        <VCard class="create-practice__repeat" padding="none">
          <VRadioGroup :model-value="'free'" :options="PAYMENT_OPTIONS" />
        </VCard>
      </div>

      <!-- ================================================================
           Описание  (textarea + 2 однострочных; опциональны → без печати)
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="velo-section-title">Описание</h2>

        <VTextarea
          v-model="form.description"
          placeholder="Расскажите подробее о вашей практике"
          :rows="4"
          autogrow
        />

        <!-- 1-row start (rows=1) = the VInput height these were before; auto-grow
             past one line per the «Новая практика» SVG (operator Q1=А). -->
        <VTextarea
          v-model="form.contraindications"
          placeholder="Противопоказания"
          :rows="1"
          autogrow
        />

        <VTextarea
          v-model="form.what_to_prepare"
          placeholder="Что подготовить"
          :rows="1"
          autogrow
        />
      </div>

      <!-- ================================================================
           Подключение  (ручной ввод Zoom-ссылки, необязательно; пусто = бэк
           сгенерит ссылку сам — operator 2026-06-18 Q3=А; авто-генерация → Зоду)
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="velo-section-title">Подключение</h2>

        <VInput v-model="form.zoom_link" placeholder="Ссылка на Zoom" @focus="scrollFieldIntoView" />
      </div>

      <!-- Submit -->
      <VButton variant="primary" block size="lg" :loading="submitting" @click="submit">
        Создать практику
      </VButton>

      <!-- Picker sheets (teleport to body; open on field tap). -->
      <DatePickerSheet
        :open="showDate"
        :model-value="form.date"
        :min="todayDate"
        @update:model-value="form.date = $event"
        @close="showDate = false"
      />
      <!-- Дата окончания серии (#10): тот же пикер, минимум — дата старта. -->
      <DatePickerSheet
        :open="showEndDate"
        :model-value="form.recurrence_end_date"
        :min="form.date || todayDate"
        title="Дата окончания"
        @update:model-value="form.recurrence_end_date = $event"
        @close="showEndDate = false"
      />
      <TimePickerSheet
        :open="showTime"
        :model-value="form.time"
        @update:model-value="form.time = $event"
        @close="showTime = false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { DateTime } from 'luxon'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import {
  VButton,
  VInput,
  VTextarea,
  VSelect,
  VCard,
  VCheckbox,
  VRadioGroup,
  VDayPicker,
} from '@/components/ui'
import { IconRequired, IconRequiredDone } from '@/components/icons'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useMasterStore } from '@/stores/master'
import { createPractice, updatePractice } from '@/api/practices'
import { formatShortDate } from '@/utils/format'
import DatePickerSheet from '@/components/shared/DatePickerSheet.vue'
import TimePickerSheet from '@/components/shared/TimePickerSheet.vue'
import UseTemplateBlock from '@/components/shared/UseTemplateBlock.vue'
import { ApiResponseError } from '@/api/client'
import { DURATION_OPTIONS, DIRECTION_OPTIONS, stylesForDirection } from '@/utils/practiceOptions'
import type { PracticeDirection, RecurrenceSpec, PracticeResponse } from '@/api/types'

const router = useRouter()
const toast = useToast()

// Back/cancel: return to the real origin. Create opens from BOTH the dashboard
// empty-state CTA and Практики's «+» (goNew) — router.back() lands on whichever
// pushed us here (fixes «back always went to Практики», operator 2026-06-23).
// Deep-link / no history → fall back to the practices list. Submit-success
// navigation (→ master-practices) is unchanged; only this Back button differs.
function onBack(): void {
  if (window.history.state?.back) router.back()
  else router.push({ name: 'master-practices' })
}

// The bottom-most fields («Число повторений», «Ссылка на Zoom») sit low on the
// long form, where the soft keyboard covers them on focus. Center the focused
// field in the (keyboard-shrunk) viewport so it stays visible while typing. The
// delay lets the keyboard finish opening — scrolling before the visualViewport
// shrinks would aim at the old, taller viewport. iOS/Telegram-webview behaviour,
// so this is device-verified on TEST (desktop has no soft keyboard).
function scrollFieldIntoView(e: FocusEvent): void {
  const el = e.target as HTMLElement | null
  if (!el) return
  window.setTimeout(() => {
    el.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }, 300)
}
const authStore = useAuthStore()
const masterStore = useMasterStore()

// Load the master's practices so «Использовать шаблон» can offer them as
// templates (no-op if already loaded from the practices list / dashboard).
onMounted(() => {
  void masterStore.fetchMyPractices()
})

const submitting = ref(false)

// Date/time picker sheets.
const showDate = ref(false)
const showTime = ref(false)
const showEndDate = ref(false) // «Завершить → Выбрать дату» (#10)

// Friendly date for a trigger field, e.g. "25 янв. 2026".
function friendlyDate(iso: string): string {
  return iso ? `${formatShortDate(`${iso}T12:00:00`)} ${iso.slice(0, 4)}` : ''
}
const dateDisplay = computed((): string => friendlyDate(form.date))
const endDateDisplay = computed((): string => friendlyDate(form.recurrence_end_date))

// Tap a blank area of the form to dismiss the soft keyboard (number/text inputs
// like «Максимум мест» have no «Готово» key) — operator 2026-06-18 (port from edit).
function dismissKeyboardOnBlank(e: MouseEvent): void {
  const t = e.target as HTMLElement
  if (!t.closest('input, textarea, select, button, [role="button"], a, label')) {
    ;(document.activeElement as HTMLElement | null)?.blur()
  }
}

// -- Recurrence period options (Повторение). The on/off toggle drives
// practice_type (series/live); when on, period/days/end build a RecurrenceSpec
// sent to the series engine (E3). --
const RECURRENCE_OPTIONS = [
  { label: 'Каждый день', value: 'daily' },
  { label: 'Каждую неделю', value: 'weekly' },
  { label: 'Раз в две недели', value: 'biweekly' },
]

// Завершение серии: never / until_date / after_count → RecurrenceSpec.end.
const RECURRENCE_END_OPTIONS = [
  { label: 'Никогда', value: 'never' },
  { label: 'Выбрать дату', value: 'until_date' },
  { label: 'После числа повторений', value: 'after_count' },
]

// «Платно» убрано (operator 2026-06-18 Q2=А) — пока только бесплатные практики.
const PAYMENT_OPTIONS = [{ value: 'free', label: 'Бесплатно' }]

// Уровень сложности — локальные мужские лейблы под слово «уровень» (Q1=Б);
// глобальный DIFFICULTY_LABEL (женский род, под «практика») не трогаем.
const DIFFICULTY_OPTIONS_CREATE = [
  { value: 'beginner', label: 'Начальный' },
  { value: 'medium', label: 'Средний' },
  { value: 'high', label: 'Высокий' },
]

// W-7: computed so todayDate is never stale after midnight
const todayDate = computed(() => new Date().toISOString().split('T')[0])

// -- Form state --
const form = reactive({
  title: '',
  // Selects start empty so the field name shows as the in-field placeholder (#6).
  direction: '',
  difficulty: '',
  style: '',
  // Повторение: is_recurring drives practice_type (series/live); when on,
  // period/days/end-condition/count are sent as a RecurrenceSpec (E3 series
  // engine). recurrence_days holds VDayPicker codes ('mon'..'sun').
  is_recurring: false,
  recurrence: 'weekly' as RecurrenceSpec['period'],
  recurrence_days: [] as string[],
  recurrence_end: 'never' as RecurrenceSpec['end'],
  recurrence_count: 40,
  recurrence_end_date: '', // ISO 'YYYY-MM-DD' when recurrence_end === 'until_date' (#10)
  date: '',
  time: '',
  duration_minutes: '',
  // Timezone is taken from the master's profile (field removed from the form).
  timezone: authStore.user?.timezone ?? 'Europe/Moscow',
  max_participants_raw: '', // string input, parsed to int|null on submit
  is_free: true, // «Платно» removed — practices are free for now (Q2=А)
  description: '',
  what_to_prepare: '',
  contraindications: '',
  // «Подключение» — ручной ввод Zoom-ссылки (Q3=А); пусто → null на submit.
  zoom_link: '',
})

// -- Validation errors --
const errors = reactive({
  title: '',
  direction: '',
  difficulty: '',
  date: '',
  time: '',
  duration_minutes: '',
  max_participants: '',
  // Recurrence end-condition errors (surfaced as field errors, mirroring the
  // weekday-required check): days required, until-date needs a date, after-count
  // needs a positive count. Reset by the Object.keys(errors) loop in validate().
  recurrence_days: '',
  recurrence_end_date: '',
  recurrence_count: '',
})

// «Использовать шаблон» source: all the master's practices, newest-created
// first (operator Q2=А — backend list order isn't guaranteed, so sort here).
const templatePractices = computed((): PracticeResponse[] =>
  [...masterStore.practices].sort((a, b) => b.created_at.localeCompare(a.created_at)),
)

// Direction-conditional style options. When the direction has no styles
// (e.g. breathwork, somatic, tantra, ...) the VSelect is hidden by v-if.
const styleOptionsForForm = computed(() => stylesForDirection(form.direction as PracticeDirection))

/** Reset style when direction changes — the previous value is likely
 *  invalid for the new direction. */
function onDirectionChange(): void {
  form.style = ''
}

/**
 * «Использовать шаблон»: prefill the form from one of the master's own past
 * practices. Copies the practice's settings EXCEPT date & time, which stay
 * fresh so a template can't schedule a practice in the past (operator Q1=А).
 * The block collapses itself after selecting.
 */
function applyTemplate(p: PracticeResponse): void {
  form.title = p.title
  form.direction = p.direction ?? ''
  form.style = p.style ?? ''
  form.difficulty = p.difficulty ?? ''
  form.duration_minutes = String(p.duration_minutes)
  form.max_participants_raw = p.max_participants != null ? String(p.max_participants) : ''
  form.description = p.description ?? ''
  form.what_to_prepare = p.what_to_prepare ?? ''
  form.contraindications = p.contraindications ?? ''
  // date & time intentionally NOT copied.
}

// -- Validation --
function validate(): boolean {
  let ok = true

  // Reset all errors
  Object.keys(errors).forEach((k) => {
    errors[k as keyof typeof errors] = ''
  })

  if (!form.title.trim()) {
    errors.title = 'Введите название'
    ok = false
  }
  if (!form.direction) {
    errors.direction = 'Выберите направление'
    ok = false
  }
  if (!form.difficulty) {
    errors.difficulty = 'Выберите сложность'
    ok = false
  }
  if (!form.date) {
    errors.date = 'Выберите дату'
    ok = false
  }
  if (!form.time) {
    errors.time = 'Выберите время'
    ok = false
  }
  // Ensure scheduled_at is in the future, interpreted in the SELECTED
  // timezone (not the browser's): a master in one tz scheduling for another
  // must be validated against the wall-clock time they actually picked.
  if (form.date && form.time) {
    const dt = DateTime.fromISO(`${form.date}T${form.time}`, {
      zone: form.timezone,
    })
    if (!dt.isValid || dt.toMillis() <= Date.now()) {
      errors.date = 'Дата должна быть в будущем'
      ok = false
    }
  }
  if (!form.duration_minutes) {
    errors.duration_minutes = 'Выберите длительность'
    ok = false
  }
  if (form.max_participants_raw) {
    const n = parseInt(form.max_participants_raw, 10)
    if (isNaN(n) || n < 1) {
      errors.max_participants = 'Введите положительное число или оставьте пустым'
      ok = false
    }
  }
  // Weekly / biweekly series require at least one weekday (the day picker shows
  // a required-seal when empty). Daily ignores days. Block an invalid spec.
  if (form.is_recurring && form.recurrence !== 'daily' && form.recurrence_days.length === 0) {
    errors.recurrence_days = 'Выберите хотя бы один день недели'
    ok = false
  }
  // End = «выбрать дату» needs a chosen date, else until_date submits null → 422
  // with no field feedback.
  if (form.is_recurring && form.recurrence_end === 'until_date' && !form.recurrence_end_date) {
    errors.recurrence_end_date = 'Выберите дату окончания'
    ok = false
  }
  // End = «после числа повторений» needs a positive count; a cleared input binds
  // to '' (HTML min doesn't block submit) → count '' → 422 with no feedback.
  if (
    form.is_recurring &&
    form.recurrence_end === 'after_count' &&
    (!form.recurrence_count || form.recurrence_count < 1)
  ) {
    errors.recurrence_count = 'Укажите число повторений (не меньше 1)'
    ok = false
  }
  return ok
}

// VDayPicker emits day codes ('mon'..'sun'); RecurrenceSpec.days needs ISO
// weekday ints (1=Mon..7=Sun). VDayPicker already emits in Mon→Sun order.
const WEEKDAY_ISO: Record<string, number> = {
  mon: 1,
  tue: 2,
  wed: 3,
  thu: 4,
  fri: 5,
  sat: 6,
  sun: 7,
}

/** Build the RecurrenceSpec from the captured form (only when is_recurring). */
function buildRecurrence(): RecurrenceSpec {
  const spec: RecurrenceSpec = {
    period: form.recurrence,
    end: form.recurrence_end,
  }
  // Daily ignores days; weekly/biweekly send the selected ISO weekdays.
  if (form.recurrence !== 'daily') {
    spec.days = form.recurrence_days.map((d) => WEEKDAY_ISO[d]).filter((n) => n != null)
  }
  if (form.recurrence_end === 'after_count') {
    spec.count = form.recurrence_count
  } else if (form.recurrence_end === 'until_date') {
    spec.until_date = form.recurrence_end_date || null
  }
  return spec
}

// -- Submit --
// FP-04: double-submit guard must come before validate() --
// parallel clicks both pass validate() before guard fires.
async function submit(): Promise<void> {
  if (submitting.value) return
  if (!validate()) return
  submitting.value = true

  try {
    // Build the UTC instant from the wall-clock date + time, interpreted in
    // the timezone the master selected (form.timezone). luxon handles DST and
    // offsets; the stored scheduled_at is then correct for every viewer's tz.
    const scheduledDt = DateTime.fromISO(`${form.date}T${form.time}`, {
      zone: form.timezone,
    })
    const scheduledAt = scheduledDt.toUTC().toISO()
    if (!scheduledAt) {
      // Should not happen (validate() already checked date/time), but toISO()
      // is typed string | null, so guard instead of sending a bad value.
      toast.error('Некорректные дата или время')
      submitting.value = false
      return
    }

    const created = await createPractice({
      // Q2=А: practice_type derived from the recurrence toggle (series/live);
      // one_on_one/replay are not creatable from this form (roadmap: advanced mode).
      practice_type: form.is_recurring ? 'series' : 'live',
      direction: form.direction,
      difficulty: form.difficulty,
      style: form.style.trim() || null,
      title: form.title.trim(),
      description: form.description.trim() || null,
      what_to_prepare: form.what_to_prepare.trim() || null,
      contraindications: form.contraindications.trim() || null,
      scheduled_at: scheduledAt,
      duration_minutes: parseInt(form.duration_minutes, 10),
      timezone: form.timezone,
      max_participants: form.max_participants_raw ? parseInt(form.max_participants_raw, 10) : null,
      // «Подключение» — ручная Zoom-ссылка; пусто → null (бэк сгенерит, → Зоду).
      zoom_link: form.zoom_link.trim() || null,
      is_free: form.is_free,
      price_cents: 0,
      currency: 'eur',
      // E3: when recurring, send the series spec; non-recurring → null.
      recurrence: form.is_recurring ? buildRecurrence() : null,
    })

    // Publish immediately: a freshly created practice must be live & bookable,
    // not a draft that needs a second edit→«Опубликовать» step (operator
    // 2026-06-17). The backend create defaults to 'draft'; we run the same
    // draft→scheduled PATCH the edit screen uses, so the practice appears on the
    // dashboard «Ближайшая практика» (scheduled/live only) right away.
    await updatePractice(created.id, { status: 'scheduled' })

    toast.success('Практика создана!')
    // Invalidate cached list so it reloads on practices view
    await masterStore.refreshMyPractices()
    // Open the new practice's detail screen; replace (not push) so «назад» from
    // it lands on the origin (practices / dashboard), not back on this form (#1).
    router.replace({ name: 'master-practice-detail', params: { id: created.id } })
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось создать практику')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.create-practice {
  min-height: 100%;
  background: transparent;
  display: flex;
  flex-direction: column;
}

.create-practice__content {
  flex: 1;
  /* F-5 rail sync: ride MobileLayout's 24px rail (no local h-padding). Top
     trimmed so the floating header sits closer to the first field (#1, port
     from the edit form). */
  padding: var(--space-2) 0 var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* -- Section -- */
.create-practice__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* Required-fields legend banner (DS, Phase-3) — pink glass plate, rose seal. */
.create-practice__legend {
  display: flex;
  align-items: center;
  gap: var(--velo-banner-gap-icon-text);
  background: var(--velo-glass-pink-40);
  border: 1px solid var(--velo-pink-300);
  border-radius: 12px;
  padding: 10px var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-pink-700);
}

.create-practice__legend-seal {
  flex-shrink: 0;
  color: var(--velo-rating-good);
}

/* Повторение cards (white plates). */
.create-practice__repeat {
  padding: var(--space-3) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.create-practice__repeat-title {
  font-family: var(--font-body);
  font-size: var(--text-base);  color: var(--velo-text-primary);
}

/* -- Date/time picker trigger field (mirrors the white VInput plate) -- */
.create-practice__field {
  margin-bottom: var(--space-4);
}

.create-practice__field-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.create-practice__picker {
  flex: 1;
  min-width: 0;
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

.create-practice__picker--empty {
  color: var(--velo-text-muted);
}

.create-practice__picker--error {
  border-color: var(--velo-error);
}

.create-practice__seal {
  flex-shrink: 0;
  display: flex;
  color: var(--velo-error);
}

.create-practice__seal--done {
  color: var(--velo-required-done);
}

.create-practice__field-error {
  display: block;
  font-size: var(--text-xs);
  color: var(--velo-error);
  margin-top: var(--space-1);
}

/* -- Повторение: карточка повтора (grow) + печать обязательности справа (Q2=В). -- */
.create-practice__seal-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
}

.create-practice__grow {
  flex: 1;
  min-width: 0;
}

.create-practice__seal-card {
  flex-shrink: 0;
  display: flex;
  color: var(--velo-error);
  margin-top: var(--space-2);
}

.create-practice__seal-card--done {
  color: var(--velo-required-done);
}

/* -- Дни недели: карточка-обёртка для DS-примитива VDayPicker. -- */
.create-practice__days {
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-md);
  padding: var(--velo-card-padding-y) var(--space-3);
}

/* -- «После числа повторений»: счётчик-пилюля (captured-only). -- */
/* «Завершить» sub-control (end date button / repeat-count input) — sits below
   the radios; needs a visible edge on the white card. */
.create-practice__end-control {
  margin-top: var(--space-3);
  /* This trigger reuses .create-practice__picker (flex: 1), but here it sits in a
     flex-COLUMN card, where flex-basis:0% would collapse its height:40px to the
     text line («Дата окончания» squished). flex:0 0 auto restores the 40px; the
     date/time row keeps flex:1 (correct there — grows width in a flex row). */
  flex: 0 0 auto;
}

.create-practice__end-control.create-practice__picker {
  border-color: var(--velo-border);
}

.create-practice__count-input {
  width: 160px;
  height: var(--velo-size-40);
  padding: 0 var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  background: var(--velo-bg-card-solid);
  border: 2px solid var(--velo-border);
  border-radius: var(--velo-radius-badge);
}

.create-practice__count-input:focus {
  outline: none;
  border-color: var(--velo-border-input-focus);
}

.create-practice__count-input::placeholder {
  color: var(--velo-text-muted);
}
</style>
