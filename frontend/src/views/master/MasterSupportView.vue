<!--
  VELO Frontend -- MasterSupportView (Phase-3 Master DS, 2026-06-13)

  Support / contact form, reached from the master profile hub («Поддержка»).
  Built to SVGs «5 Support» / «5 Support 2» / «5 Support (files added)» /
  «Check-in Success» (the form's success screen).

  Flow В (operator 2026-06-13): «Отправить» shows the designed success screen
  («Сообщение отправлено!»). There is NO support backend yet, so the ticket is
  NOT actually sent — this is a stub of the designed flow (Zod wires real ticket
  intake). The honest fallback is on the form: «Или напишите: support@velo.app»
  is a real mailto: link. Attachments are captured locally but NOT uploaded
  (no storage backend).

  Stub → Zod (roadmap Screen 18): ticket intake (topic + message + attachments)
  → delivery / «личные сообщения»; file upload + storage; the «Добавить
  направление практики» topic may route to its own flow.

  Route: /master/support (name 'master-support', meta.hideTabBar — back-nav
  screen, no tab bar per the design).
-->
<template>
  <div class="support">
    <VHeader title="Поддержка" show-back @back="router.back()" />

    <!-- ===================== SUCCESS ===================== -->
    <div v-if="submitted" class="support__success">
      <div class="support__ok-circle"><IconCheck :size="46" /></div>
      <h2 class="support__ok-title">Сообщение отправлено!</h2>
      <p class="support__ok-text">Скоро свяжемся с вами в личных сообщениях</p>
      <VButton variant="primary" block class="support__ok-cta" @click="onGoHome">
        На главную
      </VButton>
    </div>

    <!-- ===================== FORM ===================== -->
    <div v-else class="support__content">
      <div class="support__hero">
        <IconSupport :size="56" class="support__hero-ic" />
        <div class="support__hero-title">Как мы можем помочь?</div>
        <div class="support__hero-sub">Обычно отвечаем в течение 24 часов</div>
      </div>

      <!-- Topic -->
      <section class="support__section">
        <h2 class="support__title">Тема</h2>
        <div class="support__card">
          <VRadioGroup v-model="topic" :options="TOPICS" />
          <div v-if="topic === 'other'" class="support__other">
            <input
              v-model="otherText"
              type="text"
              class="support__other-input"
              placeholder="Укажите ваш вариант"
            />
            <IconArrowRight :size="18" class="support__other-arrow" />
          </div>
        </div>
      </section>

      <!-- Message -->
      <section class="support__section">
        <h2 class="support__title">Сообщение</h2>
        <VTextarea
          v-model="message"
          :rows="5"
          placeholder="Опишите вашу проблему или вопрос..."
        />
      </section>

      <!-- Attachments (UI built; files captured locally, NOT uploaded — stub) -->
      <section class="support__section">
        <h2 class="support__title">Прикрепить файл</h2>
        <div class="support__upload">
          <button type="button" class="support__drop" @click="openFilePicker">
            <IconFile :size="26" />
            <span>+ Добавить файл (5MB)</span>
          </button>
          <input
            ref="fileInput"
            type="file"
            multiple
            class="support__file-input"
            @change="onFilesPicked"
          />
          <div v-if="attachments.length" class="support__thumbs">
            <button
              v-for="(file, i) in attachments"
              :key="i"
              type="button"
              class="support__thumb"
              :title="file.name"
              aria-label="Удалить файл"
              @click="removeAttachment(i)"
            >
              <IconClose :size="12" />
            </button>
          </div>
        </div>
      </section>

      <a class="support__email" :href="emailHref">Или напишите: support@velo.app</a>

      <VButton
        variant="primary"
        block
        :disabled="!canSubmit"
        class="support__submit"
        @click="onSubmit"
      >
        Отправить
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VButton, VRadioGroup, VTextarea } from '@/components/ui'
import {
  IconSupport,
  IconCheck,
  IconFile,
  IconClose,
  IconArrowRight,
} from '@/components/icons'

const router = useRouter()

