<!--
  VELO Frontend -- MasterPromocodesView (promocodes list, 2026-06-13)

  Route /master/promocodes, built to the «4 Promo codes» design. STUB: no
  promocodes backend → hardcoded sample list; copy / delete / add toast
  «недоступно» (add navigates to the equally-stub create form). -> Zod.
-->

<template>
  <div class="promo">
    <VHeader title="Промокоды" show-back @back="router.back()">
      <template #action>
        <button type="button" class="promo__add" aria-label="Новый промокод" @click="onNew">
          <IconPlus :size="20" />
        </button>
      </template>
    </VHeader>

    <div class="promo__list">
      <div v-for="p in promos" :key="p.id" class="promo__item">
        <div class="promo__card">
          <span class="promo__icon"><IconPromo :size="40" /></span>
          <span class="promo__divider" aria-hidden="true"></span>
          <div class="promo__info">
            <div class="promo__code">{{ p.code }}</div>
            <div class="promo__meta">
              <div>Скидка: {{ p.discount }}</div>
              <div>Использовано: {{ p.used }}</div>
              <div>Действует до: {{ p.until }}</div>
            </div>
          </div>
        </div>
        <div class="promo__actions">
          <VButton variant="primary" @click="onCopy(p.code)">Копировать</VButton>
          <VButton variant="danger" @click="onDelete">Удалить</VButton>
        </div>
      </div>
    </div>

    <Banner
      variant="warning"
      body="Промокоды для участников, которые уже оплатили вне платформы"
      class="promo__note"
    >
      <template #icon><IconHint :size="22" /></template>
    </Banner>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton } from '@/components/ui'
import Banner from '@/components/shared/Banner.vue'
import { IconPlus, IconPromo, IconHint } from '@/components/icons'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()

// STUB sample (no promocodes backend) -> Zod.
const promos = [
  { id: '1', code: 'ALEX-VIP', discount: '100%', used: '7 из 10', until: '28.02.2026' },
  { id: '2', code: 'ДРУЗЬЯ-50', discount: '50%', used: '3 из ∞', until: '31.12.2026' },
]

function onNew(): void {
  router.push({ name: 'master-promocode-new' })
}
// Copy needs no backend — write the code straight to the clipboard (B2).
async function onCopy(code: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(code)
    toast.success('Промокод скопирован')
  } catch {
    toast.error('Не удалось скопировать')
  }
}
// Delete needs a backend (no promocodes API yet) — stub. -> Zod.
function onDelete(): void {
  toast.info('Удаление промокодов появится позже')
}
</script>

<style scoped>
.promo {
  display: flex;
  flex-direction: column;
}

.promo__add {
  width: var(--velo-size-40);
  height: var(--velo-size-40);
  border-radius: var(--radius-full);
  border: none;
  background: var(--velo-primary);
  color: var(--velo-white);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.promo__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  padding: var(--space-4) 0;
}

.promo__item {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.promo__card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.promo__icon {
  flex-shrink: 0;
  color: var(--velo-primary);
}

.promo__divider {
  align-self: stretch;
  width: 0;
  border-left: var(--velo-divider-width) dashed var(--velo-divider);
}

.promo__info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.promo__code {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.promo__meta {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.6;
}

.promo__actions {
  display: flex;
  gap: var(--space-3);
}

.promo__actions > * {
  flex: 1;
}

.promo__note {
  margin-top: var(--space-2);
}
</style>
