// =============================================================================
// VELO Frontend -- Admin Helper Utilities (F8-fix W-5)
// =============================================================================
//
// Shared pure functions used across admin views:
//   AdminMastersView, AdminMasterReviewView,
//   AdminReportsView, AdminReportDetailView.
//
// Extracted to eliminate copy-paste of statusVariant / statusLabel /
// targetLabel / displayName between views.
// =============================================================================

import type { AdminMasterListItem } from '@/api/admin'

// ============================================================================
// Master helpers
// ============================================================================

/**
 * Build display name from AdminMasterListItem first_name + last_name.
 * Falls back to 'Пользователь' when both are null.
 */
export function masterDisplayName(
  item: Pick<AdminMasterListItem, 'first_name' | 'last_name'>,
): string {
  const parts = [item.first_name, item.last_name].filter(Boolean)
  return parts.length > 0 ? parts.join(' ') : 'Пользователь'
}

/**
 * Map master_status to VBadge variant.
 */
export function masterStatusVariant(status: string): 'warning' | 'success' | 'error' | 'info' {
  if (status === 'pending') return 'warning'
  if (status === 'verified') return 'success'
  if (status === 'rejected') return 'error'
  return 'info'
}

/**
 * Map master_status to Russian label.
 */
export function masterStatusLabel(status: string): string {
  if (status === 'pending') return 'Ожидает'
  if (status === 'verified') return 'Верифицирован'
  if (status === 'rejected') return 'Отклонён'
  return status
}

// ============================================================================
// Report helpers
// ============================================================================

/**
 * Map report status to VBadge variant.
 */
export function reportStatusVariant(status: string): 'warning' | 'success' | 'error' | 'info' {
  if (status === 'pending') return 'warning'
  if (status === 'resolved') return 'success'
  if (status === 'dismissed') return 'info'
  return 'info'
}

/**
 * Map report status to Russian label.
 */
export function reportStatusLabel(status: string): string {
  if (status === 'pending') return 'Ожидает'
  if (status === 'resolved') return 'Решена'
  if (status === 'dismissed') return 'Отклонена'
  return status
}

/**
 * Map report target_type to a Russian label.
 */
export function reportTargetLabel(type: string): string {
  if (type === 'user') return 'Юзер'
  if (type === 'master') return 'Мастер'
  if (type === 'practice') return 'Практика'
  return type
}

// ============================================================================
// Date helpers
// ============================================================================

/**
 * Format ISO date string to short Russian locale date.
 */
export function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

/**
 * Format ISO date string to Russian locale datetime.
 */
export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Relative "time ago" label for report/moderation cards (operator SVG
 * «1 Moderation»): «только что» / «N мин назад» / «N ч назад» / «Вчера», then
 * the absolute «DD MMM» for older items. Abbreviated units sidestep Russian
 * plural forms while staying readable.
 */
export function formatRelative(iso: string): string {
  const then = new Date(iso).getTime()
  const diffMin = Math.floor((Date.now() - then) / 60000)
  if (diffMin < 1) return 'только что'
  if (diffMin < 60) return `${diffMin} мин назад`
  const diffH = Math.floor(diffMin / 60)
  if (diffH < 24) return `${diffH} ч назад`
  const d = new Date(iso)
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  const sameDay = (a: Date, b: Date): boolean =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  if (sameDay(d, yesterday)) return 'Вчера'
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}
