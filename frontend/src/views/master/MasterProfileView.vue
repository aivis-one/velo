<!--
  VELO Frontend -- MasterProfileView (Phase F7, updated TD-FE-ROLE-SWITCH)

  Master profile screen. Route: /master/profile (tab "👤 Я").
  No masterStatusGuard -- accessible even while pending (so master sees their info).

  Sections:
    1. Profile header -- VAvatar + display_name + VBadge + bio + methods chips + стаж.
       Data from masterStore.profile (lazy fetch on mount).

    2. Payout settings -- inline form (v-show).
       - payout === null  → "Не настроено" banner + кнопка "Добавить реквизиты"
       - payout !== null  → method label + masked details + кнопка "Изменить"
       - Form: VSelect method + dynamic fields by method:
           bank_transfer → iban (required), account_holder (optional), swift (optional)
           paypal        → email (required)
           revolut       → tag (required)
       - PATCH /me/payout → masterStore.profile.payout updated in-place + toast.success
       - Client-side validation before submit (iban not empty, email has @, tag not empty)
       - Double-submit guard

    3. Finance link -- card tapping to /master/finance.

    4. Switch to user mode (TD-FE-ROLE-SWITCH) -- sets uiMode='user', navigates to
       /user/profile. Visible to all masters (and admins in master mode).

  Key patterns:
    - masterStore.profile already loaded by masterStatusGuard for verified masters.
      For pending masters: fetchMyProfile() will fail (they're not role='master' yet)
      -- we guard with authStore.role check before fetching.
    - After PATCH success: update masterStore.profile.payout directly from response
      (no full profile re-fetch needed -- balances haven't changed).
-->

<template>
  <div class="master-profile">
    <!-- Loading skeleton -->
    <template v-if="masterStore.profileLoading && !masterStore.profile">
      <div class="master-profile__loader">
        <VLoader size="lg" />
      </div>
    </template>

    <template v-else>
      <!-- ==================================================================
           SECTION 1: PROFILE HEADER
           ================================================================== -->
      <div class="master-profile__header">
        <VAvatar :name="displayName" size="xl" />

        <div class="master-profile__header-info">
          <h1 class="master-profile__name">{{ displayName }}</h1>
          <VBadge v-if="isVerified" variant="success">✓ Верифицирован</VBadge>
          <VBadge v-else variant="warning">На рассмотрении</VBadge>
        </div>
      </div>

      <!-- Bio -->
      <div v-if="bio" class="master-profile__section">
        <div class="master-profile__section-title">О СЕБЕ</div>
        <p class="master-profile__bio">{{ bio }}</p>
      </div>

      <!-- Methods chips -->
      <div v-if="methods.length > 0" class="master-profile__section">
        <div class="master-profile__section-title">НАПРАВЛЕНИЯ</div>
        <div class="master-profile__chips">
          <span
            v-for="method in methods"
            :key="method"
            class="master-profile__chip"
          >
            {{ method }}
          </span>
        </div>
      </div>

      <!-- Experience -->
      <div v-if="experienceYears != null" class="master-profile__section">
        <div class="master-profile__section-title">ОПЫТ</div>
        <p class="master-profile__experience">
          {{ experienceYears }} {{ pluralYears(experienceYears) }}
        </p>
      </div>

      <!-- ==================================================================
           SECTION 2: PAYOUT SETTINGS
           ================================================================== -->
      <div class="master-profile__section master-profile__payout-section">
        <div class="master-profile__section-title">💳 РЕКВИЗИТЫ ВЫПЛАТ</div>

        <!-- Current state (not editing) -->
        <template v-if="!showPayoutForm">
          <!-- Not configured -->
          <div v-if="!hasPayout" class="master-profile__payout-empty">
            <p class="master-profile__payout-empty-text">
              Реквизиты не настроены. Укажите их, чтобы запрашивать выводы.
            </p>
            <VButton variant="secondary" size="sm" @click="openPayoutForm(false)">
              + Добавить реквизиты
            </VButton>
          </div>

          <!-- Configured -->
          <div v-else class="master-profile__payout-configured">
            <div class="master-profile__payout-row">
              <span class="master-profile__payout-method">
                {{ methodLabel(masterStore.profile!.payout!.method) }}
              </span>
              <VBadge variant="success">Настроено</VBadge>
            </div>
            <p class="master-profile__payout-details-text">
              {{ maskedDetails(masterStore.profile!.payout!) }}
            </p>
            <VButton variant="outline" size="sm" @click="openPayoutForm(true)">
              Изменить
            </VButton>
          </div>
        </template>

        <!-- Inline payout form -->
        <div v-show="showPayoutForm" class="master-profile__payout-form">
          <VSelect
            v-model="payoutForm.method"
            label="Способ выплаты"
            :options="METHOD_OPTIONS"
            @update:model-value="onMethodChange"
          />

          <!-- bank_transfer fields -->
          <template v-if="payoutForm.method === 'bank_transfer'">
            <VInput
              v-model="payoutForm.iban"
              label="IBAN *"
              placeholder="DE89 3704 0044 0532 0130 00"
              :error="formErrors.iban"
            />
            <VInput
              v-model="payoutForm.accountHolder"
              label="Имя владельца счёта"
              placeholder="Ivan Ivanov"
            />
            <VInput
              v-model="payoutForm.swift"
              label="BIC / SWIFT (необязательно)"
              placeholder="COBADEFFXXX"
            />
          </template>

          <!-- paypal fields -->
          <template v-else-if="payoutForm.method === 'paypal'">
            <VInput
              v-model="payoutForm.email"
              label="PayPal Email *"
              type="email"
              placeholder="you@example.com"
              :error="formErrors.email"
            />
          </template>

          <!-- revolut fields -->
          <template v-else-if="payoutForm.method === 'revolut'">
            <VInput
              v-model="payoutForm.tag"
              label="Revolut Tag или телефон *"
              placeholder="@username или +49123456789"
              :error="formErrors.tag"
            />
          </template>

          <!-- Actions -->
          <div class="master-profile__payout-form-actions">
            <VButton
              variant="primary"
              :loading="savingPayout"
              :disabled="savingPayout"
              @click="savePayout"
            >
              Сохранить
            </VButton>
            <VButton variant="ghost" :disabled="savingPayout" @click="closePayoutForm">
              Отмена
            </VButton>
          </div>
        </div>
      </div>

      <!-- ==================================================================
           SECTION 3: FINANCE LINK
           ================================================================== -->
      <div
        class="master-profile__finance-link"
        @click="router.push({ name: 'master-finance' })"
      >
        <div class="master-profile__finance-link-left">
          <span class="master-profile__finance-link-icon">💰</span>
          <div>
            <div class="master-profile__finance-link-title">Финансы и выводы</div>
            <div class="master-profile__finance-link-sub">
              Баланс · История выводов
            </div>
          </div>
        </div>
        <span class="master-profile__finance-link-arrow">→</span>
      </div>

      <!-- ==================================================================
           SECTION 4: SWITCH TO USER MODE (TD-FE-ROLE-SWITCH)
           ================================================================== -->
      <div class="master-profile__section master-profile__switch-section">
        <div class="master-profile__section-title">РЕЖИМ ПРОСМОТРА</div>
        <p class="master-profile__switch-desc">
          Перейдите в интерфейс пользователя, чтобы просматривать каталог и бронировать практики.
        </p>
        <VButton variant="secondary" @click="switchToUserMode">
          Перейти в интерфейс пользователя →
        </VButton>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VButton, VBadge, VAvatar, VInput, VSelect, VLoader } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useMasterStore } from '@/stores/master'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { updatePayoutDetails } from '@/api/masters'
