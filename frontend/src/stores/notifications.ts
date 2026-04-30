// =============================================================================
// VELO Frontend — Notifications Settings Store (S2-S3 SPEEDRUN MEGA-2 §C46)
//
// Local-only toggles persisted via localStorage. No backend wiring at v1.
// 4 toggles: push, reminders, fromMasters, fromSupport.
// =============================================================================

import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useNotificationsStore = defineStore('notifications', () => {
  const push = ref(true)
  const reminders = ref(true)
  const fromMasters = ref(false)
  const fromSupport = ref(false)

  const KEYS = {
    push: 'velo:notif-push',
    reminders: 'velo:notif-reminders',
    fromMasters: 'velo:notif-from-masters',
    fromSupport: 'velo:notif-from-support',
  } as const

  function init(): void {
    const read = (k: string, fallback: boolean): boolean => {
      try {
        const raw = localStorage.getItem(k)
        return raw === null ? fallback : raw === 'true'
      } catch {
        return fallback
      }
    }
    push.value = read(KEYS.push, true)
    reminders.value = read(KEYS.reminders, true)
    fromMasters.value = read(KEYS.fromMasters, false)
    fromSupport.value = read(KEYS.fromSupport, false)
  }

  watch(push, (v) => {
    try {
      localStorage.setItem(KEYS.push, String(v))
    } catch {
      /* ignore quota / disabled */
    }
  })
  watch(reminders, (v) => {
    try {
      localStorage.setItem(KEYS.reminders, String(v))
    } catch {
      /* ignore */
    }
  })
  watch(fromMasters, (v) => {
    try {
      localStorage.setItem(KEYS.fromMasters, String(v))
    } catch {
      /* ignore */
    }
  })
  watch(fromSupport, (v) => {
    try {
      localStorage.setItem(KEYS.fromSupport, String(v))
    } catch {
      /* ignore */
    }
  })

  return {
    push,
    reminders,
    fromMasters,
    fromSupport,
    init,
  }
})
