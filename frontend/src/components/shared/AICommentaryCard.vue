<!--
  VELO Frontend — AICommentaryCard (S2-S3 SPEEDRUN MEGA-2 §C45)

  Mint-tagged AI-commentary card. v1: always isPlaceholder=true with
  static text per BACKEND-COORDINATION § A.8 mock.
-->

<template>
  <article class="aic">
    <span class="aic__chip">
      <IconBrain :size="16" />
      <span>VELO AI</span>
    </span>
    <h3 class="aic__title">
      {{ title }}
    </h3>
    <p class="aic__body">
      {{ body }}
    </p>
    <p
      v-if="isPlaceholder"
      class="aic__hint"
    >
      Это пример комментария. Реальная аналитика появится позже.
    </p>
  </article>
</template>

<script setup lang="ts">
import { IconBrain } from '@/components/icons'

withDefaults(
  defineProps<{
    title: string
    body: string
    isPlaceholder?: boolean
  }>(),
  { isPlaceholder: true },
)
</script>

<style scoped>
.aic {
  background: var(--surface-default);
  border: 1px solid var(--mint-primary, var(--text-primary));
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.aic__chip {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: var(--mint-primary, var(--surface-steel-alpha-15));
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-family: var(--font-body);
  font-weight: 500;
}

.aic__title {
  font-family: var(--font-heading);
  font-size: var(--text-base);
  margin: 0;
  font-weight: 400;
  color: var(--text-primary);
}

.aic__body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--text-primary);
  margin: 0;
}

.aic__hint {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin: 0;
}
</style>
