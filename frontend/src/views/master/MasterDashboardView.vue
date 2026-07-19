<!--
  VELO Frontend -- MasterDashboardView (Master DS rebuild 2026-06-11)

  Master dashboard, rebuilt to the approved design (operator SVG: zero / week /
  month / scroll). Rendered inside MasterShell (fog + tab bar from the shell).

  Structure (DS-first — every value is a --velo-* token / DS component):
    - Greeting + notification bell (badge only when unread > 0).
    - Stats: label + period toggle (Неделя / Месяц) + 3 VStatCard with optional
      delta trend. Period toggle = the user-dashboard pattern (NOT VSegment).
    - "Мои ученики" row (VMenuRow).
    - Zero state only: "Создать первую практику" (VButton) -> create.
    - "Саммари недели" (VCard placeholder).
    - "Ближайшие практики": up to 2 upcoming practice cards, each with
      "Изменить" -> edit and "Check-ins" -> attendance.

  STUBS (no backend yet -> roadmap for Zod; non-working taps show a toast):
    - Stats: only the practices total is real; participants/income + all deltas
      and the Неделя/Месяц period scoping have no API -> "—", toggle visual-only.
    - Notification bell (no feed), "Мои ученики" (no screen), AI summary
      "Подробнее" (no master-AI), practice checkin-count + recurrence meta
      (no fields) -> rendered only when the data exists (v-if), absent for now.
-->

