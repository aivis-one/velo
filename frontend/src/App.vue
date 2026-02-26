<!--
  VELO Frontend -- Root Component (updated Phase F1.3)

  Auth flow on mount:
    1. Show LoadingView while auth initializes
    2. If standalone (no Telegram) -> StandaloneStubView
    3. If auth failed -> StandaloneStubView (fallback)
    4. If auth succeeded -> RouterView (the actual app)
-->

<template>
  <LoadingView v-if="!isReady" />
  <StandaloneStubView v-else-if="isStandalone || !isAuthenticated" />
  <RouterView v-else />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import LoadingView from '@/views/auth/LoadingView.vue'
import StandaloneStubView from '@/views/auth/StandaloneStubView.vue'

const { isReady, isAuthenticated, isStandalone, initAuth } = useAuth()

onMounted(() => {
  initAuth()
})
</script>