import { ApiResponseError } from '@/api/client'
import type { PayoutDetails } from '@/api/types'

// ---------------------------------------------------------------------------
// Router + stores
// ---------------------------------------------------------------------------

const router = useRouter()
const toast = useToast()
const masterStore = useMasterStore()
const authStore = useAuthStore()
const uiStore = useUiStore()

// ---------------------------------------------------------------------------
// Profile computed values
// ---------------------------------------------------------------------------

const displayName = computed(
  () => masterStore.profile?.display_name ?? authStore.user?.first_name ?? 'Мастер',
)
const isVerified = computed(() => masterStore.profile?.status === 'verified')
const bio = computed(() => masterStore.profile?.bio ?? '')
const methods = computed(() => masterStore.profile?.methods ?? [])
const experienceYears = computed(() => masterStore.profile?.experience_years ?? null)
const hasPayout = computed(() => masterStore.profile?.payout != null)

function pluralYears(n: number): string {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod100 >= 11 && mod100 <= 14) return 'лет'
  if (mod10 === 1) return 'год'
  if (mod10 >= 2 && mod10 <= 4) return 'года'
  return 'лет'
}

// ---------------------------------------------------------------------------
// Payout form state
// ---------------------------------------------------------------------------

const METHOD_OPTIONS = [
  { value: 'bank_transfer', label: 'Банковский перевод (IBAN)' },
  { value: 'paypal', label: 'PayPal' },
  { value: 'revolut', label: 'Revolut' },
]

