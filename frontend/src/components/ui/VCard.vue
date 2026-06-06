<!--
  VELO Frontend -- VCard Component (Phase F2.1; padding variants 2026-06-06)

  Единый белый card-канон: opaque white + 1px --velo-border-card + --radius-md.
  Slot-контейнер для ВСЕХ белых карт/секций приложения (DS-governance).

  Usage:
    <VCard>Content</VCard>                     padding md (--space-4, деф)
    <VCard padding="sm">Compact</VCard>        padding --space-3
    <VCard padding="none">Edge-to-edge</VCard> padding 0 (свой паддинг на классе)
    <VCard clickable @click="open(id)">…</VCard>
  Доп. layout (flex/gap/cursor и т.п.) задаётся классом на самом <VCard> —
  Vue мержит class на корень .v-card.
-->

<template>
  <div
    class="v-card"
    :class="{
      'v-card--clickable': clickable,
      'v-card--pad-sm': padding === 'sm',
      'v-card--no-padding': padding === false || padding === 'none',
    }"
    :role="clickable ? 'button' : undefined"
    :tabindex="clickable ? 0 : undefined"
    @click="clickable ? $emit('click', $event) : undefined"
    @keydown.enter.space.prevent="clickable ? $emit('click', $event) : undefined"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    clickable?: boolean
    /** md (--space-4, деф) | sm (--space-3) | none/false (0, свой паддинг) | true=md */
    padding?: boolean | 'sm' | 'md' | 'none'
  }>(),
  {
    clickable: false,
    padding: true,
  },
)

defineEmits<{
  click: [event: MouseEvent | KeyboardEvent]
}>()
</script>

<style scoped>
.v-card {
  /* White surface standard (Figma 2026-06): opaque white fill + 1px white
     border + radius-md. Replaces the old glass fill (--velo-bg-card) + blue
     border (--velo-border), which no longer match the design. */
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
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

.v-card--pad-sm {
  padding: var(--space-3);
}

.v-card--no-padding {
  padding: 0;
}
</style>
