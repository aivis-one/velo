<!--
  VELO Frontend -- MasterSummaryView (Master DS, 2026-06-11; honesty-cleanup 2026-07-12)

  "Саммари недели" — the master's AI weekly insights, reached from the dashboard
  summary card ("Подробнее"). Rendered inside MasterShell.

  HONEST STUB: no master-AI / feedback-aggregation backend for the insight or key
  feedbacks -> both render honest placeholders (no fabricated numbers/names).
  Documents the contract for Zod: insight (string), key_feedbacks [{ rating, name,
  comment }]. «Требуют внимания» below is REAL (E5) and unaffected by this cleanup.
-->

<template>
  <div class="summary">
    <VHeader title="Саммари недели" show-back @back="router.push({ name: 'master-dashboard' })" />

    <div class="summary__content">
      <!-- AI insight (honest placeholder — no master-AI backend yet) -->
      <h2 class="velo-section-title">AI-инсайты за неделю</h2>
      <VCard>
        <p class="summary__insight">{{ insight }}</p>
      </VCard>

      <!-- Key feedbacks (honest empty-state — no feedback-aggregation backend yet) -->
      <h2 class="velo-section-title">Ключевые отзывы</h2>
      <VEmptyState variant="note" title="Отзывы появятся здесь, когда будут собраны" />

      <!-- Needs attention (REAL: the master's students with needs_attention).
           Each row taps through to the real student profile; the message button
           is @click.stop so it does not navigate. -->
      <h2 class="velo-section-title">Требуют внимания</h2>
      <div v-if="attnLoading" class="summary__attn-state">
        <VLoader />
      </div>
      <VEmptyState
        v-else-if="attnError"
        icon="warning"
        title="Не удалось загрузить"
        :description="attnError"
      >
        <VButton size="sm" variant="outline" @click="loadStudents">Повторить</VButton>
      </VEmptyState>
      <template v-else>
        <div
          v-for="student in needsAttention"
          :key="student.id"
          class="summary__attn summary__attn--clickable"
          role="button"
          tabindex="0"
          @click="openProfile(student)"
          @keydown.enter.space.prevent="openProfile(student)"
        >
          <VAvatar :name="student.name" size="md" />
          <div class="summary__attn-body">
            <div class="summary__attn-name">{{ student.name }}</div>
            <div class="summary__attn-meta">Практик: {{ student.practices_count }}</div>
            <span class="summary__attn-badge"><IconWarning :size="14" />Требует внимания</span>
          </div>
          <button
            class="summary__msg"
            aria-label="Написать сообщение"
            @click.stop="openMessage(student.name)"
          >
            <IconMessages :size="22" />
          </button>
        </div>
        <VEmptyState
          v-if="needsAttention.length === 0"
          icon="group"
          title="Все ученики в порядке"
          description="Здесь появятся те, кому нужно внимание"
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
import { VCard, VAvatar, VLoader, VEmptyState, VButton } from '@/components/ui'
import { IconMessages, IconWarning } from '@/components/icons'
import SendMessageModal from '@/components/shared/SendMessageModal.vue'
import { getStudents } from '@/api/masters'
import type { StudentListItem } from '@/api/types'

const router = useRouter()

// -- HONEST STUB (no master-AI / feedback-aggregation backend → roadmap for
//    Zod). No fabricated numbers/names — see VEmptyState below for key
//    feedbacks. --
const insight = ref('Сводка появится, когда подключится аналитика')

// -- «Требуют внимания» — REAL (E5: GET /masters/me/students). Same source as
//    MasterStudentsView; show only students flagged needs_attention. --
const students = ref<StudentListItem[]>([])
const attnLoading = ref(true)
const attnError = ref('')

async function loadStudents(): Promise<void> {
  attnLoading.value = true
  attnError.value = ''
  try {
    const res = await getStudents()
    students.value = res.items
  } catch {
    attnError.value = 'Попробуйте ещё раз'
  } finally {
    attnLoading.value = false
  }
}
onMounted(loadStudents)

const needsAttention = computed((): StudentListItem[] =>
  students.value.filter((s) => s.needs_attention),
)

// The detail endpoint carries no name → pass it forward (mirror MasterStudentsView).
function openProfile(student: StudentListItem): void {
  router.push({
    name: 'master-student-profile',
    params: { id: student.id },
    query: { name: student.name },
  })
}

const msgOpen = ref(false)
const msgName = ref('')
function openMessage(name: string): void {
  msgName.value = name
  msgOpen.value = true
}
</script>

<style scoped>
.summary {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.summary__content {
  flex: 1;
  /* F-5 rail sync: ride MobileLayout's 24px rail (no local h-padding). */
  padding: var(--space-4) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.summary__insight {
  margin: 0;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-primary);
  line-height: 1.55;
}

/* Loader while the students fetch is in flight. */
.summary__attn-state {
  display: flex;
  justify-content: center;
  padding: var(--space-6) 0;
}

/* -- Needs-attention row (mirrors MasterStudentsView .students__row) -- */
.summary__attn {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: var(--velo-card-padding-y) var(--space-4);
}

.summary__attn--clickable {
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.summary__attn--clickable:active {
  opacity: 0.85;
}

.summary__attn-body {
  flex: 1;
  min-width: 0;
}

.summary__attn-name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.summary__attn-meta {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin-top: var(--velo-gap-2);
}

/* «Требует внимания» chip — same DS treatment as MasterStudentsView. */
.summary__attn-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--velo-card-gap-icon-title);
  margin-top: var(--velo-gap-6);
  padding: 3px 10px;
  border-radius: var(--velo-radius-badge);
  background: var(--velo-warning-bg);
  color: var(--velo-peach-500);
  font-size: var(--text-xs);
}

.summary__attn-badge svg {
  color: var(--velo-warning);
}

.summary__msg {
  width: var(--velo-size-46);
  height: var(--velo-size-46);
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

.summary__msg:active {
  opacity: 0.85;
}
</style>
