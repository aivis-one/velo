<!--
  VELO Frontend -- AdminDashboardView (Admin DS rebuild 2026-06-14)

  Admin dashboard, rebuilt to the operator's design (SVG: ПАНЕЛЬ / 1 Dashboard).
  Rendered inside AdminShell -> AdminLayout (fog feed + 24px rail + VAdminTabBar).

  Structure (DS-first — every value is a --velo-* token / DS component):
    - Header: "Admin" + an eye/observe button (stub until its target screen lands).
    - Alert banners: masters awaiting verification (warning) + reports awaiting
      moderation (alert) — shown only when their count > 0.
    - Статистика: title + period toggle (Неделя / Месяц, user/master pattern) +
      3 VStatCard + a week stepper.
    - Выручка: amount card + "Баланс по мастерам" link.
    - Engagement: 3 VProgressRow (Check-in / Feedback / Return rate).

  STUBS (no backend yet -> roadmap for Zod; non-working taps show a toast):
    - Real: practices/masters/users counts + pending verification/moderation
      counts (the 3 stat cards + both banners + both tab badges).
    - Stub: stat deltas, revenue, engagement rates, the Неделя/Месяц period scoping
      + week stepper, the eye button, "Баланс по мастерам". Rendered, but "—" /
      visual-only / toast on tap.
-->

<template>
  <div class="admin-dashboard">
    <!-- Header (scrolls within the fog feed, like the master greeting) -->
    <div class="admin-dashboard__header">
      <h1 class="admin-dashboard__title">Admin</h1>
      <button class="admin-dashboard__eye" aria-label="Просмотр" @click="stub">
        <IconView :size="22" />
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="admin-dashboard__loader">
      <VLoader size="lg" />
    </div>

    <template v-else>
      <!-- Alert banners -->
      <Banner
        v-if="pendingVerifications > 0"
        variant="warning"
        :title="verificationTitle"
        clickable
        @click="router.push({ name: 'admin-masters' })"
      >
        <template #icon><IconPending :size="28" /></template>
      </Banner>
      <Banner
        v-if="pendingModeration > 0"
        variant="alert"
        :title="moderationTitle"
        clickable
        @click="router.push({ name: 'admin-reports' })"
      >
        <template #icon><IconWarning :size="28" /></template>
      </Banner>

      <!-- Статистика: title + period toggle -->
      <div class="admin-dashboard__section">
        <span class="admin-dashboard__section-title">Статистика</span>
        <div class="admin-dashboard__period" role="tablist" aria-label="Период статистики">
          <button
            class="admin-dashboard__period-btn"
            :class="{ 'admin-dashboard__period-btn--active': period === 'week' }"
            @click="period = 'week'"
          >
            Неделя
          </button>
          <button
            class="admin-dashboard__period-btn"
            :class="{ 'admin-dashboard__period-btn--active': period === 'month' }"
            @click="period = 'month'"
          >
            Месяц
          </button>
        </div>
      </div>

      <div class="admin-dashboard__stats">
        <VStatCard :value="practicesValue" label="Практик" :delta="practicesDelta" />
        <VStatCard :value="mastersValue" label="Мастеров" :delta="mastersDelta" />
        <VStatCard :value="participantsValue" label="Участников" :delta="participantsDelta" />
      </div>

      <!-- Week stepper (visual-only until a period-scoped stats API exists) -->
      <div class="admin-dashboard__week">
        <button
          class="admin-dashboard__week-nav admin-dashboard__week-nav--prev"
          aria-label="Предыдущая неделя"
          @click="stub"
        >
          <IconArrowRight :size="20" />
        </button>
        <span class="admin-dashboard__week-range">{{ weekRange }}</span>
        <button class="admin-dashboard__week-nav" aria-label="Следующая неделя" @click="stub">
          <IconArrowRight :size="20" />
        </button>
      </div>

      <!-- Выручка -->
      <div class="admin-dashboard__section">
        <span class="admin-dashboard__section-title">Выручка</span>
      </div>
      <VCard class="admin-dashboard__revenue">
        <div class="admin-dashboard__revenue-amount">{{ revenueValue }}</div>
        <div v-if="revenueDelta" class="admin-dashboard__revenue-delta">{{ revenueDelta }}</div>
      </VCard>
      <button class="admin-dashboard__morelink" @click="router.push({ name: 'admin-revenue' })">
        <span>Баланс по мастерам</span>
        <IconArrowRight :size="20" />
      </button>

      <!-- Engagement -->
      <div class="admin-dashboard__section">
        <span class="admin-dashboard__section-title">Engagement</span>
      </div>
      <VCard class="admin-dashboard__engagement">
        <VProgressRow label="Check-in rate" :value="checkinRate" clickable @click="router.push({ name: 'admin-checkin-rate' })" />
        <VProgressRow label="Feedback rate" :value="feedbackRate" clickable @click="router.push({ name: 'admin-feedback-rate' })" />
        <VProgressRow label="Return rate" :value="returnRate" clickable @click="router.push({ name: 'admin-return-rate' })" />
      </VCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VStatCard, VCard, VLoader, VProgressRow } from '@/components/ui'
import Banner from '@/components/shared/Banner.vue'
import { IconView, IconPending, IconWarning, IconArrowRight } from '@/components/icons'
import { useToast } from '@/composables/useToast'
import { useAdminStore } from '@/stores/admin'