<template>
  <div class="master-dashboard">
    <!-- Loading skeleton -->
    <template v-if="masterStore.profileLoading && !masterStore.profile">
      <div class="master-dashboard__skeleton">
        <VLoader size="lg" />
      </div>
    </template>

    <template v-else>
      <!-- ================================================================
           NOTIFICATION BELL (greeting removed — operator tester-fix
           2026-06-17, mirroring the user dashboard). Bell stays top-right.
           ================================================================ -->
      <div class="master-dashboard__bell-row">
        <button class="master-dashboard__bell" aria-label="Уведомления" @click="onBell">
          <IconBellPlain :size="21" />
          <span v-if="unreadCount > 0" class="master-dashboard__bell-badge">{{ unreadCount }}</span>
        </button>
      </div>

      <!-- ================================================================
           STATS (period toggle + 3 cards)
           ================================================================ -->
      <div class="master-dashboard__section-header">
        <span class="master-dashboard__stats-title">
          {{ isNewMaster ? 'Моя статистика' : 'Статистика' }}
        </span>
        <VSegmentTrack
          v-model="period"
          :options="PERIOD_OPTIONS"
          variant="toggle"
          aria-label="Период статистики"
        />
      </div>

      <!-- Income card removed from the dashboard (operator tester-fix 2026-06-17). -->
      <div class="master-dashboard__stats-grid">
        <VStatCard
          :value="practicesStat"
          label="Практик"
          :delta="practicesDelta"
          :delta-tone="practicesDeltaTone"
        />
        <VStatCard
          :value="participantsStat"
          label="Участников"
          :delta="participantsDelta"
          :delta-tone="participantsDeltaTone"
        />
      </div>

      <!-- ================================================================
           МОИ УЧЕНИКИ (stub — no screen yet)
           ================================================================ -->
      <VMenuRow label="Мои ученики" @click="onStudents">
        <template #icon><IconGroup :size="24" /></template>
      </VMenuRow>

      <!-- ================================================================
           ZERO-STATE CTA
           ================================================================ -->
      <!-- Shown whenever there is no upcoming practice (not only brand-new
           masters) — operator tester-fix 2026-06-17; «первую» dropped. -->
      <VButton
        v-if="nearestPractices.length === 0"
        variant="primary"
        block
        @click="router.push({ name: 'master-practice-new' })"
      >
        Создать практику
      </VButton>

      <!-- ================================================================
           САММАРИ НЕДЕЛИ (honest placeholder — no master-AI backend yet;
           honesty-cleanup 2026-07-12: dropped the fabricated insight text)
           ================================================================ -->
      <h2 class="velo-section-title">Саммари недели</h2>
      <!-- The whole block opens the full summary on tap (operator tester-fix
           2026-06-17; «Подробнее» button removed) — the target screen still has
           real content («Требуют внимания»), so the tap-through stays. -->
      <VCard v-if="!isNewMaster" clickable @click="router.push({ name: 'master-summary' })">
        <p class="master-dashboard__summary-text">Сводка появится с аналитикой</p>
      </VCard>
      <VCard v-else>
        <p class="master-dashboard__empty-text">Данных пока нет — создайте первую практику</p>
      </VCard>

      <!-- ================================================================
           БЛИЖАЙШИЕ ПРАКТИКИ (up to 2)
           ================================================================ -->
      <h2 class="velo-section-title">
        {{ nearestPractices.length > 1 ? 'Ближайшие практики' : 'Ближайшая практика' }}
      </h2>

      <template v-if="masterStore.practicesLoading && nearestPractices.length === 0">
        <div class="master-dashboard__loading-row">
          <VLoader size="sm" />
        </div>
      </template>

      <template v-else-if="nearestPractices.length > 0">
        <div
          v-for="practice in nearestPractices"
          :key="practice.id"
          class="master-dashboard__practice-block"
        >
          <article
            class="master-dashboard__practice-card"
            role="button"
            tabindex="0"
            @click="openPractice(practice)"
            @keydown.enter.space.prevent="openPractice(practice)"
          >
            <div class="master-dashboard__practice-top">
              <span class="master-dashboard__practice-icon">
                <component :is="practiceIconFor(practice)" :size="46" />
              </span>
              <div class="master-dashboard__practice-info">
                <div class="master-dashboard__practice-title">{{ practice.title }}</div>
                <div class="master-dashboard__practice-sub">{{ practiceWhen(practice) }}</div>
              </div>
            </div>
            <!-- Meta rows span the full card width BELOW the head (parity with the
                 «Практики › Предстоящие» reference card), so the weekday list has
                 room and never wraps mid-word; icons match the list at :16 (DB-5). -->
            <div class="master-dashboard__practice-meta">
              <span class="master-dashboard__meta-item">
                <IconGroup :size="16" />
                {{ formatParticipants(practice.current_participants, practice.max_participants) }}
              </span>
              <span v-if="checkinLabel(practice)" class="master-dashboard__meta-item">
                <IconCheckin :size="16" /> {{ checkinLabel(practice) }}
              </span>
              <span v-if="recurrenceLabel(practice)" class="master-dashboard__meta-item">
                <IconRepeat :size="16" /> {{ recurrenceLabel(practice) }}
              </span>
            </div>
            <div
              v-if="remainingSessionsLabel(practice)"
              class="master-dashboard__practice-meta master-dashboard__practice-meta--row2"
            >
              <span class="master-dashboard__meta-item">
                <IconHourglass :size="16" /> {{ remainingSessionsLabel(practice) }}
              </span>
            </div>
          </article>
          <!-- Like the user dashboard: left = Zoom (1-click launch; stub toast
               until Zoom ships), right = Check-ins. Edit/delete moved to the
               practice screen, reached by tapping the card (openPractice). -->
          <div class="master-dashboard__practice-actions">
            <VButton variant="secondary" block @click="onZoom(practice)">Zoom</VButton>
            <VButton
              variant="primary"
              block
              @click="router.push({ name: 'master-attendance', params: { id: practice.id } })"
            >
              Check-ins
            </VButton>
          </div>
        </div>
      </template>

      <template v-else>
        <VCard>
          <p class="master-dashboard__empty-text">
            {{
              isNewMaster ? 'Данных пока нет — создайте первую практику' : 'Нет предстоящих практик'
            }}
          </p>
        </VCard>
      </template>
    </template>
  </div>

  <!-- Post-approval onboarding carousel — full-screen overlay above the shell
       (tab bar + header). Teleported to body to escape any ancestor transform
       (fog / bg-stabilizer) that would otherwise trap position:fixed. -->
  <Teleport to="body">
    <div
      v-if="showMasterOnboarding"
      class="master-onboarding-overlay"
      :style="{ paddingTop: contentSafeTop + 'px' }"
    >
      <MasterOnboardingView @done="onMasterOnboardingDone" />
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { VButton, VLoader, VStatCard, VCard, VMenuRow, VSegmentTrack } from '@/components/ui'
import { IconBellPlain, IconGroup, IconCheckin, IconRepeat, IconHourglass } from '@/components/icons'
import { useMasterStore } from '@/stores/master'
import { useAuthStore } from '@/stores/auth'
import { useSafeArea } from '@/composables/useSafeArea'
import MasterOnboardingView from '@/views/master/MasterOnboardingView.vue'
import { isMasterOnboardingCompleted, shouldShowMasterOnboarding } from '@/utils/masterOnboarding'
import { useToast } from '@/composables/useToast'
import { formatDateShort, formatTime, formatDuration, formatParticipants, localSortKey } from '@/utils/format'
import { platform } from '@/platform'
import { practiceIconFor } from '@/utils/displayHelpers'
import { checkinLabel, recurrenceLabel, remainingSessionsLabel } from '@/utils/practiceCardMeta'
import { practiceHasEnded } from '@/utils/practiceStatus'
import { getMasterStats } from '@/api/masters'
import type { PracticeResponse, MasterStatsResponse } from '@/api/types'

