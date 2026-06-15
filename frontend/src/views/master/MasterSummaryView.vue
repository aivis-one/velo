<!--
  VELO Frontend -- MasterSummaryView (Master DS, 2026-06-11)

  "Саммари недели" — the master's AI weekly insights, reached from the dashboard
  summary card ("Подробнее"). Rendered inside MasterShell.

  STUB: no master-AI / feedback-aggregation backend. Placeholder data below;
  documents the contract for Zod (roadmap: Agent-Velo/master-ds-zod-roadmap.md):
    insight (string), key_feedbacks [{ rating, name, comment }],
    needs_attention [{ name, reason }].
-->

<template>
  <div class="summary">
    <VHeader title="Саммари недели" show-back @back="router.push({ name: 'master-dashboard' })" />

    <div class="summary__content">
      <!-- AI insight -->
      <h3 class="summary__section-title">AI-инсайты за неделю</h3>
      <VCard>
        <p class="summary__insight">{{ insight }}</p>
      </VCard>

      <!-- Key feedbacks -->
      <h3 class="summary__section-title">Ключевые отзывы</h3>
      <div v-for="fb in keyFeedbacks" :key="fb.id" class="summary__fb">
        <span class="summary__fb-ic" :class="`summary__fb-ic--${fb.rating}`">
          <component :is="fb.rating === 'fire' ? IconRatingFire : IconRatingConfused" :size="30" />
        </span>
        <div class="summary__fb-body">
          <div class="summary__fb-name">{{ fb.name }}</div>
          <div class="summary__fb-text">{{ fb.comment }}</div>
        </div>
      </div>

      <!-- Needs attention -->
      <h3 class="summary__section-title">Требуют внимания</h3>
      <div v-for="item in needsAttention" :key="item.id" class="summary__attn">
        <VAvatar :name="item.name" size="md" />
        <div class="summary__attn-body">
          <div class="summary__attn-name">{{ item.name }}</div>
          <div class="summary__attn-reason"><IconRatingConfused :size="14" />{{ item.reason }}</div>
        </div>
        <button
          class="summary__msg"
          aria-label="Написать сообщение"
          @click="openMessage(item.name)"
        >
          <IconMessages :size="22" />
        </button>
      </div>
    </div>

    <SendMessageModal :open="msgOpen" :name="msgName" @close="msgOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { VHeader } from '@/components/layout'
import { VCard, VAvatar } from '@/components/ui'
import { IconRatingFire, IconRatingConfused, IconMessages } from '@/components/icons'
import SendMessageModal from '@/components/shared/SendMessageModal.vue'

const router = useRouter()

// -- STUB data (no master-AI / feedback-aggregation backend → roadmap for Zod). --
const insight = ref(
  '«На этой неделе вы провели 12 практик для 89 участников. 85% отметили хорошее ' +
    'или отличное состояние после занятий. Анна П. оставила запрос на индивидуальную ' +
    'консультацию — рекомендую связаться с ней.»',
)
const keyFeedbacks = ref<
  Array<{ id: number; rating: 'fire' | 'confused'; name: string; comment: string }>
>([
  { id: 1, rating: 'fire', name: 'Мария К.', comment: '«Лучшая практика за месяц!»' },
  { id: 2, rating: 'confused', name: 'Анна П.', comment: '«Хотела бы индивидуальную практику»' },
])
const needsAttention = ref<Array<{ id: number; name: string; reason: string }>>([
  { id: 1, name: 'Анна П.', reason: 'Запрос на консультацию' },
])

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

.summary__section-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: var(--space-1) 0 0;
}

.summary__insight {
  margin: 0;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-primary);
  line-height: 1.55;
}

/* -- Key feedback card -- */
.summary__fb {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: 13px var(--space-4);
}

.summary__fb-ic {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.summary__fb-ic--fire {
  color: var(--velo-peach-500);
}
.summary__fb-ic--confused {
  color: var(--velo-text-primary);
}

.summary__fb-body {
  flex: 1;
  min-width: 0;
}

.summary__fb-name {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
}

.summary__fb-text {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin-top: 3px;
}

/* -- Needs-attention row -- */
.summary__attn {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  border-radius: var(--radius-md);
  padding: 13px var(--space-4);
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

.summary__attn-reason {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-text-secondary);
  margin-top: 2px;
}

.summary__msg {
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

.summary__msg:active {
  opacity: 0.85;
}
</style>
