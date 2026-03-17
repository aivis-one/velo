// =============================================================================
// VELO Frontend -- Tab Bar Config (Phase F2.2)
// =============================================================================
//
// Tab items per role. Used by shell components (UserShell, MasterShell,
// AdminShell) to configure VTabBar.
// =============================================================================

import type { TabItem } from '@/components/layout/VTabBar.vue'
import {
  IconHome,
  IconCalendar,
  IconDiary,
  IconProfile,
  IconBrain,
  IconGroup,
  IconWarning,
} from '@/components/icons'

export const USER_TABS: TabItem[] = [
  { icon: IconHome, label: 'Дашборд', to: '/user/dashboard' },
  { icon: IconCalendar, label: 'Календарь', to: '/user/calendar' },
  { icon: IconDiary, label: 'Дневник', to: '/user/diary' },
  { icon: IconProfile, label: 'Я', to: '/user/profile' },
]

export const MASTER_TABS: TabItem[] = [
  { icon: IconHome, label: 'Дашборд', to: '/master/dashboard' },
  { icon: IconCalendar, label: 'Практики', to: '/master/practices' },
  { icon: IconBrain, label: 'Аналитика', to: '/master/analytics' },
  { icon: IconProfile, label: 'Я', to: '/master/profile' },
]

export const ADMIN_TABS: TabItem[] = [
  { icon: IconHome, label: 'Дашборд', to: '/admin/dashboard' },
  { icon: IconGroup, label: 'Мастера', to: '/admin/masters' },
  { icon: IconWarning, label: 'Модерация', to: '/admin/reports' },
]
