<!--
  VELO Frontend -- MasterFinanceView (Phase F7, fixed W-1/W-2/W-3)

  Master finance screen. Route: /master/finance (inside MasterShell).
  Guard: masterStatusGuard (verified masters only).

  Sections:
    1. Balance card -- available_cents + frozen_cents from masterStore.profile.
       Profile is already loaded by masterStatusGuard (lazy fetch on mount).

    2. Withdraw form (v-show) -- shown when master clicks "Вывести средства".
       - Amount input (euros, converted to cents for API call).
       - "Вывести всё" button -- fills input with available_cents / 100.
       - If payout not configured: warning banner with link to /master/profile.
       - On success: toast + refresh profile (balances) + reload withdrawals.

    3. Withdrawals history -- GET /masters/me/withdrawals, paginated.
       "Показать ещё" loads next page (offset += LIMIT).

  Key patterns:
    - Double-submit guard: if (submitting.value) return
    - masterStore.fetchMyProfile(true) after withdrawal to refresh balances.
    - ApiResponseError.detail for user-facing error messages.
    - formatMoney(cents, 'EUR', 'ru', true) for all monetary values.
    - MIN_WITHDRAWAL_EUROS = 50 (mirrors backend min_withdrawal_cents=5000).
    - WITHDRAWAL_FEE_EUROS = 2 (mirrors backend withdrawal_fee_cents=200).

  Fixes (W-1/W-2/W-3 from F7 review):
    W-1: amountCents uses eurStringToCents() -- no parseFloat * 100 float trap.
    W-2: fillMaxAmount uses centsToEurString() -- consistent utility usage.
    W-3: "Вы получите" hint hidden when amountCents === 0 (empty/invalid input).
-->