const router = useRouter()
const toast = useToast()
const adminStore = useAdminStore()

// Period toggle. Visual-only until a period-scoped stats API exists (roadmap).
const period = ref<'week' | 'month'>('week')

const loading = computed((): boolean => adminStore.loading && !adminStore.stats)

const pendingVerifications = computed((): number => adminStore.pendingVerifications)
const pendingModeration = computed((): number => adminStore.pendingModeration)

// Russian plural picker: [one, few, many].
function plural(n: number, forms: [string, string, string]): string {
  const m10 = n % 10
  const m100 = n % 100
  if (m10 === 1 && m100 !== 11) return forms[0]
  if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return forms[1]
  return forms[2]
}

const verificationTitle = computed(
  (): string =>
    `${pendingVerifications.value} ${plural(pendingVerifications.value, ['мастер', 'мастера', 'мастеров'])} на верификации`,
)
const moderationTitle = computed(
  (): string =>
    `${pendingModeration.value} ${plural(pendingModeration.value, ['обращение', 'обращения', 'обращений'])} на модерации`,
)

// =========================================================================
// Stats. The 3 counts are real (GET /admin/stats). Deltas have no backend yet
// -> empty (VStatCard hides the trend line when delta is empty). Roadmap: Zod.
// =========================================================================
const practicesValue = computed((): string => String(adminStore.stats?.practices_count ?? '—'))
const mastersValue = computed((): string => String(adminStore.stats?.masters_count ?? '—'))
const participantsValue = computed((): string => String(adminStore.stats?.users_count ?? '—'))
const practicesDelta = computed((): string => '')
const mastersDelta = computed((): string => '')
const participantsDelta = computed((): string => '')

// Revenue + engagement: no API yet -> stub. Revenue "—"; engagement rows render an
// empty track + "—". Bound through computeds so wiring the future API is one line.
const revenueValue = computed((): string => '—')
const revenueDelta = computed((): string => '')
const checkinRate = computed<number | null>((): number | null => null)
const feedbackRate = computed<number | null>((): number | null => null)
const returnRate = computed<number | null>((): number | null => null)

// Current ISO week range (Mon–Sun), client-side. The period toggle + week steps
// are visual-only until a period-scoped stats API exists (roadmap for Zod).
const weekRange = computed((): string => {
  const now = new Date()
  const dow = (now.getDay() + 6) % 7 // Mon = 0
  const mon = new Date(now)
  mon.setDate(now.getDate() - dow)
  const sun = new Date(mon)
  sun.setDate(mon.getDate() + 6)
  const fmt = (d: Date): string =>
    d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }).replace('.', '')
  return `${fmt(mon)} - ${fmt(sun)}`
})

// Stub taps (no backend / no target screen yet -> toast; build-full-design).
function stub(): void {
  toast.info('Раздел пока недоступен')
}

onMounted(() => {
  void adminStore.fetchDashboard()
})
</script>

<style scoped>
.admin-dashboard {
  /* Horizontal rail comes from AdminLayout's fog mode (--velo-rail-pad-x); the
     top/bottom clearance (under the header fade + over the tab bar) is the
     layout's too. Only the vertical rhythm between blocks lives here. */
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* -- Header -- */
.admin-dashboard__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  min-height: 44px;
}

.admin-dashboard__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.admin-dashboard__eye {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border: none;
  border-radius: var(--radius-full);
  background: var(--velo-primary);
  color: var(--velo-white);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.admin-dashboard__eye:active {
  opacity: 0.85;
}

/* -- Loader -- */
.admin-dashboard__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

/* -- Section header (+ optional period toggle) -- */
.admin-dashboard__section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.admin-dashboard__section-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

/* -- Period toggle (user/master dashboard pattern) -- */
.admin-dashboard__period {
  display: flex;
  gap: 2px;
  background: var(--velo-glass-blue-15);
  border: 1px solid var(--velo-glass-border);
  border-radius: var(--radius-xl);
  padding: 2px;
}

.admin-dashboard__period-btn {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-primary);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-xl);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.admin-dashboard__period-btn--active {
  background: var(--velo-primary);
  color: var(--velo-white);
}

/* -- Stats grid -- */
.admin-dashboard__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

/* -- Week stepper -- */
.admin-dashboard__week {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-1);
}

.admin-dashboard__week-nav {
  width: 60px;
  height: 35px;
  flex-shrink: 0;
  border: none;
  border-radius: var(--radius-xl);
  background: var(--velo-white);
  color: var(--velo-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.admin-dashboard__week-nav:active {
  opacity: 0.8;
}

/* Reuse the single arrow glyph, mirrored for "previous". */
.admin-dashboard__week-nav--prev {
  transform: scaleX(-1);
}

.admin-dashboard__week-range {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

/* -- Revenue -- */
.admin-dashboard__revenue {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.admin-dashboard__revenue-amount {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.64px;
  line-height: 1.1;
}

.admin-dashboard__revenue-delta {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-teal-600);
}

.admin-dashboard__morelink {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-2);
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  padding: 0;
}

.admin-dashboard__morelink:active {
  opacity: 0.8;
}

/* -- Engagement -- */
.admin-dashboard__engagement {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}
</style>
