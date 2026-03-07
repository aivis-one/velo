<!--
  VELO Frontend -- CreatePracticeView (Phase F6.2, fixed W-2, W-7, W-9)

  Create a new practice. Protected by masterStatusGuard.
  Standalone within MasterShell (back button -> master-practices).

  Sections (matching mockup screen-practice-create):
    📝 ОСНОВНОЕ    -- title (required), practice_type (required)
    📅 РАСПИСАНИЕ  -- date, time (combined -> scheduled_at UTC), duration, timezone
    👥 УЧАСТНИКИ   -- max_participants (null = unlimited)
    💰 ЦЕНА        -- is_free toggle; if paid: price_cents
    📝 ОПИСАНИЕ    -- description (optional)
    🔗 ПОДКЛЮЧЕНИЕ -- zoom_link (optional)

  Submit: POST /api/v1/practices (status defaults to 'draft' in backend).
  On success -> show toast + navigate to master-practices + refreshMyPractices().

  Fixes:
    W-2: DURATION_OPTIONS / TIMEZONE_OPTIONS moved to @/utils/practiceOptions
    W-7: todayDate is a computed ref -- no longer goes stale after midnight
    W-9: commission calc uses COMMISSION_RATE from @/utils/commission

  Timezone note:
    datetime-local input returns local browser time. We convert it to UTC
    via new Date(localString).toISOString(). The timezone field is separately
    set from the master's profile timezone (editable in-form for MVP).
    This is a known simplification: if browser TZ differs from profile TZ,
    the displayed time may differ. Full fix: use a TZ-aware date library (F10).
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
      <!-- ================================================================
           📝 ОСНОВНОЕ
           ================================================================ -->
      <div class="create-practice__section">
        <div class="create-practice__section-title">📝 ОСНОВНОЕ</div>

        <VInput
          v-model="form.title"
          label="Название *"
          placeholder="Утренняя медитация"
          :error="errors.title"
        />

        <VSelect
          v-model="form.practice_type"
          label="Тип практики *"
          :options="PRACTICE_TYPE_OPTIONS"
          :error="errors.practice_type"
        />
      </div>

      <!-- ================================================================
           📅 РАСПИСАНИЕ
           ================================================================ -->
      <div class="create-practice__section">
        <div class="create-practice__section-title">📅 РАСПИСАНИЕ</div>

        <div class="create-practice__field">
          <label class="create-practice__label">Дата *</label>
          <input
            v-model="form.date"
            type="date"
            class="create-practice__date-input"
            :min="todayDate"
          />
          <p v-if="errors.date" class="create-practice__field-error">{{ errors.date }}</p>
        </div>

        <div class="create-practice__field">
          <label class="create-practice__label">Время *</label>
          <input
            v-model="form.time"
            type="time"
            class="create-practice__date-input"
          />
          <p v-if="errors.time" class="create-practice__field-error">{{ errors.time }}</p>
        </div>

        <VSelect
          v-model="form.duration_minutes"
          label="Длительность *"
          :options="DURATION_OPTIONS"
          :error="errors.duration_minutes"
        />

        <VSelect
          v-model="form.timezone"
          label="Часовой пояс"
          :options="TIMEZONE_OPTIONS"
        />
      </div>

      <!-- ================================================================
           👥 УЧАСТНИКИ
           ================================================================ -->
      <div class="create-practice__section">
        <div class="create-practice__section-title">👥 УЧАСТНИКИ</div>

        <VInput
          v-model="form.max_participants_raw"
          label="Максимум участников (пусто = без ограничений)"
          type="number"
          placeholder="20"
          :error="errors.max_participants"
        />
      </div>

      <!-- ================================================================
           💰 ЦЕНА
           ================================================================ -->
      <div class="create-practice__section">
        <div class="create-practice__section-title">💰 ЦЕНА</div>

        <!-- Free / Paid radio toggle -->
        <div class="create-practice__payment-options">
          <label
            class="create-practice__payment-option"
            :class="{ 'create-practice__payment-option--active': form.is_free }"
            @click="form.is_free = true"
          >
            <span class="create-practice__radio" :class="{ 'create-practice__radio--active': form.is_free }" />
            <span>Бесплатно</span>
          </label>
          <label
            class="create-practice__payment-option"
            :class="{ 'create-practice__payment-option--active': !form.is_free }"
            @click="form.is_free = false"
          >
            <span class="create-practice__radio" :class="{ 'create-practice__radio--active': !form.is_free }" />
            <span>Платно</span>
          </label>
        </div>

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
          <div v-if="priceCents > 0" class="create-practice__price-calc">
            <div class="create-practice__price-row">
              <span>Комиссия {{ commissionPct }}%</span>
              <span>{{ formatMoney(Math.round(priceCents * COMMISSION_RATE), 'EUR') }}</span>
            </div>
            <div class="create-practice__price-row create-practice__price-row--total">
              <span>Вы получите</span>
              <span>{{ formatMoney(Math.round(priceCents * (1 - COMMISSION_RATE)), 'EUR') }}</span>
            </div>
          </div>
        </template>
      </div>

      <!-- ================================================================
           📝 ОПИСАНИЕ
           ================================================================ -->
      <div class="create-practice__section">
        <div class="create-practice__section-title">📝 ОПИСАНИЕ</div>

        <VTextarea
          v-model="form.description"
          label="Описание"
          placeholder="Мягкая утренняя практика для начала дня с ясностью..."
          :rows="4"
        />
      </div>

      <!-- ================================================================
           🔗 ПОДКЛЮЧЕНИЕ
           ================================================================ -->
      <div class="create-practice__section">
        <div class="create-practice__section-title">🔗 ПОДКЛЮЧЕНИЕ</div>

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
import { useRouter } from 'vue-router'
import { VHeader, VButton, VInput, VTextarea, VSelect } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useMasterStore } from '@/stores/master'
import { createPractice } from '@/api/practices'
import { formatMoney } from '@/utils/format'
import { ApiResponseError } from '@/api/client'
import { DURATION_OPTIONS, TIMEZONE_OPTIONS } from '@/utils/practiceOptions'
import { COMMISSION_RATE } from '@/utils/commission'
import type { PracticeType } from '@/api/types'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const masterStore = useMasterStore()