const showPayoutForm = ref(false)
const savingPayout = ref(false)

// Flat reactive form -- each method uses different subset of fields.
const payoutForm = reactive({
  method: 'bank_transfer',
  // bank_transfer
  iban: '',
  accountHolder: '',
  swift: '',
  // paypal
  email: '',
  // revolut
  tag: '',
})

const formErrors = reactive({
  iban: '',
  email: '',
  tag: '',
})

/** Open form, pre-filling from existing payout if editing. */
function openPayoutForm(editing: boolean): void {
  clearFormErrors()
  if (editing && masterStore.profile?.payout) {
    const p = masterStore.profile.payout
    payoutForm.method = p.method
    const d = p.details as Record<string, string>
    payoutForm.iban = d['iban'] ?? ''
    payoutForm.accountHolder = d['account_holder'] ?? ''
    payoutForm.swift = d['swift'] ?? ''
    payoutForm.email = d['email'] ?? ''
    payoutForm.tag = d['tag'] ?? d['phone'] ?? ''
  } else {
    payoutForm.method = 'bank_transfer'
    payoutForm.iban = ''
    payoutForm.accountHolder = ''
    payoutForm.swift = ''
    payoutForm.email = ''
    payoutForm.tag = ''
  }
  showPayoutForm.value = true
}

function closePayoutForm(): void {
  showPayoutForm.value = false
  clearFormErrors()
}

/** Clear field-specific errors when method changes. */
function onMethodChange(): void {
  clearFormErrors()
}

function clearFormErrors(): void {
  formErrors.iban = ''
  formErrors.email = ''
  formErrors.tag = ''
}

/** Build PayoutDetails body for PATCH request from flat form fields. */
function buildPayoutBody(): PayoutDetails | null {
  clearFormErrors()
  let valid = true

  if (payoutForm.method === 'bank_transfer') {
    if (!payoutForm.iban.trim()) {
      formErrors.iban = 'IBAN обязателен'
      valid = false
    }
    if (!valid) return null
    const details: Record<string, string> = { iban: payoutForm.iban.trim() }
    if (payoutForm.accountHolder.trim()) {
      details['account_holder'] = payoutForm.accountHolder.trim()
    }
    if (payoutForm.swift.trim()) {
      details['swift'] = payoutForm.swift.trim()
    }
    return { method: 'bank_transfer', details }
  }

  if (payoutForm.method === 'paypal') {
    if (!payoutForm.email.trim() || !payoutForm.email.includes('@')) {
      formErrors.email = 'Введите корректный email'
      valid = false
    }
    if (!valid) return null
    return { method: 'paypal', details: { email: payoutForm.email.trim() } }
  }

  if (payoutForm.method === 'revolut') {
    if (!payoutForm.tag.trim()) {
      formErrors.tag = 'Укажите Revolut tag или телефон'
      valid = false
    }
    if (!valid) return null
    // Detect phone vs tag by leading '+'.
    const value = payoutForm.tag.trim()
    const key = value.startsWith('+') ? 'phone' : 'tag'
    return { method: 'revolut', details: { [key]: value } }
  }

  return null
}

