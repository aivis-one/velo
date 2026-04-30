<!--
  VELO Frontend -- RegisterView (S2 P06 C18 — PWA-only mock)

  Name + email + password + ToS/Privacy + Google/Apple OAuth registration form
  for PWA standalone users (decision #028). All submits mock until backend
  lands § A.1 + § A.2.

  Skin reference: docs/04_assets/velo-design-system-2026-04-30/project/uploads/03_Register.png
  Path Y direct-port: visual fidelity to skin is MEDIUM target.

  ToS/Privacy URLs pending product copy — placeholder href="#" + console.warn
  on click until URLs are provided.
-->

<template>
  <div class="register">
    <img
      class="register__mandala"
      src="@/assets/brand/mandala-runes.svg"
      alt=""
      aria-hidden="true"
    >

    <div class="register__brand">
      <h2 class="register__wordmark">
        VELΘ
      </h2>
    </div>

    <h1 class="register__title">
      Создать аккаунт
    </h1>
    <p class="register__subtitle">
      Начните свой путь к осознанности
    </p>

    <form
      class="register__form"
      @submit.prevent="onSubmit"
    >
      <VInput
        v-model="firstName"
        type="text"
        placeholder="Как вас зовут?"
      />
      <VInput
        v-model="email"
        type="email"
        placeholder="E-mail"
      />
      <VInput
        v-model="password"
        type="password"
        placeholder="Пароль (от 8 символов)"
      />

      <VButton
        type="submit"
        variant="primary"
        size="md"
        block
      >
        Создать аккаунт
      </VButton>
    </form>

    <div class="register__divider">
      <span class="register__divider-text">или</span>
    </div>

    <div class="register__oauth">
      <button
        type="button"
        class="register__oauth-btn"
        @click="onGoogleOAuth"
      >
        Войти через Google
      </button>
      <button
        type="button"
        class="register__oauth-btn"
        @click="onAppleOAuth"
      >
        Войти через Apple
      </button>
    </div>

    <div class="register__footer">
      <span class="register__footer-text">Уже есть аккаунт?</span>
      <button
        type="button"
        class="register__footer-link"
        @click="onGoToLogin"
      >
        Войти
      </button>
    </div>

    <p class="register__tos">
      Нажимая «Создать аккаунт» или «Войти», я принимаю
      <a
        href="#"
        class="register__tos-link"
        @click.prevent="onToS"
      >Условия использования</a>
      и соглашаюсь с
      <a
        href="#"
        class="register__tos-link"
        @click.prevent="onPrivacy"
      >Политикой конфиденциальности</a>.
    </p>

    <button
      type="button"
      class="register__back"
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

const firstName = ref('')
const email = ref('')
const password = ref('')

function onSubmit(): void {
  // Mock — BACKEND-COORDINATION § A.1 not landed yet.
  toast.info('Регистрация в разработке')
}

function onGoogleOAuth(): void {
  // Mock — BACKEND-COORDINATION § A.2 not landed yet.
  toast.info('OAuth Google скоро будет доступен')
}

function onAppleOAuth(): void {
  toast.info('OAuth Apple скоро будет доступен')
}

function onGoToLogin(): void {
  router.push({ name: 'login' })
}

function onToS(): void {
  console.warn('[C18] ToS URL pending product copy')
}

function onPrivacy(): void {
  console.warn('[C18] Privacy Policy URL pending product copy')
}

function onBack(): void {
  router.back()
}
</script>

<style scoped>
.register {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-6);
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--surface-default);
}

.register__mandala {
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

.register__brand,
.register__title,
.register__subtitle,
.register__form,
.register__divider,
.register__oauth,
.register__footer,
.register__tos,
.register__back {
  position: relative;
  z-index: 1;
}

.register__brand {
  display: flex;
  justify-content: center;
  margin-top: var(--space-2);
}

.register__wordmark {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.register__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: var(--space-4) 0 0;
  text-align: center;
}

.register__subtitle {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-3);
  text-align: center;
}

.register__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.register__divider {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin: var(--space-3) 0;
}

.register__divider::before,
.register__divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-subtle);
}

.register__divider-text {
  color: var(--text-muted);
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.register__oauth {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.register__oauth-btn {
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

.register__oauth-btn:hover {
  opacity: 0.9;
}

.register__footer {
  display: flex;
  justify-content: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.register__footer-text {
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: var(--text-sm);
}

.register__footer-link {
  background: transparent;
  border: none;
  color: var(--steel-button);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  cursor: pointer;
  padding: 0;
}

.register__tos {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--text-muted);
  text-align: center;
  line-height: 1.4;
  margin: var(--space-3) 0 0;
}

.register__tos-link {
  color: var(--text-secondary);
  text-decoration: underline;
}

.register__back {
  align-self: flex-start;
  margin-top: auto;
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  padding: var(--space-2);
}
</style>
