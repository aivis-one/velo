<!--
  VELO Frontend -- PracticeLiveView (screen 14, Practice-Live)

  Full-screen view for a practice that is currently in progress (LIVE).
  Header has a back arrow (VHeader show-back) so the user can return to the
  previous screen without leaving the practice. "Покинуть практику" remains
  the explicit way to leave (sets left_at + back to dashboard).

  Layout (top -> bottom):
    - Video placeholder (no real video in MVP; Zoom is external)
    - Info card: title + master + "В эфире" badge
    - Actions:
        "Войти"            -- join (sets joined_at) + open Zoom link
        "Check-in"         -- go to the check-in form
        "Покинуть практику" -- leave (sets left_at) + back to dashboard

  Data:
    - practicesStore.fetchPractice(practiceId) -> zoom_link, title, master_name, status
    - bookingsStore -> the user's booking for this practice (booking.id, joined_at)

  Backend (Phase 5.4, ready):
    POST /bookings/{id}/join   -- confirmed + scheduled/live, 409 if already joined
    POST /bookings/{id}/leave  -- requires joined_at, 400 if not joined

  Security (AUDIT-0520-02): the Zoom link is only opened when it starts with
  "https://". Otherwise "Войти" is disabled.

  Route: /user/practice-live/:practiceId
-->

<template>
  <div class="live">
    <!-- Back arrow -> dashboard. Using router.back() returned the user into
         the check-in success/form screen, creating a check-in <-> live loop. -->
    <VHeader show-back @back="goBack" />

    <!-- Themed direction placeholder in place of a real video stream
         (no real video in MVP; Zoom is external). -->
    <PracticePlaceholder
      class="live__video"
      :direction="practice?.direction"
      :title="practice?.title"
    />

    <!-- Info card -->
    <div class="live__info">
      <h2 class="live__title">{{ practice?.title ?? 'Практика' }}</h2>
      <p class="live__master">с {{ practice?.master_name ?? 'Мастером' }}</p>
      <span class="live__badge">
        <span class="live__badge-dot" />
        В эфире
      </span>
    </div>

    <!-- Actions -->
    <div class="live__actions">
      <VButton
        variant="primary"
        size="lg"
        block
        :disabled="!canJoin || joining"
        :loading="joining"
        @click="onEnter"
      >
        Войти
      </VButton>

      <!-- One check-in per practice: once done, the button locks and shows
           why (so it does not read as a random disabled control). -->
      <VButton
        variant="secondary"
        size="lg"
        block
        :disabled="alreadyCheckedIn"
        @click="onCheckin"
      >
        <template v-if="alreadyCheckedIn">
          <IconCheck :size="16" /> Check-in сделан
        </template>
        <template v-else>Check-in</template>
      </VButton>

      <VButton
        variant="danger"
        size="lg"
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePracticesStore } from '@/stores/practices'
import { useBookingsStore } from '@/stores/bookings'
import { useToast } from '@/composables/useToast'
import { platform } from '@/platform'
import { VButton } from '@/components/ui'
import { VHeader } from '@/components/layout'
import { IconCheck } from '@/components/icons'
import PracticePlaceholder from '@/components/shared/PracticePlaceholder.vue'

const route = useRoute()
const router = useRouter()
const practicesStore = usePracticesStore()
const bookingsStore = useBookingsStore()
const toast = useToast()

const practiceId = route.params.practiceId as string

const joining = ref(false)
const leaving = ref(false)

const practice = computed(() => practicesStore.selected)

/** The current user's booking for this practice (any active-ish status). */
const myBooking = computed(() =>
  bookingsStore.bookings.find(
    (b) => b.practice_id === practiceId && b.status !== 'cancelled',
  ),
)

/** One check-in per practice: once the booking has it, the button locks. */
const alreadyCheckedIn = computed(() => !!myBooking.value?.has_checkin)

/** A Zoom link is usable only if it is an https URL (AUDIT-0520-02). */
const hasValidZoom = computed(
  () => !!practice.value?.zoom_link?.startsWith('https://'),
)

/** "Войти" is enabled only with a booking and a valid Zoom link. */
const canJoin = computed(() => !!myBooking.value && hasValidZoom.value)

// -- Actions --

/**
 * "Войти": check in (if not joined yet) and open the Zoom link.
 * A 409 "Already joined" is treated as a no-op -- we still open Zoom.
 */
async function onEnter(): Promise<void> {
  if (!practice.value?.zoom_link || !hasValidZoom.value) return
  if (joining.value) return

  joining.value = true
  try {
    const booking = myBooking.value
    // Only call join if we have a booking that has not joined yet.
    if (booking && booking.joined_at === null) {
      const result = await bookingsStore.joinBooking(booking.id)
      // Ignore "already joined" -- opening Zoom is still the right action.
      if (!result.ok && !result.error.toLowerCase().includes('already')) {
        toast.error(result.error)
      }
    }
    try { platform.hapticFeedback('medium') } catch { /* silent fallback */ }
    platform.openLink(practice.value.zoom_link)
  } finally {
    joining.value = false
  }
}

function onCheckin(): void {
  if (alreadyCheckedIn.value) return
  router.push({ name: 'user-checkin', params: { practiceId } })
}

/** Back arrow -> dashboard (breaks the check-in <-> live loop). */
function goBack(): void {
  router.push({ name: 'user-dashboard' })
}

/**
 * "Покинуть практику": always returns to the dashboard. We only call the
 * leave API if the user had actually joined (otherwise the backend returns
 * 400 "Cannot leave without joining first").
 */
async function onLeave(): Promise<void> {
  if (leaving.value) return

  leaving.value = true
  try {
    const booking = myBooking.value
    if (booking && booking.joined_at !== null && booking.left_at === null) {
      const result = await bookingsStore.leaveBooking(booking.id)
      if (!result.ok) toast.error(result.error)
    }
  } finally {
    leaving.value = false
    router.push({ name: 'user-dashboard' })
  }
}

onMounted(() => {
  if (practicesStore.selected?.id !== practiceId) {
    practicesStore.fetchPractice(practiceId)
  }
  // Needed to resolve the user's booking id for join/leave.
  bookingsStore.fetchMyBookings()
})
</script>

<style scoped>
.live {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  padding: var(--space-6) var(--space-4);
  min-height: 100%;
}

/* Direction placeholder: PracticePlaceholder already carries the
   336x199 aspect, glass-blue background, white border and glow shadow.
   Layout-only overrides here. */
.live__video {
  align-self: center;
}

/* Info card */
.live__info {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-2);
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.live__title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.live__master {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--velo-text-secondary);
}

/* "В эфире" badge */
.live__badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-xl);
  background: var(--velo-glass-teal-30);
  border: 1px solid var(--velo-teal-400);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-teal-700);
}

.live__badge-dot {
  width: 7px;
  height: 7px;
  border-radius: var(--radius-full);
  background: var(--velo-teal-400);
}

/* Actions */
.live__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-top: auto;
}
</style>
