<!--
=============================================================================
VELO Frontend — Master invite claim (Batch-INVITE, ПРОМТ №258)
=============================================================================

Landing for the one-time invite deeplink master_onboarding__<token>
(route /master/invite/:token, standalone — outside the shells, like
/master/apply). On mount the token is claimed against the caller's OWN
account (the backend binds structurally: a stranger's link has no matching
marker). SUCCESS -> straight into the existing apply wizard. FAILURE ->
an honest error state with a way back — no fake progress:
  - invite_invalid  -> link is wrong / already used (one-time)
  - already_master  -> nothing to claim, offer the master dashboard
=============================================================================
-->

<template>
  <div class="invite-claim">
    <div class="invite-claim__content">
      <!-- Claiming -->
      <template v-if="claiming">
        <VLoader size="lg" />
        <p class="invite-claim__subtitle">Проверяем приглашение…</p>
      </template>

      <!-- Honest failure: consumed / foreign / garbage / already master -->
      <template v-else-if="errorTitle">
        <h2 class="invite-claim__title">{{ errorTitle }}</h2>
        <p class="invite-claim__subtitle">{{ errorDescription }}</p>
        <div class="invite-claim__actions">
          <VButton
            v-if="alreadyMaster"
            variant="primary"
            block
            @click="router.replace({ name: 'master-dashboard' })"
          >
            В кабинет мастера
          </VButton>
          <VButton
            v-else
            variant="primary"
            block
            @click="router.replace({ name: 'user-dashboard' })"
          >
            На главную
          </VButton>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { claimMasterInvite } from '@/api/masters'
import { ApiResponseError } from '@/api/client'
import { useToast } from '@/composables/useToast'
import VButton from '@/components/ui/VButton.vue'
import VLoader from '@/components/ui/VLoader.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const claiming = ref(true)
const errorTitle = ref('')
const errorDescription = ref('')
const alreadyMaster = ref(false)

onMounted(async () => {
  const token = String(route.params.token ?? '')
  try {
    await claimMasterInvite(token)
    // Claimed (one-time, consumed) — hand off to the regular apply wizard.
    toast.success('Приглашение принято!')
    void router.replace({ name: 'master-apply' })
  } catch (e) {
    if (e instanceof ApiResponseError && e.code === 'already_master') {
      alreadyMaster.value = true
      errorTitle.value = 'Вы уже мастер'
      errorDescription.value =
        'Это приглашение вам больше не нужно — кабинет мастера уже открыт.'
    } else {
      // invite_invalid (wrong / already used / someone else's) and anything
      // else network-shaped: one honest message, no oracle about which.
      errorTitle.value = 'Ссылка недействительна'
      errorDescription.value =
        'Приглашение одноразовое: возможно, оно уже использовано или ссылка ' +
        'повреждена. Запросите новую ссылку у администратора.'
    }
  } finally {
    claiming.value = false
  }
})
</script>

<style scoped>
.invite-claim {
  min-height: 100dvh;
  min-height: 100vh;
  background: transparent;
  display: flex;
  flex-direction: column;
}

.invite-claim__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* Standalone route (outside MobileLayout) — apply the screen rail directly
     so content matches the app's 24px rail (WS-1). */
  padding: var(--space-8) var(--velo-rail-pad-x) var(--space-5);
  gap: var(--space-4);
}

.invite-claim__title {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  color: var(--velo-text-primary);
  text-align: center;
  -webkit-text-stroke: var(--velo-text-stroke-strong) var(--velo-text-primary);
}

.invite-claim__subtitle {
  font-size: var(--text-base);
  color: var(--velo-text-secondary);
  text-align: center;
  max-width: 300px;
  line-height: 1.5;
  margin: 0;
}

.invite-claim__actions {
  width: 100%;
  max-width: 300px;
  margin-top: var(--space-4);
}
</style>
