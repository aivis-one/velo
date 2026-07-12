<!--
=============================================================================
VELO Frontend — Master invite claim (Batch-INVITE, ПРОМТ №258)
=============================================================================

Landing for the generic one-time invite deeplink master_onboarding__<token>
(route /master/invite/:token, standalone — outside the shells, like
/master/apply). On mount the token is claimed: the backend burns it in Redis
(first claim wins). SUCCESS -> straight into the existing apply wizard.
FAILURE -> an honest error state with a way back — no fake progress:
  - invite_invalid (404) -> link is wrong / already used (one-time)
Verified masters never reach here: applyGuard bounces them to the dashboard.
=============================================================================
-->

<template>
  <div class="invite-claim">
    <div class="invite-claim__content velo-kbd-scroll">
      <!-- Claiming -->
      <template v-if="claiming">
        <VLoader size="lg" />
        <p class="invite-claim__subtitle">Проверяем приглашение…</p>
      </template>

      <!-- Honest failure: consumed / wrong / garbage token -->
      <template v-else-if="errorTitle">
        <h2 class="invite-claim__title">{{ errorTitle }}</h2>
        <p class="invite-claim__subtitle">{{ errorDescription }}</p>
        <div class="invite-claim__actions">
          <VButton
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
import { useToast } from '@/composables/useToast'
import VButton from '@/components/ui/VButton.vue'
import VLoader from '@/components/ui/VLoader.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const claiming = ref(true)
const errorTitle = ref('')
const errorDescription = ref('')

onMounted(async () => {
  const token = String(route.params.token ?? '')
  try {
    await claimMasterInvite(token)
    // Claimed (one-time, burned) — hand off to the regular apply wizard.
    toast.success('Приглашение принято!')
    void router.replace({ name: 'master-apply' })
  } catch {
    // invite_invalid (wrong / already used) and anything else network-shaped:
    // one honest message, no oracle about which.
    errorTitle.value = 'Ссылка недействительна'
    errorDescription.value =
      'Приглашение одноразовое: возможно, оно уже использовано или ссылка ' +
      'повреждена. Запросите новую ссылку у администратора.'
  } finally {
    claiming.value = false
  }
})
</script>

<style scoped>
.invite-claim {
  /* Fill AppFrame's stable height — never dvh/vh (collapse on keyboard). Canon §2. */
  min-height: 100%;
  background: transparent;
  display: flex;
  flex-direction: column;
}

.invite-claim__content {
  flex: 1;
  /* ROOT-LOCK: own the scroll (html/body/#app no longer absorb overflow). */
  min-height: 0;
  overflow-y: auto;
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
