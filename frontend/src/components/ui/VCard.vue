<!--
  VELO Frontend -- VCard Component (Phase F2.1)

  Slot-based container card. Matches mockup .card styles.

  Usage:
    <VCard>Content here</VCard>
    <VCard clickable @click="open(id)">Clickable card</VCard>
    <VCard :padding="false">No padding (e.g. for images)</VCard>
-->

<template>
  <div
    class="v-card"
    :class="{
      'v-card--clickable': clickable,
      'v-card--no-padding': !padding,
    }"
    @click="clickable ? $emit('click', $event) : undefined"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    clickable?: boolean
    padding?: boolean
  }>(),
  {
    clickable: false,
    padding: true,
  },
)

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<style scoped>
.v-card {
  /* White surface standard (Figma 2026-06): opaque white fill + 1px white
     border + radius-md. Replaces the old glass fill (--velo-bg-card) + blue
     border (--velo-border), which no longer match the design. */
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  transition: all var(--transition-base);
}

.v-card--clickable {
  cursor: pointer;
}

.v-card--clickable:active {
  transform: translateY(0);
}

.v-card--no-padding {
  padding: 0;
}
</style>
