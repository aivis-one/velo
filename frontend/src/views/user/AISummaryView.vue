<!--
  VELO Frontend — AISummaryView (S2-S3 SPEEDRUN MEGA-2 §C50)

  Static placeholder content per BACKEND § A.8 mock. Header chip + body
  paragraphs + recommendation cards.
-->

<template>
  <div class="ai">
    <header class="ai__header">
      <button
        type="button"
        class="ai__back"
        aria-label="Назад"
        @click="router.back()"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="ai__title">
        AI-саммари
      </h1>
    </header>

    <article class="ai__hero">
      <span class="ai__hero-icon">
        <IconBrain :size="22" />
      </span>
      <div class="ai__hero-text">
        <h2 class="ai__hero-title">
          Саммари недели
        </h2>
        <p class="ai__hero-sub">
          16–22 января
        </p>
      </div>
    </article>

    <article class="ai__body">
      <p>
        На этой неделе вы посетили 3 практики и отметили улучшение настроения после каждой медитации.
      </p>
      <p class="ai__mood-line">
        Ваш уровень энергии вырос с
        <img
          :src="moodNeutralSvg"
          alt="нейтрально"
          class="ai__mood-img"
        >
        до
        <img
          :src="moodCalmSvg"
          alt="спокойно"
          class="ai__mood-img"
        >.
      </p>
    </article>

    <h3 class="ai__sub">
      Рекомендации
    </h3>
    <article class="ai__rec">
      <p>Попробуйте добавить вечернюю медитацию для лучшего сна.</p>
    </article>
    <article class="ai__rec">
      <p>Вы хорошо реагируете на практики с Alex Mindful.</p>
    </article>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { IconArrowBack, IconBrain } from '@/components/icons'
import moodNeutralSvg from '@/assets/mood/mood-neutral.svg'
import moodCalmSvg from '@/assets/mood/mood-calm.svg'

const router = useRouter()
</script>

<style scoped>
.ai {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
}

.ai__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.ai__back {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.ai__hero {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--mint-primary, var(--surface-default));
  color: white;
  border: 1px solid var(--mint-primary, var(--text-primary));
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.ai__hero-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.16);
  color: white;
  flex-shrink: 0;
}

.ai__hero-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ai__hero-title {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  margin: 0;
  font-weight: 500;
}

.ai__hero-sub {
  margin: 0;
  font-size: var(--text-sm);
  opacity: 0.85;
}

.ai__body {
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  font-family: var(--font-body);
  color: var(--text-primary);
}

.ai__body p {
  margin: 0;
  font-size: var(--text-base);
}

.ai__mood-line {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.ai__mood-img {
  width: 24px;
  height: 24px;
  vertical-align: middle;
}

.ai__sub {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  margin: var(--space-2) 0 0;
  font-weight: 400;
  color: var(--text-primary);
}

.ai__rec {
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.ai__rec p {
  margin: 0;
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
}
</style>