<template>
  <div class="finance-view">
    <!-- ====================================================================
         BALANCE CARD
         ==================================================================== -->
    <div class="finance-view__balance-card">
      <div class="finance-view__balance-row">
        <div>
          <div class="finance-view__balance-label">Доступно к выводу</div>
          <div class="finance-view__balance-value">{{ formattedAvailable }}</div>
        </div>
        <IconFinance :size="28" class="finance-view__balance-icon" />
      </div>

      <div v-if="frozenCents > 0" class="finance-view__frozen-row">
        <span class="finance-view__frozen-label">На рассмотрении:</span>
        <span class="finance-view__frozen-value">{{ formattedFrozen }}</span>
      </div>

      <VButton
        variant="primary"
        block
        class="finance-view__withdraw-btn"
        :disabled="availableCents === 0"
        @click="toggleWithdrawForm"
      >
        {{ showWithdrawForm ? 'Скрыть форму' : 'Вывести средства' }}
      </VButton>
    </div>

    <!-- ====================================================================
         PAYOUT REQUISITES (moved here from the profile hub)
         ==================================================================== -->
    <VCard class="finance-view__section finance-view__payout-section" padding="none">
      <div class="finance-view__section-title">РЕКВИЗИТЫ ВЫПЛАТ</div>

      <template v-if="!showPayoutForm">
        <div v-if="!hasPayout" class="finance-view__payout-empty">
          <p class="finance-view__payout-empty-text">
            Реквизиты не настроены. Укажите их, чтобы выводить средства.
          </p>
          <VButton variant="secondary" size="sm" @click="openPayoutForm(false)">
            + Добавить реквизиты
          </VButton>
        </div>

        <div v-else class="finance-view__payout-configured">
          <div class="finance-view__payout-row">
            <span class="finance-view__payout-method">
              {{ methodLabel(masterStore.profile!.payout!.method) }}
            </span>
            <VBadge variant="success">Настроено</VBadge>
          </div>
          <p class="finance-view__payout-details-text">
            {{ maskedDetails(masterStore.profile!.payout!) }}
          </p>
          <VButton variant="outline" size="sm" @click="openPayoutForm(true)">
            Изменить
          </VButton>
        </div>
      </template>

      <div v-show="showPayoutForm" class="finance-view__payout-form">
        <VSelect
          v-model="payoutForm.method"
          label="Способ выплаты"
          :options="METHOD_OPTIONS"
          @update:model-value="onMethodChange"
        />

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

        <template v-else-if="payoutForm.method === 'paypal'">
          <VInput
            v-model="payoutForm.email"
            label="PayPal Email *"
            type="email"
            placeholder="you@example.com"
            :error="formErrors.email"
          />
        </template>

        <template v-else-if="payoutForm.method === 'revolut'">
          <VInput
            v-model="payoutForm.tag"
            label="Revolut Tag или телефон *"
            placeholder="@username или +49123456789"
            :error="formErrors.tag"
          />
        </template>

        <div class="finance-view__payout-form-actions">
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
    </VCard>

    <!-- ====================================================================
         WITHDRAW FORM
         ==================================================================== -->
    <div v-show="showWithdrawForm" class="finance-view__section finance-view__withdraw-section">
      <div class="finance-view__section-title">ЗАПРОС ВЫВОДА</div>

      <!-- No payout configured warning -->
      <div v-if="!hasPayout" class="finance-view__warning">
        <p class="finance-view__warning-text">
          Сначала укажите реквизиты в разделе «Реквизиты выплат» выше.
        </p>
        <VButton variant="secondary" size="sm" @click="openPayoutForm(false)">
          + Добавить реквизиты
        </VButton>
      </div>

      <!-- Withdraw form (shown when payout is configured) -->
      <template v-else>
        <div class="finance-view__amount-group">
          <label class="finance-view__label">Сумма вывода (EUR)</label>
          <div class="finance-view__amount-row">
            <VInput
              v-model="amountInput"
              type="number"
              :min="MIN_WITHDRAWAL_EUROS"
              step="0.01"
              placeholder="0.00"
            />
            <VButton variant="secondary" size="sm" @click="fillMaxAmount">
              Всё
            </VButton>
          </div>
          <p class="finance-view__hint">
            Минимум {{ formatMoney(MIN_WITHDRAWAL_EUROS * 100, 'EUR', 'ru', true) }} ·
            Комиссия {{ formatMoney(WITHDRAWAL_FEE_EUROS * 100, 'EUR', 'ru', true) }}
            <!-- W-3: show net amount only when input is valid (amountCents > 0) -->
            <template v-if="amountCents > 0">
              · Вы получите {{ formattedNetAmount }}
            </template>
          </p>
          <p v-if="amountError" class="finance-view__error">{{ amountError }}</p>
        </div>

        <VButton
          variant="primary"
          block
          :loading="submitting"
          :disabled="submitting || !!amountError || !amountInput"
          @click="submitWithdrawal"
        >
          Запросить вывод
        </VButton>
      </template>
    </div>

    <!-- ====================================================================
         WITHDRAWALS HISTORY
         ==================================================================== -->
    <VCard class="finance-view__section" padding="none">
      <div class="finance-view__section-title">ИСТОРИЯ ВЫВОДОВ</div>

      <!-- Loading state -->
      <div v-if="historyLoading && withdrawals.length === 0" class="finance-view__loader">
        <VLoader size="md" />
      </div>

      <!-- Empty state -->
      <div
        v-else-if="!historyLoading && withdrawals.length === 0"
        class="finance-view__empty"
      >
        <p class="finance-view__empty-text">Выводов ещё не было</p>
      </div>

      <!-- List -->
      <div v-else class="finance-view__history-list">
        <div
          v-for="w in withdrawals"
          :key="w.id"
          class="finance-view__history-item"
        >
          <!-- Left: amount + method -->
          <div class="finance-view__history-left">
            <div class="finance-view__history-amount">
              {{ formatMoney(w.amount_cents, 'EUR', 'ru', true) }}
            </div>
            <div class="finance-view__history-meta">
              {{ methodLabel(w.payout_details.method) }} ·
              {{ withdrawalDate(w) }}
            </div>
            <div v-if="w.fee_cents > 0" class="finance-view__history-fee">
              Комиссия {{ formatMoney(w.fee_cents, 'EUR', 'ru', true) }} ·
              Вы получите {{ formatMoney(w.amount_cents - w.fee_cents, 'EUR', 'ru', true) }}
            </div>
          </div>

          <!-- Right: status badge -->
          <VBadge :variant="statusVariant(w.status)">
            {{ statusLabel(w.status) }}
          </VBadge>
        </div>
      </div>

      <!-- Load more -->
      <VButton
        v-if="hasMore"
        variant="ghost"
        block
        :loading="historyLoading"
        class="finance-view__load-more"
        @click="loadMoreWithdrawals"
      >
        Показать ещё
      </VButton>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { VButton, VBadge, VLoader, VCard, VInput, VSelect } from '@/components/ui'
