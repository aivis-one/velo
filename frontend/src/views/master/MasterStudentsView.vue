<!--
  VELO Frontend -- MasterStudentsView (Master DS, 2026-06-11)

  "Мои ученики" — the master's students list. Reached from the dashboard row.
  Rendered inside MasterShell.

  STUB: there is no students/CRM backend yet (no aggregate of who attends a
  master's practices). The list below is placeholder data and documents the
  contract for Zod (roadmap: Agent-Velo/master-ds-zod-roadmap.md):
    Student { id, name, practices_count, needs_attention }
  Search filters the loaded list client-side. The message action opens the
  shared (stub) send-message sheet.
-->

<template>
  <div class="students">
    <VHeader title="Мои ученики" show-back @back="router.push({ name: 'master-dashboard' })" />

    <div class="students__content">
      <!-- Loading -->
      <div v-if="loading" class="students__state">
        <VLoader size="lg" />
      </div>

      <!-- Error -->
      <VEmptyState
        v-else-if="error"
        icon="warning"
        title="Не удалось загрузить учеников"
        :description="error"
      >
        <VButton size="sm" variant="outline" @click="load">Повторить</VButton>
      </VEmptyState>

      <template v-else>
        <!-- Search (glass pill; client-side filter over the loaded list) -->
        <div class="students__search">
          <input
            v-model="query"
            class="students__search-input"
            type="text"
            placeholder="Искать…"
            aria-label="Искать ученика"
          />
          <span class="students__search-btn" aria-hidden="true"><IconSearch :size="18" /></span>
        </div>

        <!-- List -->
        <div
          v-for="student in filtered"
          :key="student.id"
          class="students__row"
          role="button"
          tabindex="0"
          @click="openProfile(student)"
          @keydown.enter.space.prevent="openProfile(student)"
        >
          <VAvatar :name="student.name" size="md" />
          <div class="students__body">
            <div class="students__name">{{ student.name }}</div>
            <div class="students__meta">Практик: {{ student.practices_count }}</div>
            <span v-if="student.needs_attention" class="students__attn">
              <IconWarning :size="14" />Требует внимания
            </span>
          </div>
          <button
            class="students__msg"
            aria-label="Написать сообщение"
            @click.stop="openMessage(student.name)"
          >
            <IconMessages :size="22" />
          </button>
        </div>

        <!-- Empty: no students at all vs no search match -->
        <VEmptyState
          v-if="students.length === 0"
          icon="group"
          title="Учеников пока нет"
          description="Они появятся после первых практик"
        />
        <VEmptyState
          v-else-if="filtered.length === 0"
          icon="group"
          title="Никого не найдено"
          description="Попробуйте изменить запрос"
        />
      </template>
    </div>

    <SendMessageModal :open="msgOpen" :name="msgName" @close="msgOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VAvatar, VEmptyState, VLoader, VButton } from '@/components/ui'
import { IconSearch, IconWarning, IconMessages } from '@/components/icons'
import SendMessageModal from '@/components/shared/SendMessageModal.vue'
import { getStudents } from '@/api/masters'
import type { StudentListItem } from '@/api/types'

const router = useRouter()

// -- Students (E5: GET /masters/me/students). Search filters the loaded page
//    client-side; needs_attention drives the inline warning badge. --
const students = ref<StudentListItem[]>([])
const loading = ref(true)
const error = ref('')

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    const res = await getStudents()
    students.value = res.items
  } catch {
    error.value = 'Попробуйте ещё раз'
  } finally {
    loading.value = false
  }
}
onMounted(load)

const query = ref('')
const filtered = computed((): StudentListItem[] => {
  const q = query.value.trim().toLowerCase()
  if (!q) return students.value
  return students.value.filter((s) => s.name.toLowerCase().includes(q))
})

// The detail endpoint carries no name → pass it forward from the list row.
function openProfile(student: StudentListItem): void {
  router.push({
    name: 'master-student-profile',
    params: { id: student.id },
    query: { name: student.name },
  })
}

// -- Send-message sheet (stub — E4 messaging not delivered) --
const msgOpen = ref(false)
const msgName = ref('')
function openMessage(name: string): void {
  msgName.value = name
  msgOpen.value = true
}
</script>

<style scoped>
.students {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.students__content {
  flex: 1;
  /* F-5 rail sync: ride MobileLayout's 24px rail (no local h-padding).
     Top trimmed to raise the search closer to the header (design «3 Students»). */
  padding: var(--space-2) 0 var(--space-4);
  display: flex;
  flex-direction: column;
  /* Inter-card spacing tightened to the design (~10px → nearest token). */
  gap: var(--space-2);
}

.students__state {
  display: flex;
  justify-content: center;
  padding: var(--space-6) 0;
}

/* -- Search (glass pill + primary circle button) -- */
.students__search {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 50px;
  /* Gap to the first student card (design ~25px = space-2 row gap + this). */
  margin-bottom: var(--space-4);
  padding: 5px 5px 5px var(--space-5);
  background: var(--velo-glass-blue-15);
  border: 1px solid var(--velo-glass-border);
  border-radius: var(--radius-xl);
  /* Frost the busy mandala behind the translucent fill so the interior reads
     clean, not muddy (design «3 Students» uses a backdrop blur). */
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  /* White halo behind the pill (design drop-shadow → DS glow token). */
  box-shadow: var(--velo-shadow-glow);
}

.students__search-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: var(--text-16, 16px);
  color: var(--velo-text-primary);
}

.students__search-input::placeholder {
  color: var(--velo-text-muted);
}

.students__search-input:focus {
  outline: none;
}

.students__search-btn {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--velo-primary);
  color: var(--velo-white);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* -- Student row -- */
.students__row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: 13px var(--space-4);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.students__row:active {
  opacity: 0.85;
}

.students__body {
  flex: 1;
  min-width: 0;
}

.students__name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.students__meta {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin-top: 2px;
}

.students__attn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 6px;
  padding: 3px 10px;
  border-radius: var(--velo-radius-badge);
  background: var(--velo-warning-bg);
  color: var(--velo-peach-500);
  font-size: var(--text-xs);
}

.students__attn svg {
  color: var(--velo-warning);
}

.students__msg {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  border: none;
  border-radius: var(--radius-full);
  background: var(--velo-primary);
  color: var(--velo-white);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.students__msg:active {
  opacity: 0.85;
}
</style>