const router = useRouter()
const masterStore = useMasterStore()
const authStore = useAuthStore()
const { contentSafeTop } = useSafeArea()
const toast = useToast()

// -- Period toggle. Drives the period-scoped stats row (E7). --
const period = ref<'week' | 'month'>('week')
const PERIOD_OPTIONS: ReadonlyArray<{ value: 'week' | 'month'; label: string }> = [
  { value: 'week', label: 'Неделя' },
  { value: 'month', label: 'Месяц' },
]

// True for a brand-new master with no practices at all (zero state).
const isNewMaster = computed(
  (): boolean => (masterStore.practicesTotal ?? masterStore.practices.length) === 0,
)

// =========================================================================
// Stats (E7: GET /masters/me/stats?period). Both «Практик» and «Участников»
// are period-scoped (D1); the toggle refetches. income_cents is returned but
// rendered on Finance/Analytics, not here (D2). "—" until the fetch resolves.
// =========================================================================
const stats = ref<MasterStatsResponse | null>(null)

async function loadStats(): Promise<void> {
  stats.value = await getMasterStats(period.value)
}

const practicesStat = computed((): string =>
  stats.value ? String(stats.value.practices_count) : '—',
)
const participantsStat = computed((): string =>
  stats.value ? String(stats.value.participants_count) : '—',
)

/** Signed percent string for a delta; '' (hidden) when null. */
function deltaStr(pct: number | null | undefined): string {
  if (pct == null) return ''
  const r = Math.round(pct)
  if (r === 0) return '0%'
  return `${r > 0 ? '+' : '−'}${Math.abs(r)}%`
}
/** Tone: positive → up (teal), negative → down (rose, D5), zero/null → muted. */
function deltaTone(pct: number | null | undefined): 'up' | 'down' | 'muted' {
  if (pct == null || Math.round(pct) === 0) return 'muted'
  return pct > 0 ? 'up' : 'down'
}

const practicesDelta = computed((): string => deltaStr(stats.value?.practices_delta_pct))
const participantsDelta = computed((): string => deltaStr(stats.value?.participants_delta_pct))
const practicesDeltaTone = computed(() => deltaTone(stats.value?.practices_delta_pct))
const participantsDeltaTone = computed(() => deltaTone(stats.value?.participants_delta_pct))

// Refetch the stats row when the period toggle changes.
watch(period, () => {
  void loadStats().catch(() => {
    /* keep the previous values on a transient refetch error */
  })
})

// Notifications feed not built yet → no unread count (roadmap for Zod).
const unreadCount = computed((): number => 0)

// =========================================================================
// Nearest upcoming practices (up to 2). Scheduled/live AND not yet ended;
// soonest first. Symmetric with the user dashboard's reactive 60s clock so a
// card drops off exactly when its practice ends.
// =========================================================================
const now = ref(Date.now())
let clockInterval: ReturnType<typeof setInterval> | null = null

const nearestPractices = computed((): PracticeResponse[] =>
  masterStore.practices
    .filter(
      (p) => (p.status === 'scheduled' || p.status === 'live') && !practiceHasEnded(p, now.value),
    )
    // LOCAL wall-clock order (each card renders in its own p.timezone), so the
    // top-2 slice matches the times shown across differing timezones (CR-1/CR-2).
    .sort((a, b) => localSortKey(a.scheduled_at, a.timezone) - localSortKey(b.scheduled_at, b.timezone))
    .slice(0, 2),
)

// "Завтра, 07:00 • 45 мин" — rendered in the practice's own timezone (the master
// set it), matching MasterPracticesView.
function practiceWhen(p: PracticeResponse): string {
  const day = formatDateShort(p.scheduled_at, p.timezone)
  const time = formatTime(p.scheduled_at, p.timezone)
  return `${day}, ${time} • ${formatDuration(p.duration_minutes)}`
}

