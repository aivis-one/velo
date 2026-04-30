<!--
  VELO Frontend -- OAuthLoadingView (S2 P06 C19 — mock callback state)

  Splash screen for OAuth callback. Per BACKEND-COORDINATION § A.2, OAuth
  endpoints are not landed yet; this view is a UI shell that surfaces a
  not-ready toast and redirects back to /welcome after a brief delay so
  the user perceives a transient loading state instead of a blank flash.

  Skin reference: docs/04_assets/velo-design-system-2026-04-30/project/uploads/04_OAuth.png
  Path Y direct-port: visual reuses LoadingView pattern (VeloLogo + spinner).
-->

<template>
  <div class="oauth-loading">
    <VeloLogo
      class="oauth-loading__logo"
      :size="120"
    />
    <h1 class="oauth-loading__title">
      Авторизация…
    </h1>
    <div
      class="oauth-loading__spinner"
      role="status"
      aria-label="Загрузка"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VeloLogo } from '@/components/ui'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()

const MOCK_DELAY_MS = 1500

onMounted(() => {
  // Mock — BACKEND-COORDINATION § A.2 not landed yet. Brief perceived
  // loading state, then surface mock-not-ready toast and redirect.
  setTimeout(() => {
    toast.info('OAuth скоро будет доступен')
    router.replace({ name: 'welcome' })
  }, MOCK_DELAY_MS)
})
</script>

<style scoped>
.oauth-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  gap: var(--space-4);
  padding: var(--space-6);
  background: var(--surface-default);
}

.oauth-loading__logo {
  animation: oauth-loading-pulse 2s ease-in-out infinite;
}

.oauth-loading__title {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.oauth-loading__spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-subtle);
  border-top-color: var(--steel-button);
  border-radius: 50%;
  animation: oauth-loading-spin 0.8s linear infinite;
  margin-top: var(--space-4);
}

@keyframes oauth-loading-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes oauth-loading-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
