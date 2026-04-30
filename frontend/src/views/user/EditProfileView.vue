<!--
  VELO Frontend -- EditProfileView (S2 P09 C34 — skin 72)

  First name + last name + bio + Save (PATCH /api/v1/users/me direct call,
  no api/users.ts wrapper). Avatar read-only with toast (decision #038).
  "Удалить аккаунт" → native confirm → mock toast per BACKEND § A.4.

  Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="ep">
    <VHeader
      title="Редактировать профиль"
      show-back
      @back="$router.back()"
    />

    <div class="ep__body">
      <section class="ep__avatar">
        <div class="ep__avatar-icon">
          <IconProfile :size="48" />
        </div>
        <button
          type="button"
          class="ep__avatar-cap"
          @click="onAvatarClick"
        >
          Изменить фото
        </button>
      </section>

      <form
        class="ep__form"
        @submit.prevent="onSave"
      >
        <label class="ep__field">
          <span>Имя</span>
          <input
            v-model="firstName"
            type="text"
            maxlength="100"
          >
        </label>
        <label class="ep__field">
          <span>Фамилия</span>
          <input
            v-model="lastName"
            type="text"
            maxlength="100"
          >
        </label>
        <label class="ep__field">
          <span>О себе</span>
          <textarea
            v-model="bio"
            rows="3"
            maxlength="500"
            placeholder="Расскажите немного о себе…"
          />
        </label>

        <button
          type="button"
          class="ep__delete"
          @click="onDelete"
        >
          <IconArrowBack :size="16" />
          <span>Удалить аккаунт</span>
        </button>

        <VButton
          type="submit"
          variant="primary"
          size="md"
          block
          :loading="saving"
        >
          Сохранить
        </VButton>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VButton } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { IconProfile, IconArrowBack } from '@/components/icons'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { api } from '@/api/client'
import { extractApiError } from '@/composables/useApiError'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const firstName = ref('')
const lastName = ref('')
const bio = ref('')
const saving = ref(false)

function onAvatarClick(): void {
  // Per decision #038, avatar is Telegram-managed.
  toast.info('Аватар управляется Telegram')
}

async function onSave(): Promise<void> {
  if (saving.value) return
  saving.value = true
  try {
    await api.patch('/api/v1/users/me', {
      first_name: firstName.value.trim() || null,
      last_name: lastName.value.trim() || null,
    })
    await auth.fetchMe()
    toast.success('Сохранено')
    router.back()
  } catch (e) {
    toast.error(extractApiError(e, 'Не удалось сохранить'))
  } finally {
    saving.value = false
  }
}

function onDelete(): void {
  const ok = window.confirm(
    'Вы уверены? После удаления восстановить аккаунт будет уже невозможно.',
  )
  if (!ok) return
  // BACKEND § A.4 not landed; mock per Path Y graceful degrade.
  toast.info('Удаление аккаунта в разработке. Свяжитесь с поддержкой.')
}

onMounted(() => {
  const u = auth.user
  if (u) {
    firstName.value = u.first_name ?? ''
    lastName.value = u.last_name ?? ''
    bio.value = ''
  }
})
</script>

<style scoped>
.ep {
  display: flex;
  flex-direction: column;
}

.ep__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.ep__avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.ep__avatar-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: var(--radius-full);
  background: var(--surface-default);
  color: var(--text-secondary);
}

.ep__avatar-cap {
  background: transparent;
  border: none;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--steel-button);
  cursor: pointer;
}

.ep__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.ep__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.ep__field input,
.ep__field textarea {
  padding: var(--space-3);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  resize: none;
  box-sizing: border-box;
}

.ep__delete {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: transparent;
  border: none;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--pink-primary);
  cursor: pointer;
  padding: var(--space-2) 0;
}
</style>
