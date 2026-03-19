<!--
  VELO Frontend -- MasterApplyView (Phase F6.1)

  3-step master application form. Standalone route (no MasterShell,
  no tab bar) -- accessible to role='user'.

  Steps:
    1. Profile  -- display_name (required), email, phone
    2. Experience -- methods (checkboxes), experience_years (select), bio
    3. Documents -- placeholder (no real upload in MVP), terms checkbox

  All data collected across steps is sent as one POST /api/v1/masters/apply
  on step 3 submit. On success -> /master/pending.

  Back button on step 1 -> router.back() (returns to previous page,
  typically /user/profile). Steps 2-3 -> go to previous step.

  Note on checkboxes: uses custom native-checkbox markup (.apply-view__checkbox-item),
  NOT the VCheckbox component -- VCheckbox is intentionally NOT imported here.
-->

<template>
  <div class="apply-view">
    <!-- Header -->
    <VHeader
      title="Заявка"
      show-back
      @back="onBack"
    />

    <!-- Progress bar -->
    <div class="apply-view__progress">
      <div
        v-for="n in 3"
        :key="n"
        class="apply-view__progress-step"
        :class="{
          'apply-view__progress-step--completed': step > n,
          'apply-view__progress-step--active': step === n,
        }"
      />
    </div>

    <div class="apply-view__content">
      <!-- ================================================================
           STEP 1: Profile
           ================================================================ -->
      <template v-if="step === 1">
        <h3 class="apply-view__step-title">Шаг 1: Профиль</h3>

        <VInput
          v-model="form.display_name"
          label="Имя *"
          placeholder="Alex Mindful"
          :error="errors.display_name"
        />

        <VInput
          v-model="form.email"
          label="Email"
          type="email"
          placeholder="alex@example.com"
        />

        <VInput
          v-model="form.phone"
          label="Телефон"
          type="tel"
          placeholder="+7 (999) 123-45-67"
        />

        <VButton variant="primary" block size="lg" class="apply-view__next" @click="goToStep2">
          Далее →
        </VButton>
      </template>

      <!-- ================================================================
           STEP 2: Experience
           ================================================================ -->
      <template v-else-if="step === 2">
        <h3 class="apply-view__step-title">Шаг 2: Опыт</h3>

        <!-- Methods checkboxes (custom native markup -- not VCheckbox) -->
        <div class="apply-view__field">
          <label class="apply-view__label">Направления практик *</label>
          <div class="apply-view__checkbox-list">
            <label
              v-for="method in AVAILABLE_METHODS"
              :key="method"
              class="apply-view__checkbox-item"
            >
              <input
                type="checkbox"
                :value="method"
                :checked="form.methods.includes(method)"
                @change="toggleMethod(method)"
              />
              <span class="apply-view__checkbox-mark">
                {{ form.methods.includes(method) ? '✓' : '' }}
              </span>
              <span class="apply-view__checkbox-label">{{ method }}</span>
            </label>
            <!-- "Other" with text input -->
            <label class="apply-view__checkbox-item">
              <input
                type="checkbox"
                :checked="otherMethodEnabled"
                @change="toggleOtherMethod"
              />
              <span class="apply-view__checkbox-mark">
                {{ otherMethodEnabled ? '✓' : '' }}
              </span>
              <span class="apply-view__checkbox-label">Другое</span>
            </label>
            <VInput
              v-if="otherMethodEnabled"
              v-model="otherMethodText"
              placeholder="Укажите направление..."
            />
          </div>
          <p v-if="errors.methods" class="apply-view__field-error">{{ errors.methods }}</p>
        </div>

        <!-- Experience years -->
        <VSelect
          v-model="experienceLabel"
          label="Опыт преподавания *"
          :options="EXPERIENCE_OPTIONS"
          :error="errors.experience_years"
        />

        <!-- Bio -->
        <VTextarea
          v-model="form.bio"
          label="О себе (опционально)"
          placeholder="Расскажите о вашем опыте и подходе к практикам..."
          :rows="4"
        />

        <VButton variant="primary" block size="lg" class="apply-view__next" @click="goToStep3">
          Далее →
        </VButton>
      </template>

      <!-- ================================================================
           STEP 3: Documents (placeholder -- no real upload in MVP)
           ================================================================ -->
      <template v-else>
        <h3 class="apply-view__step-title">Шаг 3: Документы</h3>

        <!-- Passport upload placeholder -->
        <div class="apply-view__field">
          <label class="apply-view__label">Паспорт (скан или фото) *</label>
          <div class="apply-view__upload-area">
            <span class="apply-view__upload-icon">📄</span>
            <p class="apply-view__upload-text">+ Загрузить документ</p>
          </div>
          <p class="apply-view__hint">Для верификации личности. Не публикуется.</p>
        </div>

        <!-- Certificates upload placeholder -->
        <div class="apply-view__field">
          <label class="apply-view__label">Сертификаты</label>
          <div class="apply-view__upload-area">
            <span class="apply-view__upload-icon">📄</span>
            <p class="apply-view__upload-text">+ Добавить сертификат</p>
          </div>
          <p class="apply-view__hint">Можно загрузить несколько файлов.</p>
        </div>

        <!-- Terms checkbox (custom native markup) -->
        <div class="apply-view__terms">
          <label class="apply-view__checkbox-item" @click="form.termsAccepted = !form.termsAccepted">
            <span
              class="apply-view__checkbox-mark"
              :class="{ 'apply-view__checkbox-mark--checked': form.termsAccepted }"
            >
              {{ form.termsAccepted ? '✓' : '' }}
            </span>
            <span class="apply-view__checkbox-label">
              Я соглашаюсь с условиями использования
            </span>
          </label>
          <p v-if="errors.terms" class="apply-view__field-error">{{ errors.terms }}</p>
        </div>

        <VButton
          variant="primary"
          block
          size="lg"
          class="apply-view__next"
          :loading="submitting"
          @click="submit"
        >
          Отправить заявку
        </VButton>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton, VInput, VTextarea, VSelect } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { applyMaster } from '@/api/masters'
