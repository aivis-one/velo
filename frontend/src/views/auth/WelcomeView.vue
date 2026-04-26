<!--
  VELO Frontend -- WelcomeView (S1-P03 C11 greenfield)

  TMA splash route at /welcome.

  Per decision #012: bundle AuthScreen is NOT 1:1 reference — third-party login
  UI is dropped (Velo authenticates via Telegram initData only).
  Per decision #013: VELO is TMA-first; standalone non-TMA users see
  StandaloneStubView via platform layer, not this route.

  Visual reference: bundle WelcomeScreen.jsx (mandala-runes backdrop + VELΘ
  wordmark overlay + tagline + CTA). Single CTA only — "Открыть в Telegram" —
  matches Velo's TMA-first auth flow. No secondary registration button.
-->

<template>
  <div class="welcome">
    <div class="welcome__brand">
      <img
        src="@/assets/brand/mandala-runes.svg"
        alt=""
        class="welcome__mandala"
      />
      <h1 class="welcome__wordmark">VELΘ</h1>
    </div>

    <p class="welcome__tagline">
      Пространство для практики<br />и внутреннего развития
    </p>

    <a
      :href="botUrl"
      class="welcome__cta"
      target="_blank"
      rel="noopener"
    >
      Открыть в Telegram
    </a>
  </div>
</template>

<script setup lang="ts">
const botUrl = import.meta.env.VITE_TELEGRAM_BOT_URL || 'https://t.me/velo_testbot'
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

.welcome__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 336px;
  height: 50px;
  margin-top: auto;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  text-decoration: none;
  border-radius: var(--radius-full);
  border: 1px solid #ffffff;
  box-shadow: var(--shadow-glow-white);
  background: var(--steel-button);
  color: white;
  transition: opacity var(--transition-fast);
}

.welcome__cta:hover {
  opacity: 0.9;
}

.welcome__cta:active {
  opacity: 0.8;
}
</style>
