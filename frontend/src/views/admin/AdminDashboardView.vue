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

  DATA SOURCES:
    - Stat cards (Практик/Мастеров/Участников) + percent deltas + revenue come
      from the period-scoped /admin/stats/overview (E7), refetched on the
      Неделя/Месяц toggle and the ← / → period stepper (offset).
    - Alert banners + tab badges come from /admin/stats (cumulative pending
      counts) via adminStore.fetchDashboard.
    - Engagement rates (Check-in/Feedback/Return) still use the per-metric
      endpoints here; they are rewired to period+offset in a follow-up.
-->

<template>
  <div class="admin-dashboard">
    <!-- Header (scrolls within the fog feed, like the master greeting) -->
    <div class="admin-dashboard__header">
      <h1 class="admin-dashboard__title">Admin</h1>
      <button
        class="admin-dashboard__eye"
        aria-label="Профиль"
        @click="router.push({ name: 'admin-profile' })"
      >
        <IconProfile :size="22" />
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
            @click="selectPeriod('week')"
          >
            Неделя
          </button>
          <button
            class="admin-dashboard__period-btn"
            :class="{ 'admin-dashboard__period-btn--active': period === 'month' }"
            @click="selectPeriod('month')"
          >
            Месяц
          </button>
        </div>
      </div>

      <div class="admin-dashboard__stats">
        <VStatCard
          :value="practicesValue"
          label="Практик"
          :delta="practicesDelta"
          :delta-tone="practicesDeltaTone"
          clickable
          @click="router.push({ name: 'admin-practices' })"
        />
        <VStatCard
          :value="mastersValue"
          label="Мастеров"
          :delta="mastersDelta"
          :delta-tone="mastersDeltaTone"
          clickable
          @click="router.push({ name: 'admin-masters' })"
        />
        <VStatCard
          :value="participantsValue"
          label="Участников"
          :delta="participantsDelta"
          :delta-tone="participantsDeltaTone"
          clickable
          @click="router.push({ name: 'admin-participants' })"
        />
      </div>

      <!-- Period stepper: ← / → over the navigated week/month (D3) -->
      <div class="admin-dashboard__week">
        <button
          class="admin-dashboard__week-nav admin-dashboard__week-nav--prev"
          aria-label="Предыдущий период"
          @click="stepPrev"
        >
          <IconArrowRight :size="20" />
        </button>
        <span class="admin-dashboard__week-range">{{ periodRange }}</span>
        <button
          class="admin-dashboard__week-nav"
          aria-label="Следующий период"
          :disabled="!canStepNext"
          @click="stepNext"
        >
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
      <VListRow
        title="Выплаты"
        subtitle="Запросы мастеров на вывод"
        clickable
        @click="router.push({ name: 'admin-withdrawals' })"
      >
        <template #trailing><IconArrowRight :size="20" /></template>
      </VListRow>

      <!-- Engagement -->
      <div class="admin-dashboard__section">
        <span class="admin-dashboard__section-title">Engagement</span>
      </div>
      <VCard class="admin-dashboard__engagement">
        <VProgressRow
          label="Check-in rate"
          :value="checkinRate"
          clickable
          @click="router.push({ name: 'admin-checkin-rate' })"
        />
        <VProgressRow
          label="Feedback rate"
          :value="feedbackRate"
          clickable
          @click="router.push({ name: 'admin-feedback-rate' })"
        />
        <VProgressRow
          label="Return rate"
          :value="returnRate"
          clickable
          @click="router.push({ name: 'admin-return-rate' })"
        />
      </VCard>

      <!-- Система: пользователи + заявки на смену методов -->
      <div class="admin-dashboard__section">
        <span class="admin-dashboard__section-title">Система</span>
      </div>
      <VListRow
        title="Пользователи"
        subtitle="Все пользователи · назначение мастеров"
        clickable
        @click="router.push({ name: 'admin-users' })"
      >
        <template #trailing><IconArrowRight :size="20" /></template>
      </VListRow>
      <VListRow
        title="Заявки на смену методов"
        subtitle="Мастера меняют свои направления"
        clickable
        @click="router.push({ name: 'admin-method-requests' })"
      >
        <template #trailing>
          <span class="admin-dashboard__row-trailing">
            <VBadge v-if="pendingMethodChanges > 0" variant="error">{{ pendingMethodChanges }}</VBadge>
            <IconArrowRight :size="20" />
          </span>
        </template>
      </VListRow>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VStatCard, VCard, VLoader, VProgressRow, VListRow, VBadge } from '@/components/ui'
import Banner from '@/components/shared/Banner.vue'
import { IconProfile, IconPending, IconWarning, IconArrowRight } from '@/components/icons'
import { useAdminStore } from '@/stores/admin'
import { getCheckinMetric, getFeedbackMetric, getReturnMetric, getAdminRevenue } from '@/api/admin'
import { formatMoney } from '@/utils/format'

const router = useRouter()
const adminStore = useAdminStore()

// Period toggle (Неделя/Месяц) + stepper offset (0 = current, -1 = previous …).
const period = ref<'week' | 'month'>('week')
const periodOffset = ref(0)

function selectPeriod(p: 'week' | 'month'): void {
  periodOffset.value = 0 // switching granularity resets to the current period
  period.value = p
}
function stepPrev(): void {
  periodOffset.value -= 1
}
function stepNext(): void {
  if (periodOffset.value < 0) periodOffset.value += 1 // no stepping into the future
}
const canStepNext = computed((): boolean => periodOffset.value < 0)

