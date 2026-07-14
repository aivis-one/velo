<!--
  VELO Frontend -- AdminCatalogView (batch P, P2; made editable R5 stage 3c)

  The practice-taxonomy catalog: each direction with its styles (виды).
  Reached from the Admin dashboard «Каталог практик» row.

  R5 stage 3c: now editable, backed by the stage-2 admin CRUD API
  (GET/POST/PATCH /api/v1/admin/taxonomy/*) -- add direction, add style
  under a direction, edit label, deactivate/reactivate (is_active toggle,
  NEVER a hard delete -- existing masters' stored methods strings must keep
  resolving against a retired direction/style). Source badge (seed/custom)
  shows which rows came from the R5 migration vs were added here or
  auto-promoted (R5 stage 4) from an approved custom method.

  Scope: MASTER METHODS catalog only. Does not touch practice-creation
  taxonomy (settings.practice_allowed_directions / config) -- unrelated,
  untouched by this screen (operator decision, batch R R5).

  Every mutation refetches the full catalog rather than patching local state
  -- simplest correct approach for a low-traffic admin screen with a nested
  direction->styles shape.
-->

<template>
  <div class="admin-catalog">
    <header class="admin-catalog__top">
      <VBackButton @click="router.back()" />
      <span class="admin-catalog__title">Каталог практик</span>
    </header>

    <VCard class="admin-catalog__note" padding="none">
      Управление каталогом. Изменения видны мастерам сразу при выборе методов.
    </VCard>

    <!-- Add direction -->
    <VCard class="admin-catalog__add" padding="none">
      <VInput
        v-model="newDirectionLabel"
        placeholder="Новое направление…"
        class="admin-catalog__add-input"
      />
      <VButton
        variant="primary"
        size="sm"
        :loading="addingDirection"
        :disabled="!newDirectionLabel.trim()"
        @click="addDirection"
      >
        + Добавить
      </VButton>
    </VCard>

    <div v-if="loading" class="admin-catalog__loader"><VLoader size="lg" /></div>

    <VEmptyState
      v-else-if="error"
      icon="warning"
      title="Не удалось загрузить каталог"
      description="Проверьте соединение и попробуйте ещё раз"
    >
      <template #action><VButton variant="primary" @click="load">Повторить</VButton></template>
    </VEmptyState>

    <VCard
      v-else
      v-for="dir in directions"
      :key="dir.id"
      class="admin-catalog__dir"
      :class="{ 'admin-catalog__dir--inactive': !dir.is_active }"
      padding="none"
    >
      <div class="admin-catalog__dir-head">
        <template v-if="editingDirectionId === dir.id">
          <VInput v-model="draftLabel" class="admin-catalog__edit-input" />
          <button type="button" class="admin-catalog__icon-btn" aria-label="Сохранить" @click="saveDirectionLabel(dir)">
            <IconCheck :size="18" />
          </button>
          <button type="button" class="admin-catalog__icon-btn" aria-label="Отмена" @click="cancelEdit">
            <IconClose :size="18" />
          </button>
        </template>
        <template v-else>
          <span class="admin-catalog__dir-title">{{ dir.label }}</span>
          <VBadge :variant="dir.source === 'seed' ? 'muted' : 'blue'">{{ dir.source }}</VBadge>
          <button type="button" class="admin-catalog__icon-btn" aria-label="Редактировать" @click="startEditDirection(dir)">
            <IconEdit :size="18" />
          </button>
          <VButton
            v-if="dir.is_active"
            variant="ghost"
            size="sm"
            :loading="togglingId === dir.id"
            @click="toggleDirectionActive(dir)"
          >
            Деактивировать
          </VButton>
          <VButton
            v-else
            variant="secondary"
            size="sm"
            :loading="togglingId === dir.id"
            @click="toggleDirectionActive(dir)"
          >
            Активировать
          </VButton>
        </template>
      </div>

      <template v-if="dir.is_active">
        <div v-if="dir.styles.length" class="admin-catalog__chips">
          <VChip
            v-for="st in dir.styles"
            :key="st.id"
            size="sm"
            :class="{ 'admin-catalog__chip--inactive': !st.is_active }"
            clickable
            @click="toggleStyleActive(st)"
          >
            {{ st.label }} {{ st.is_active ? '✕' : '· Активировать' }}
          </VChip>
        </div>
        <div v-else class="admin-catalog__none">Без видов</div>

        <div class="admin-catalog__add-style">
          <VInput
            v-model="newStyleLabel[dir.id]"
            placeholder="Новый вид…"
            class="admin-catalog__add-style-input"
          />
          <VButton
            variant="secondary"
            size="sm"
            :loading="addingStyleFor === dir.id"
            :disabled="!(newStyleLabel[dir.id] ?? '').trim()"
            @click="addStyle(dir)"
          >
            +
          </VButton>
        </div>
      </template>
      <div v-else class="admin-catalog__none">
        Неактивно — скрыто у мастеров, старые методы сохраняются
      </div>
    </VCard>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VBackButton, VCard, VChip, VInput, VButton, VBadge, VLoader, VEmptyState } from '@/components/ui'
import { IconEdit, IconClose, IconCheck } from '@/components/icons'
import { useToast } from '@/composables/useToast'
import { ApiResponseError } from '@/api/client'
import {
  getFullTaxonomy,
  createTaxonomyDirection,
  createTaxonomyStyle,
  updateTaxonomyDirection,
  updateTaxonomyStyle,
  type TaxonomyDirectionItem,
  type TaxonomyStyleItem,
} from '@/api/taxonomy'

const router = useRouter()
const toast = useToast()

const directions = ref<TaxonomyDirectionItem[]>([])
const loading = ref(false)
const error = ref(false)

async function load(): Promise<void> {
  loading.value = true
  error.value = false
  try {
    const res = await getFullTaxonomy()
    directions.value = res.directions
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

// -- Add direction --
const newDirectionLabel = ref('')
const addingDirection = ref(false)

/** Cyrillic labels have no natural ASCII slug and nothing reads `value` for
 *  a display purpose (every consumer shows `label`) -- same synthetic-slug
 *  approach as the backend's stage-4 auto-promote. */
function genSlug(): string {
  return `custom_${Math.random().toString(36).slice(2, 10)}`
}

async function addDirection(): Promise<void> {
  const label = newDirectionLabel.value.trim()
  if (!label || addingDirection.value) return
  addingDirection.value = true
  try {
    await createTaxonomyDirection({ value: genSlug(), label })
    newDirectionLabel.value = ''
    toast.success('Направление добавлено')
    await load()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось добавить направление')
  } finally {
    addingDirection.value = false
  }
}

// -- Add style (per direction) --
const newStyleLabel = reactive<Record<string, string>>({})
const addingStyleFor = ref<string | null>(null)

async function addStyle(dir: TaxonomyDirectionItem): Promise<void> {
  const label = (newStyleLabel[dir.id] ?? '').trim()
  if (!label || addingStyleFor.value) return
  addingStyleFor.value = dir.id
  try {
    await createTaxonomyStyle(dir.id, { value: genSlug(), label })
    newStyleLabel[dir.id] = ''
    toast.success('Вид добавлен')
    await load()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось добавить вид')
  } finally {
    addingStyleFor.value = null
  }
}

// -- Edit label (direction only -- styles are short enough not to need it
//    from this screen; deactivate/reactivate covers the common style edit) --
const editingDirectionId = ref<string | null>(null)
const draftLabel = ref('')

function startEditDirection(dir: TaxonomyDirectionItem): void {
  editingDirectionId.value = dir.id
  draftLabel.value = dir.label
}

function cancelEdit(): void {
  editingDirectionId.value = null
}

async function saveDirectionLabel(dir: TaxonomyDirectionItem): Promise<void> {
  const label = draftLabel.value.trim()
  if (!label) return
  try {
    await updateTaxonomyDirection(dir.id, { label })
    editingDirectionId.value = null
    toast.success('Сохранено')
    await load()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось сохранить')
  }
}

// -- Deactivate / reactivate --
const togglingId = ref<string | null>(null)

async function toggleDirectionActive(dir: TaxonomyDirectionItem): Promise<void> {
  if (togglingId.value) return
  togglingId.value = dir.id
  try {
    await updateTaxonomyDirection(dir.id, { is_active: !dir.is_active })
    await load()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось изменить статус')
  } finally {
    togglingId.value = null
  }
}

async function toggleStyleActive(st: TaxonomyStyleItem): Promise<void> {
  if (togglingId.value) return
  togglingId.value = st.id
  try {
    await updateTaxonomyStyle(st.id, { is_active: !st.is_active })
    await load()
  } catch (e) {
    toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось изменить статус')
  } finally {
    togglingId.value = null
  }
}

onMounted(load)
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

.admin-catalog__loader {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
}

/* -- Add direction -- */
.admin-catalog__add {
  padding: var(--space-3);
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.admin-catalog__add-input {
  flex: 1;
  min-width: 0;
  margin-bottom: 0;
}

.admin-catalog__dir {
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.admin-catalog__dir--inactive {
  opacity: 0.6;
}

.admin-catalog__dir-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.admin-catalog__dir-title {
  flex: 1;
  min-width: 0;
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
}

.admin-catalog__edit-input {
  flex: 1;
  min-width: 0;
  margin-bottom: 0;
}

.admin-catalog__icon-btn {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--velo-glass-blue-15);
  color: var(--velo-primary);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
}

.admin-catalog__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.admin-catalog__chip--inactive {
  opacity: 0.55;
}

.admin-catalog__none {
  font-size: var(--text-xs);
  color: var(--velo-text-muted);
}

.admin-catalog__add-style {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.admin-catalog__add-style-input {
  flex: 1;
  min-width: 0;
  margin-bottom: 0;
}
</style>
