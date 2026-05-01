<!--
  VELO Frontend -- MasterPendingView (Phase F6.1; refreshed S4 P14 C55)

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
    - Success icon + title (IconSuccess for pending, IconWarning for rejected per #048)
    - "Рассмотрим в течение 24-48 часов" message
    - Status badge (pending / rejected)
    - Rejection reason via Callout(amber) if status=rejected (with "Re-apply" link)
    - "Обновить статус" button

  Path Y MEDIUM (#047). No emojis (#048).
-->

<template>
  <div class="pending-view">
    <!-- Header (no back button -- user is in a holding state) -->
    <VHeader title="Заявка" />

    <div class="pending-view__content">
      <!-- Status icon (Velo DS) -->
      <div
        class="pending-view__icon"
        :class="{ 'pending-view__icon--rejected': profileStatus === 'rejected' }"
      >
        <IconWarning
          v-if="profileStatus === 'rejected'"
          :size="40"
        />
        <IconSuccess
          v-else
          :size="40"
        />
      </div>

      <h2 class="pending-view__title">
        {{ profileStatus === 'rejected' ? 'Заявка отклонена' : 'Заявка отправлена!' }}
      </h2>

      <p class="pending-view__subtitle">
        {{ profileStatus === 'rejected' ? 'См. причину ниже' : 'Рассмотрим в течение 24-48 часов' }}
      </p>

      <!-- Status badge (real data for role='master', static for role='user') -->
      <div class="pending-view__status">
        <template v-if="masterStore.profileLoading">
          <VLoader size="sm" />
        </template>
        <template v-else-if="profileStatus === 'rejected'">
          <VBadge variant="error">
            Заявка отклонена
          </VBadge>
          <Callout
            v-if="rejectionReason"
            variant="amber"
            :icon="IconWarning"
            title="Причина отклонения"
          >
            {{ rejectionReason }}
          </Callout>
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
          <VBadge variant="warning">
            На проверке
          </VBadge>
        </template>
      </div>

      <!-- Info card -->
      <div class="pending-view__info-card">
        <p class="pending-view__info-text">
          Когда ваша заявка будет рассмотрена, вы получите
          уведомление в Telegram.
        </p>
      </div>

      <!-- Refresh button -->
      <VButton
        variant="primary"
        block
        :loading="refreshing"
        @click="refreshStatus"
      >
        Обновить статус
      </VButton>

      <!-- Back to catalog -->
      <VButton
        variant="ghost"
        block
        @click="router.push({ name: 'user-dashboard' })"
      >
        Вернуться к каталогу
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton, VBadge, VLoader } from '@/components/ui'
import { IconSuccess, IconWarning } from '@/components/icons'
import Callout from '@/components/shared/Callout.vue'
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
  if (
    authStore.role === 'master' &&
    masterStore.profile?.status === 'verified'
  ) {
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
  padding: var(--space-8) var(--space-4) var(--space-6);
  gap: var(--space-4);
}

/* -- Status icon (circle with IconSuccess or IconWarning) -- */
.pending-view__icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--teal-primary, var(--mint-primary, var(--steel-button)));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.pending-view__icon--rejected {
  background: var(--pink-primary);
}

.pending-view__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  color: var(--text-primary);
  text-align: center;
  font-weight: 400;
  margin: 0;
}

.pending-view__subtitle {
  font-size: var(--text-base);
  color: var(--text-secondary);
  text-align: center;
  font-family: var(--font-body);
  margin: 0;
}

/* -- Status area -- */
.pending-view__status {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
  gap: var(--space-3);
}

.pending-view__reapply {
  align-self: center;
  margin-top: var(--space-1);
}

/* -- Info card -- */
.pending-view__info-card {
  width: 100%;
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.pending-view__info-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.6;
  font-family: var(--font-body);
  margin: 0;
}
</style>
