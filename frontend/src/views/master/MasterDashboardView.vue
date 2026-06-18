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
    - "Ближайшие практики": up to 3 upcoming practice cards, each with
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
          <IconBell :size="21" />
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
        <VStatCard :value="practicesStat" label="Практик" :delta="practicesDelta" />
        <VStatCard :value="participantsStat" label="Участников" :delta="participantsDelta" />
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
           САММАРИ НЕДЕЛИ (placeholder — no master-AI backend yet)
           ================================================================ -->
      <h2 class="velo-section-title">Саммари недели</h2>
      <!-- The whole block opens the full summary on tap (operator tester-fix
           2026-06-17; «Подробнее» button removed). When a summary exists the
           teaser is clamped to 2 lines with an ellipsis so it reads as "tap to
           expand" — same idiom as the diary feed card (Variant B). The new
           master has nothing to open, so it keeps a plain placeholder. -->
      <VCard v-if="!isNewMaster" clickable @click="router.push({ name: 'master-summary' })">
        <p class="master-dashboard__summary-text">{{ WEEKLY_SUMMARY_INSIGHT }}</p>
      </VCard>
      <VCard v-else>
        <p class="master-dashboard__empty-text">Данных пока нет — создайте первую практику</p>
      </VCard>

      <!-- ================================================================
           БЛИЖАЙШИЕ ПРАКТИКИ (up to 3)
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
                <div class="master-dashboard__practice-meta">
                  <span class="master-dashboard__meta-item">
                    <IconGroup :size="15" />
                    {{
                      formatParticipants(practice.current_participants, practice.max_participants)
                    }}
                  </span>
                  <!-- checkin-count + recurrence meta render once the backend
                       provides the fields (roadmap for Zod). -->
                </div>
              </div>
            </div>
          </article>
          <!-- Like the user dashboard: left = Zoom (1-click launch; stub toast
               until Zoom ships), right = Check-ins. Edit/delete moved to the
               practice screen, reached by tapping the card (openPractice). -->
          <div class="master-dashboard__practice-actions">
            <VButton variant="secondary" block @click="onZoom">Zoom</VButton>
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { VButton, VLoader, VStatCard, VCard, VMenuRow, VSegmentTrack } from '@/components/ui'
import { IconBell, IconGroup } from '@/components/icons'
import { useMasterStore } from '@/stores/master'
import { useToast } from '@/composables/useToast'
import { formatDateShort, formatTime, formatDuration, formatParticipants } from '@/utils/format'
import { practiceIconFor } from '@/utils/displayHelpers'
import { practiceHasEnded } from '@/utils/practiceStatus'
import { WEEKLY_SUMMARY_INSIGHT } from '@/utils/masterSummaryStub'
import type { PracticeResponse } from '@/api/types'

const router = useRouter()
const masterStore = useMasterStore()
const toast = useToast()

// -- Period toggle. Visual-only until a period-scoped stats API exists (roadmap). --
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
// Stats. Practices total is real; participants has no backend yet → "—".
// The period toggle is visual-only now (income was removed from the dashboard
// — operator tester-fix 2026-06-17; it was the only period-scoped stat).
// =========================================================================
const practicesStat = computed((): string =>
  String(masterStore.practicesTotal ?? masterStore.practices.length),
)
const participantsStat = computed((): string => '—')
const practicesDelta = computed((): string => '')
const participantsDelta = computed((): string => '')

// Notifications feed not built yet → no unread count (roadmap for Zod).
const unreadCount = computed((): number => 0)

// =========================================================================
// Nearest upcoming practices (up to 3). Scheduled/live AND not yet ended;
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
    .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())
    .slice(0, 3),
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
// Zoom — stub until delivery (mirrors the user dashboard's Zoom button).
function onZoom(): void {
  toast.info('Zoom пока недоступен')
}

// -- Load data on mount --
onMounted(async () => {
  clockInterval = setInterval(() => {
    now.value = Date.now()
  }, 60_000)
  // Both calls are lazy -- skip if already populated by guard / prior navigation.
  await masterStore.fetchMyProfile()
  await masterStore.fetchMyPractices()
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
})
</script>

<style scoped>
.master-dashboard {
  /* F-5 rail sync: horizontal padding removed — MobileLayout supplies the 24px
     screen rail (--velo-rail-pad-x). Vertical kept for breathing room. */
  padding: var(--space-4) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
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
  min-height: 44px;
}

.master-dashboard__bell {
  position: relative;
  width: 44px;
  height: 44px;
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
  font-weight: 400;
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
  font-weight: 400;
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

.master-dashboard__practice-meta {
  display: flex;
  align-items: center;
  gap: var(--velo-card-meta-row-gap);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: var(--velo-card-letter-spacing-meta);
  margin-top: 2px;
}

.master-dashboard__meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
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
