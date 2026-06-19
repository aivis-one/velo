<!--
  VELO Frontend -- MasterPendingView (Phase F6.1)

  Standalone route (no MasterShell, no tab bar).
  Shown after master application is submitted or when masterStatusGuard
  detects that profile.status !== 'verified'.

  Two cases handled:
    1. role='user'   -- just applied, can't call GET /masters/me yet.
                        Shows static "application submitted" screen.
                        "Обновить" calls authStore.fetchMe() to re-check
                        role. If role flips to 'master', redirect to dashboard.
    2. role='master' -- fetches master profile from store, shows real status.
                        If status becomes 'verified', redirect to dashboard.

  Both cases show:
    - Success icon + title
    - "Рассмотрим в течение 24-48 часов" message
    - Status badge (pending / rejected)
    - Rejection reason if status=rejected (with "Re-apply" link)
    - "Обновить статус" button
-->

<template>
  <div class="pending-view">
    <!-- Header (no back button -- user is in a holding state) -->
    <VHeader title="Заявка" />

    <div class="pending-view__content">
      <!-- Submitted icon -->
      <div class="pending-view__icon"><IconCheck :size="40" /></div>

      <h2 class="pending-view__title">Заявка отправлена!</h2>

      <p class="pending-view__subtitle">Рассмотрим в течение 24-48 часов</p>

      <!-- Status badge (real data for role='master', static for role='user') -->
      <div class="pending-view__status">
        <template v-if="masterStore.profileLoading">
          <VLoader size="sm" />
        </template>
        <template v-else-if="profileStatus === 'rejected'">
          <VBadge variant="error">Заявка отклонена</VBadge>
          <p v-if="rejectionReason" class="pending-view__rejection">
            Причина: {{ rejectionReason }}
          </p>
          <VButton
            variant="outline"
            size="sm"
            class="pending-view__reapply"
            @click="router.push({ name: 'master-apply' })"
          >
            Подать новую заявку
          </VButton>
        </template>
        <template v-else>
          <VBadge variant="warning">На проверке</VBadge>
        </template>
      </div>

      <!-- Info card -->
      <VCard class="pending-view__info-card" padding="none">
        <p class="pending-view__info-text">
          Когда ваша заявка будет рассмотрена, вы получите уведомление в Telegram.
        </p>
      </VCard>

      <!-- Refresh button -->
      <VButton variant="primary" block :loading="refreshing" @click="refreshStatus">
        Обновить статус
      </VButton>

      <!-- Back to catalog -->
      <VButton variant="ghost" block @click="router.push({ name: 'user-dashboard' })">
        Вернуться к каталогу
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton, VBadge, VLoader, VCard } from '@/components/ui'
import { IconCheck } from '@/components/icons'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useMasterStore } from '@/stores/master'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const masterStore = useMasterStore()

const refreshing = ref(false)

// -- Derived profile status --
// For role='user': always 'pending' (can't fetch master profile yet)
// For role='master': taken from loaded profile
const profileStatus = computed(() => {
  if (authStore.role !== 'master') return 'pending'
  return masterStore.profile?.status ?? 'pending'
})

// Rejection reason from JSONB data -- not in MasterProfileResponse directly,
// but status 'rejected' means backend has set it. We show a generic message
// since the rejection reason is not exposed in the public profile endpoint.
const rejectionReason = computed((): string => {
  if (profileStatus.value !== 'rejected') return ''
  // MasterProfileResponse doesn't expose rejection_reason. Show generic text.
  return 'Заявка не прошла верификацию. Пожалуйста, подайте повторную заявку с актуальными данными.'
})

// -- On mount: if role='master', load profile to show real status --
onMounted(async () => {
  if (authStore.role === 'master') {
    await masterStore.fetchMyProfile(true)
    checkIfVerified()
  }
})

// -- Redirect if already verified --
function checkIfVerified(): void {
  if (authStore.role === 'master' && masterStore.profile?.status === 'verified') {
    router.replace({ name: 'master-dashboard' })
  }
}

// -- Refresh status --
async function refreshStatus(): Promise<void> {
  if (refreshing.value) return
  refreshing.value = true

  try {
    // Always re-fetch user role first (covers role='user' -> role='master' transition)
    await authStore.fetchMe()

    if (authStore.role === 'master') {
      // Now fetch master profile to get real status
      await masterStore.fetchMyProfile(true)
      checkIfVerified()
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
  /* Standalone route (outside MobileLayout) — apply the screen rail inset
     directly so content matches the app's 24px rail (WS-1, 2026-06-19). */
  padding: var(--space-8) var(--velo-rail-pad-x) var(--space-5);
  gap: var(--space-4);
}

/* -- Success icon (circle with checkmark, matches mockup screen-submitted) -- */
.pending-view__icon {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background: var(--velo-success);
  color: var(--velo-white);
  font-size: 36px;  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.pending-view__title {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  color: var(--velo-text-primary);
  text-align: center;
}

.pending-view__subtitle {
  font-size: var(--text-base);
  color: var(--velo-text-secondary);
  text-align: center;
}

/* -- Status area -- */
.pending-view__status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.pending-view__rejection {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  text-align: center;
  max-width: 300px;
  line-height: 1.5;
}

.pending-view__reapply {
  margin-top: var(--space-1);
}

/* -- Info card -- */
.pending-view__info-card {
  width: 100%;
  padding: var(--space-4);
}

.pending-view__info-text {
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  text-align: center;
  line-height: 1.6;
}
</style>