import { IconFinance } from '@/components/icons'
import { useToast } from '@/composables/useToast'
import { useViewerTimezone } from '@/composables/useViewerTimezone'
import { useMasterStore } from '@/stores/master'
import { getMyWithdrawals, createWithdrawal, updatePayoutDetails } from '@/api/masters'
import { ApiResponseError } from '@/api/client'
import { formatMoney, formatDateShort } from '@/utils/format'
import { eurStringToCents, centsToEurString } from '@/utils/currency'
import type { WithdrawalResponse, WithdrawalStatus, PayoutDetails } from '@/api/types'

// TD-FE-W6: imported from utils/constants -- mirrors backend config.py.
// min_withdrawal_cents=5000, withdrawal_fee_cents=200.
import { MIN_WITHDRAWAL_EUROS, WITHDRAWAL_FEE_EUROS } from '@/utils/constants'

/** Items per history page. */
const LIMIT = 20

// ---------------------------------------------------------------------------
// Router + stores
// ---------------------------------------------------------------------------

const toast = useToast()
const masterStore = useMasterStore()
const viewerTz = useViewerTimezone()

// ---------------------------------------------------------------------------
// Balance (derived from master store profile)
// ---------------------------------------------------------------------------

const availableCents = computed(() => masterStore.profile?.available_cents ?? 0)
const frozenCents = computed(() => masterStore.profile?.frozen_cents ?? 0)
const hasPayout = computed(() => masterStore.profile?.payout != null)

const formattedAvailable = computed(() =>
  formatMoney(availableCents.value, 'EUR', 'ru', true),
)

const formattedFrozen = computed(() =>
  formatMoney(frozenCents.value, 'EUR', 'ru', true),
)

// ---------------------------------------------------------------------------
// Payout requisites (moved here from the profile hub)
// ---------------------------------------------------------------------------

const METHOD_OPTIONS = [
  { value: 'bank_transfer', label: 'Банковский перевод (IBAN)' },
  { value: 'paypal', label: 'PayPal' },
  { value: 'revolut', label: 'Revolut' },
]

const showPayoutForm = ref(false)
const savingPayout = ref(false)

const payoutForm = reactive({
  method: 'bank_transfer',
  iban: '',
  accountHolder: '',
  swift: '',
  email: '',
  tag: '',
})

const formErrors = reactive({ iban: '', email: '', tag: '' })

function clearFormErrors(): void {
  formErrors.iban = ''
  formErrors.email = ''
  formErrors.tag = ''
}

/** Open the payout form, pre-filling from the existing payout when editing. */
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

function onMethodChange(): void {
  clearFormErrors()
}

/** Build the PayoutDetails body from the flat form, validating required fields. */
function buildPayoutBody(): PayoutDetails | null {
  clearFormErrors()
  if (payoutForm.method === 'bank_transfer') {
    if (!payoutForm.iban.trim()) {
      formErrors.iban = 'IBAN обязателен'
      return null
    }
    const details: Record<string, string> = { iban: payoutForm.iban.trim() }
    if (payoutForm.accountHolder.trim()) details['account_holder'] = payoutForm.accountHolder.trim()
    if (payoutForm.swift.trim()) details['swift'] = payoutForm.swift.trim()
    return { method: 'bank_transfer', details }
  }
  if (payoutForm.method === 'paypal') {
    if (!payoutForm.email.trim() || !payoutForm.email.includes('@')) {
      formErrors.email = 'Введите корректный email'
      return null
    }
    return { method: 'paypal', details: { email: payoutForm.email.trim() } }
  }
  if (payoutForm.method === 'revolut') {
    if (!payoutForm.tag.trim()) {
      formErrors.tag = 'Укажите Revolut tag или телефон'
      return null
    }
    const value = payoutForm.tag.trim()
    const key = value.startsWith('+') ? 'phone' : 'tag'
    return { method: 'revolut', details: { [key]: value } }
  }
  return null
}

async function savePayout(): Promise<void> {
  if (savingPayout.value) return
  const body = buildPayoutBody()
  if (!body) return
  savingPayout.value = true
  try {
    const result = await updatePayoutDetails(body)
    if (masterStore.profile) masterStore.profile.payout = result
    showPayoutForm.value = false
    toast.success('Реквизиты сохранены')
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Не удалось сохранить реквизиты'
    toast.error(msg)
  } finally {
    savingPayout.value = false
  }
}

