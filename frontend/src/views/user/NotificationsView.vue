<!--
  VELO Frontend — NotificationsView (S2-S3 SPEEDRUN MEGA-2 §C46)

  4 toggle rows backed by useNotificationsStore (localStorage-persisted).
  Inline switch (label + checkbox visually styled). Path Y MEDIUM.
-->

<template>
  <div class="notif">
    <header class="notif__header">
      <button
        type="button"
        class="notif__back"
        aria-label="Назад"
        @click="router.back()"
      >
        <IconArrowBack :size="20" />
      </button>
      <h1 class="notif__title">
        Уведомления
      </h1>
    </header>

    <div class="notif__list">
      <label
        v-for="row in rows"
        :key="row.key"
        class="notif__row"
      >
        <span class="notif__label">{{ row.label }}</span>
        <input
          type="checkbox"
          class="notif__switch"
          :checked="row.value"
          @change="row.set(($event.target as HTMLInputElement).checked)"
        >
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { IconArrowBack } from '@/components/icons'
import { useNotificationsStore } from '@/stores/notifications'

const router = useRouter()
const notif = useNotificationsStore()

const rows = computed(() => [
  {
    key: 'push',
    label: 'Push-уведомления',
    value: notif.push,
    set: (v: boolean) => {
      notif.push = v
    },
  },
  {
    key: 'reminders',
    label: 'Напоминания о практиках',
    value: notif.reminders,
    set: (v: boolean) => {
      notif.reminders = v
    },
  },
  {
    key: 'fromMasters',
    label: 'Сообщения от мастеров',
    value: notif.fromMasters,
    set: (v: boolean) => {
      notif.fromMasters = v
    },
  },
  {
    key: 'fromSupport',
    label: 'Сообщения от поддержки',
    value: notif.fromSupport,
    set: (v: boolean) => {
      notif.fromSupport = v
    },
  },
])
</script>

<style scoped>
.notif {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
}

.notif__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.notif__back {
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

.notif__title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.notif__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.notif__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
  border-radius: var(--radius-full);
  cursor: pointer;
}

.notif__label {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
}

.notif__switch {
  appearance: none;
  -webkit-appearance: none;
  width: 44px;
  height: 24px;
  border-radius: var(--radius-full);
  background: var(--surface-steel-alpha-15);
  border: 1px solid var(--text-primary);
  position: relative;
  cursor: pointer;
  transition: background 0.2s;
}

.notif__switch::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--text-primary);
  transition: transform 0.2s;
}

.notif__switch:checked {
  background: var(--steel-button);
  border-color: var(--steel-button);
}

.notif__switch:checked::before {
  background: white;
  transform: translateX(20px);
}
</style>
