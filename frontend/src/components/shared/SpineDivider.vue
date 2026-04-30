<!--
  VELO Frontend — SpineDivider (S2-S3 SPEEDRUN MEGA-2 §C36)

  Date label centered between connector dots, used as date header in
  Diary timeline view. Path Y MEDIUM — text-glyph arrows (▶ ◀) instead of
  ornate SVG chevrons; SVG ornament deferred to S5+ NIT.
-->

<template>
  <div class="spine-divider">
    <span
      class="spine-divider__dot"
      aria-hidden="true"
    />
    <span class="spine-divider__label">▶ {{ date }} ◀</span>
    <span
      class="spine-divider__dot"
      aria-hidden="true"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{ date: string }>()
</script>

<style scoped>
.spine-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) 0;
}

.spine-divider__dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--text-secondary);
  opacity: 0.4;
}

.spine-divider__label {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  color: var(--text-primary);
  letter-spacing: 0.04em;
}
</style>