/** Masked summary of the configured payout details. */
function maskedDetails(payout: PayoutDetails): string {
  const d = payout.details as Record<string, string>
  switch (payout.method) {
    case 'bank_transfer': {
      const iban = (d['iban'] ?? '').replace(/\s/g, '')
      const last4 = iban.slice(-4)
      return last4 ? `IBAN ···· ${last4}` : 'IBAN настроен'
    }
    case 'paypal': {
      const email = d['email'] ?? ''
      const at = email.indexOf('@')
      return at > 1 ? email[0] + '···' + email.slice(at) : email || 'Email настроен'
    }
    case 'revolut':
      return d['tag'] ?? d['phone'] ?? 'Настроено'
    default:
      return 'Настроено'
  }
}

// ---------------------------------------------------------------------------
// Withdraw form state
// ---------------------------------------------------------------------------

const showWithdrawForm = ref(false)
const amountInput = ref<string>('')
const submitting = ref(false)

function toggleWithdrawForm(): void {
  showWithdrawForm.value = !showWithdrawForm.value
  if (!showWithdrawForm.value) {
    amountInput.value = ''
  }
}

/** Fill amount input with full available balance in euros.
 * W-2: centsToEurString() uses integer division + toFixed(2) -- no float issues.
 */
function fillMaxAmount(): void {
  amountInput.value = centsToEurString(availableCents.value)
}

// W-1: eurStringToCents() avoids IEEE-754 float precision trap.
// parseFloat('14.57') * 100 = 1456.9999... -- unreliable.
// eurStringToCents parses integer + fractional parts as integers.
const amountCents = computed((): number => eurStringToCents(amountInput.value))

/** Inline validation message for amount input. */
const amountError = computed((): string => {
  if (!amountInput.value) return ''
  const cents = amountCents.value
  if (cents <= 0) return 'Введите корректную сумму'
  if (cents < MIN_WITHDRAWAL_EUROS * 100) {
    return `Минимальная сумма вывода ${formatMoney(MIN_WITHDRAWAL_EUROS * 100, 'EUR', 'ru', true)}`
  }
  if (cents > availableCents.value) {
    return 'Недостаточно средств'
  }
  return ''
})

/** Net amount master receives after fee deduction. */
const formattedNetAmount = computed((): string => {
  const cents = amountCents.value
  if (cents <= 0) return formatMoney(0, 'EUR', 'ru', true)
  const net = Math.max(0, cents - WITHDRAWAL_FEE_EUROS * 100)
  return formatMoney(net, 'EUR', 'ru', true)
})

async function submitWithdrawal(): Promise<void> {
  // Double-submit guard.
  if (submitting.value) return
  if (amountError.value || !amountCents.value) return

  submitting.value = true
  try {
    await createWithdrawal(amountCents.value)
    toast.success('Запрос на вывод отправлен. Ожидайте решения администратора.')
    amountInput.value = ''
    showWithdrawForm.value = false
    // Refresh profile to update available/frozen balances.
    await masterStore.fetchMyProfile(true)
    // Reload withdrawal history from start.
    await reloadHistory()
  } catch (e) {
    const msg = e instanceof ApiResponseError ? e.detail : 'Не удалось создать запрос'
    toast.error(msg)
  } finally {
    submitting.value = false
  }
}

// ---------------------------------------------------------------------------
// Withdrawal history
// ---------------------------------------------------------------------------

const withdrawals = ref<WithdrawalResponse[]>([])
const historyTotal = ref(0)
const historyOffset = ref(0)
const historyLoading = ref(false)

const hasMore = computed(
  () => withdrawals.value.length < historyTotal.value,
)

async function reloadHistory(): Promise<void> {
  historyLoading.value = true
  historyOffset.value = 0
  try {
    const data = await getMyWithdrawals(LIMIT, 0)
    withdrawals.value = data.items
    historyTotal.value = data.total
    historyOffset.value = data.items.length
  } catch {
    // Non-critical -- history remains empty, balance card still works.
  } finally {
    historyLoading.value = false
  }
}

async function loadMoreWithdrawals(): Promise<void> {
  if (historyLoading.value) return
  historyLoading.value = true
  try {
    const data = await getMyWithdrawals(LIMIT, historyOffset.value)
    withdrawals.value.push(...data.items)
    historyTotal.value = data.total
    historyOffset.value += data.items.length
  } catch {
    toast.error('Не удалось загрузить историю выводов')
  } finally {
    historyLoading.value = false
  }
}

// ---------------------------------------------------------------------------
// Status helpers
// ---------------------------------------------------------------------------

