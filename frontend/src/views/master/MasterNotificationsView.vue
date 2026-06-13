<!--
  VELO Frontend -- MasterNotificationsView (Phase-3 Master DS)

  Master-side notification preferences, reached from the master profile hub
  («Уведомления»). Operator decision 2026-06-13 (В1=Б): this is a SEPARATE
  master-only screen, NOT the shared user NotificationsView. The master design is
  far richer (bookings / participants / messages / analytics + a delivery
  schedule); the user view stays untouched (user role is frozen).

  Grouped on/off rows (label + optional sub + VSwitch) plus a «График
  уведомлений» block: a from/to delivery window (VSelect) and a VDayPicker.

  BACKEND (stub → Zod): the typed contract NotificationSettings carries only the
  four USER keys (push / practice_reminders / master_messages / support_messages)
  — NONE of the master keys, and no schedule. So this screen holds its state
  LOCALLY and does NOT persist yet (we don't fake a save). Zod task: extend
  NotificationSettings(+Update) with the master keys + a `schedule {from,to,days}`
  object, regen generated.ts, then wire persistence (a one-line updateProfile in
  each handler below) + real push delivery / quiet-hours. Defaults below mirror
  the operator-approved design.

  Route: /master/profile/notifications (name 'master-notifications',
  meta.hideTabBar — back-nav settings sub-screen, no tab bar per the design).
-->
<template>
  <div class="master-notifications">
    <VHeader title="Уведомления" show-back @back="router.back()" />

    <div class="master-notifications__content">
      <section v-for="group in GROUPS" :key="group.title" class="mn-section">
        <h2 class="mn-section__title">{{ group.title }}</h2>
        <div v-for="row in group.rows" :key="row.key" class="mn-card">
          <div class="mn-card__text">
            <span class="mn-card__title">{{ row.label }}</span>
            <span v-if="row.sub" class="mn-card__sub">{{ row.sub }}</span>
          </div>
          <VSwitch
            :model-value="toggles[row.key]"
            :aria-label="row.label"
            @update:model-value="(v) => onToggle(row.key, v)"
          />
        </div>
      </section>

      <!-- Delivery schedule -->
      <section class="mn-section">
        <h2 class="mn-section__title">График уведомлений</h2>
        <p class="mn-section__sub">Получать уведомления с</p>
        <div class="mn-sched">
          <div class="mn-sched__time">
            <VSelect
              :model-value="schedule.from"
              :options="TIME_OPTIONS"
              @update:model-value="(v) => onScheduleTime('from', v)"
            />
          </div>
          <span class="mn-sched__sep">до</span>
          <div class="mn-sched__time">
            <VSelect
              :model-value="schedule.to"
              :options="TIME_OPTIONS"
              @update:model-value="(v) => onScheduleTime('to', v)"
            />
          </div>
        </div>
        <VDayPicker
          :model-value="schedule.days"
          aria-label="Дни доставки уведомлений"
          @update:model-value="onScheduleDays"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VSwitch, VSelect, VDayPicker } from '@/components/ui'

const router = useRouter()

// --- Toggle rows -----------------------------------------------------------
// Forward-looking keys (not yet in the typed NotificationSettings contract; see
// the file header), grouped exactly as the operator design.
type ToggleKey =
  | 'new_booking'
  | 'booking_cancelled'
  | 'reminder'
  | 'new_checkin'
  | 'new_feedback'
  | 'msg_participants'
  | 'msg_support'
  | 'ai_summary'
  | 'monthly_report'

interface Row {
  key: ToggleKey
  label: string
  sub?: string
}
interface Group {
  title: string
  rows: Row[]
}

const GROUPS: Group[] = [
  {
    title: 'Практики',
    rows: [
      { key: 'new_booking', label: 'Новое бронирование', sub: 'Кто-то записался' },
      { key: 'booking_cancelled', label: 'Отмена бронирования', sub: 'Кто-то отменил' },
      { key: 'reminder', label: 'Напоминание', sub: 'За 1 час до начала' },
    ],
  },
  {
    title: 'Участники',
    rows: [
      {
        key: 'new_checkin',
        label: 'Новый check-in',
        sub: 'Участник отметился о состоянии перед практикой',
      },
      { key: 'new_feedback', label: 'Новый feedback', sub: 'Участник оставил отзыв' },
    ],
  },
  {
    title: 'Сообщения',
    rows: [
      { key: 'msg_participants', label: 'От участников' },
      { key: 'msg_support', label: 'От поддержки' },
    ],
  },
  {
    title: 'Аналитика',
    rows: [
      { key: 'ai_summary', label: 'AI-саммари', sub: 'По понедельникам' },
      { key: 'monthly_report', label: 'Ежемесячный отчет', sub: '1-го числа месяца' },
    ],
  },
]

// Defaults mirror the operator-approved design (all on except the monthly report).
const toggles = reactive<Record<ToggleKey, boolean>>({
  new_booking: true,
  booking_cancelled: true,
  reminder: true,
  new_checkin: true,
  new_feedback: true,
  msg_participants: true,
  msg_support: true,
  ai_summary: true,
  monthly_report: false,
})

// --- Delivery schedule -----------------------------------------------------
const schedule = reactive<{ from: string; to: string; days: string[] }>({
  from: '08:00',
  to: '22:00',
  days: ['mon', 'tue', 'wed', 'thu', 'fri'],
})

// Half-hour options 00:00…23:30 (value === label).
const TIME_OPTIONS: { value: string; label: string }[] = Array.from(
  { length: 48 },
  (_, i) => {
    const h = String(Math.floor(i / 2)).padStart(2, '0')
    const m = i % 2 === 0 ? '00' : '30'
    const t = `${h}:${m}`
    return { value: t, label: t }
  },
)

// --- Handlers --------------------------------------------------------------
// Local-only until the backend contract is extended (see file header). We do NOT
// call updateProfile with master keys: they are not in NotificationSettingsUpdate
// and would be a contract violation. Wiring is a one-liner once Zod lands them.
function onToggle(key: ToggleKey, value: boolean): void {
  toggles[key] = value
  // TODO(Zod): persist once NotificationSettings carries the master keys.
}
function onScheduleTime(edge: 'from' | 'to', value: string): void {
  schedule[edge] = value
  // TODO(Zod): persist the schedule once the contract carries it.
}
function onScheduleDays(days: string[]): void {
  schedule.days = days
  // TODO(Zod): persist the schedule days once the contract carries it.
}
</script>

<style scoped>
.master-notifications {
  display: flex;
  flex-direction: column;
  /* Break out of the layout's content padding so VHeader spans full width —
     mirrors the sibling settings screens (NotificationsView/LanguageTimezone). */
  margin: calc(-1 * var(--space-4));
}

.master-notifications__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  padding: 0 var(--space-4) var(--space-4);
}

.mn-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.mn-section__title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

.mn-section__sub {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: 0.02em;
  margin: calc(-1 * var(--space-1)) 0 0;
}

.mn-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  min-height: 51px;
  padding: var(--space-3) 18px;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
}

.mn-card__text {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.mn-card__title {
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.mn-card__sub {
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  letter-spacing: 0.02em;
  line-height: 1.25;
}

.mn-sched {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.mn-sched__time {
  flex: 1;
}

/* VSelect carries a bottom margin for form stacking; drop it in the inline row. */
.mn-sched__time :deep(.v-select) {
  margin-bottom: 0;
}

.mn-sched__sep {
  font-size: var(--text-base);
  color: var(--velo-text-secondary);
}
</style>