import { ApiResponseError } from '@/api/client'

const router = useRouter()
const toast = useToast()

// -- Step state --
const step = ref(1)
const submitting = ref(false)

// -- Available practice methods (from mockup) --
const AVAILABLE_METHODS = [
  'Медитация',
  'Mindfulness / MBSR',
  'Дыхательные практики',
  'Йога',
  'Кундалини йога',
  'Звукотерапия',
]

// -- Experience years options: label -> integer value mapping --
const EXPERIENCE_OPTIONS = [
  { label: 'Менее 1 года', value: '0' },
  { label: '1-3 года',     value: '2' },
  { label: '3-5 лет',      value: '4' },
  { label: '5-10 лет',     value: '7' },
  { label: 'Более 10 лет', value: '11' },
]

// -- Form state --
const form = reactive({
  // Step 1
  display_name: '',
  email: '',
  phone: '',
  // Step 2
  methods: [] as string[],
  bio: '',
  // Step 3
  termsAccepted: false,
})

// "Other" method handling
const otherMethodEnabled = ref(false)
const otherMethodText = ref('')

// Experience years stored as string label, mapped to int on submit
const experienceLabel = ref('')

// -- Validation errors --
const errors = reactive({
  display_name: '',
  methods: '',
  experience_years: '',
  terms: '',
})

// -- Methods helpers --
function toggleMethod(method: string): void {
  const idx = form.methods.indexOf(method)
  if (idx === -1) {
    form.methods.push(method)
  } else {
    form.methods.splice(idx, 1)
  }
}

function toggleOtherMethod(): void {
  otherMethodEnabled.value = !otherMethodEnabled.value
  if (!otherMethodEnabled.value) {
    otherMethodText.value = ''
  }
}

// -- All methods including "other" text --
const allMethods = computed((): string[] => {
  const result = [...form.methods]
  if (otherMethodEnabled.value && otherMethodText.value.trim()) {
    result.push(otherMethodText.value.trim())
  }
  return result
})

// -- Experience years numeric value --
const experienceYears = computed((): number => {
  const opt = EXPERIENCE_OPTIONS.find((o) => o.value === experienceLabel.value)
  return opt ? parseInt(opt.value, 10) : 0
})

