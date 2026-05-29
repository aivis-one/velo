<!--
  VELO Frontend -- EditProfileView (Profile redesign Screens C + D)

  Edit-profile form (Figma node 4715:3685, 72_Edit Profile) plus the
  delete-account confirmation modal (Figma node 73, 73_Delete-confirm).

  FIELDS:
    - Name      -> first_name (real column; last_name left as-is, per the
                  master-name convention _master_full_name = first + last).
    - E-mail    -> DISABLED stub. The app has no email capture yet (see the
                  main profile screen decision); shown greyed out with a
                  "появится позже" placeholder, never sent.
    - Phone     -> credentials JSONB "phone". Soft, international validation
                  (digits/space/+()-, >=5 digits). Empty string clears it.
    - About     -> credentials JSONB "bio", max 2000 chars. Empty clears.
    - Change photo -> stub toast (no upload infra; avatar comes from Telegram).

  SAVE: collects only changed fields and sends them via updateProfile (PATCH
  /users/me). phone/bio cleared by sending "" (not null) -- matches the
  backend variant (b) semantics.

  DELETE (Screen D): the red "Удалить аккаунт" opens a confirm modal. On
  confirm we call deleteMe() then authStore.logout(). MVP backend semantics:
  this resets onboarding rather than erasing data, so the next login shows
  the welcome flow again with old data intact.

  VInput note: VInput has no `error` prop (unlike VTextarea), so the phone
  validation message is rendered as a sibling <p> under the field.

  Route: /user/profile/edit (name: 'user-edit-profile')
-->

<template>
  <div class="edit-profile">
    <VHeader
      title="Редактировать профиль"
      show-back
      @back="router.push({ name: 'user-profile' })"
    />

    <div class="edit-profile__content">
      <!-- Avatar + change photo (stub) -->
      <div class="edit-profile__avatar-block">
        <VAvatar :name="displayName" :url="user?.avatar_url ?? undefined" size="xl" />
        <button type="button" class="edit-profile__change-photo" @click="onChangePhoto">
          Изменить фото
        </button>
      </div>

      <!-- Name -->
      <VInput
        v-model="form.firstName"
        label="Имя"
        placeholder="Ваше имя"
      />

      <!-- E-mail (disabled stub) -->
      <VInput
        v-model="emailStub"
        label="E-mail"
        type="email"
        placeholder="появится позже"
        :disabled="true"
      />

      <!-- Phone -->
      <VInput
        v-model="form.phone"
        label="Телефон"
        type="tel"
        placeholder="+7 (___) ___-__-__"
      />
      <p v-if="phoneError" class="edit-profile__field-error">{{ phoneError }}</p>

      <!-- About -->
      <VTextarea
        v-model="form.bio"
        label="О себе"
        :rows="4"
        placeholder="Расскажите немного о себе"
        :error="bioError"
      />

      <!-- Save -->
      <VButton
        variant="primary"
        block
        :loading="saving"
        @click="onSave"
      >
        Сохранить
      </VButton>

      <!-- Delete account (opens modal D) -->
      <button type="button" class="edit-profile__delete" @click="showDeleteModal = true">
        Удалить аккаунт
      </button>
    </div>

    <!-- ===== Screen D: delete confirmation modal ===== -->
    <VModal :open="showDeleteModal" @close="showDeleteModal = false">
      <div class="edit-profile__modal">
        <h2 class="edit-profile__modal-title">Удалить аккаунт?</h2>
        <p class="edit-profile__modal-text">
          Вы уверены? После удаления восстановить аккаунт будет уже невозможно.
        </p>
        <div class="edit-profile__modal-actions">
          <VButton
            variant="danger"
            block
            :loading="deleting"
            @click="onConfirmDelete"
          >
            Да, удалить
          </VButton>
          <VButton
            variant="ghost"
            block
            :disabled="deleting"
            @click="showDeleteModal = false"
          >
            Нет, оставить
          </VButton>
        </div>
      </div>
    </VModal>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VInput, VTextarea, VButton, VAvatar, VModal } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { deleteMe } from '@/api/users'
import { ApiResponseError } from '@/api/client'
import type { UserUpdate } from '@/api/types'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const displayName = computed(() => {
  const u = user.value
  if (!u) return ''
  const parts = [u.first_name, u.last_name].filter(Boolean)
  return parts.length > 0 ? parts.join(' ') : 'Пользователь'
})