const loading = computed((): boolean => adminStore.loading && !adminStore.stats)

const pendingVerifications = computed((): number => adminStore.pendingVerifications)
const pendingModeration = computed((): number => adminStore.pendingModeration)
// A2: unread indicator for incoming master method-change requests.
const pendingMethodChanges = computed((): number => adminStore.pendingMethodChanges)

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
// Stat cards (period-new, option А): values + percent deltas come from the
// period-scoped overview (E7). Практик = practices scheduled in period,
// Мастеров = new masters, Участников = new users. Deltas are period-over-period
// percent (green up / rose down); null (no prior base) hides the trend line.
// =========================================================================
const overview = computed(() => adminStore.overview)

function pctDelta(v: number | null | undefined): string {
  if (v === null || v === undefined) return ''
  return `${v >= 0 ? '+' : ''}${v}%`
}
function pctTone(v: number | null | undefined): 'up' | 'down' | 'muted' {
  if (v === null || v === undefined) return 'muted'
  return v >= 0 ? 'up' : 'down'
}

const practicesValue = computed((): string => String(overview.value?.practices_count ?? '—'))
const mastersValue = computed((): string => String(overview.value?.new_masters ?? '—'))
const participantsValue = computed((): string => String(overview.value?.new_users ?? '—'))
const practicesDelta = computed((): string => pctDelta(overview.value?.practices_delta_pct))
const mastersDelta = computed((): string => pctDelta(overview.value?.new_masters_delta_pct))
const participantsDelta = computed((): string => pctDelta(overview.value?.new_users_delta_pct))
const practicesDeltaTone = computed(() => pctTone(overview.value?.practices_delta_pct))
const mastersDeltaTone = computed(() => pctTone(overview.value?.new_masters_delta_pct))
const participantsDeltaTone = computed(() => pctTone(overview.value?.new_users_delta_pct))

// Revenue (E9). Weekly GMV from /admin/revenue, best-effort. €0.00 while seed
// practices are free (priced templates land with the seed-pricing task). Delta
// needs E7 (not delivered) -> blank.
const revenueCents = ref<number | null>(null)
const revenueValue = computed((): string =>
  revenueCents.value !== null ? formatMoney(revenueCents.value, 'EUR', 'ru', true) : '—',
)
const revenueDelta = computed((): string => '')

// Engagement headline rates (E9). Fetched best-effort on mount; a failed metric
// leaves its row at an empty track + "—". The detail screens carry the breakdown.
const checkinRate = ref<number | null>(null)
const feedbackRate = ref<number | null>(null)
const returnRate = ref<number | null>(null)

async function loadEngagement(): Promise<void> {
  const p = period.value
  const off = periodOffset.value
  const [checkin, feedback, ret, revenue] = await Promise.allSettled([
    getCheckinMetric(p, off),
    getFeedbackMetric(p, off),
    getReturnMetric(p, off),
    getAdminRevenue(),
  ])
  if (checkin.status === 'fulfilled') checkinRate.value = checkin.value.rate_pct
  if (feedback.status === 'fulfilled') feedbackRate.value = feedback.value.rate_pct
  if (ret.status === 'fulfilled') returnRate.value = ret.value.rate_pct
  if (revenue.status === 'fulfilled') revenueCents.value = revenue.value.revenue_cents
}

// Navigated period label, client-side: week -> "Mon - Sun", month -> "Июль 2026",
// both shifted by periodOffset. Cosmetic mirror of the backend UTC calendar bounds.
const periodRange = computed((): string => {
  const now = new Date()
  if (period.value === 'week') {
    const dow = (now.getDay() + 6) % 7 // Mon = 0
    const mon = new Date(now)
    mon.setDate(now.getDate() - dow + periodOffset.value * 7)
    const sun = new Date(mon)
    sun.setDate(mon.getDate() + 6)
    const fmt = (d: Date): string =>
      d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }).replace('.', '')
    return `${fmt(mon)} - ${fmt(sun)}`
  }
  const m = new Date(now.getFullYear(), now.getMonth() + periodOffset.value, 1)
  return m.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
})

// Refetch the overview + engagement rates whenever the period or the stepper
// offset changes (D1/D3 cards + D4/D5 engagement share one window).
watch([period, periodOffset], () => {
  void adminStore.fetchOverview(period.value, periodOffset.value)
  void loadEngagement()
})

onMounted(() => {
  void adminStore.fetchDashboard()
  void adminStore.fetchOverview(period.value, periodOffset.value)
  void loadEngagement()
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
  min-height: var(--velo-size-44);
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
  width: var(--velo-size-40);
  height: var(--velo-size-40);
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
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

/* A2: trailing badge + chevron on the method-requests row */
.admin-dashboard__row-trailing {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

/* -- Period toggle (user/master dashboard pattern) -- */
.admin-dashboard__period {
  display: flex;
  gap: var(--velo-gap-2);
  background: var(--velo-glass-blue-15);
  border: var(--velo-border-width) solid var(--velo-glass-border);
  border-radius: var(--radius-xl);
  padding: var(--velo-gap-2);
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
  width: var(--velo-size-60);
  height: var(--velo-size-35);
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
  color: var(--velo-text-primary);
  letter-spacing: var(--velo-letter-spacing-064);
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
