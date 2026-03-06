<!--
  VELO Frontend -- TopupView (Phase F5)

  Balance topup screen:
    - Current balance display
    - Preset amounts (EUR 5, 10, 20, 50)
    - Custom amount input (EUR 1-500)
    - "Пополнить" button -> POST /api/v1/payments/topup -> redirect

  In stub mode (Stripe not configured): backend instantly credits
  balance and returns success URL. Redirect lands on TopupSuccessView.

  Route: /user/topup (name: 'user-topup')
-->

<template>
  <div class="topup">
    <!-- Balance -->
    <div class="topup__balance">
      <span class="topup__balance-label">Ваш баланс</span>
      <span class="topup__balance-value">{{ balanceStore.formattedBalance }}</span>
    </div>

    <!-- Preset amounts -->
    <div class="topup__section-title">Выберите сумму</div>
    <div class="topup__presets">
      <button
        v-for="preset in PRESETS"
        :key="preset"
        class="topup__preset"
        :class="{ 'topup__preset--active': selectedCents === preset && !customMode }"
        @click="selectPreset(preset)"
      >
        {{ formatEur(preset) }}
      </button>
    </div>

    <!-- Custom amount -->
    <div class="topup__custom">
      <div
        class="topup__custom-toggle"
        :class="{ 'topup__custom-toggle--active': customMode }"
        @click="enableCustom"
      >
        Другая сумма
      </div>
      <div v-if="customMode" class="topup__custom-input-wrap">
        <span class="topup__custom-currency">€</span>
        <input
          ref="customInput"
          v-model="customValue"
          type="number"
          class="topup__custom-input"
          placeholder="1 — 500"
          min="1"
          max="500"
          step="1"
          inputmode="numeric"
          @input="onCustomInput"
        />
      </div>
    </div>

    <!-- Error -->
    <div v-if="validationError" class="topup__error">
      {{ validationError }}
    </div>

    <!-- Action -->
    <div class="topup__action">
      <VButton
        variant="primary"
        size="lg"
        block
        :loading="loading"
        :disabled="!canSubmit"
        @click="onTopup"
      >
        Пополнить {{ selectedLabel }}
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { VButton } from '@/components/ui'
import { useBalanceStore } from '@/stores/balance'
import { useToast } from '@/composables/useToast'
import { createTopup } from '@/api/payments'
import { ApiResponseError } from '@/api/client'
import { formatMoney } from '@/utils/format'

const balanceStore = useBalanceStore()
const toast = useToast()

// -- Constants --
const PRESETS = [500, 1000, 2000, 5000] // cents: €5, €10, €20, €50
const MIN_CENTS = 100    // €1.00 (from backend config)
const MAX_CENTS = 50000  // €500.00 (from backend config)

// -- State --
const selectedCents = ref(1000) // default €10
const customMode = ref(false)
const customValue = ref('')
const loading = ref(false)
const customInput = ref<HTMLInputElement | null>(null)

// -- Computed --
const customCents = computed(() => {
  const euros = parseFloat(customValue.value)
  if (isNaN(euros) || euros <= 0) return 0
  return Math.round(euros * 100)
})

const effectiveCents = computed(() =>
  customMode.value ? customCents.value : selectedCents.value,
)

const validationError = computed(() => {
  if (!customMode.value) return ''
  if (!customValue.value) return ''
  if (customCents.value < MIN_CENTS) return 'Минимальная сумма — €1'
  if (customCents.value > MAX_CENTS) return 'Максимальная сумма — €500'
  return ''
})

const canSubmit = computed(() =>
  effectiveCents.value >= MIN_CENTS &&
  effectiveCents.value <= MAX_CENTS &&
  !validationError.value &&
  !loading.value,
)

const selectedLabel = computed(() => {
  if (effectiveCents.value <= 0) return ''
  return formatMoney(effectiveCents.value, 'EUR')
})

// -- Actions --

function formatEur(cents: number): string {
  return `€${cents / 100}`
}

function selectPreset(cents: number): void {
  customMode.value = false
  customValue.value = ''
  selectedCents.value = cents
}

async function enableCustom(): Promise<void> {
  customMode.value = true
  await nextTick()
  customInput.value?.focus()
}

function onCustomInput(): void {
  // Prevent negative values in UI.
  const val = parseFloat(customValue.value)
  if (val < 0) customValue.value = ''
}

async function onTopup(): Promise<void> {
  if (!canSubmit.value) return

  loading.value = true
  try {
    const response = await createTopup(effectiveCents.value)

    // Redirect to Stripe checkout (or success URL in stub mode).
    window.location.href = response.checkout_url
  } catch (e) {
    if (e instanceof ApiResponseError) {
      toast.error(e.detail)
    } else {
      toast.error('Не удалось создать платёж')
    }
  } finally {
    loading.value = false
  }
}

// -- Lifecycle --
onMounted(() => {
  balanceStore.refresh()
})
</script>

<style scoped>
.topup {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* Balance */
.topup__balance {
  text-align: center;
  padding: var(--space-6);
  background: white;
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-lg);
}

.topup__balance-label {
  display: block;
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  margin-bottom: var(--space-2);
}

.topup__balance-value {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--velo-primary);
}

/* Section title */
.topup__section-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--velo-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Presets */
.topup__presets {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.topup__preset {
  padding: var(--space-4);
  background: white;
  border: 2px solid var(--velo-border);
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--velo-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.topup__preset:hover {
  border-color: var(--velo-primary-light);
}

.topup__preset--active {
  border-color: var(--velo-primary);
  background: rgba(51, 77, 110, 0.05);
  color: var(--velo-primary);
}

/* Custom amount */
.topup__custom-toggle {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-primary);
  cursor: pointer;
  text-align: center;
  border: 1px dashed var(--velo-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.topup__custom-toggle:hover {
  border-color: var(--velo-primary-light);
}

.topup__custom-toggle--active {
  border-color: var(--velo-primary);
  background: rgba(51, 77, 110, 0.05);
}

.topup__custom-input-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: white;
  border: 2px solid var(--velo-primary);
  border-radius: var(--radius-md);
}

.topup__custom-currency {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--velo-text-muted);
}

.topup__custom-input {
  flex: 1;
  border: none;
  outline: none;
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--velo-text-primary);
  background: transparent;
}

.topup__custom-input::placeholder {
  color: var(--velo-text-muted);
  font-weight: 400;
}

/* Hide number input spinners */
.topup__custom-input::-webkit-outer-spin-button,
.topup__custom-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.topup__custom-input[type='number'] {
  -moz-appearance: textfield;
}

/* Error */
.topup__error {
  font-size: var(--text-sm);
  color: var(--velo-error);
  text-align: center;
}

/* Action */
.topup__action {
  margin-top: var(--space-2);
}
</style>
