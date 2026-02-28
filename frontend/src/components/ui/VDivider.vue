<!--
  VELO Frontend -- VDivider Component (Phase F2.1)

  Horizontal divider. Optionally shows centered text.
  Matches mockup .divider styles.

  Usage:
    <VDivider />
    <VDivider label="или" />
-->

<template>
  <div v-if="label" class="v-divider v-divider--labeled">
    <span class="v-divider__text">{{ label }}</span>
  </div>
  <hr v-else class="v-divider" />
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string
  }>(),
  {
    label: '',
  },
)
</script>

<style scoped>
.v-divider {
  border: none;
  border-top: 1px solid var(--velo-border);
  margin: var(--space-4) 0;
}

.v-divider--labeled {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  color: var(--velo-text-muted);
  font-size: var(--text-sm);
  margin: var(--space-6) 0;
  border: none;
}

.v-divider--labeled::before,
.v-divider--labeled::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--velo-border);
}

.v-divider__text {
  white-space: nowrap;
}
</style>
