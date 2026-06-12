<!--
  VELO Frontend -- CreatePracticeView (Phase F6.2, fixed W-2, W-6, W-7, W-9)

  Create a new practice. Protected by masterStatusGuard.
  Standalone within MasterShell (back button -> master-practices).

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
    <VHeader
      title="Новая практика"
      show-back
      @back="router.push({ name: 'master-practices' })"
    />

    <div class="create-practice__content">
      <!-- Required-fields legend (DS banner, Phase-3). -->
      <div class="create-practice__legend">
        <IconRequired class="create-practice__legend-seal" :size="22" />
        <span>— поля, обязательные для заполнения</span>
      </div>

      <!-- ================================================================
           Основное  (Q2=А: 3 поля — Направление / Вид=style / Уровень=difficulty;
           practice_type не показываем, выводим из «Повторения»)
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="create-practice__section-title">Основное</h2>

        <VInput
          v-model="form.title"
          label="Название"
          placeholder="Утренняя медитация"
          :error="errors.title"
          required
        />

        <!-- Направление = дисциплина (meditation/yoga/…). -->
        <VSelect
          v-model="form.direction"
          label="Направление практики"
          :options="DIRECTION_OPTIONS"
          :error="errors.direction"
          required
          @update:modelValue="onDirectionChange"
        />

        <!-- Вид практики = style (зависит от направления; «Без вида», если стилей нет). -->
        <VSelect
          v-model="form.style"
          label="Вид практики"
          :options="styleSelectOptions"
          required
        />

        <!-- Уровень = difficulty. -->
        <VSelect
          v-model="form.difficulty"
          label="Уровень"
          :options="DIFFICULTY_OPTIONS"
          :error="errors.difficulty"
          required
        />
      </div>

      <!-- ================================================================
           Расписание
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="create-practice__section-title">Расписание</h2>

        <!-- W-7: todayDate is computed -- never stale after midnight -->
        <VInput
          v-model="form.date"
          label="Дата"
          type="date"
          :min="todayDate"
          :error="errors.date"
          required
        />

        <VInput
          v-model="form.time"
          label="Время"
          type="time"
          :error="errors.time"
          required
        />

        <VSelect
          v-model="form.duration_minutes"
          label="Длительность"
          :options="DURATION_OPTIONS"
          :error="errors.duration_minutes"
          required
        />

        <!-- Часовой пояс: дефолт из профиля мастера, не обязательное (Q1). -->
        <VSelect
          v-model="form.timezone"
          label="Часовой пояс"
          :options="TIMEZONE_OPTIONS"
        />
      </div>

      <!-- ================================================================
           Повторение  (Q2=А: тогл «Сделать регулярной» → practice_type
           series/live — РЕАЛЬНО; период повтора пока без бэка, captured-only,
           см. master-ds-zod-roadmap.md)
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="create-practice__section-title">Повторение</h2>

        <VCard class="create-practice__repeat" padding="none">
          <VCheckbox v-model="form.is_recurring" label="Сделать регулярной" />
        </VCard>

        <VCard v-if="form.is_recurring" class="create-practice__repeat" padding="none">
          <div class="create-practice__repeat-title">Повтор:</div>
          <VRadioGroup v-model="form.recurrence" :options="RECURRENCE_OPTIONS" />
        </VCard>
      </div>

      <!-- ================================================================
           УЧАСТНИКИ
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="create-practice__section-title">Участники</h2>

        <VInput
          v-model="form.max_participants_raw"
          label="Максимум участников (пусто = без ограничений)"
          type="number"
          placeholder="20"
          :error="errors.max_participants"
        />
      </div>

      <!-- ================================================================
           ЦЕНА
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="create-practice__section-title">Цена</h2>

        <!-- Free / Paid segment -->
        <VSegment
          :model-value="form.is_free ? 'free' : 'paid'"
          :options="PAYMENT_OPTIONS"
          @update:model-value="form.is_free = $event === 'free'"
        />

        <!-- Price fields (visible only if paid) -->
        <template v-if="!form.is_free">
          <VInput
            v-model="form.price_eur_raw"
            label="Цена (EUR) *"
            type="number"
            placeholder="15"
            :error="errors.price_cents"
          />
          <!-- W-9: commission calc via COMMISSION_RATE constant -->
          <VCard v-if="priceCents > 0" class="create-practice__price-calc" padding="none">
            <div class="create-practice__price-row">
              <span>Комиссия {{ commissionPct }}%</span>
              <span>{{ formatMoney(Math.round(priceCents * COMMISSION_RATE), 'EUR') }}</span>
            </div>
            <div class="create-practice__price-row create-practice__price-row--total">
              <span>Вы получите</span>
              <span>{{ formatMoney(Math.round(priceCents * (1 - COMMISSION_RATE)), 'EUR') }}</span>
            </div>
          </VCard>
        </template>
      </div>

      <!-- ================================================================
           ОПИСАНИЕ
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="create-practice__section-title">Описание</h2>

        <VTextarea
          v-model="form.description"
          label="Описание"
          placeholder="Мягкая утренняя практика для начала дня с ясностью..."
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

      <!-- ================================================================
           ПОДКЛЮЧЕНИЕ
           ================================================================ -->
      <div class="create-practice__section">
        <h2 class="create-practice__section-title">Подключение</h2>

        <VInput
          v-model="form.zoom_link"
          label="Zoom ссылка"
          type="url"
          placeholder="https://zoom.us/j/..."
          :error="errors.zoom_link"
        />
        <p class="create-practice__hint">Участники получат ссылку за 10 минут до начала</p>
      </div>

      <!-- Submit -->
      <VButton
        variant="primary"
        block
        size="lg"
        :loading="submitting"
        @click="submit"
      >
        Создать практику
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { DateTime } from 'luxon'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton, VInput, VTextarea, VSelect, VCard, VSegment, VCheckbox, VRadioGroup } from '@/components/ui'
import { IconRequired } from '@/components/icons'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useMasterStore } from '@/stores/master'
import { createPractice } from '@/api/practices'
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
import { eurStringToCents } from '@/utils/currency'
import type { PracticeDirection } from '@/api/types'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const masterStore = useMasterStore()

