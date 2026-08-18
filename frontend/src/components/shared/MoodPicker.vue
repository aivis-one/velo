<!--
  VELO Frontend -- MoodPicker (B57, PROMPT No761)

  The "Мое состояние" control: three discrete face buttons, one optionally
  selected. Selecting the already-selected one CLEARS it, because the field is
  optional by the owner's spec and a person who taps by accident needs a way
  back to "not answered".

  ⚠ NOT A DUPLICATE OF `MoodSlider.vue`, which sits beside it in this folder.
  That one is a 1..10 SCORE rendered as a slider track with three zone icons
  (check-in + feedback). This is a three-way CHOICE with no numeric value and
  no track. They look adjacent and are different controls.

  Lives in `components/shared/` rather than `components/ui/` on the measured
  house split: `ui/` is the content-agnostic primitive barrel, `shared/` holds
  composed feature pieces (MoodSlider, DatePickerSheet, TimePickerSheet,
  MethodTaxonomyPicker all live here and are imported by path, not from a
  barrel). This component owns a specific artwork set, so it is not a primitive.

  Colour: each state's accent comes from `--velo-rating-*` via
  `ACTIVITY_MOODS[].colorVar` -- see `utils/activityEntry.ts` for why those and
  not the similarly-named `--velo-mood-*`. No hex appears in this file.

  Usage:
    <MoodPicker v-model="mood" />
    <MoodPicker v-model="mood" :size="48" aria-label="Настроение" />
-->

<template>
  <div class="mood-picker" role="radiogroup" :aria-label="ariaLabel" @keydown="onKeydown">
    <button
      v-for="(opt, i) in ACTIVITY_MOODS"
      :key="opt.key"
      ref="optionEls"
      type="button"
      class="mood-picker__opt"
      role="radio"
      :aria-checked="modelValue === opt.key"
      :aria-label="opt.label"
      :tabindex="rovingIndex === i ? 0 : -1"
      :style="swatch(opt)"
      @click="select(i)"
    >
      <IconActivityMood :mood="opt.key" :selected="modelValue === opt.key" :size="size" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { IconActivityMood } from '@/components/icons'
import { ACTIVITY_MOODS, type ActivityMood, type ActivityMoodOption } from '@/utils/activityEntry'

const props = withDefaults(
  defineProps<{
    /** The chosen state, or null when the person has not answered. */
    modelValue?: ActivityMood | null
    /** Rendered glyph edge in px. 63 is the design size (measured, 01.svg). */
    size?: number
    ariaLabel?: string
  }>(),
  { modelValue: null, size: 63, ariaLabel: 'Мое состояние' },
)

const emit = defineEmits<{
  'update:modelValue': [value: ActivityMood | null]
}>()

/**
 * `role="radiogroup"` + `role="radio"` implies the ARIA APG roving-tabindex
 * contract -- exactly one option in the Tab sequence, arrow keys move the
 * roving stop, Home/End jump to the ends (found missing in verification: the
 * roles were correct, the keyboard contract behind them was not built).
 * `rovingIndex` starts at whichever option is selected so re-entering the
 * group by Tab lands on the current answer, not always the first face.
 */
const rovingIndex = ref(
  Math.max(
    0,
    ACTIVITY_MOODS.findIndex((o) => o.key === props.modelValue),
  ),
)
const optionEls = ref<HTMLButtonElement[]>([])

function select(i: number): void {
  rovingIndex.value = i
  const opt = ACTIVITY_MOODS[i]
  if (opt) emit('update:modelValue', props.modelValue === opt.key ? null : opt.key)
}

function focusOption(i: number): void {
  rovingIndex.value = i
  optionEls.value[i]?.focus()
}

function onKeydown(e: KeyboardEvent): void {
  const last = ACTIVITY_MOODS.length - 1
  switch (e.key) {
    case 'ArrowRight':
    case 'ArrowDown':
      e.preventDefault()
      focusOption(rovingIndex.value >= last ? 0 : rovingIndex.value + 1)
      break
    case 'ArrowLeft':
    case 'ArrowUp':
      e.preventDefault()
      focusOption(rovingIndex.value <= 0 ? last : rovingIndex.value - 1)
      break
    case 'Home':
      e.preventDefault()
      focusOption(0)
      break
    case 'End':
      e.preventDefault()
      focusOption(last)
      break
    case ' ':
    case 'Enter':
      // Native <button> already activates on Space/Enter via click; this
      // exists only so the key does not also fall through unhandled.
      break
    default:
      break
  }
}

/**
 * Selection is expressed as a swap of two custom properties and nothing else:
 * resting = white circle + coloured face, selected = coloured circle + white
 * face. The glyph component reads both and never learns which state it is in.
 */
function swatch(opt: ActivityMoodOption): Record<string, string> {
  const selected = props.modelValue === opt.key
  return {
    '--vam-face': selected ? opt.colorVar : 'var(--velo-white)',
    '--vam-ink': selected ? 'var(--velo-white)' : opt.colorVar,
  }
}
</script>

<style scoped>
.mood-picker {
  display: flex;
  justify-content: center;
  /* 25px measured between adjacent 63px circles in 01/02/03.svg; no spacing
     token matches (--space-5 is 24), so the design value is kept literal and
     named here rather than rounded to make a token fit. */
  gap: 25px;
}

.mood-picker__opt {
  padding: 0;
  border: none;
  background: none;
  border-radius: var(--radius-full);
  line-height: 0;
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.mood-picker__opt:hover {
  transform: scale(1.06);
}

.mood-picker__opt:focus-visible {
  /* Matches the established idiom (VTabBar/VAdminTabBar), not a new value. */
  outline: 2px solid var(--velo-primary);
  outline-offset: 2px;
}
</style>
