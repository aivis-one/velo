<!--
  VELO Frontend -- FeedbackSuccessView (S2 P08 C32 — skin 30)

  Post-feedback confirmation. Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="fs">
    <div class="fs__icon">
      <IconHeart :size="48" />
    </div>
    <h1 class="fs__title">
      Спасибо за feedback!
    </h1>
    <p class="fs__body">
      Ваш отзыв поможет нам улучшить практики.
    </p>
    <VButton
      variant="primary"
      size="md"
      block
      @click="$router.push('/user/diary')"
    >
      В дневник
    </VButton>
    <RouterLink
      to="/user/dashboard"
      class="fs__home"
    >
      На главную
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import { VButton } from '@/components/ui'
import { IconHeart } from '@/components/icons'
</script>

<style scoped>
.fs {
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

.fs__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
  color: var(--pink-primary);
}

.fs__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.fs__body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
  max-width: 320px;
}

.fs__home {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-decoration: underline;
}
</style>
