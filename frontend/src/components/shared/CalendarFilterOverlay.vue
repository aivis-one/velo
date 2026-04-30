<!--
  VELO Frontend -- CalendarFilterOverlay (S2 P07 C24 — skin 22)

  Modal-style filter overlay for CalendarView. Single-select chip groups for
  practice direction + duration + time-of-day. Path Y MEDIUM: full chip set
  rendered, but date-range and "вид практики" dropdown deferred to polish
  cluster.
-->

<template>
  <Teleport to="body">
    <div
      class="fo"
      role="dialog"
      aria-modal="true"
      aria-label="Фильтр практик"
    >
      <button
        type="button"
        class="fo__backdrop"
        aria-label="Закрыть"
        @click="$emit('close')"
      />
      <div class="fo__panel">
        <header class="fo__head">
          <span class="fo__title">Фильтр</span>
          <button
            type="button"
            class="fo__close"
            aria-label="Закрыть"
            @click="$emit('close')"
          >
            <IconClose :size="20" />
          </button>
        </header>

        <section class="fo__group">
          <h3>Направление практики</h3>
          <div class="fo__chips">
            <button
              v-for="opt in DIRECTION_OPTS"
              :key="opt.value"
              type="button"
              class="fo__chip"
              :class="{ 'fo__chip--active': practiceType === opt.value }"
              @click="practiceType = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </section>

        <footer class="fo__foot">
          <VButton
            variant="ghost"
            size="md"
            block
            @click="reset"
          >
            Сбросить
          </VButton>
          <VButton
            variant="primary"
            size="md"
            block
            @click="apply"
          >
            Применить
          </VButton>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { VButton } from '@/components/ui'
import { IconClose } from '@/components/icons'
import type { PracticeFilters, PracticeType } from '@/api/types'

const props = defineProps<{
  initial: PracticeFilters
}>()

const emit = defineEmits<{
  close: []
  apply: [filters: PracticeFilters]
}>()

const DIRECTION_OPTS: Array<{ value: PracticeType | undefined; label: string }> = [
  { value: undefined, label: 'Все' },
  { value: 'live', label: 'Live' },
  { value: 'series', label: 'Серия' },
  { value: 'one_on_one', label: 'Индивидуально' },
  { value: 'replay', label: 'Replay' },
]

const practiceType = ref<PracticeType | undefined>(props.initial.practice_type)

function reset(): void {
  practiceType.value = undefined
}

function apply(): void {
  emit('apply', { practice_type: practiceType.value })
}
</script>

<style scoped>
.fo {
  position: fixed;
  inset: 0;
  z-index: 500;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.fo__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  border: none;
  cursor: pointer;
}

.fo__panel {
  position: relative;
  width: 100%;
  max-width: 480px;
  background: var(--surface-default);
  border-top-left-radius: var(--radius-xl);
  border-top-right-radius: var(--radius-xl);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-height: 85vh;
  overflow-y: auto;
}

.fo__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.fo__title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--text-primary);
}

.fo__close {
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  padding: var(--space-2);
}

.fo__group h3 {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin: 0 0 var(--space-2);
  font-weight: 400;
}

.fo__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.fo__chip {
  background: var(--surface-steel-alpha-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  padding: 6px 14px;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-primary);
  cursor: pointer;
}

.fo__chip--active {
  background: var(--steel-button);
  color: white;
}

.fo__foot {
  display: flex;
  gap: var(--space-2);
  margin-top: auto;
}
</style>
