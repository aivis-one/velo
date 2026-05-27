// Shared practice form options.
// Used by CreatePracticeView and EditPracticeView to avoid duplication (W-2).

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

// -- Calendar taxonomy options --
// direction / difficulty are required Practice fields (stored in
// data.taxonomy on the backend). Values MUST match the backend allowed
// lists in config.py (practice_allowed_directions / _difficulties).
// Shared by the master create/edit forms and the Calendar filter UI.

export const DIRECTION_OPTIONS: { label: string; value: string }[] = [
  { label: 'Медитация',           value: 'meditation' },
  { label: 'Йога',                value: 'yoga' },
  { label: 'Дыхательные практики', value: 'breathwork' },
  { label: 'Соматика',            value: 'somatic' },
  { label: 'Тантра',              value: 'tantra' },
  { label: 'Женский круг',        value: 'womens_circle' },
  { label: 'Мужской круг',        value: 'mens_circle' },
  { label: 'Кундалини',           value: 'kundalini' },
]

export const DIFFICULTY_OPTIONS: { label: string; value: string }[] = [
  { label: 'Начальная', value: 'beginner' },
  { label: 'Средняя',   value: 'medium' },
  { label: 'Высокая',   value: 'high' },
]

// PLACEHOLDER list -- mirrors backend config.practice_allowed_styles.
// Values MUST match that list; to be replaced with the real catalog by
// the client. Used by the master create/edit forms and the Calendar filter.
export const STYLE_OPTIONS: { label: string; value: string }[] = [
  { label: 'Хатха йога',    value: 'hatha' },
  { label: 'Кундалини йога', value: 'kundalini' },
  { label: 'Виньяса флоу',  value: 'vinyasa' },
  { label: 'Инь йога',      value: 'yin' },
]
