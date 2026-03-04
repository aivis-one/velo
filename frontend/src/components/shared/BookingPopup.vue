<!--
  VELO Frontend -- BookingPopup Component (Phase F4.1)

  Purchase flow popup built on VModal.

  Flow:
    1. Shows practice summary (title, date, master, price)
    2. Optional promo code input + "OK" -> preview-purchase API
    3. Displays discount if promo applied
    4. "Оплатить" button -> purchase API (booking + ledger)
    5. Error handling: insufficient balance, full, already booked

  Props:
    practice   — PracticeResponse from the detail view
    open       — controls visibility (v-model pattern via emit)

  Emits:
    close      — close the popup
    purchased  — purchase succeeded (parent refreshes data)
-->

<template>
  <VModal :open="open" @close="onClose">
    <h2 class="popup__title">Бронирование</h2>

    <!-- Summary -->
    <div class="popup__summary">
      <div class="popup__row">
        <span class="popup__label">Практика</span>
        <span class="popup__value">{{ practice.title }}</span>
      </div>
      <div class="popup__row">
        <span class="popup__label">Дата</span>
        <span class="popup__value">{{ formattedDate }}</span>
      </div>
      <div class="popup__row">
        <span class="popup__label">Мастер</span>
        <span class="popup__value">{{ practice.master_name ?? 'Мастер' }}</span>
      </div>
    </div>

    <!-- Promo code -->
    <div class="popup__promo">
      <input
        v-model.trim="promoCode"
        type="text"
        class="popup__promo-input"
        placeholder="Промокод"
        :disabled="purchasing"
        @keydown.enter="onApplyPromo"
      />
      <VButton
        size="sm"
        variant="secondary"
        :loading="previewing"
        :disabled="!promoCode || purchasing"
        @click="onApplyPromo"
      >
        OK
      </VButton>
    </div>

    <!-- Promo result -->
    <div v-if="promoApplied" class="popup__discount">
      <span class="popup__discount-label">Скидка {{ discountPercent }}%</span>
      <span class="popup__discount-value">
        −{{ formattedDiscount }}
      </span>
    </div>

    <!-- Total -->
    <div class="popup__total">
      <span class="popup__total-label">Итого</span>
      <span class="popup__total-value">{{ formattedTotal }}</span>
    </div>

    <!-- Insufficient balance warning -->
    <div v-if="insufficientBalance" class="popup__warning">
      Недостаточно средств. Ваш баланс: {{ balanceStore.formattedBalance }}
    </div>

    <!-- Actions -->
    <div class="popup__actions">
      <VButton
        variant="primary"
        size="lg"
        block
        :loading="purchasing"
        :disabled="purchasing || previewing"
        @click="onPurchase"
      >
        {{ purchaseButtonText }}
      </VButton>
      <VButton
        variant="ghost"
        block
        :disabled="purchasing"
        @click="onClose"
      >
        Отмена
      </VButton>
    </div>
  </VModal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VModal, VButton } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useBalanceStore } from '@/stores/balance'
import { purchasePractice, previewPurchase } from '@/api/bookings'
import { ApiResponseError } from '@/api/client'
import { formatDate, formatMoney } from '@/utils/format'
import type { PracticeResponse, PreviewPurchaseResponse } from '@/api/types'

const props = defineProps<{
  practice: PracticeResponse
  open: boolean
}>()

const emit = defineEmits<{
  close: []
  purchased: []
}>()

const router = useRouter()
const toast = useToast()
const balanceStore = useBalanceStore()

// -- State --
const promoCode = ref('')
const previewing = ref(false)
const purchasing = ref(false)
const preview = ref<PreviewPurchaseResponse | null>(null)

// -- Computed --
const formattedDate = computed(() =>
  formatDate(props.practice.scheduled_at, props.practice.timezone),
)

const promoApplied = computed(() =>
  preview.value !== null && preview.value.discount_cents > 0,
)

const discountPercent = computed(() =>
  preview.value?.discount_percent ?? 0,
)

const formattedDiscount = computed(() => {
  if (!preview.value) return ''
  return formatMoney(preview.value.discount_cents, preview.value.currency)
})

