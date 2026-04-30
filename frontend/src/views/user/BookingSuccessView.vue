<!--
  VELO Frontend -- BookingSuccessView (S2 P08 C27 — skin 26)

  Confirmation screen post-purchase. Hands-clap success icon + headline +
  body + master-request textarea (mock per BACKEND § B.4) + CTAs.

  Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="bs">
    <div class="bs__card">
      <div class="bs__icon">
        <IconHandsClap :size="32" />
      </div>
      <h1 class="bs__title">
        Практика забронирована!
      </h1>
      <p class="bs__body">
        Ссылка на Zoom придёт за 10 минут до начала.
      </p>
    </div>

    <section class="bs__request">
      <h3>Ваш запрос мастеру (необязательно)</h3>
      <textarea
        v-model="note"
        class="bs__textarea"
        placeholder="Концентрация, настрой на работу"
        rows="3"
        maxlength="500"
      />
      <Callout
        variant="mint"
        :icon="IconHeart"
      >
        Оставляя запрос, вы помогаете мастеру подготовить практику с учётом ваших пожеланий.
      </Callout>
    </section>

    <div class="bs__cta">
      <VButton
        variant="ghost"
        size="md"
        block
        @click="onSendNote"
      >
        Отправить запрос
      </VButton>
      <VButton
        variant="primary"
        size="md"
        block
        @click="$router.push('/user/calendar')"
      >
        В календарь
      </VButton>
    </div>

    <RouterLink
      to="/user/dashboard"
      class="bs__home"
    >
      На главную
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { VButton } from '@/components/ui'
import { IconHandsClap, IconHeart } from '@/components/icons'
import Callout from '@/components/shared/Callout.vue'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const note = ref('')

function onSendNote(): void {
  // BACKEND § B.4 not landed; mock notification per Path Y graceful degrade.
  toast.info('Запрос мастеру скоро будет доступен')
}
</script>

<style scoped>
.bs {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-6);
  min-height: 100vh;
  min-height: 100dvh;
}

.bs__card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-3);
  padding: var(--space-6);
  background: var(--surface-default);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.bs__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: var(--radius-full);
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
  color: var(--text-primary);
}

.bs__title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.bs__body {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.bs__request {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.bs__request h3 {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin: 0;
  font-weight: 400;
}

.bs__textarea {
  width: 100%;
  padding: var(--space-3);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  resize: none;
  box-sizing: border-box;
}

.bs__cta {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.bs__home {
  text-align: center;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-decoration: underline;
}
</style>
