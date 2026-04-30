<!--
  VELO Frontend — MyReservationsView (S2-S3 SPEEDRUN MEGA-2 §C52)

  Two sections — upcoming + past — backed by bookingsStore getters from
  MEGA-1 (#33). Status chip rendered via statusChipVariant helper.
-->

<template>
  <div class="res">
    <header class="res__header">
      <button
        type="button"
        class="res__back"
        aria-label="Назад"
        @click="router.back()"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="res__title">
        Мои бронирования
      </h1>
    </header>

    <div
      v-if="loading"
      class="res__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="!hasAny"
      class="res__empty"
    >
      У вас пока нет бронирований.
    </div>
    <div
      v-else
      class="res__body"
    >
      <section
        v-if="bookings.upcomingBookings.length"
        class="res__section"
      >
        <h3 class="res__sub">
          Предстоящие
        </h3>
        <ReservationCard
          v-for="b in bookings.upcomingBookings"
          :key="b.id"
          :booking="b"
          :chip="bookings.statusChipVariant(b)"
          @click="onOpen(b)"
        />
      </section>

      <section
        v-if="bookings.pastBookings.length"
        class="res__section"
      >
        <h3 class="res__sub">
          Прошедшие
        </h3>
        <ReservationCard
          v-for="b in bookings.pastBookings"
          :key="b.id"
          :booking="b"
          :chip="bookings.statusChipVariant(b)"
          @click="onOpen(b)"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { IconArrowBack } from '@/components/icons'
import ReservationCard from '@/components/shared/ReservationCard.vue'
import { useBookingsStore } from '@/stores/bookings'
import type { BookingWithPracticeResponse } from '@/api/types'

const router = useRouter()
const bookings = useBookingsStore()

const loading = ref(false)

const hasAny = computed(
  () =>
    bookings.upcomingBookings.length > 0 ||
    bookings.pastBookings.length > 0,
)

function onOpen(b: BookingWithPracticeResponse): void {
  if (b.status === 'confirmed') {
    const today = new Date().toISOString().slice(0, 10)
    if (b.practice.scheduled_at.slice(0, 10) === today) {
      router.push(`/user/practices/${b.practice.id}/booked`)
      return
    }
  }
  router.push(`/user/booking/${b.id}`)
}

onMounted(async () => {
  if (bookings.bookings.length === 0) {
    loading.value = true
    try {
      await bookings.fetchMyBookings()
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.res {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.res__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.res__back {
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

.res__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.res__loader,
.res__empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.res__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.res__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.res__sub {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}
</style>
