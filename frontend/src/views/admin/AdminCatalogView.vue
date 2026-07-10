<!--
  VELO Frontend -- AdminCatalogView (batch P, P2)

  READ-ONLY view of the practice taxonomy: each direction with its styles (виды).
  Reached from the Admin dashboard «Каталог практик» row.

  Editing is intentionally NOT here yet — an admin-editable catalog needs a
  runtime backend store + endpoint (A4 / Zod: the source of truth moves off the
  static config/enum). Until then this is an honest read-only view. No dead
  add/delete controls.

  CLEAN WIRING: the taxonomy is built ONCE in `buildCatalog()` from the hardcoded
  practiceOptions. When Zod's `GET /catalog` lands, that single function (or the
  `catalog` ref seed) is the ONLY swap point — the template renders a
  CatalogDirection[] regardless of source.
-->

<template>
  <div class="admin-catalog">
    <header class="admin-catalog__top">
      <VBackButton @click="router.back()" />
      <span class="admin-catalog__title">Каталог практик</span>
    </header>

    <!-- Honest note: read-only until the catalog backend lands. -->
    <VCard class="admin-catalog__note" padding="none">
      Просмотр каталога. Редактирование появится с бэкендом каталога.
    </VCard>

    <VCard
      v-for="dir in catalog"
      :key="dir.value"
      class="admin-catalog__dir"
      padding="none"
    >
      <div class="admin-catalog__dir-title">{{ dir.label }}</div>
      <div v-if="dir.styles.length" class="admin-catalog__chips">
        <VChip v-for="st in dir.styles" :key="st.value" size="sm">{{ st.label }}</VChip>
      </div>
      <div v-else class="admin-catalog__none">Без видов</div>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { VBackButton, VCard, VChip } from '@/components/ui'
import { DIRECTION_OPTIONS, stylesForDirection } from '@/utils/practiceOptions'

const router = useRouter()

interface CatalogStyle {
  value: string
  label: string
}
interface CatalogDirection {
  value: string
  label: string
  styles: CatalogStyle[]
}

// SINGLE SWAP POINT for the future `GET /catalog` (A4/Zod): replace this
// hardcoded build with the fetched catalog (`catalog.value = await getCatalog()`
// in onMounted) and the template below renders unchanged.
function buildCatalog(): CatalogDirection[] {
  return DIRECTION_OPTIONS.map((dir) => ({
    value: dir.value,
    label: dir.label,
    styles: stylesForDirection(dir.value).map((st) => ({ value: st.value, label: st.label })),
  }))
}

const catalog = ref<CatalogDirection[]>(buildCatalog())
</script>

<style scoped>
.admin-catalog {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.admin-catalog__top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: var(--velo-size-44);
}

.admin-catalog__title {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.admin-catalog__note {
  padding: var(--space-3);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  line-height: 1.4;
}

.admin-catalog__dir {
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.admin-catalog__dir-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.admin-catalog__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.admin-catalog__none {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}
</style>