// -- Stub actions (no backend) --
function onBell(): void {
  toast.info('Уведомления пока недоступны')
}
function onStudents(): void {
  router.push({ name: 'master-students' })
}
// Tap the card → the practice screen (edit/cancel/delete live there via «…»).
function openPractice(p: PracticeResponse): void {
  router.push({ name: 'master-practice-detail', params: { id: p.id } })
}
// Zoom — open the practice's link via the platform abstraction (routes
// Telegram-SDK openLink vs window.open). Master screens carry the full
// PracticeResponse, so zoom_link is available; guard for a real https URL
// (mirrors PracticeLiveView's hasValidZoom), else nudge the master to add one.
function onZoom(p: PracticeResponse): void {
  if (p.zoom_link && p.zoom_link.startsWith('https://')) {
    platform.openLink(p.zoom_link)
  } else {
    toast.info('Добавьте ссылку на Zoom в настройках практики')
  }
}

// =========================================================================
// Post-approval onboarding carousel (Phase D, slice-1). Shown ONCE to a
// freshly-verified master as a full-screen overlay (Teleport) on first
// dashboard entry. Gate + null-tolerant flag read in utils/masterOnboarding;
// the per-session guard lives in the master store so it survives this view's
// unmount/remount but resets on logout. E15 shipped (№256/257): the server
// flag (master_onboarding_completed) persists, so the carousel stays done
// across sessions and devices.
// =========================================================================
const showMasterOnboarding = computed(() =>
  shouldShowMasterOnboarding({
    role: authStore.role,
    profileStatus: masterStore.profile?.status,
    completed: isMasterOnboardingCompleted(authStore.user),
    shownThisSession: masterStore.onboardingShownThisSession,
  }),
)

function onMasterOnboardingDone(): void {
  // Hide the overlay immediately (gate → false), then persist best-effort.
  masterStore.onboardingShownThisSession = true
  void persistMasterOnboarding()
}

async function persistMasterOnboarding(): Promise<void> {
  try {
    // E15 (№256/257): the field is persisted by the backend and typed on
    // UserUpdate — plain PATCH, source of truth across devices/re-login.
    await authStore.updateProfile({ master_onboarding_completed: true })
  } catch {
    // Best-effort only: the session guard already prevents a re-show this
    // session; the next successful PATCH persists it. Not surfaced to the user.
  }
}

// -- Load data on mount --
onMounted(async () => {
  clockInterval = setInterval(() => {
    now.value = Date.now()
  }, 60_000)
  // Period-scoped stats row (E7); independent of the practices list fetch.
  void loadStats().catch(() => {
    /* leave cards at "—" if the stats fetch fails */
  })
  // Both calls are lazy -- skip if already populated by guard / prior navigation.
  await masterStore.fetchMyProfile()
  await masterStore.fetchMyPractices()
  // E12 swap (ПРОМТ №419): the check-in meta now reads checkin_count straight
  // off the practice (already on masterStore.practices) -- the insights
  // eager-load that used to feed it is gone, one fewer network round-trip.
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
})
</script>

<style scoped>
/* Full-screen onboarding overlay. Replicates the app's photo background
   (ПРОМТ №383: now `#app-bg` in global.css, was `#app::before`) so it obscures
   the dashboard behind it and the transparent carousel reads exactly like the
   user OnboardingView. Below the toast layer (--z-toast) so error toasts
   still surface. This is a SEPARATE, intentional second paint of the same
   image -- not a bug: `#app-bg` sits BEHIND `#app` (z-index:-1), and this
   overlay sits ABOVE `#app` (z-index:var(--z-popup)) to obscure it, so it
   can't just show `#app-bg` through a transparent background -- it needs its
   own opaque copy. Audited №383: this view has no focusable inputs (a
   read-only carousel), so it never triggers the Android
   focus-scroll-bypasses-overflow-hidden path that #app::before was vulnerable
   to -- safe as `position:absolute` against body's frozen box.
   position:absolute (was fixed, bg-freeze batch): this is Teleported to
   <body>, so a `fixed` layer tracked the visual viewport directly -- on a
   platform where the keyboard resizes that viewport, this SECOND copy of the
   mandala moved independently of the real background underneath it (a
   confirmed jump vector, audit ПРОМТ №378). `body` is now position:relative
   (global.css) with a frozen height, so `absolute; inset:0` here resolves
   against that stable box instead -- full-bleed coverage, immune to the
   keyboard, on every platform. */