// E-mail is a disabled stub -- bound to a constant, never edited or sent.
const emailStub = ref('')

// Editable form, initialised from the current profile.
const form = reactive({
  firstName: user.value?.first_name ?? '',
  phone: user.value?.phone ?? '',
  bio: user.value?.bio ?? '',
})

// -- Validation (mirrors backend soft rules) --------------------------------
const PHONE_ALLOWED = /^[0-9 +()-]*$/

const phoneError = computed((): string => {
  const v = form.phone.trim()
  if (v === '') return '' // empty = clear, allowed
  if (!PHONE_ALLOWED.test(v)) {
    return 'Телефон может содержать только цифры, пробелы и + ( ) -'
  }
  const digits = (v.match(/\d/g) ?? []).length
  if (digits < 5) return 'Введите корректный номер телефона'
  if (v.length > 20) return 'Слишком длинный номер'
  return ''
})

const bioError = computed((): string =>
  form.bio.length > 2000 ? 'Не более 2000 символов' : '',
)

const hasErrors = computed(() => !!phoneError.value || !!bioError.value)

// -- Actions ----------------------------------------------------------------
function onChangePhoto(): void {
  toast.info('Опция временно недоступна')
}

const saving = ref(false)

async function onSave(): Promise<void> {
  if (saving.value) return
  if (hasErrors.value) {
    toast.error('Проверьте правильность заполнения полей')
    return
  }

  // Build a partial update with only the fields that actually changed.
  // phone/bio: send "" to clear (backend variant b). first_name: only send a
  // non-empty value (empty name is rejected by the backend min_length).
  const body: UserUpdate = {}
  const nextName = form.firstName.trim()
  if (nextName && nextName !== (user.value?.first_name ?? '')) {
    body.first_name = nextName
  }
  const nextPhone = form.phone.trim()
  if (nextPhone !== (user.value?.phone ?? '')) {
    body.phone = nextPhone
  }
  if (form.bio !== (user.value?.bio ?? '')) {
    body.bio = form.bio
  }

  if (Object.keys(body).length === 0) {
    toast.info('Нет изменений')
    return
  }

  saving.value = true
  try {
    await authStore.updateProfile(body)
    toast.info('Профиль сохранён')
    router.push({ name: 'user-profile' })
  } catch (error) {
    const message =
      error instanceof ApiResponseError
        ? error.detail || 'Не удалось сохранить профиль'
        : 'Не удалось сохранить профиль'
    toast.error(message)
  } finally {
    saving.value = false
  }
}

// -- Delete (Screen D) ------------------------------------------------------
const showDeleteModal = ref(false)
const deleting = ref(false)

async function onConfirmDelete(): Promise<void> {
  if (deleting.value) return
  deleting.value = true
  try {
    await deleteMe()
    // Reuse the standard logout flow: closes the Mini App in Telegram /
    // clears the session in standalone. On next login the user re-onboards.
    await authStore.logout()
    router.replace({ path: '/' })
  } catch (error) {
    deleting.value = false
    showDeleteModal.value = false
    const message =
      error instanceof ApiResponseError
        ? error.detail || 'Не удалось удалить аккаунт'
        : 'Не удалось удалить аккаунт'
    toast.error(message)
  }
}
</script>

<style scoped>
.edit-profile {
  display: flex;
  flex-direction: column;
  margin: calc(-1 * var(--space-4));
}

.edit-profile__content {
  padding: 0 var(--space-4) var(--space-8);
}

.edit-profile__avatar-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) 0 var(--space-6);
}

.edit-profile__change-photo {
  background: transparent;
  border: none;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-primary);
  cursor: pointer;
}

.edit-profile__field-error {
  margin: calc(-1 * var(--space-3)) 0 var(--space-4);
  font-size: var(--text-xs);
  color: var(--velo-error);
}

.edit-profile__delete {
  display: block;
  width: 100%;
  margin-top: var(--space-5);
  padding: var(--space-3);
  background: transparent;
  border: none;
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-error);
  cursor: pointer;
}

/* -- Delete modal -- */
.edit-profile__modal {
  text-align: center;
}

.edit-profile__modal-title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0 0 var(--space-3);
}

.edit-profile__modal-text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-secondary);
  margin: 0 0 var(--space-6);
}

.edit-profile__modal-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
</style>
