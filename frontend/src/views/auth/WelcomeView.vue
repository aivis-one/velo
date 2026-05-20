<!--
  VELO Frontend -- Welcome View (onboarding 01_Welcome)

  First screen shown to every authenticated user on each app open
  (per product decision: Welcome always, for everyone).

  In Telegram the user is already authenticated via initData, so:
    - "Войти" is effectively a "continue" button -> emits `enter`.
      App.vue then routes new users into the onboarding carousel and
      returning users straight to the dashboard.
    - "Создать аккаунт" is meaningless inside Telegram (the account already
      exists) -- it is only relevant for the standalone/browser build (F10),
      so it is hidden unless isStandalone is true.

  Style mirrors StandaloneStubView (glass pill buttons, slogan). Logo uses the
  white mandala variant at a large size to match Figma 01_Welcome; the wordmark
  is part of the logo, so there is no separate text heading.
-->

<template>
  <div class="welcome">
    <div class="welcome__logo">
      <!-- White mandala variant, large -- matches Figma 01_Welcome.
           The logo already contains the VELO wordmark, so no text heading. -->
      <VeloLogo variant="white" :size="220" />
    </div>
    <p class="welcome__message">
      Пространство для практики<br />и внутреннего развития
    </p>

    <div class="welcome__actions">
      <button
        type="button"
        class="welcome__button welcome__button--primary"
        @click="$emit('enter')"
      >
        Войти
      </button>

      <!-- Standalone/browser only: account creation has no meaning in Telegram. -->
      <button
        v-if="isStandalone"
        type="button"
        class="welcome__button welcome__button--glass"
        @click="$emit('create-account')"
      >
        Создать аккаунт
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import VeloLogo from '@/components/ui/VeloLogo.vue'
import { useAuth } from '@/composables/useAuth'

defineEmits<{
  /** "Войти" tapped -- continue into the app (carousel or dashboard). */
  enter: []
  /** "Создать аккаунт" tapped -- standalone build only (F10). */
  'create-account': []
}>()

const { isStandalone } = useAuth()
</script>

<style scoped>
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--space-6);
  background: transparent;
  text-align: center;
}

.welcome__logo {
  margin-bottom: var(--space-4);
}

.welcome__message {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin: 0 0 var(--space-8) 0;
  max-width: 280px;
  line-height: 1.5;
}

.welcome__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  width: 100%;
  max-width: var(--velo-content-width);
}

.welcome__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 50px;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  cursor: pointer;
  border-radius: var(--radius-full);
  border: 1px solid #ffffff;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  box-shadow: var(--velo-shadow-glow);
  transition: opacity var(--transition-fast);
}

.welcome__button:hover {
  opacity: 0.9;
}

.welcome__button:focus-visible {
  outline: 2px solid var(--velo-primary);
  outline-offset: 2px;
}

.welcome__button--primary {
  background: var(--velo-primary);
  color: white;
}

/* Glass variant: transparent fill, primary-colored label (matches mockup). */
.welcome__button--glass {
  background: var(--velo-glass-white-01);
  color: var(--velo-text-primary);
}
</style>
