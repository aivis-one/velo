<!--
  VELO Frontend -- PracticeDetailView (S2 P08 C26 — refresh per skin 24/28)

  Practice header card -> О практике / Что подготовить accordions ->
  Master section -> Контраиндикации callout -> Стоимость row ->
  Забронировать CTA. Single component handles paid + free variants
  (decision #040: unified /purchase endpoint).

  Path Y MEDIUM. No emojis (#048).
-->

<template>
  <div class="pd">
    <VHeader
      title="Практика"
      show-back
      @back="$router.back()"
    />

    <div
      v-if="loading"
      class="pd__loader"
    >
      Загрузка…
    </div>
    <div
      v-else-if="!practice"
      class="pd__error"
    >
      Практика не найдена
    </div>
    <div
      v-else
      class="pd__body"
    >
      <section class="pd__head">
        <component
          :is="iconFor(practice.practice_type)"
          class="pd__icon"
          :size="40"
        />
        <h1 class="pd__title">
          {{ practice.title }}
        </h1>
        <div class="pd__meta">
          <span>{{ formatDateShort(practice.scheduled_at, practice.timezone) }}</span>
          <span>·</span>
          <span>{{ formatTime(practice.scheduled_at, practice.timezone) }}</span>
          <span>·</span>
          <span>{{ formatDuration(practice.duration_minutes) }}</span>
        </div>
        <div
          v-if="practice.max_participants !== null"
          class="pd__meta"
        >
          <span>{{ practice.current_participants }} / {{ practice.max_participants }} мест</span>
        </div>
      </section>

      <details
        v-if="practice.description"
        class="pd__acc"
      >
        <summary>О практике</summary>
        <p>{{ practice.description }}</p>
      </details>

      <details
        v-if="practice.what_to_prepare"
        class="pd__acc"
      >
        <summary>Что подготовить</summary>
        <p>{{ practice.what_to_prepare }}</p>
      </details>

      <section class="pd__section">
        <h3>Мастер</h3>
        <MasterCardSummary
          :name="practice.master_name ?? 'Мастер'"
          :master-id="practice.master_id"
          :methods="practice.master_methods"
          verified
        />
      </section>

      <Callout
        v-if="practice.contraindications"
        variant="amber"
        :icon="IconWarning"
        title="Противопоказания"
      >
        {{ practice.contraindications }}
      </Callout>

      <section class="pd__price">
        <span class="pd__price-label">Стоимость</span>
        <span class="pd__price-value">
          {{ practice.is_free ? 'Бесплатно' : formatMoney(practice.price_cents, practice.currency) }}
        </span>
      </section>

      <VButton
        variant="primary"
        size="md"
        block
        :loading="purchasing"
        @click="onBook"
      >
        Забронировать
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VButton } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { IconWarning } from '@/components/icons'
import MasterCardSummary from '@/components/shared/MasterCardSummary.vue'
import Callout from '@/components/shared/Callout.vue'
import { PRACTICE_TYPE_ICON } from '@/utils/displayHelpers'
import { formatMoney, formatTime, formatDateShort, formatDuration } from '@/utils/format'
import { getPractice } from '@/api/practices'
import { purchasePractice as purchaseBooking } from '@/api/bookings'
import { useToast } from '@/composables/useToast'
import { extractApiError } from '@/composables/useApiError'
import type { PracticeResponse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const practice = ref<PracticeResponse | null>(null)
const loading = ref(false)
const purchasing = ref(false)

function iconFor(t: string) {
  return PRACTICE_TYPE_ICON[t] ?? PRACTICE_TYPE_ICON.live
}

async function load(): Promise<void> {
  const id = route.params.id as string
  loading.value = true
  try {
    practice.value = await getPractice(id)
  } catch (e) {
    toast.error(extractApiError(e, 'Не удалось загрузить практику'))
  } finally {
    loading.value = false
  }
}

async function onBook(): Promise<void> {
  if (!practice.value || purchasing.value) return
  purchasing.value = true
  try {
    // Unified /purchase per decision #040 (paid + free).
    await purchaseBooking(practice.value.id)
    router.push(`/user/practices/${practice.value.id}/booking-success`)
  } catch (e) {
    toast.error(extractApiError(e, 'Не удалось забронировать'))
  } finally {
    purchasing.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.pd {
  display: flex;
  flex-direction: column;
}

.pd__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.pd__loader,
.pd__error {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

.pd__head {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.pd__icon {
  color: var(--text-primary);
}

.pd__title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.pd__meta {
  display: flex;
  gap: var(--space-1);
  flex-wrap: wrap;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-family: var(--font-body);
}

.pd__acc {
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
}

.pd__acc summary {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  cursor: pointer;
  list-style: none;
}

.pd__acc summary::-webkit-details-marker {
  display: none;
}

.pd__acc p {
  margin: var(--space-3) 0 0;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

.pd__section h3 {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0 0 var(--space-2);
  font-weight: 400;
  color: var(--text-primary);
}

.pd__price {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.pd__price-label {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.pd__price-value {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  color: var(--text-primary);
}
</style>
