// Shared practice form options.
// Used by CreatePracticeView and EditPracticeView to avoid duplication (W-2).

import type { PracticeDirection } from '@/api/types'

export const DURATION_OPTIONS: { label: string; value: string }[] = [
  { label: '30 минут', value: '30' },
  { label: '45 минут', value: '45' },
  { label: '60 минут', value: '60' },
  { label: '75 минут', value: '75' },
  { label: '90 минут', value: '90' },
  { label: '120 минут', value: '120' },
]

export const TIMEZONE_OPTIONS: { label: string; value: string }[] = [
  { label: 'Europe/Moscow (UTC+3)',      value: 'Europe/Moscow' },
  { label: 'Europe/Berlin (UTC+1/2)',    value: 'Europe/Berlin' },
  { label: 'Europe/London (UTC+0/1)',    value: 'Europe/London' },
  { label: 'UTC',                        value: 'UTC' },
  { label: 'Asia/Yerevan (UTC+4)',       value: 'Asia/Yerevan' },
  { label: 'Asia/Tbilisi (UTC+4)',       value: 'Asia/Tbilisi' },
  { label: 'Asia/Almaty (UTC+5)',        value: 'Asia/Almaty' },
  { label: 'Asia/Dubai (UTC+4)',         value: 'Asia/Dubai' },
  { label: 'America/New_York (UTC-5/4)', value: 'America/New_York' },
]

// -- Calendar taxonomy options (front-first, 10 directions, 2026-05-28) --
// direction / difficulty are required Practice fields (stored in
// data.taxonomy on the backend). Values MUST match the future backend
// allowed list once B-2 lands (handoff §9). See api/types.ts for the
// matching literal union and the migration plan.
// Shared by the master create/edit forms and the Calendar filter UI.

export interface DirectionOption {
  label: string
  value: PracticeDirection
}

export const DIRECTION_OPTIONS: DirectionOption[] = [
  { label: 'Медитация',            value: 'meditation' },
  { label: 'Йога',                 value: 'yoga' },
  { label: 'Дыхательные практики', value: 'breathwork' },
  { label: 'Соматика',             value: 'somatic' },
  { label: 'Тантра',               value: 'tantra' },
  { label: 'Круги',                value: 'circles' },
  { label: 'Саундхиллинг',         value: 'sound_healing' },
  { label: 'Арт-практики',         value: 'art' },
  { label: 'Нарративные практики', value: 'narrative' },
  { label: 'Движение',             value: 'movement' },
]

export const DIFFICULTY_OPTIONS: { label: string; value: string }[] = [
  { label: 'Начальная', value: 'beginner' },
  { label: 'Средняя',   value: 'medium' },
  { label: 'Высокая',   value: 'high' },
]

export interface StyleOption {
  label: string
  value: string
}

// Style -> direction map. ONLY directions that have styles are keyed.
// Other directions (breathwork / somatic / tantra / sound_healing / art /
// narrative / movement) have NO styles — code branches must hide the style
// selector when STYLE_OPTIONS_BY_DIRECTION[direction] is undefined.
// Mirrors the future backend practice_allowed_styles with direction scoping
// (handoff §9 B-2).
export const STYLE_OPTIONS_BY_DIRECTION: Partial<Record<PracticeDirection, StyleOption[]>> = {
  meditation: [
    { label: 'Медитация молчания',    value: 'silence' },
    { label: 'Медитация присутствия', value: 'presence' },
    { label: 'Звуковая медитация',    value: 'sound' },
    { label: 'Даосская медитация',    value: 'taoist' },
  ],
  yoga: [
    { label: 'Йога-нидра',     value: 'nidra' },
    { label: 'Инь-йога',       value: 'yin' },
    { label: 'Хатха-йога',     value: 'hatha' },
    { label: 'Виньяса',        value: 'vinyasa' },
    { label: 'Кундалини-йога', value: 'kundalini' },
    { label: 'Аштанга-йога',   value: 'ashtanga' },
  ],
  circles: [
    { label: 'Женский круг', value: 'womens' },
    { label: 'Мужской круг', value: 'mens' },
    { label: 'Круг шеринга', value: 'sharing' },
  ],
}

/** Returns the style options for a given direction, or [] when the
 *  direction has no styles. */
export function stylesForDirection(direction: PracticeDirection | undefined | null): StyleOption[] {
  if (!direction) return []
  return STYLE_OPTIONS_BY_DIRECTION[direction] ?? []
}

/** True when the direction has at least one style — used by filter / forms
 *  to decide whether to render the "Вид практики" selector. */
export function directionHasStyles(direction: PracticeDirection | undefined | null): boolean {
  return stylesForDirection(direction).length > 0
}