// -- Topic ------------------------------------------------------------------
const TOPICS = [
  { value: 'withdrawal', label: 'Проблема с выводом' },
  { value: 'practices', label: 'Вопрос по практикам' },
  { value: 'technical', label: 'Технические проблемы' },
  { value: 'add_direction', label: 'Добавить направление практики' },
  { value: 'rejected', label: 'Вопрос по отклоненной заявке' },
  { value: 'other', label: 'Другое' },
]
const topic = ref('withdrawal')
const otherText = ref('')
const message = ref('')

// -- Attachments (captured locally only; no upload backend — see header) -----
const MAX_FILES = 5
const attachments = ref<File[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

function openFilePicker(): void {
  fileInput.value?.click()
}

function onFilesPicked(e: Event): void {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  attachments.value = [...attachments.value, ...Array.from(input.files)].slice(0, MAX_FILES)
  // Reset so picking the same file again re-triggers change.
  input.value = ''
}

function removeAttachment(i: number): void {
  attachments.value.splice(i, 1)
}

// -- Submit (flow В) --------------------------------------------------------
const emailHref = 'mailto:support@velo.app'

const canSubmit = computed(() => {
  const hasMessage = message.value.trim().length > 0
  const hasTopic = topic.value !== 'other' || otherText.value.trim().length > 0
  return hasMessage && hasTopic
})

const submitted = ref(false)

function onSubmit(): void {
  if (!canSubmit.value) return
  // Flow В: show the designed success screen. No support backend yet — the ticket
  // is NOT actually sent (stub → Zod). The real fallback channel is the mailto:
  // link above. When the backend lands, POST the topic/message/attachments here.
  submitted.value = true
}

function onGoHome(): void {
  router.push({ name: 'master-dashboard' })
}
</script>

<style scoped>
.support {
  display: flex;
  flex-direction: column;
  margin: calc(-1 * var(--space-4));
}

.support__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  padding: 0 var(--space-4) var(--space-4);
}

/* Drop VTextarea's form-stacking bottom margin inside a gap'd section. */
.support__section :deep(.v-textarea) {
  margin-bottom: 0;
}

/* -- Hero -- */
.support__hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  text-align: center;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-5);
}

.support__hero-ic {
  color: var(--velo-primary);
}

.support__hero-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  -webkit-text-stroke: 0.3px currentColor;
}

.support__hero-sub {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
}

/* -- Section -- */
.support__section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.support__title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
  -webkit-text-stroke: 0.3px currentColor;
}

/* -- Topic card -- */
.support__card {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--space-3) 18px;
}

.support__other {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-3);
  height: 40px;
  padding: 0 16px;
  border: 1.5px solid var(--velo-primary);
  border-radius: var(--radius-full);
}

.support__other-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.support__other-input::placeholder {
  color: var(--velo-text-muted);
}

.support__other-arrow {
  flex-shrink: 0;
  color: var(--velo-primary);
}

/* -- Attachments -- */
.support__upload {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: 14px;
}

.support__drop {
  width: 100%;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px dashed var(--velo-text-primary);
  border-radius: 9px;
  background: transparent;
  color: var(--velo-text-primary);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-base);
}

.support__file-input {
  display: none;
}

.support__thumbs {
  display: flex;
  gap: var(--space-2);
  margin-top: 10px;
  flex-wrap: wrap;
}

.support__thumb {
  width: 54px;
  height: 54px;
  padding: 4px;
  border-radius: 9px;
  background: var(--velo-glass-blue-15);
  border: 1px solid var(--velo-border-light);
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  color: var(--velo-text-secondary);
  cursor: pointer;
  flex-shrink: 0;
}

/* -- Email fallback + submit -- */
.support__email {
  text-align: center;
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  text-decoration: none;
}

.support__submit {
  margin-top: var(--space-1);
}

/* -- Success -- */
.support__success {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: var(--space-3);
  min-height: 70vh;
  padding: 0 var(--space-4) var(--space-4);
}

.support__ok-circle {
  width: 93px;
  height: 93px;
  border-radius: 50%;
  background: var(--velo-glass-teal-30);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--velo-success);
}

.support__ok-title {
  font-family: var(--font-body);
  font-size: 28px;
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: var(--space-2) 0 0;
  -webkit-text-stroke: 0.3px currentColor;
}

.support__ok-text {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  line-height: 1.35;
  margin: 0;
}

.support__ok-cta {
  align-self: stretch;
  margin-top: var(--space-5);
}
</style>
