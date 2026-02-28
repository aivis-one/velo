// =============================================================================
// VELO Frontend -- Tab Bar Config (Phase F2.2)
// =============================================================================
//
// Tab items per role. Used by shell components (UserShell, MasterShell,
// AdminShell) to configure VTabBar.
// =============================================================================

import type { TabItem } from '@/components/layout/VTabBar.vue'

export const USER_TABS: TabItem[] = [
  { icon: '🏠', label: 'Дашборд', to: '/user/dashboard' },
  { icon: '📅', label: 'Календарь', to: '/user/calendar' },
  { icon: '📔', label: 'Дневник', to: '/user/diary' },
  { icon: '👤', label: 'Я', to: '/user/profile' },
]

export const MASTER_TABS: TabItem[] = [
  { icon: '📊', label: 'Дашборд', to: '/master/dashboard' },
  { icon: '📅', label: 'Практики', to: '/master/practices' },
  { icon: '📈', label: 'Аналитика', to: '/master/analytics' },
  { icon: '👤', label: 'Я', to: '/master/profile' },
]

export const ADMIN_TABS: TabItem[] = [
  { icon: '📊', label: 'Дашборд', to: '/admin/dashboard' },
  { icon: '👥', label: 'Мастера', to: '/admin/masters' },
  { icon: '⚠️', label: 'Модерация', to: '/admin/reports' },
]
