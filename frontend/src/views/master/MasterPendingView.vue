<!--
  VELO Frontend -- MasterPendingView (verdict screens, slice-2 C2)

  Standalone route (no MasterShell, no tab bar). Shown after a master
  application is submitted, or when masterStatusGuard sends a non-verified
  master here. Restyled to the operator Figma — three distinct states keyed on
  the application status:

    1. «Заявка отправлена» (pending) — SVG-6. role='user' just applied (can't
       fetch /masters/me yet) OR role='master' pending. Keeps the polling
       («Обновить статус») + «Вернуться к каталогу».
    2. «Ваша заявка одобрена!» (verified) — SVG-7. Explicit approved screen with
       a single «Войти в кабинет» CTA → master dashboard (which chains into the
       post-approval onboarding carousel). Replaces the old auto-redirect.
    3. «Отказ» (rejected) — SVG-8. Amber, generic reason until rejection_reason
       is exposed (Zod E14); TWO CTAs (FORK-4): «Написать в поддержку» AND
       «Подать новую заявку» (the re-apply path is kept).

  Illustrations extracted from the design SVGs to public/onboarding/master-verdict-*.svg.
-->

<template>
  <div class="pending-view">
    <VHeader title="Заявка" />

    <div class="pending-view__content">
      <template v-if="masterStore.profileLoading">
        <VLoader size="lg" />
      </template>

      <!-- ================= APPROVED (verified) ================= -->
      <template v-else-if="profileStatus === 'verified'">
        <img
          src="/onboarding/master-verdict-approved.svg"
          alt=""
          class="pending-view__illu pending-view__illu--lg"
        />
        <h2 class="pending-view__title">Ваша заявка одобрена!</h2>
        <p class="pending-view__subtitle">
          Переключитесь в режим мастера, чтобы открыть кабинет. Вернуться в режим
          пользователя можно в любой момент из настроек.
        </p>
        <div class="pending-view__actions">
          <VButton variant="primary" block :loading="switching" @click="enterMasterMode">
            Перейти в режим мастера
          </VButton>
        </div>
      </template>

      <!-- ================= REJECTED ================= -->
      <template v-else-if="profileStatus === 'rejected'">
        <img
          src="/onboarding/master-verdict-reject.svg"
          alt=""
          class="pending-view__illu pending-view__illu--lg"
        />
        <h2 class="pending-view__title">Спасибо за заявку!</h2>
        <p class="pending-view__subtitle">К сожалению, мы пока не можем одобрить вашу заявку.</p>

        <div class="pending-view__reason">
          <div class="pending-view__reason-label">Причина:</div>
          <div class="pending-view__reason-text">{{ rejectionReason }}</div>
        </div>

        <div class="pending-view__actions">
          <VButton variant="primary" block @click="router.push({ name: 'master-support' })">
            Написать в поддержку
          </VButton>
        </div>
      </template>

      <!-- ================= SENT (pending) ================= -->
      <template v-else>
        <img src="/onboarding/master-verdict-sent.svg" alt="" class="pending-view__illu" />
        <h2 class="pending-view__title">Заявка отправлена!</h2>
        <p class="pending-view__subtitle">Рассмотрим за 24–48 часов, сообщим в push и на email</p>

        <div class="pending-view__actions">
          <VButton variant="primary" block :loading="refreshing" @click="refreshStatus">
            Обновить статус
          </VButton>
          <VButton variant="ghost" block @click="router.push({ name: 'user-dashboard' })">
            Вернуться к каталогу
          </VButton>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton, VLoader } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useMasterStore } from '@/stores/master'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const masterStore = useMasterStore()

const refreshing = ref(false)
const switching = ref(false)

// -- Derived application status --
// T4: approval no longer flips role — an approved applicant stays role='user'
// and gains master CAPABILITY (a verified MasterProfile), surfaced as 'master'
// in authStore.allowedRoles (GET /users/me role_switch). So:
//   role='master'                    -> the loaded profile status.
//   role='user' + capability(master) -> approved ('verified').
//   otherwise                        -> 'pending'.
// (A rejected applicant is role='user' with no capability -> shows 'pending'
//  here; surfacing the rejection to a role='user' account is deferred to T5.)
const profileStatus = computed(() => {
  if (authStore.role === 'master') return masterStore.profile?.status ?? 'pending'
  if (authStore.allowedRoles.includes('master')) return 'verified'
  // T5: a rejected applicant stays role='user' with no capability; the verdict
  // is surfaced on GET /users/me (master_application) so the reject screen is
  // reachable without the master-only /masters/me endpoint.
  if (authStore.masterApplication?.status === 'rejected') return 'rejected'
  return 'pending'
})

