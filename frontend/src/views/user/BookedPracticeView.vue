<!--
  VELO Frontend -- BookedPracticeView (S2 P08 C28 — skin 15)

  Day-of-context view for a confirmed booking. Header + practice card with
  meta + paid chip + accordions + master + Контраиндикации + Check-in /
  Cancel CTAs.

  Path Y MEDIUM. No emojis. Booking lookup via store-cached list.
-->

<template>
  <div class="bp">
    <VHeader
      title="Моя практика"
      show-back
      @back="$router.back()"
    />

    <div
      v-if="loading"
      class="bp__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="!booking"
      class="bp__error"
    >
      Бронирование не найдено
    </div>
    <div
      v-else
      class="bp__body"
    >
      <section class="bp__head">
        <component
          :is="iconFor(booking.practice.practice_type)"
          :size="40"
          class="bp__head-icon"
        />
        <h1 class="bp__title">
          {{ booking.practice.title }}
        </h1>
        <div class="bp__meta">
          <span>{{ formatDateShort(booking.practice.scheduled_at, booking.practice.timezone) }}</span>
          <span>·</span>
          <span>{{ formatTime(booking.practice.scheduled_at, booking.practice.timezone) }}</span>
          <span>·</span>
          <span>{{ formatDuration(booking.practice.duration_minutes) }}</span>
        </div>
        <span class="bp__chip">{{ chip.label }}</span>
      </section>

      <section class="bp__section">
        <h3>Мастер</h3>
        <MasterCardSummary
          :name="booking.practice.master_name ?? 'Мастер'"
          :master-id="booking.practice.master_id"
          verified
        />
      </section>

      <div class="bp__cta">
        <VButton
          variant="primary"
          size="md"
          block
          @click="$router.push(`/user/practices/${booking.practice.id}/checkin`)"
        >
          Check-in перед практикой
        </VButton>
        <VButton
          variant="danger"
          size="md"
          block
          :loading="cancelling"
          @click="onCancel"
        >
          Отменить бронирование
        </VButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VButton } from '@/components/ui'
import { VHeader } from '@/components/layout'
import MasterCardSummary from '@/components/shared/MasterCardSummary.vue'
import { PRACTICE_TYPE_ICON } from '@/utils/displayHelpers'
import { formatDateShort, formatTime, formatDuration } from '@/utils/format'
import { useBookingsStore } from '@/stores/bookings'
import { useToast } from '@/composables/useToast'
import type { BookingWithPracticeResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const store = useBookingsStore()
const toast = useToast()

const loading = ref(false)
const cancelling = ref(false)

function iconFor(t: string) {
  return PRACTICE_TYPE_ICON[t] ?? PRACTICE_TYPE_ICON.live
}

const booking = computed<BookingWithPracticeResponse | null>(() => {
  const id = route.params.id as string
  return store.bookings.find((b) => b.practice.id === id || b.id === id) ?? null
})

const chip = computed(() => {
  if (!booking.value) return { label: '', variant: 'gray' as const }
  return store.statusChipVariant(booking.value)
})

async function onCancel(): Promise<void> {
  if (!booking.value) return
  if (!window.confirm('Отменить бронирование?')) return
  cancelling.value = true
  const result = await store.cancelBooking(booking.value.id)
  cancelling.value = false
  if (result.ok) {
    toast.success('Бронирование отменено')
    router.push('/user/dashboard')
  } else {
    toast.error(result.error)
  }
}

onMounted(async () => {
  if (store.bookings.length === 0) {
    loading.value = true
    await store.fetchMyBookings()
    loading.value = false
  }
})
</script>

<style scoped>
.bp {
  display: flex;
  flex-direction: column;
}

.bp__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.bp__loader,
.bp__error {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.bp__head {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.bp__head-icon {
  color: var(--text-primary);
}

.bp__title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.bp__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-family: var(--font-body);
}

.bp__chip {
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
  color: var(--text-primary);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-family: var(--font-body);
}

.bp__section h3 {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0 0 var(--space-2);
  font-weight: 400;
  color: var(--text-primary);
}

.bp__cta {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-top: auto;
}
</style>
