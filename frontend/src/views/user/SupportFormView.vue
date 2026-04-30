<!--
  VELO Frontend — SupportFormView (S2-S3 SPEEDRUN MEGA-2 §C48)

  Subject + message form. Mock submit per BACKEND § A.6. Toast on send.
-->

<template>
  <div class="sup">
    <header class="sup__header">
      <button
        type="button"
        class="sup__back"
        aria-label="Назад"
        @click="router.back()"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="sup__title">
        Поддержка
      </h1>
    </header>

    <article class="sup__hero">
      <span class="sup__hero-icon">
        <IconQuestion :size="36" />
      </span>
      <h2 class="sup__hero-title">
        Как мы можем помочь?
      </h2>
      <p class="sup__hero-body">
        Обычно отвечаем в течение 24 часов.
      </p>
    </article>

    <form
      class="sup__form"
      @submit.prevent="onSubmit"
    >
      <h3 class="sup__field-label">
        Тема
      </h3>
      <input
        v-model="subject"
        type="text"
        class="sup__input"
        placeholder="О чём ваш вопрос?"
      >

      <h3 class="sup__field-label">
        Сообщение
      </h3>
      <textarea
        v-model="message"
        class="sup__textarea"
        rows="8"
        placeholder="Опишите вашу проблему или вопрос..."
      />

      <button
        type="submit"
        class="sup__submit"
        :disabled="!canSubmit"
      >
        Отправить
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { IconArrowBack, IconQuestion } from '@/components/icons'

const router = useRouter()
const toast = useToast()

const subject = ref('')
const message = ref('')

const canSubmit = computed(
  () => subject.value.trim().length > 0 && message.value.trim().length > 0,
)

function onSubmit(): void {
  if (!canSubmit.value) return
  // BACKEND § A.6 — support endpoint not landed; mock send + toast.
  toast.success('Сообщение отправлено')
  subject.value = ''
  message.value = ''
  router.back()
}
</script>

<style scoped>
.sup {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.sup__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.sup__back {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--text-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sup__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.sup__hero {
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-6) var(--space-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  text-align: center;
}

.sup__hero-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--surface-steel-alpha-15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}

.sup__hero-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.sup__hero-body {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.sup__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.sup__field-label {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  margin: var(--space-2) 0 0;
  color: var(--text-primary);
  font-weight: 400;
}

.sup__input,
.sup__textarea {
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  color: var(--text-primary);
  font-size: var(--text-base);
}

.sup__textarea {
  resize: vertical;
  min-height: 160px;
}

.sup__submit {
  margin-top: var(--space-3);
  padding: var(--space-3);
  background: var(--steel-button);
  color: white;
  border: 0;
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 500;
  cursor: pointer;
}

.sup__submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