// Real rejection reason from the profile (E14: surfaced on MasterProfileResponse
// from data.account.rejection_reason). Falls back to a generic line when the
// admin left no reason (or on the preview path).
const rejectionReason = computed((): string => {
  if (profileStatus.value !== 'rejected') return ''
  return (
    masterStore.profile?.rejection_reason ??
    authStore.masterApplication?.rejection_reason ??
    'Заявка не прошла верификацию. Свяжитесь с поддержкой для повторной заявки.'
  )
})

// On mount: refresh the account so the status-keyed state renders. For a
// role='master' account load the profile; for role='user' re-fetch /users/me so
// a just-granted master capability (approval) is reflected in allowedRoles.
onMounted(async () => {
  if (authStore.role === 'master') {
    await masterStore.fetchMyProfile(true)
  } else {
    await authStore.fetchMe()
  }
})

// -- Enter master mode -- (T4: approved applicant self-switches role user->master)
async function enterMasterMode(): Promise<void> {
  if (switching.value) return
  switching.value = true
  try {
    await authStore.switchRole('master')
    router.push({ name: 'master-dashboard' })
  } catch {
    toast.error('Не удалось переключиться в режим мастера')
  } finally {
    switching.value = false
  }
}

// -- Refresh status -- (re-checks the approval: role flip OR capability grant)
async function refreshStatus(): Promise<void> {
  if (refreshing.value) return
  refreshing.value = true
  try {
    // Re-fetch the account: covers both a role='master' promotion and the T4
    // capability grant (allowedRoles gains 'master' on approval).
    await authStore.fetchMe()
    if (authStore.role === 'master') {
      await masterStore.fetchMyProfile(true)
    } else if (!authStore.allowedRoles.includes('master')) {
      toast.info('Заявка ещё на рассмотрении')
    }
    // else: approved — profileStatus flips to 'verified' reactively.
  } catch {
    toast.error('Не удалось проверить статус')
  } finally {
    refreshing.value = false
  }
}
</script>

<style scoped>
.pending-view {
  min-height: 100dvh;
  min-height: 100vh;
  background: transparent;
  display: flex;
  flex-direction: column;
}

.pending-view__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* Standalone route (outside MobileLayout) — apply the screen rail directly
     so content matches the app's 24px rail (WS-1, 2026-06-19). */
  padding: var(--space-8) var(--velo-rail-pad-x) var(--space-5);
  gap: var(--space-4);
}

/* -- Verdict illustration (extracted from the design SVGs) -- */
.pending-view__illu {
  width: 96px;
  height: 96px;
  object-fit: contain;
  flex-shrink: 0;
}

.pending-view__illu--lg {
  width: 160px;
  height: 160px;
}

.pending-view__title {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  color: var(--velo-text-primary);
  text-align: center;
  -webkit-text-stroke: var(--velo-text-stroke-strong) var(--velo-text-primary);
}

.pending-view__subtitle {
  font-size: var(--text-base);
  color: var(--velo-text-secondary);
  text-align: center;
  max-width: 300px;
  line-height: 1.5;
  margin: 0;
}

/* -- Rejection reason (amber) -- */
.pending-view__reason {
  width: 100%;
  background: var(--velo-warning-bg);
  border: var(--velo-banner-border-width) solid var(--velo-warning-border);
  border-radius: var(--velo-radius-9);
  padding: var(--space-3) var(--space-4);
}

.pending-view__reason-label {
  font-size: var(--text-xs);
  color: var(--velo-warning-text);
  letter-spacing: 0.02em;
}

.pending-view__reason-text {
  font-size: var(--text-base);
  color: var(--velo-warning-text);
  line-height: 1.4;
  margin-top: var(--space-1);
}

/* -- Actions -- */
.pending-view__actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-top: var(--space-2);
}
</style>