const STATUS_LABEL: Record<WithdrawalStatus, string> = {
  pending: 'На рассмотрении',
  approved: 'Одобрен',
  rejected: 'Отклонён',
}

function statusLabel(s: WithdrawalStatus): string {
  return STATUS_LABEL[s] ?? s
}

function statusVariant(s: WithdrawalStatus): 'warning' | 'success' | 'error' {
  switch (s) {
    case 'pending': return 'warning'
    case 'approved': return 'success'
    case 'rejected': return 'error'
  }
}

const METHOD_LABEL: Record<string, string> = {
  bank_transfer: 'Банк. перевод',
  paypal: 'PayPal',
  revolut: 'Revolut',
}

function methodLabel(method: string): string {
  return METHOD_LABEL[method] ?? method
}

/** Withdrawal creation date, shown in the master's own profile timezone. */
function withdrawalDate(w: WithdrawalResponse): string {
  return formatDateShort(w.created_at, viewerTz.value)
}

// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------

onMounted(async () => {
  // Profile is already loaded by masterStatusGuard -- lazy fetch skips if so.
  await masterStore.fetchMyProfile()
  await reloadHistory()
})
</script>

<style scoped>
.finance-view {
  /* F-5 rail sync: horizontal padding removed — MobileLayout supplies the 24px
     screen rail. Vertical kept. Matches the User zone. */
  padding: var(--space-4) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* -- Balance card -- */
.finance-view__balance-card {
  background: var(--velo-primary);
  color: white;
  border-radius: var(--radius-md);
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.finance-view__balance-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.finance-view__balance-label {
  font-size: var(--text-sm);
  opacity: 0.8;
  margin-bottom: var(--space-1);
}

.finance-view__balance-value {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  letter-spacing: -0.5px;
}

.finance-view__balance-icon {
  opacity: 0.8;
  /* Vector IconFinance inherits white (currentColor) from the primary card. */
}

/* Forward arrow on the "Перейти в профиль" button. */
.finance-view__btn-arrow {
  margin-left: var(--space-2);
  vertical-align: middle;
}

.finance-view__frozen-row {
  display: flex;
  gap: var(--space-2);
  font-size: var(--text-sm);
  opacity: 0.8;
}

.finance-view__withdraw-btn {
  margin-top: var(--space-1);
}

/* -- Section -- */
.finance-view__section {
  padding: var(--space-4);
}

.finance-view__section-title {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: var(--space-4);
}

/* -- Withdraw form -- */
.finance-view__withdraw-section {
  border: 1px solid var(--velo-border-card);
}

.finance-view__warning {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--velo-glass-blue-15);
  border-radius: var(--radius-md);
}

.finance-view__warning-text {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.5;
}

/* -- Payout requisites (moved from the profile hub) -- */
.finance-view__payout-section {
  border: 1px solid var(--velo-border-card);
}

.finance-view__payout-empty,
.finance-view__payout-configured {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.finance-view__payout-empty-text {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.5;
}

.finance-view__payout-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.finance-view__payout-method {
  font-weight: 400;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.finance-view__payout-details-text {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  font-family: monospace;
  letter-spacing: 0.03em;
}

.finance-view__payout-form {
  margin-top: var(--space-2);
}

.finance-view__payout-form-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.finance-view__amount-group {
  margin-bottom: var(--space-4);
}

.finance-view__label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin-bottom: var(--space-2);
}

.finance-view__amount-row {
  display: flex;
  gap: var(--space-2);
  align-items: stretch;
}

/* VInput grows to fill the row; drop its default bottom margin (hint/error sit below). */
.finance-view__amount-row :deep(.v-input) {
  flex: 1;
  margin-bottom: 0;
}

.finance-view__hint {
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  line-height: 1.5;
}

.finance-view__error {
  margin-top: var(--space-1);
  font-size: var(--text-xs);
  color: var(--velo-error);
}

/* -- History -- */
.finance-view__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-5) 0;
}

.finance-view__empty {
  padding: var(--space-5) 0;
  text-align: center;
}

.finance-view__empty-text {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
}

.finance-view__history-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.finance-view__history-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--velo-border-light);
}

.finance-view__history-item:last-child {
  border-bottom: none;
}

.finance-view__history-left {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.finance-view__history-amount {
  font-weight: 400;
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.finance-view__history-meta {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

.finance-view__history-fee {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

.finance-view__load-more {
  margin-top: var(--space-3);
}
</style>
