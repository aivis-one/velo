<!--
  VELO Frontend -- MasterNewPromocodeView (create-promocode form, 2026-06-13)

  Route /master/promocodes/new, built to the «5 New promo code» design. STUB: no
  promocodes backend → «Создать промокод» toasts «недоступно». Reuses the Phase-3
  required-seal pattern (`required` prop on VInput/VSelect + legend). -> Zod.
-->

<template>
  <div class="new-promo">
    <VHeader title="Новый промокод" show-back solid @back="router.back()" />

    <div class="new-promo__content">
      <!-- Required-fields legend (DS, Phase-3). -->
      <div class="new-promo__legend">
        <IconRequired class="new-promo__legend-seal" :size="22" />
        <span>— поля, обязательные для заполнения</span>
      </div>

      <VInput
        v-model="form.code"
        label="Код промокода"
        placeholder="Латиница, цифры, дефис"
        required
      />
      <VSelect v-model="form.discount" label="Скидка" :options="DISCOUNT_OPTIONS" required />
      <VInput v-model="form.until" label="Действует до" type="date" :min="todayISO" required />
      <VInput
        v-model="form.limit"
        label="Лимит использований"
        type="number"
        min="1"
        placeholder="10"
      />

      <VButton variant="primary" block class="new-promo__submit" @click="onCreate">
        Создать промокод
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VInput, VSelect, VButton } from '@/components/ui'
import { IconRequired } from '@/components/icons'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()

const DISCOUNT_OPTIONS = [
  { value: '10', label: '10%' },
  { value: '25', label: '25%' },
  { value: '50', label: '50%' },
  { value: '75', label: '75%' },
  { value: '100', label: '100%' },
]

const form = reactive({
  code: '',
  discount: '100',
  until: '',
  limit: '',
})

// «Действует до» must be in the future — native date-picker min = today (B6).
const todayISO = computed((): string => new Date().toISOString().slice(0, 10))

// Usage limit starts at 1 — clamp away 0 / negatives the number spinner allows (B1).
watch(
  () => form.limit,
  (v) => {
    if (v !== '' && Number(v) < 1) form.limit = '1'
  },
)

function onCreate(): void {
  // No promocodes backend yet -> stub per the operator rule. -> Zod.
  toast.info('Промокоды пока недоступны')
}
</script>

<style scoped>
.new-promo {
  display: flex;
  flex-direction: column;
}

.new-promo__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4) 0 var(--space-8);
}

/* Required-fields legend — mirrors CreatePracticeView. */
.new-promo__legend {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  /* Brighter than the default --velo-error-bg (was too pale, operator 2026-06-19):
     stronger pink fill + a defining error border. */
  background: var(--velo-error-bg-strong);
  border: 1.5px solid var(--velo-error-border);
  color: var(--velo-danger-text);
  font-size: var(--text-sm);
}

.new-promo__legend-seal {
  flex-shrink: 0;
  color: var(--velo-error);
}

.new-promo__submit {
  margin-top: var(--space-4);
}
</style>