/** Final price to pay (after promo discount if applied). */
const totalCents = computed(() =>
  preview.value?.paid_cents ?? props.practice.price_cents,
)

const totalCurrency = computed(() =>
  preview.value?.currency ?? props.practice.currency,
)

const formattedTotal = computed(() =>
  formatMoney(totalCents.value, totalCurrency.value),
)

const insufficientBalance = computed(() =>
  !props.practice.is_free && !balanceStore.hasEnough(totalCents.value),
)

const purchaseButtonText = computed(() => {
  if (insufficientBalance.value) return 'Пополнить баланс'
  if (props.practice.is_free) return 'Записаться'
  return 'Оплатить'
})

// -- Actions --

function onClose(): void {
  if (purchasing.value) return
  resetState()
  emit('close')
}

function resetState(): void {
  promoCode.value = ''
  preview.value = null
  previewing.value = false
  purchasing.value = false
}

async function onApplyPromo(): Promise<void> {
  if (!promoCode.value || previewing.value) return

  previewing.value = true
  try {
    preview.value = await previewPurchase(
      props.practice.id,
      promoCode.value,
    )
  } catch (e) {
    preview.value = null
    if (e instanceof ApiResponseError) {
      toast.error(e.detail)
    } else {
      toast.error('Не удалось проверить промокод')
    }
  } finally {
    previewing.value = false
  }
}

async function onPurchase(): Promise<void> {
  // Redirect to topup if insufficient balance.
  if (insufficientBalance.value) {
    resetState()
    emit('close')
    router.push({ name: 'user-topup' })
    return
  }

  purchasing.value = true
  try {
    const appliedPromo = promoApplied.value ? promoCode.value : undefined
    await purchasePractice(props.practice.id, appliedPromo)

    // Refresh balance after successful purchase.
    await balanceStore.refresh()

    toast.success('Вы записаны!')
    resetState()
    emit('purchased')
  } catch (e) {
    if (e instanceof ApiResponseError) {
      // Handle specific backend errors.
      if (e.status === 400 && e.detail.includes('Insufficient balance')) {
        toast.error('Недостаточно средств на балансе')
      } else if (e.status === 400 && e.detail.includes('full')) {
        toast.error('Мест больше нет')
      } else if (e.status === 409) {
        toast.error('Вы уже записаны на эту практику')
      } else {
        toast.error(e.detail)
      }
    } else {
      toast.error('Ошибка при бронировании')
    }
  } finally {
    purchasing.value = false
  }
}
</script>

<style scoped>
.popup__title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0 0 var(--space-5);
}

/* Summary rows */
.popup__summary {
  margin-bottom: var(--space-5);
}

.popup__row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: var(--space-2) 0;
}

.popup__row + .popup__row {
  border-top: 1px solid var(--velo-border-light);
}

.popup__label {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
}

.popup__value {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--velo-text-primary);
  text-align: right;
  max-width: 60%;
}

/* Promo input */
.popup__promo {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.popup__promo-input {
  flex: 1;
  padding: 10px var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  background: white;
  border: 1px solid var(--velo-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);
}

.popup__promo-input:focus {
  outline: none;
  border-color: var(--velo-primary);
  box-shadow: 0 0 0 3px rgba(51, 77, 110, 0.1);
}

.popup__promo-input::placeholder {
  color: var(--velo-text-muted);
}

/* Discount line */
.popup__discount {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-4);
  background: rgba(34, 197, 94, 0.1);
  border-radius: var(--radius-sm);
}

.popup__discount-label {
  font-size: var(--text-sm);
  color: var(--velo-success);
  font-weight: 500;
}

.popup__discount-value {
  font-size: var(--text-sm);
  color: var(--velo-success);
  font-weight: 600;
}

/* Total */
.popup__total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) 0;
  margin-bottom: var(--space-4);
  border-top: 1px solid var(--velo-border);
}

.popup__total-label {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--velo-text-primary);
}

.popup__total-value {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--velo-primary);
}

/* Warning */
.popup__warning {
  padding: var(--space-3);
  margin-bottom: var(--space-4);
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid var(--velo-warning);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  color: #92400E;
}

/* Actions */
.popup__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
