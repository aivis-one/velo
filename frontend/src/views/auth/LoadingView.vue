<!--
  VELO Frontend -- Loading View (DS-6)

  Displayed while auth initialization is in progress.
  Uses the SAME white mandala as WelcomeView (logo-white.svg, large) so the
  loading -> welcome transition is seamless: no blue-mandala flash before the
  white one (the default `logo.svg` is the colored/blue variant). The white
  logo already contains the VELΘ wordmark, so there is no separate title.
  Spinner stays as the loading cue.
-->

<template>
  <div class="loading">
    <div class="loading__logo">
      <VeloLogo variant="white" :size="440" spin />
    </div>
    <div class="loading__spinner" />
  </div>
</template>

<script setup lang="ts">
import VeloLogo from '@/components/ui/VeloLogo.vue'
</script>

<style scoped>
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* Fill AppFrame's content area (it owns viewport height + safe-area once,
     app-wide). A fresh 100dvh here double-applies and makes the logo jump. */
  min-height: 100%;
  background: transparent;
  gap: var(--space-4);
  /* The white logo is intentionally larger than the viewport (Figma bleed,
     same as WelcomeView). Clip horizontal overflow so it bleeds symmetrically
     instead of producing a horizontal scrollbar. */
  overflow-x: hidden;
}

.loading__logo {
  /* Match WelcomeView: let the oversized logo bleed without being squeezed. */
  flex-shrink: 0;
}

.loading__spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--velo-border-light);
  border-top-color: var(--velo-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-top: var(--space-4);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