.master-onboarding-overlay {
  position: absolute;
  inset: 0;
  z-index: var(--z-popup);
  background: url('/bg/background.png') center / cover no-repeat;
  box-sizing: border-box;
}

.master-dashboard {
  /* F-5 rail sync: horizontal padding removed — MobileLayout supplies the 24px
     screen rail (--velo-rail-pad-x). Top padding removed too (greeting gone —
     the lone bell rode too low under the shell's fog-top clearance; operator
     2026-06-23, SVG «Dashboard»): the bell now sits right under the shared 60px
     clearance, matching the SVG's tight top band. Bottom kept for breathing room. */
  padding: 0 0 var(--space-4);
  display: flex;
  flex-direction: column;
  /* Vertical rhythm tightened one step (16→14) after the greeting was removed —
     the lone bell band left the top reading sparse (DB-3, operator 2026-07-01).
     Device-tunable. */
  gap: var(--space-3);
}

/* -- Skeleton -- */
.master-dashboard__skeleton {
  display: flex;
  justify-content: center;
  padding: var(--space-10) 0;
}

/* -- Bell row (greeting removed — bell stays top-right) -- */
.master-dashboard__bell-row {
  display: flex;
  justify-content: flex-end;
  min-height: var(--velo-size-44);
}

.master-dashboard__bell {
  position: relative;
  width: var(--velo-size-44);
  height: var(--velo-size-44);
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

.master-dashboard__bell:active {
  opacity: 0.85;
}

.master-dashboard__bell-badge {
  position: absolute;
  top: -1px;
  right: -1px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: var(--radius-xl);
  background: var(--velo-pink-300);
  color: var(--velo-white);
  font-size: var(--text-10);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* -- Stats header + period toggle (user-dashboard pattern) -- */
.master-dashboard__section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.master-dashboard__stats-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

/* -- Stats grid (2 cards — income removed) -- */
.master-dashboard__stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

/* -- Section title -- */

/* -- Empty/placeholder card text -- */
.master-dashboard__empty-text {
  margin: 0;
  text-align: center;
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  line-height: 1.5;
  padding: var(--space-1) var(--space-2);
}

/* -- Summary teaser: 2-line clamp + ellipsis so the card reads as "tap to
      expand" (mirrors the diary feed card, Variant B). -- */
.master-dashboard__summary-text {
  margin: 0;
  color: var(--velo-text-secondary);
  font-size: var(--text-sm);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

/* -- Loading row -- */
.master-dashboard__loading-row {
  display: flex;
  justify-content: center;
  padding: var(--space-4) 0;
}

/* -- Practice block (card + actions row) -- */
.master-dashboard__practice-block {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.master-dashboard__practice-card {
  display: flex;
  flex-direction: column;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--velo-card-padding-y) var(--velo-card-padding-x);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.master-dashboard__practice-card:active {
  opacity: 0.85;
}

.master-dashboard__practice-top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.master-dashboard__practice-icon {
  flex-shrink: 0;
  color: var(--velo-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.master-dashboard__practice-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--velo-card-gap-icon-title);
}

.master-dashboard__practice-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: var(--velo-card-letter-spacing-title);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.master-dashboard__practice-sub {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: var(--velo-card-letter-spacing-meta);
}

/* Full-width meta row below the head (parity with the «Практики» reference
   card): flex-wrap so items reflow as whole chips, generous column gap so the
   weekday list fits without splitting mid-word (DB-5). */
.master-dashboard__practice-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2) var(--space-4);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: var(--velo-card-letter-spacing-meta);
  margin-top: var(--space-3);
}

/* Second meta row («Осталось N из M занятий») — tighter under the first and
   centered, mirroring the reference card's row-2. */
.master-dashboard__practice-meta--row2 {
  margin-top: var(--space-2);
  justify-content: center;
}

.master-dashboard__meta-item {
  display: inline-flex;
  align-items: center;
  gap: var(--velo-card-gap-icon-title);
  white-space: nowrap;
}

.master-dashboard__practice-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
  /* Side inset so the buttons land at the design width (~145px) instead of
     full-bleed to the rail (design «1 Dashboard»). */
  padding: 0 var(--space-4);
}

/* Card action buttons: 20px label (design); secondary action is a light glass
   fill (blue-200 @ .15) — far more transparent than the default secondary. */
.master-dashboard__practice-actions :deep(.v-btn) {
  font-size: var(--text-lg);
}

.master-dashboard__practice-actions :deep(.v-btn--secondary) {
  background: var(--velo-glass-blue-200-15);
}
</style>
