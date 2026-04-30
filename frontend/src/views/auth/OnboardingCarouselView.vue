<!--
  VELO Frontend -- OnboardingCarouselView (S2 P06 C20 — PWA mock)

  Single view with 3 intro slides + carousel state index 0..2 per
  decision #034 + DESIGN-DECISIONS-LOG § A.2. Skip button advances
  directly to /onboarding/timezone. "Далее" advances index; on last
  slide button label is "Продолжить" and routes to /onboarding/timezone.

  Skin references:
    docs/04_assets/velo-design-system-2026-04-30/project/uploads/05_Onboarding 1.png
    docs/04_assets/velo-design-system-2026-04-30/project/uploads/06_Onboarding 2.png
    docs/04_assets/velo-design-system-2026-04-30/project/uploads/07_Onboarding 3.png

  Path Y: illustrations in frontend/src/assets/illustrations/ are bundle
  placeholders; do not visually match designer's skin illustrations.
  Theme-proximity mapping used; designer-supplied skin-aligned illustrations
  pending future batch (BACKLOG entry at Phase 06 CLOSE).

  Button-only navigation; swipe-gesture deferred to polish cluster.
-->

<template>
  <div class="onboarding">
    <button
      type="button"
      class="onboarding__skip"
      @click="onSkip"
    >
      Пропустить
    </button>

    <div class="onboarding__slide">
      <img
        class="onboarding__illustration"
        :src="currentSlide.illustration"
        alt=""
        aria-hidden="true"
      >
      <h1 class="onboarding__title">
        {{ currentSlide.title }}
      </h1>
      <p class="onboarding__body">
        {{ currentSlide.body }}
      </p>
    </div>

    <div
      class="onboarding__dots"
      role="tablist"
      aria-label="Шаги онбординга"
    >
      <span
        v-for="(_, idx) in slides"
        :key="idx"
        class="onboarding__dot"
        :class="{ 'onboarding__dot--active': idx === currentIndex }"
      />
    </div>

    <VButton
      variant="primary"
      size="md"
      block
      @click="onNext"
    >
      {{ ctaLabel }}
    </VButton>

    <button
      v-if="currentIndex > 0"
      type="button"
      class="onboarding__back"
      aria-label="Назад"
      @click="onBack"
    >
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <polyline points="15 18 9 12 15 6" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VButton } from '@/components/ui'
import aiAnalytics from '@/assets/illustrations/ai-analytics.svg'
import livePractices from '@/assets/illustrations/live-practices.svg'
import selfMap from '@/assets/illustrations/self-map.svg'

interface Slide {
  illustration: string
  title: string
  body: string
}

const router = useRouter()
const currentIndex = ref(0)

// Copy from skins 05/06/07; illustration mapping is theme-proximity placeholder
// per Path Y (BACKLOG entry pending for designer-supplied per-slide assets).
const slides: Slide[] = [
  {
    illustration: livePractices,
    title: 'Найдите свою практику',
    body: 'Выбирайте из медитаций, breathwork и других практик с лучшими мастерами',
  },
  {
    illustration: aiAnalytics,
    title: 'Ведите дневник',
    body: 'Отслеживайте свое состояние до и после практик, получайте AI-инсайты',
  },
  {
    illustration: selfMap,
    title: 'Общайтесь с мастерами',
    body: 'Задавайте вопросы и получайте персональные рекомендации от экспертов',
  },
]

// `slides` is a const non-empty literal; `currentIndex.value` is clamped to
// 0..slides.length-1 by onNext/onBack. Non-null assertion is safe; satisfies
// noUncheckedIndexedAccess strict mode.
const currentSlide = computed<Slide>(() => slides[currentIndex.value]!)

const isLastSlide = computed(() => currentIndex.value === slides.length - 1)
const ctaLabel = computed(() => (isLastSlide.value ? 'Продолжить' : 'Далее'))

function onNext(): void {
  if (isLastSlide.value) {
    router.push({ name: 'onboarding-timezone' })
  } else {
    currentIndex.value++
  }
}

function onSkip(): void {
  router.push({ name: 'onboarding-timezone' })
}

function onBack(): void {
  if (currentIndex.value > 0) {
    currentIndex.value--
  } else {
    router.back()
  }
}
</script>

<style scoped>
.onboarding {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--space-6);
  gap: var(--space-4);
  background: var(--surface-default);
}

.onboarding__skip {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  cursor: pointer;
  padding: var(--space-2);
}

.onboarding__slide {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  flex: 1;
  text-align: center;
  max-width: 320px;
}

.onboarding__illustration {
  width: 240px;
  height: 240px;
  max-width: 80vw;
  object-fit: contain;
}

.onboarding__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.onboarding__body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.onboarding__dots {
  display: flex;
  gap: var(--space-2);
  margin: var(--space-4) 0;
}

.onboarding__dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--surface-steel-alpha-15);
  transition: background var(--transition-fast);
}

.onboarding__dot--active {
  background: var(--steel-button);
}

.onboarding__back {
  position: absolute;
  bottom: var(--space-4);
  left: var(--space-4);
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  padding: var(--space-2);
}
</style>
