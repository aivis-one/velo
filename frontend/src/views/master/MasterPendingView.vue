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
        <div class="pending-view__actions">
          <VButton variant="primary" block @click="router.push({ name: 'master-dashboard' })">
            Войти в кабинет
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
          <VButton variant="ghost" block @click="router.push({ name: 'master-apply' })">
            Подать новую заявку
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

// -- Derived application status --
// role='user' (just applied) can't fetch /masters/me yet -> always 'pending'.
// role='master' -> the loaded profile status (verified / rejected / pending).
const profileStatus = computed(() => {
  if (authStore.role !== 'master') return 'pending'
  return masterStore.profile?.status ?? 'pending'
})

// Generic reason until rejection_reason is exposed on MasterProfileResponse
// (Zod E14). The admin captures a reason on reject, but it is not surfaced here.
const rejectionReason = computed((): string => {
  if (profileStatus.value !== 'rejected') return ''
  return 'Заявка не прошла верификацию. Пожалуйста, подайте повторную заявку с актуальными данными.'
})

// On mount: load the master profile so the status-keyed state renders. No
// auto-redirect on verified — the «Одобрено» screen + CTA handles that now.
onMounted(async () => {
  if (authStore.role === 'master') {
    await masterStore.fetchMyProfile(true)
  }
})

// -- Refresh status -- (re-checks the user->master promotion + profile status)
async function refreshStatus(): Promise<void> {
  if (refreshing.value) return
  refreshing.value = true
  try {
    // Re-fetch user role first (covers the role='user' -> 'master' transition).
    await authStore.fetchMe()
    if (authStore.role === 'master') {
      await masterStore.fetchMyProfile(true)
    } else {
      toast.info('Заявка ещё на рассмотрении')
    }
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
