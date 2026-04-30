<!--
  VELO Frontend — RelationshipChain (S2-S3 SPEEDRUN MEGA-2 §C45)

  Horizontal chain of icons connected via white pill connectors.
  items = component refs to render in each circle.
-->

<template>
  <div class="chain">
    <template
      v-for="(item, idx) in items"
      :key="idx"
    >
      <span
        class="chain__node"
        :class="`chain__node--${item.kind}`"
      >
        <component
          :is="item.icon"
          :size="20"
        />
      </span>
      <span
        v-if="idx < items.length - 1"
        class="chain__link"
        aria-hidden="true"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  items: Array<{
    icon: Component
    kind: 'mood' | 'flame' | 'feather' | 'dream' | 'neutral'
  }>
}>()
</script>

<style scoped>
.chain {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  flex-wrap: wrap;
  padding: var(--space-3);
}

.chain__node {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--text-primary);
  background: var(--surface-default);
  color: var(--text-primary);
}

.chain__node--mood {
  background: var(--steel-button);
  color: white;
  border-color: var(--steel-button);
}

.chain__node--flame {
  background: var(--warm-deep);
  color: white;
  border-color: var(--warm-deep);
}

.chain__node--dream {
  background: var(--surface-steel-alpha-15);
}

.chain__node--feather {
  background: var(--surface-default);
}

.chain__link {
  width: 24px;
  height: 6px;
  border-radius: 3px;
  background: var(--surface-default);
  border: 1px solid var(--text-primary);
}
</style>
