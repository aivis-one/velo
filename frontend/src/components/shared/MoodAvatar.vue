<!--
  VELO Frontend -- MoodAvatar (Master DS, 2026-06-11)

  Mood face used as a participant avatar on the master's check-ins / student
  screens. Reuses the diary's mood-face assets (IconMoodLow/Mid/High — pastel
  gradient circles with a face) and the shared 1..10 -> low/mid/high mapping
  (moodZoneFromScore), so the mood face matches the diary everywhere.

  Usage: <MoodAvatar :mood="checkin.mood" :size="46" />
-->

<template>
  <component :is="moodIcon" :size="size" />
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { IconMoodLow, IconMoodMid, IconMoodHigh } from '@/components/icons'
import { moodZoneFromScore } from '@/utils/displayHelpers'

const props = withDefaults(
  defineProps<{
    /** Mood score 1..10 (as stored on Checkin). */
    mood: number
    size?: number
  }>(),
  { size: 46 },
)

const moodIcon = computed<Component>(() => {
  const zone = moodZoneFromScore(props.mood)
  if (zone === 'low') return IconMoodLow
  if (zone === 'high') return IconMoodHigh
  return IconMoodMid
})
</script>