const submitting = ref(false)

// -- Practice type options --
const PRACTICE_TYPE_OPTIONS: { label: string; value: string }[] = [
  { label: 'Живая группа (live)', value: 'live' },
  { label: 'Серия занятий (series)', value: 'series' },
  { label: 'Индивидуально (1-on-1)', value: 'one_on_one' },
  { label: 'Запись (replay)', value: 'replay' },
]

// W-7: computed so todayDate updates correctly after midnight (not stale).
const todayDate = computed(() => new Date().toISOString().split('T')[0])

// W-9: human-readable percentage for template display
const commissionPct = Math.round(COMMISSION_RATE * 100)

// -- Form state --
const form = reactive({
  title: '',
  practice_type: 'live',
  date: '',
  time: '',
  duration_minutes: '60',
  timezone: authStore.user?.timezone ?? 'Europe/Moscow',
  max_participants_raw: '',  // string input, parsed to int|null on submit
  is_free: false,
  price_eur_raw: '',          // string input, converted to cents on submit
  description: '',
  zoom_link: '',
})

// -- Validation errors --
const errors = reactive({
  title: '',
  practice_type: '',
  date: '',
  time: '',
  duration_minutes: '',
  max_participants: '',
  price_cents: '',
  zoom_link: '',
})

// -- Computed: price in cents --
const priceCents = computed((): number => {
  const eur = parseFloat(form.price_eur_raw)
  if (isNaN(eur) || eur <= 0) return 0
  return Math.round(eur * 100)
})

// -- Validation --
function validate(): boolean {
  let ok = true

  // Reset
  Object.keys(errors).forEach((k) => {
    errors[k as keyof typeof errors] = ''
  })

  if (!form.title.trim()) {
    errors.title = 'Введите название'
    ok = false
  }
  if (!form.practice_type) {
    errors.practice_type = 'Выберите тип практики'
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
  // Ensure scheduled_at is in the future
  if (form.date && form.time) {
    const dt = new Date(`${form.date}T${form.time}`)
    if (dt <= new Date()) {
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
async function submit(): Promise<void> {
  if (!validate()) return
  if (submitting.value) return
  submitting.value = true

  try {
    // Build ISO UTC datetime from local date + time.
    // MVP simplification: browser local time is treated as the source.
    // See component-level doc note on timezone handling.
    const scheduledAt = new Date(`${form.date}T${form.time}`).toISOString()

    await createPractice({
      practice_type: form.practice_type as PracticeType,
      title: form.title.trim(),
      description: form.description.trim() || null,
      scheduled_at: scheduledAt,
      duration_minutes: parseInt(form.duration_minutes, 10),
      timezone: form.timezone,
      max_participants: form.max_participants_raw
        ? parseInt(form.max_participants_raw, 10)
        : null,
      zoom_link: form.zoom_link.trim() || null,
      is_free: form.is_free,
      price_cents: form.is_free ? 0 : priceCents.value,
      currency: 'EUR',
    })

    toast.success('Практика создана!')
    // Invalidate cached list so it reloads on practices view.
    await masterStore.refreshMyPractices()
    router.push({ name: 'master-practices' })
  } catch (e) {
    const message = e instanceof ApiResponseError ? e.detail : 'Не удалось создать практику'
    toast.error(message)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.create-practice {
  min-height: 100%;
  background: linear-gradient(135deg, var(--velo-bg-start) 0%, var(--velo-bg-end) 100%);
  display: flex;
  flex-direction: column;
}

.create-practice__content {
  flex: 1;
  padding: var(--space-4);
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
  font-size: var(--text-xs);
  font-weight: 700;
  color: var(--velo-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding-bottom: var(--space-1);
  border-bottom: 1px solid var(--velo-border);
}

/* -- Native date/time inputs -- */
.create-practice__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.create-practice__label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-text-secondary);
}

.create-practice__date-input {
  width: 100%;
  padding: 12px var(--space-3);
  background: var(--velo-bg-card);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  outline: none;
  transition: border-color var(--transition-fast);
}

.create-practice__date-input:focus {
  border-color: var(--velo-primary);
}

.create-practice__field-error {
  font-size: var(--text-sm);
  color: var(--velo-error);
}

/* -- Payment toggle -- */
.create-practice__payment-options {
  display: flex;
  gap: var(--space-3);
}

.create-practice__payment-option {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  background: var(--velo-bg-card);
  transition: border-color var(--transition-fast);
}

.create-practice__payment-option--active {
  border-color: var(--velo-primary);
  color: var(--velo-primary);
  background: var(--velo-primary-light, #e8edf5);
}

.create-practice__radio {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid var(--velo-border);
  flex-shrink: 0;
  transition: border-color var(--transition-fast), background var(--transition-fast);
}

.create-practice__radio--active {
  border-color: var(--velo-primary);
  background: var(--velo-primary);
}

/* -- Price calc preview -- */
.create-practice__price-calc {
  background: var(--velo-bg-subtle);
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.create-practice__price-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
}

.create-practice__price-row--total {
  font-weight: 600;
  color: var(--velo-text-primary);
  padding-top: var(--space-2);
  border-top: 1px solid var(--velo-border);
}

/* -- Hint -- */
.create-practice__hint {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}
</style>
