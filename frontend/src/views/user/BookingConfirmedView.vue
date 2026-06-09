<!--
  VELO Frontend -- BookingConfirmedView (Calendar iteration, frame 5)

  Full-screen confirmation shown AFTER a successful booking. Figma 541:2120:
    - Success card: celebration icon (IconSuccess) in a teal circle,
      "Практика забронирована!", "Ссылка на Zoom появится за 10 минут до
      начала." (static line).
    - "Ваш запрос мастеру (по желанию)" textarea + teal info banner.
      VISUAL ONLY: "Отправить запрос" is a stub (TD-ASK-MASTER) -- questions
      to a master are a separate cross-cutting feature (practice-bound or
      general, routed to the master's Telegram bot with replies back to the
      user). Until that exists, the field accepts text but goes nowhere and
      the button shows a toast.
    - No in-page navigation buttons: the bottom tab bar handles it (this route
      highlights the Calendar tab via meta.activeTab).

  Reached via router.push from PracticeDetailView.onPurchased. The screen is
  self-contained: it loads the practice by id (survives reload / deep link).

  Route: /user/booking-confirmed/:practiceId (name: user-booking-confirmed)
-->

<template>
  <div class="booking-confirmed">
    <!-- Loading -->
    <div v-if="store.selectedLoading && !practice" class="booking-confirmed__loader">
      <VLoader size="lg" />
    </div>

    <!-- Error / not found -->
    <VEmptyState
      v-else-if="store.selectedError || !practice"
      icon="warning"
      title="Практика не найдена"
      :description="store.selectedError ?? 'Не удалось загрузить практику'"
    >
      <VButton size="sm" @click="goToDashboard">На главную</VButton>
    </VEmptyState>

    <!-- Content -->
    <div v-else class="booking-confirmed__content">
      <!-- Success card -->
      <VCard class="booking-confirmed__card" padding="none">
        <span class="booking-confirmed__icon">
          <IconSuccess :size="56" />
        </span>
        <h1 class="booking-confirmed__title">Практика забронирована!</h1>
        <p class="booking-confirmed__text">
          Ссылка на Zoom появится за 10 минут до начала.
        </p>
      </VCard>

      <!-- Ask-master request (VISUAL ONLY, TD-ASK-MASTER) -->
      <div class="booking-confirmed__ask">
        <VTextarea
          v-model="masterRequest"
          label="Ваш запрос мастеру (по желанию)"
          placeholder="Концентрация, настрой на работу"
          :rows="2"
        />
        <Banner
          variant="info"
          body="Оставляя запрос, вы помогаете мастеру подготовить практику с учётом ваших пожеланий"
        >
          <template #icon><IconSupport :size="28" /></template>
        </Banner>
        <VButton variant="secondary" size="lg" block @click="onSendRequest">
          Отправить запрос
        </VButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePracticesStore } from '@/stores/practices'
import { useToast } from '@/composables/useToast'
import { VLoader, VEmptyState, VButton, VTextarea, VCard } from '@/components/ui'
import Banner from '@/components/shared/Banner.vue'
import { IconSuccess, IconSupport } from '@/components/icons'

const route = useRoute()
const router = useRouter()
const store = usePracticesStore()
const toast = useToast()

const practice = computed(() => store.selected)

// Local-only request text. Goes nowhere yet (TD-ASK-MASTER).
const masterRequest = ref('')

function onSendRequest(): void {
  // Questions-to-master is a separate feature with its own backend and
  // Telegram-bot routing. Stubbed for now (TD-ASK-MASTER).
  toast.info('Вопросы мастеру -- скоро')
}

function goToDashboard(): void {
  router.push({ name: 'user-dashboard' })
}

onMounted(() => {
  const id = route.params.practiceId as string
  // Load the practice so the title can be shown. Self-contained: works on
  // direct navigation / reload, not only via the booking redirect.
  store.fetchPractice(id)
})
</script>

<style scoped>
.booking-confirmed {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.booking-confirmed__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

.booking-confirmed__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  /* Horizontal rail comes from MobileLayout (--velo-rail-pad-x); vertical only
     here so content sits on the single 24px rail (no double inset). */
  padding: var(--space-4) 0;
}

/* Success card */
.booking-confirmed__card {
  padding: var(--space-5) var(--space-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-3);
}

.booking-confirmed__icon {
  width: 88px;
  height: 88px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}

.booking-confirmed__title {
  font-family: var(--font-body);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin: 0;
}

.booking-confirmed__text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* Ask-master block */
.booking-confirmed__ask {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* Field + info banner are now the DS VTextarea + Banner components (own styles). */
</style>
