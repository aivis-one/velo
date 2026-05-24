/**
 * VELO Frontend -- Icon Components barrel export (DS-5)
 *
 * SVG icons from Design_prototype/assets/icons/ as Vue components.
 * Most icons use currentColor fill and accept a `size` prop (default 24).
 * Exception: the mood faces (IconMoodLow/Mid/High) are illustrative assets
 * that keep their own pastel gradients (default size 40), like VeloLogo.
 *
 * Usage:
 *   import { IconHome, IconCalendar } from '@/components/icons'
 */

export { default as IconHome } from './IconHome.vue'
export { default as IconCalendar } from './IconCalendar.vue'
export { default as IconDiary } from './IconDiary.vue'
export { default as IconProfile } from './IconProfile.vue'
export { default as IconGroup } from './IconGroup.vue'
export { default as IconWarning } from './IconWarning.vue'
export { default as IconBrain } from './IconBrain.vue'
export { default as IconClock } from './IconClock.vue'
export { default as IconMeditation } from './IconMeditation.vue'
export { default as IconBreathwork } from './IconBreathwork.vue'
export { default as IconYoga } from './IconYoga.vue'
export { default as IconRatingConfused } from './IconRatingConfused.vue'
export { default as IconRatingGood } from './IconRatingGood.vue'
export { default as IconRatingFire } from './IconRatingFire.vue'
export { default as IconHeart } from './IconHeart.vue'
export { default as IconFeedback } from './IconFeedback.vue'
export { default as IconRuble } from './IconRuble.vue'
export { default as IconSuccess } from './IconSuccess.vue'
export { default as IconSupport } from './IconSupport.vue'

// -- Dashboard flow (DS-dashboard): monochrome glyphs (currentColor) --
export { default as IconCheck } from './IconCheck.vue'
export { default as IconArrowRight } from './IconArrowRight.vue'
export { default as IconClose } from './IconClose.vue'

// -- Mood faces: colored illustrative assets (own gradients, default size 40) --
export { default as IconMoodLow } from './IconMoodLow.vue'
export { default as IconMoodMid } from './IconMoodMid.vue'
export { default as IconMoodHigh } from './IconMoodHigh.vue'