const submitting = ref(false)

// -- Recurrence period options (Повторение). The on/off toggle IS real — it
// drives practice_type (series/live) on submit. The daily/weekly/biweekly value
// is captured in form state but NOT yet a backend field (see
// master-ds-zod-roadmap.md "recurrence period + series engine"). --
const RECURRENCE_OPTIONS = [
  { label: 'Каждый день',      value: 'daily' },
  { label: 'Каждую неделю',    value: 'weekly' },
  { label: 'Раз в две недели', value: 'biweekly' },
]

const PAYMENT_OPTIONS = [
  { value: 'free', label: 'Бесплатно' },
  { value: 'paid', label: 'Платно' },
]

// W-7: computed so todayDate is never stale after midnight
const todayDate = computed(() => new Date().toISOString().split('T')[0])

// W-9: human-readable commission percentage for template
const commissionPct = Math.round(COMMISSION_RATE * 100)

// -- Form state --
const form = reactive({
  title: '',
  direction: 'meditation',
  difficulty: 'beginner',
  style: '',
  // Повторение: is_recurring drives practice_type (series/live) on submit;
  // recurrence (period) is captured but not yet persisted (no backend field).
  is_recurring: false,
  recurrence: 'weekly',
  date: '',
  time: '',
  duration_minutes: '60',
  timezone: authStore.user?.timezone ?? 'Europe/Moscow',
  max_participants_raw: '',  // string input, parsed to int|null on submit
  is_free: false,
  price_eur_raw: '',          // string input, converted to cents on submit
  description: '',
  what_to_prepare: '',
  contraindications: '',
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
  price_cents: '',
  zoom_link: '',
})

// W-6: use eurStringToCents() -- avoids parseFloat(raw) * 100 float precision trap.
const priceCents = computed((): number => eurStringToCents(form.price_eur_raw))

// Direction-conditional style options. When the direction has no styles
// (e.g. breathwork, somatic, tantra, ...) the VSelect is hidden by v-if.
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
  if (!form.is_free) {
    if (!form.price_eur_raw) {
      errors.price_cents = 'Введите цену'
      ok = false
    } else if (priceCents.value < 100) {
      errors.price_cents = 'Минимальная цена — €1,00'
      ok = false
    }
  }
  if (form.zoom_link && !form.zoom_link.startsWith('https://')) {
    errors.zoom_link = 'Ссылка должна начинаться с https://'
    ok = false
  }

  return ok
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

    await createPractice({
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
      max_participants: form.max_participants_raw
        ? parseInt(form.max_participants_raw, 10)
        : null,
      zoom_link: form.zoom_link.trim() || null,
      is_free: form.is_free,
      price_cents: form.is_free ? 0 : priceCents.value,
      currency: 'eur',
    })

    toast.success('Практика создана!')
    // Invalidate cached list so it reloads on practices view
    await masterStore.refreshMyPractices()
    router.push({ name: 'master-practices' })
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
  /* F-5 rail sync: ride MobileLayout's 24px rail (no local h-padding). */
  padding: var(--space-4) 0;
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

.create-practice__section-title {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
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
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
}

/* -- Price calc preview -- */
.create-practice__price-calc {
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.create-practice__price-row {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.create-practice__price-row--total {
  font-weight: 400;
  color: var(--velo-text-primary);
  padding-top: var(--space-2);
  border-top: 1px solid var(--velo-border-light);
}

/* -- Hint -- */
.create-practice__hint {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-muted);
}
</style>