// -- Navigation --
function onBack(): void {
  if (step.value > 1) {
    step.value -= 1
  } else {
    router.back()
  }
}

// -- Step 1 validation and advance --
function goToStep2(): void {
  errors.display_name = ''
  if (!form.display_name.trim()) {
    errors.display_name = 'Пожалуйста, введите имя'
    return
  }
  step.value = 2
}

// -- Step 2 validation and advance --
function goToStep3(): void {
  errors.methods = ''
  errors.experience_years = ''

  if (allMethods.value.length === 0) {
    errors.methods = 'Выберите хотя бы одно направление'
    return
  }
  if (!experienceLabel.value) {
    errors.experience_years = 'Выберите опыт преподавания'
    return
  }
  step.value = 3
}

// -- Final submit --
// FP-04: double-submit guard must come before any validation --
// parallel clicks both pass termsAccepted check before guard fires.
async function submit(): Promise<void> {
  if (submitting.value) return

  errors.terms = ''

  if (!form.termsAccepted) {
    errors.terms = 'Необходимо принять условия использования'
    return
  }

  submitting.value = true

  try {
    await applyMaster({
      profile: {
        display_name: form.display_name.trim(),
        email: form.email.trim() || null,
        phone: form.phone.trim() || null,
      },
      experience: {
        methods: allMethods.value,
        experience_years: experienceYears.value,
        bio: form.bio.trim() || null,
        certifications: [],
      },
      documents: [],
    })

    toast.success('Заявка отправлена!')
    router.push({ name: 'master-pending' })
  } catch (e) {
    const message =
      e instanceof ApiResponseError ? e.detail : 'Не удалось отправить заявку'
    toast.error(message)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.apply-view {
  min-height: 100dvh;
  min-height: 100vh;
  background: transparent;
  display: flex;
  flex-direction: column;
}

/* -- Progress bar -- */
.apply-view__progress {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--velo-glass-blue-15);
  border-bottom: 1px solid var(--velo-border-light);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.apply-view__progress-step {
  flex: 1;
  height: 4px;
  border-radius: var(--radius-full);
  background: var(--velo-border-light);
  transition: background var(--transition-base);
}

.apply-view__progress-step--active {
  background: var(--velo-primary);
}

.apply-view__progress-step--completed {
  background: var(--velo-success);
}

/* -- Content area -- */
.apply-view__content {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.apply-view__step-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  color: var(--velo-text-primary);
  margin-bottom: var(--space-2);
}

/* -- Methods checkbox list -- */
.apply-view__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.apply-view__label {
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

.apply-view__checkbox-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.apply-view__checkbox-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
  user-select: none;
  /* Hide native checkbox -- rendered as custom mark */
}

.apply-view__checkbox-item input[type='checkbox'] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.apply-view__checkbox-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: 2px solid var(--velo-border-light);
  border-radius: 5px;
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-primary);
  background: var(--velo-glass-blue-15);
  flex-shrink: 0;
  transition: border-color var(--transition-fast);
}

.apply-view__checkbox-mark--checked,
.apply-view__checkbox-item input:checked + .apply-view__checkbox-mark {
  border-color: var(--velo-primary);
  background: var(--velo-primary);
  color: white;
}

.apply-view__checkbox-label {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.apply-view__field-error {
  font-size: var(--text-sm);
  color: var(--velo-error);
}

/* -- Upload placeholder -- */
.apply-view__upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-5);
  border: 2px dashed var(--velo-border-light);
  border-radius: var(--radius-md);
  background: var(--velo-glass-blue-15);
  gap: var(--space-2);
  cursor: pointer;
  transition: border-color var(--transition-fast);
}

.apply-view__upload-area:hover {
  border-color: var(--velo-primary);
}

.apply-view__upload-icon {
  font-size: 28px;
}

.apply-view__upload-text {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
}

.apply-view__hint {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

/* -- Terms -- */
.apply-view__terms {
  padding: var(--space-3);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.apply-view__next {
  margin-top: auto;
}
</style>
