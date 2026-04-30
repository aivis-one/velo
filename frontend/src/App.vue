<!--
  VELO Frontend -- Root Component (updated S2 P06 C16)

  Auth gate flow on mount:
    1. Show LoadingView while auth initializes (isReady=false).
    2. Otherwise render RouterView. Standalone unauthenticated users
       reach /welcome PWA branch (decision #036) — no longer
       short-circuited at App.vue gate.

  C16: standalone users now route through /welcome PWA branch
  (decision #036). StandaloneStubView retained on disk for potential
  auth-error reuse but no longer mounted from App.vue.

  VToast is mounted once here — renders all toast notifications
  triggered via useToast() composable from any component.
-->

<template>
  <LoadingView v-if="!isReady" />
  <RouterView v-else />
  <VToast />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { VToast } from '@/components/ui'
import LoadingView from '@/views/auth/LoadingView.vue'

const { isReady, initAuth } = useAuth()

onMounted(() => {
  initAuth()
})
</script>
