// =============================================================================
// VELO Frontend -- Admin period-range label (batch P, P1)
// =============================================================================
//
// Client-side label for the admin dashboard's navigated week/month, shifted by
// an offset (0 = current, -1 = previous …). Cosmetic mirror of the backend's UTC
// calendar bounds. Shared by AdminDashboardView (the stepper) and the Engagement
// drill-in detail views so both show the SAME week when the user drills in.
// =============================================================================

/** e.g. week → "29 июн - 5 июл"; month → "Июль 2026". */
export function formatPeriodRange(period: 'week' | 'month', offset: number): string {
  const now = new Date()
  if (period === 'week') {
    const dow = (now.getDay() + 6) % 7 // Mon = 0
    const mon = new Date(now)
    mon.setDate(now.getDate() - dow + offset * 7)
    const sun = new Date(mon)
    sun.setDate(mon.getDate() + 6)
    const fmt = (d: Date): string =>
      d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }).replace('.', '')
    return `${fmt(mon)} - ${fmt(sun)}`
  }
  const m = new Date(now.getFullYear(), now.getMonth() + offset, 1)
  return m.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
}
