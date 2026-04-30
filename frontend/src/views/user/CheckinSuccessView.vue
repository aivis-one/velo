<!--
  VELO Frontend -- CheckinSuccessView (S2 P08 C30 — skin 13)

  Post-checkin confirmation. "Начать практику" → /user/practice/:id/live.
  Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="cs">
    <div class="cs__icon">
      <IconSuccess :size="48" />
    </div>
    <h1 class="cs__title">
      Check-in отправлен!
    </h1>
    <p class="cs__body">
      Спасибо! Ваше состояние записано. Хорошей практики!
    </p>
    <VButton
      variant="primary"
      size="md"
      block
      @click="$router.replace(`/user/practices/${practiceId}/live`)"
    >
      Начать практику
    </VButton>
    <RouterLink
      to="/user/dashboard"
      class="cs__home"
    >
      На главную
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { VButton } from '@/components/ui'
import { IconSuccess } from '@/components/icons'

const route = useRoute()
const practiceId = computed(() => route.params.practiceId as string)
</script>

<style scoped>
.cs {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-4);
  padding: var(--space-6);
  min-height: 100vh;
  min-height: 100dvh;
  justify-content: center;
}

.cs__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
  color: var(--text-primary);
}

.cs__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.cs__body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
  max-width: 320px;
}

.cs__home {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-decoration: underline;
}
</style>
