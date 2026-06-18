// =============================================================================
// VELO Frontend -- Master weekly-summary stub (shared source)
// =============================================================================
//
// The master's «Саммари недели» AI insight has no backend yet (roadmap for Zod:
// a weekly feedback-aggregation + AI endpoint). Until it lands, the dashboard
// teaser AND the full «Саммари недели» screen read this ONE stub so the text the
// master sees on the detail screen is the same text teased on the dashboard
// (operator 2026-06-19: the dashboard wasn't showing any summary text).
// When the real endpoint ships, both call-sites swap this constant for the fetch.
// =============================================================================

export const WEEKLY_SUMMARY_INSIGHT =
  '«На этой неделе вы провели 12 практик для 89 участников. 85% отметили хорошее ' +
  'или отличное состояние после занятий. Анна П. оставила запрос на индивидуальную ' +
  'консультацию — рекомендую связаться с ней.»'
