<!--
  VELO Frontend -- TopupCancelView (Phase F5)

  Shown when user cancels Stripe checkout (clicks browser back
  or Stripe cancel button).

  Route: /user/topup/cancel (name: 'user-topup-cancel')
-->

<template>
  <div class="topup-result">
    <div class="topup-result__icon">😕</div>
    <h1 class="topup-result__title">Оплата отменена</h1>
    <p class="topup-result__text">
      Ваш баланс не изменился. Вы можете попробовать снова.
    </p>
    <div class="topup-result__actions">
      <VButton
        variant="primary"
        size="lg"
        block
        @click="router.push({ name: 'user-topup' })"
      >
        Попробовать снова
      </VButton>
      <VButton
        variant="ghost"
        block
        @click="router.push({ name: 'user-dashboard' })"
      >
        На главную
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VButton } from '@/components/ui'

const router = useRouter()
</script>

<style scoped>
.topup-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: var(--space-6);
}

.topup-result__icon {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.topup-result__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--velo-text-primary);
  margin: 0 0 var(--space-2);
}

.topup-result__text {
  font-size: var(--text-base);
  color: var(--velo-text-secondary);
  margin: 0 0 var(--space-8);
  line-height: 1.5;
}

.topup-result__actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
