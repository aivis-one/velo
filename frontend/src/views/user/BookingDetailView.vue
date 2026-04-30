<!--
  VELO Frontend -- BookingDetailView (S2 P08 C29 — skin 18)

  Compact detail view for non-immediate bookings: practice card + status +
  master + Zoom info + cancel CTA.

  Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="bd">
    <VHeader
      title="Бронирование"
      show-back
      @back="$router.back()"
    />

    <div
      v-if="loading"
      class="bd__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="!booking"
      class="bd__error"
    >
      Бронирование не найдено
    </div>
    <div
      v-else
      class="bd__body"
    >
      <section class="bd__head">
        <component
          :is="iconFor(booking.practice.practice_type)"
          class="bd__icon"
          :size="32"
        />
        <h1>{{ booking.practice.title }}</h1>
        <div class="bd__meta">
          <span>{{ formatDateShort(booking.practice.scheduled_at, booking.practice.timezone) }}</span>
          <span>·</span>
          <span>{{ formatDuration(booking.practice.duration_minutes) }}</span>
        </div>
      </section>

      <div class="bd__row">
        <span class="bd__label">Статус</span>
        <span class="bd__chip">{{ chip.label }}</span>
      </div>

      <section class="bd__section">
        <h3>Мастер</h3>
        <MasterCardSummary
          :name="booking.practice.master_name ?? 'Мастер'"
          :master-id="booking.practice.master_id"
          verified
        />
      </section>

      <section class="bd__zoom">
        <h3>ZOOM</h3>
        <p>Ссылка будет отправлена за 10 минут до начала практики.</p>
      </section>

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
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VButton } from '@/components/ui'
import { VHeader } from '@/components/layout'
import MasterCardSummary from '@/components/shared/MasterCardSummary.vue'
import { PRACTICE_TYPE_ICON } from '@/utils/displayHelpers'
import { formatDateShort, formatDuration } from '@/utils/format'
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
  return store.bookings.find((b) => b.id === id) ?? null
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
.bd {
  display: flex;
  flex-direction: column;
}

.bd__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.bd__loader,
.bd__error {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.bd__head {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.bd__head h1 {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.bd__icon {
  color: var(--text-primary);
}

.bd__meta {
  display: flex;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-family: var(--font-body);
}

.bd__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.bd__label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.bd__chip {
  background: var(--surface-teal-alpha-30, var(--surface-steel-alpha-15));
  color: var(--text-primary);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-family: var(--font-body);
}

.bd__section h3,
.bd__zoom h3 {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0 0 var(--space-2);
  font-weight: 400;
  color: var(--text-primary);
}

.bd__zoom p {
  margin: 0;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}
</style>
