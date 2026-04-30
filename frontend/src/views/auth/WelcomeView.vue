<!--
  VELO Frontend -- WelcomeView (S2 P06 C16 — hybrid auth refactor)

  Two-branch composition keyed on platform.name (decisions #028 / #036):
    - TMA branch (platform.name === 'telegram'): preserves S1 C11 visual
      — mandala backdrop + VELΘ wordmark + tagline + single CTA
      "Открыть в Telegram" linking to VITE_TELEGRAM_BOT_URL.
    - PWA branch (platform.name === 'standalone'): same shared header
      + two CTAs ("Войти" primary, "Создать аккаунт" secondary) routing
      to /login + /register (route definitions land at C17/C18).

  Visual reference for PWA branch:
    docs/04_assets/velo-design-system-2026-04-30/project/uploads/01_Welcome.png
    (decision #029 — new design batch supersedes bundle visual layer).

  BACKLOG folds in this cycle:
    - #50: TMA bot anchor rel="noopener noreferrer" (was rel="noopener").
    - #49: removed inline `|| 'https://t.me/velo_testbot'` botUrl fallback;
      fail-fast guard now lives in main.ts.
-->

<template>
  <div class="welcome">
    <!-- Shared header: mandala backdrop + VELΘ wordmark + tagline -->
    <div class="welcome__brand">
      <img
        class="welcome__mandala"
        src="@/assets/brand/mandala-runes.svg"
        alt=""
        aria-hidden="true"
      >
      <h1 class="welcome__wordmark">
        VELΘ
      </h1>
    </div>

    <p class="welcome__tagline">
      Пространство для практики<br>и внутреннего развития
    </p>

    <!-- TMA branch: single CTA — preserved from S1 C11 -->
    <a
      v-if="isTelegram"
      :href="botUrl"
      class="welcome__cta welcome__cta--tma"
      target="_blank"
      rel="noopener noreferrer"
    >
      Открыть в Telegram
    </a>

    <!-- PWA branch: dual CTA stack — new per skin 01 (decision #029) -->
    <div
      v-else
      class="welcome__pwa-ctas"
    >
      <button
        type="button"
        class="welcome__cta welcome__cta--primary"
        @click="goLogin"
      >
        Войти
      </button>
      <button
        type="button"
        class="welcome__cta welcome__cta--secondary"
        @click="goRegister"
      >
        Создать аккаунт
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { platform } from '@/platform'

const router = useRouter()

const isTelegram = computed(() => platform.name === 'telegram')

// BACKLOG #49: no inline `|| 'https://t.me/velo_testbot'` fallback.
// Fail-fast in PROD lives in main.ts; non-PROD tolerates undefined
// (anchor href becomes string "undefined" — visible breakage by design).
const botUrl = import.meta.env.VITE_TELEGRAM_BOT_URL

function goLogin(): void {
  // C16 stub: /login route lands at C17. Path Y logic-first acceptable.
  console.warn('[C16] /login route not yet implemented — lands at C17')
  router.push('/login')
}

function goRegister(): void {
  // C16 stub: /register route lands at C18.
  console.warn('[C16] /register route not yet implemented — lands at C18')
  router.push('/register')
}
</script>

<style scoped>
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--space-6);
  background: var(--surface-default);
  text-align: center;
  gap: var(--space-6);
}

.welcome__brand {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: var(--space-12);
}

.welcome__mandala {
  width: 180px;
  height: 180px;
  opacity: 0.85;
  pointer-events: none;
}

.welcome__wordmark {
  position: absolute;
  font-family: var(--font-heading);
  /* TODO(BACKLOG): --text-display-lg token absent in variables.css and in
     new batch's colors_and_type.css. Hardcoded 56px persists from S1 C11.
     Path Y polish-deferred — propose adding token at next DS update. */
  font-size: 56px;
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0;
  line-height: 1;
}

.welcome__tagline {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--text-secondary);
  margin: 0;
  max-width: 280px;
  line-height: 1.5;
}

/* -- Shared CTA base (TMA + PWA primary + PWA secondary) -- */
.welcome__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 336px;
  height: 50px;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  text-decoration: none;
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-glow-white);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.welcome__cta:hover {
  opacity: 0.9;
}

.welcome__cta:active {
  opacity: 0.8;
}

/* -- TMA branch: single CTA pushed to bottom of viewport -- */
.welcome__cta--tma {
  background: var(--steel-button);
  color: white;
  margin-top: auto;
}

/* -- PWA branch: stacked CTAs in dedicated wrapper, pushed to bottom -- */
.welcome__pwa-ctas {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  width: 100%;
  max-width: 336px;
  margin-top: auto;
}

.welcome__cta--primary {
  background: var(--steel-button);
  color: white;
}

.welcome__cta--secondary {
  background: var(--surface-steel-alpha-15);
  color: var(--text-primary);
}
</style>
