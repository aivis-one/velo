<!--
  VELO Frontend -- UserProfileView (S2 P09 C33 — refresh per skin 70/71)

  Avatar card -> stats -> Аккаунт menu (Edit / Reservations / Messages) ->
  Settings menu -> Help menu -> Logout. Stats client-side from bookingsStore.

  Path Y MEDIUM. No emojis (#048). Some menu targets land in MEGA-2.
-->

<template>
  <div class="up">
    <header class="up__head">
      <h1>Профиль</h1>
    </header>

    <section class="up__avatar">
      <div class="up__avatar-icon">
        <IconProfile :size="48" />
      </div>
      <h2>{{ name }}</h2>
    </section>

    <div class="up__stats">
      <StatCard
        :value="attendedCount"
        label="Практик пройдено"
      />
      <StatCard
        :value="practiceHours"
        label="Часов в практике"
      />
    </div>

    <section class="up__menu">
      <h3>Аккаунт</h3>
      <ProfileMenuItem
        :icon="IconEdit"
        label="Редактировать профиль"
        to="/user/profile/edit"
      />
      <ProfileMenuItem
        :icon="IconCalendar"
        label="Мои бронирования"
        to="/user/reservations"
      />
      <ProfileMenuItem
        :icon="IconFeedback"
        label="Сообщения"
        to="/user/messages"
      />
    </section>

    <section class="up__menu">
      <h3>Настройки</h3>
      <ProfileMenuItem
        :icon="IconSupport"
        label="Уведомления"
        to="/user/profile/notifications"
      />
      <ProfileMenuItem
        :icon="IconBrain"
        label="Язык / Часовой пояс"
        to="/user/profile/language"
      />
    </section>

    <section class="up__menu">
      <h3>Помощь</h3>
      <ProfileMenuItem
        :icon="IconSupport"
        label="Поддержка"
        to="/user/profile/support"
      />
      <ProfileMenuItem
        :icon="IconArrowForward"
        label="Поделиться"
        @click="onShare"
      />
    </section>

    <ProfileMenuItem
      :icon="IconArrowBack"
      label="Выйти"
      danger
      @click="onLogout"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  IconProfile,
  IconEdit,
  IconCalendar,
  IconFeedback,
  IconSupport,
  IconBrain,
  IconArrowForward,
  IconArrowBack,
} from '@/components/icons'
import StatCard from '@/components/shared/StatCard.vue'
import ProfileMenuItem from '@/components/shared/ProfileMenuItem.vue'
import { useAuthStore } from '@/stores/auth'
import { useBookingsStore } from '@/stores/bookings'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const auth = useAuthStore()
const bookings = useBookingsStore()
const toast = useToast()

const name = computed(() => {
  const u = auth.user
  if (!u) return ''
  return [u.first_name, u.last_name].filter(Boolean).join(' ') || 'Пользователь'
})

const attendedCount = computed(
  () => bookings.bookings.filter((b) => b.status === 'attended').length,
)

const practiceHours = computed(() => {
  const totalMin = bookings.bookings
    .filter((b) => b.status === 'attended')
    .reduce((s, b) => s + (b.practice.duration_minutes ?? 0), 0)
  return (totalMin / 60).toFixed(1)
})

async function onShare(): Promise<void> {
  const url = window.location.origin
  const data = { title: 'VELO', text: 'Пространство для практики', url }
  if (navigator.share) {
    try {
      await navigator.share(data)
      return
    } catch {
      // user cancel — silent
    }
  }
  try {
    await navigator.clipboard.writeText(url)
    toast.success('Скопировано в буфер обмена')
  } catch {
    toast.info('Поделиться: ' + url)
  }
}

async function onLogout(): Promise<void> {
  if (!window.confirm('Выйти из аккаунта?')) return
  await auth.logout()
  router.push('/welcome')
}

onMounted(() => {
  if (bookings.bookings.length === 0) bookings.fetchMyBookings()
})
</script>

<style scoped>
.up {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.up__head h1 {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.up__avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-lg);
}

.up__avatar-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: var(--radius-full);
  background: var(--surface-default);
  color: var(--text-secondary);
}

.up__avatar h2 {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.up__stats {
  display: flex;
  gap: var(--space-3);
}

.up__menu {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.up__menu h3 {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin: 0 0 var(--space-1);
  font-weight: 400;
}
</style>
