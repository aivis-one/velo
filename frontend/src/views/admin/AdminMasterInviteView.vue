<!--
  VELO Frontend -- AdminMasterInviteView (Batch-INVITE, №252 layout / ПРОМТ №258)

  Standalone admin screen «Пригласить мастера» (admin-master-invite), reached
  from the «Мастера» tab. Header (back + title) -> form-card (section
  «ОДНОРАЗОВАЯ ССЫЛКА», Telegram ID input, «Создать ссылку») -> result-card
  (the composed t.me/… deeplink + «Скопировать» via the B2 clipboard pattern).

  Error contract (machine codes from POST /admin/masters/invite):
    - invite_target_not_found (404) -> INLINE field error (the person must
      open the bot once so a User row exists)
    - already_master (409)          -> toast
  Re-generate for the same/another ID simply replaces the result card
  content (backend overwrites the marker; the old link dies).
-->

<template>
  <div class="invite">
    <header class="invite__top">
      <VBackButton @click="router.back()" />
      <span class="invite__title">Пригласить мастера</span>
    </header>

    <!-- Form card -->
    <VCard class="invite__card">
      <span class="invite__section-title">ОДНОРАЗОВАЯ ССЫЛКА</span>
      <p class="invite__desc">
        Ссылка выдаёт приглашение конкретному человеку. Он должен один раз
        открыть бота — после этого укажите его Telegram ID и создайте ссылку.
      </p>

      <VInput
        v-model="telegramId"
        label="Telegram ID"
        placeholder="123456789"
        inputmode="numeric"
        :error="fieldError"
        :disabled="creating"
      />

      <VButton
        variant="primary"
        block
        :loading="creating"
        :disabled="!telegramId.trim()"
        @click="onCreate"
      >
        Создать ссылку
      </VButton>
    </VCard>

    <!-- Result card (replaced in place on re-generate) -->
    <VCard v-if="inviteLink" class="invite__card">
      <span class="invite__section-title">ССЫЛКА ГОТОВА</span>
      <p class="invite__link">{{ inviteLink }}</p>
      <VButton variant="secondary" block @click="onCopy">Скопировать</VButton>
      <p class="invite__caption">одноразовая · действует до погашения</p>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { VBackButton, VCard, VInput, VButton } from '@/components/ui'
import { inviteMaster } from '@/api/admin'
import { ApiResponseError } from '@/api/client'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()

const telegramId = ref('')
const fieldError = ref('')
const creating = ref(false)
const inviteLink = ref('')

async function onCreate(): Promise<void> {
  fieldError.value = ''

  const tid = Number(telegramId.value.trim())
  if (!Number.isInteger(tid) || tid <= 0) {
    fieldError.value = 'Введите числовой Telegram ID'
    return
  }

  creating.value = true
  try {
    const res = await inviteMaster(tid)
    inviteLink.value = res.invite_link
  } catch (e) {
    if (e instanceof ApiResponseError && e.code === 'invite_target_not_found') {
      fieldError.value =
        'Пользователь не найден — он должен один раз открыть бота'
    } else if (e instanceof ApiResponseError && e.code === 'already_master') {
      toast.error('Этот пользователь уже мастер')
    } else {
      toast.error(
        e instanceof ApiResponseError ? e.detail : 'Не удалось создать ссылку',
      )
    }
  } finally {
    creating.value = false
  }
}

// Copy needs no backend — write the link straight to the clipboard (B2).
async function onCopy(): Promise<void> {
  try {
    await navigator.clipboard.writeText(inviteLink.value)
    toast.success('Ссылка скопирована')
  } catch {
    toast.error('Не удалось скопировать')
  }
}
</script>

<style scoped>
.invite {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* -- Header: back + title (canonical admin sub-view header) -- */
.invite__top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: var(--velo-size-44);
}

.invite__title {
  flex: 1;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

/* -- Cards -- */
.invite__card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.invite__section-title {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.invite__desc {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.5;
}

.invite__link {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  word-break: break-all;
  line-height: 1.5;
}

.invite__caption {
  margin: 0;
  text-align: center;
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
  letter-spacing: 0.02em;
}
</style>
