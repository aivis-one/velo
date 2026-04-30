<!--
  VELO Frontend -- LoginView (S2 P06 C17 — PWA-only mock)

  Email/password + Google/Apple OAuth login form for PWA standalone users
  (decision #028). All submits are mock until backend lands § A.1 + § A.2;
  see BACKEND-COORDINATION.md.

  Skin reference: docs/04_assets/velo-design-system-2026-04-30/project/uploads/02_Login.png
  Path Y direct-port: visual fidelity to skin is MEDIUM target; pixel-polish
  deferred to dedicated S3+ cluster.
-->

<template>
  <div class="login">
    <img
      class="login__mandala"
      src="@/assets/brand/mandala-runes.svg"
      alt=""
      aria-hidden="true"
    >

    <div class="login__brand">
      <h2 class="login__wordmark">
        VELΘ
      </h2>
    </div>

    <h1 class="login__title">
      С возвращением!
    </h1>
    <p class="login__subtitle">
      Войдите, чтобы продолжить практику
    </p>

    <form
      class="login__form"
      @submit.prevent="onSubmit"
    >
      <VInput
        v-model="email"
        type="email"
        placeholder="E-mail"
      />
      <VInput
        v-model="password"
        type="password"
        placeholder="Пароль"
      />

      <button
        type="button"
        class="login__forgot"
        @click="onForgotPassword"
      >
        Забыли пароль?
      </button>

      <VButton
        type="submit"
        variant="primary"
        size="md"
        block
      >
        Войти
      </VButton>
    </form>

    <div class="login__divider">
      <span class="login__divider-text">или</span>
    </div>

    <div class="login__oauth">
      <button
        type="button"
        class="login__oauth-btn"
        @click="onGoogleOAuth"
      >
        Войти через Google
      </button>
      <button
        type="button"
        class="login__oauth-btn"
        @click="onAppleOAuth"
      >
        Войти через Apple
      </button>
    </div>

    <div class="login__footer">
      <span class="login__footer-text">Нет аккаунта?</span>
      <button
        type="button"
        class="login__footer-link"
        @click="onGoToRegister"
      >
        Создать
      </button>
    </div>

    <button
      type="button"
      class="login__back"
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { VButton, VInput } from '@/components/ui'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()

const email = ref('')
const password = ref('')

function onSubmit(): void {
  // Mock — BACKEND-COORDINATION § A.1 not landed yet.
  toast.info('Email-вход в разработке')
}

function onForgotPassword(): void {
  toast.info('Восстановление пароля скоро будет доступно')
}

function onGoogleOAuth(): void {
  // Mock — BACKEND-COORDINATION § A.2 not landed yet.
  toast.info('OAuth Google скоро будет доступен')
}

function onAppleOAuth(): void {
  toast.info('OAuth Apple скоро будет доступен')
}

function onGoToRegister(): void {
  router.push({ name: 'register' })
}

function onBack(): void {
  router.back()
}
</script>

<style scoped>
.login {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-6);
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--surface-default);
}

.login__mandala {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 320px;
  height: 320px;
  opacity: 0.18;
  pointer-events: none;
  z-index: 0;
}

.login__brand,
.login__title,
.login__subtitle,
.login__form,
.login__divider,
.login__oauth,
.login__footer,
.login__back {
  position: relative;
  z-index: 1;
}

.login__brand {
  display: flex;
  justify-content: center;
  margin-top: var(--space-2);
}

.login__wordmark {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.login__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: var(--space-4) 0 0;
  text-align: center;
}

.login__subtitle {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-3);
  text-align: center;
}

.login__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.login__forgot {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  text-align: right;
  cursor: pointer;
  padding: 0;
  align-self: flex-end;
}

.login__divider {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin: var(--space-3) 0;
}

.login__divider::before,
.login__divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-subtle);
}

.login__divider-text {
  color: var(--text-muted);
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.login__oauth {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.login__oauth-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 50px;
  padding: 0 var(--space-4);
  background: var(--surface-steel-alpha-15);
  color: var(--text-primary);
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-glow-white);
  font-family: var(--font-body);
  font-size: var(--text-base);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.login__oauth-btn:hover {
  opacity: 0.9;
}

.login__footer {
  display: flex;
  justify-content: center;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.login__footer-text {
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.login__footer-link {
  background: transparent;
  border: none;
  color: var(--steel-button);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  cursor: pointer;
  padding: 0;
}

.login__back {
  align-self: flex-start;
  margin-top: auto;
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  padding: var(--space-2);
}
</style>