async function savePayout(): Promise<void> {
  // Double-submit guard.
  if (savingPayout.value) return

  const body = buildPayoutBody()
  if (!body) return // validation failed, errors displayed

  savingPayout.value = true
  try {
    const result = await updatePayoutDetails(body)
    // Update store in-place -- no need to re-fetch full profile.
    if (masterStore.profile) {
      masterStore.profile.payout = result
    }
    showPayoutForm.value = false
    toast.success('Реквизиты сохранены')
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Не удалось сохранить реквизиты'
    toast.error(msg)
  } finally {
    savingPayout.value = false
  }
}

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------

const METHOD_LABEL: Record<string, string> = {
  bank_transfer: 'Банковский перевод',
  paypal: 'PayPal',
  revolut: 'Revolut',
}

function methodLabel(method: string): string {
  return METHOD_LABEL[method] ?? method
}

/** Returns a masked/summary string for configured payout details. */
function maskedDetails(payout: PayoutDetails): string {
  const d = payout.details as Record<string, string>
  switch (payout.method) {
    case 'bank_transfer': {
      const iban = d['iban'] ?? ''
      // Show last 4 chars of IBAN with mask: DE•• •••• •••• •••• 0000
      const last4 = iban.replace(/\s/g, '').slice(-4)
      return last4 ? `IBAN ···· ${last4}` : 'IBAN настроен'
    }
    case 'paypal': {
      const email = d['email'] ?? ''
      const atIdx = email.indexOf('@')
      if (atIdx > 1) {
        return email[0] + '···' + email.slice(atIdx)
      }
      return email || 'Email настроен'
    }
    case 'revolut': {
      const tag = d['tag'] ?? d['phone'] ?? ''
      return tag || 'Настроено'
    }
    default:
      return 'Настроено'
  }
}

// ---------------------------------------------------------------------------
// Switch to user mode (TD-FE-ROLE-SWITCH)
// ---------------------------------------------------------------------------

function switchToUserMode(): void {
  uiStore.setUiMode('user')
  router.push({ name: 'user-profile' })
}

// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------

onMounted(async () => {
  // Only fetch for verified masters (role='master').
  // Pending users (role='user') don't have a master profile endpoint yet.
  if (authStore.role === 'master') {
    await masterStore.fetchMyProfile()
  }
})
</script>

<style scoped>
.master-profile {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.master-profile__loader {
  display: flex;
  justify-content: center;
  padding-top: var(--space-12);
}

/* -- Header -- */
.master-profile__header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.master-profile__header-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  min-width: 0;
}

.master-profile__name {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  color: var(--velo-text-primary);
  line-height: 1.2;
  word-break: break-word;
}

/* -- Generic section -- */
.master-profile__section {
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.master-profile__section-title {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: var(--space-3);
}

.master-profile__bio {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.6;
}

.master-profile__experience {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  font-weight: 400;
}

/* -- Methods chips -- */
.master-profile__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.master-profile__chip {
  padding: var(--space-1) var(--space-3);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: 100px;
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-primary);
}

/* -- Payout section -- */
.master-profile__payout-section {
  border: 1px solid #ffffff;
}

.master-profile__payout-empty {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.master-profile__payout-empty-text {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.5;
}

.master-profile__payout-configured {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.master-profile__payout-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.master-profile__payout-method {
  font-weight: 400;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.master-profile__payout-details-text {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  font-family: monospace;
  letter-spacing: 0.03em;
}

/* -- Payout form -- */
.master-profile__payout-form {
  margin-top: var(--space-2);
}

.master-profile__payout-form-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

/* -- Finance link card -- */
.master-profile__finance-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: opacity var(--transition-fast);
  gap: var(--space-3);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.master-profile__finance-link:active {
  opacity: 0.8;
}

.master-profile__finance-link-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.master-profile__finance-link-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.master-profile__finance-link-title {
  font-weight: 400;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.master-profile__finance-link-sub {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  margin-top: 2px;
}

.master-profile__finance-link-arrow {
  font-size: var(--text-lg);
  color: var(--velo-text-muted);
  flex-shrink: 0;
}

/* -- Switch section -- */
.master-profile__switch-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.master-profile__switch-desc {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.5;
}
</style>
