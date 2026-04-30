<!--
  VELO Frontend -- PracticeLiveView (S2 P08 C31 — skin 14)

  Active-practice screen. NO BackHeader (intentional: no escape from active
  practice except via buttons). Video placeholder rect + practice card +
  three CTAs (Войти Zoom / Check-in / Покинуть практику).

  No bookings.leave endpoint (per scout §S9 anomaly) — uses cancelBooking
  for "Покинуть практику". BACKLOG entry surfaced for backend dedicated
  /bookings/{id}/leave endpoint with mid-practice exit semantics.

  Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="pl">
    <div class="pl__video">
      <VeloLogo :size="80" />
    </div>

    <div
      v-if="loading"
      class="pl__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="practice"
      class="pl__card"
    >
      <h1>{{ practice.title }}</h1>
      <p>с {{ practice.master_name ?? 'Мастером' }}</p>
      <span class="pl__live">
        <span class="pl__dot" />
        В эфире
      </span>
    </div>

    <div class="pl__cta">
      <VButton
        variant="primary"
        size="md"
        block
        :disabled="!practice?.zoom_link"
        @click="onEnterZoom"
      >
        Войти
      </VButton>
      <VButton
        variant="ghost"
        size="md"
        block
        @click="onCheckin"
      >
        Check-in
      </VButton>
      <VButton
        variant="danger"
        size="md"
        block
        :loading="leaving"
        @click="onLeave"
      >
        Покинуть практику
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VButton, VeloLogo } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useBookingsStore } from '@/stores/bookings'
import { getPractice } from '@/api/practices'
import { extractApiError } from '@/composables/useApiError'
import type { PracticeResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const bookings = useBookingsStore()

const practice = ref<PracticeResponse | null>(null)
const loading = ref(false)
const leaving = ref(false)

async function load(): Promise<void> {
  const id = route.params.practiceId as string
  loading.value = true
  try {
    practice.value = await getPractice(id)
  } catch (e) {
    toast.error(extractApiError(e, 'Не удалось загрузить практику'))
  } finally {
    loading.value = false
  }
}

function onEnterZoom(): void {
  if (practice.value?.zoom_link) {
    window.open(practice.value.zoom_link, '_blank', 'noopener,noreferrer')
  } else {
    toast.info('Ссылка ещё не пришла')
  }
}

function onCheckin(): void {
  // Mid-practice check-in re-opens the form (decision #035 — upsert pattern).
  if (practice.value) {
    router.push(`/user/practices/${practice.value.id}/checkin`)
  }
}

const myBooking = computed(() => {
  const id = route.params.practiceId as string
  return bookings.bookings.find((b) => b.practice.id === id) ?? null
})

async function onLeave(): Promise<void> {
  if (!myBooking.value) {
    router.push('/user/dashboard')
    return
  }
  if (!window.confirm('Покинуть практику?')) return
  leaving.value = true
  // No backend /bookings/{id}/leave endpoint yet (scout §S9 anomaly);
  // cancelBooking is the closest UX-equivalent for v1.
  const result = await bookings.cancelBooking(myBooking.value.id)
  leaving.value = false
  if (result.ok) {
    router.push('/user/dashboard')
  } else {
    toast.error(result.error)
  }
}

onMounted(async () => {
  await load()
  if (bookings.bookings.length === 0) {
    bookings.fetchMyBookings()
  }
})
</script>

<style scoped>
.pl {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
  min-height: 100vh;
  min-height: 100dvh;
}

.pl__video {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 16 / 10;
  background: var(--steel-button);
  border-radius: var(--radius-lg);
  color: white;
}

.pl__loader,
.pl__card {
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.pl__loader {
  text-align: center;
  color: var(--text-secondary);
}

.pl__card h1 {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.pl__card p {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.pl__live {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-primary);
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
  padding: 2px 10px;
  border-radius: var(--radius-full);
  align-self: flex-start;
}

.pl__dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--teal-primary, var(--steel-button));
}

.pl__cta {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-top: auto;
}
</style>
