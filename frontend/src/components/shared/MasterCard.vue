<!--
  VELO Frontend -- MasterCard (shared)

  Master info card used on practice/booking detail screens (Figma 15 / 18 /
  Calendar frame 4):
    - Avatar: VAvatar (real photo when master_avatar_url is set, initials
      from the name otherwise -- the project-wide avatar pattern).
    - Name + verified check
    - Method tags (VTag, cycling blue / pink / sand)
    - "Подробнее" arrow -> master public profile (/user/masters/:id)

  Extracted from PracticeDetailView so screens 15 / 18 / frame 4 share one card.
-->

<template>
  <div class="master-card-wrapper">
    <div class="master-card">
      <VAvatar
        :url="avatarUrl ?? ''"
        :name="masterName ?? 'Мастер'"
        size="xl"
      />
      <div class="master-card__info">
        <div class="master-card__name">
          {{ masterName ?? 'Мастер' }}
          <span class="master-card__verified">
            <IconCheck :size="14" />
          </span>
        </div>
        <div v-if="methods?.length" class="master-card__tags">
          <VTag
            v-for="(method, i) in methods"
            :key="method"
            :variant="TAG_VARIANTS[i % TAG_VARIANTS.length]"
          >
            {{ method }}
          </VTag>
        </div>
      </div>
    </div>
    <button
      class="master-card__more"
      aria-label="Профиль мастера"
      @click="onMore"
    >
      <span class="master-card__more-text">Подробнее</span>
      <span class="master-card__more-pill">
        <IconArrowRight :size="18" />
      </span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VTag, VAvatar } from '@/components/ui'
import { IconCheck, IconArrowRight } from '@/components/icons'
import { useToast } from '@/composables/useToast'

const props = withDefaults(
  defineProps<{
    masterName?: string | null
    methods?: string[] | null
    /** Master avatar URL (User.avatar_url). Null -> placeholder glyph. */
    avatarUrl?: string | null
    /** Master user id -- target of the "Подробнее" public profile link. */
    masterId?: string | null
  }>(),
  {
    masterName: null,
    methods: null,
    avatarUrl: null,
    masterId: null,
  },
)

// Master method tags cycle through three tints (Figma: blue / pink / sand).
const TAG_VARIANTS = ['blue', 'pink', 'sand'] as const

const router = useRouter()
const toast = useToast()

function onMore(): void {
  if (!props.masterId) {
    // No id to navigate to (defensive -- detail always passes master_id).
    toast.info('Профиль мастера недоступен')
    return
  }
  router.push({ name: 'user-master-public', params: { id: props.masterId } })
}
</script>

<style scoped>
/* F-4 sync: wrapper держит карточку + footer-кнопку «Подробнее» под ней.
 * Figma master-card.svg (336×145 canvas): card 336×104 → gap 5.5 → pill
 * 63×35 справа. Round to space-1=4 для gap (acceptable visual noise). */
.master-card-wrapper {
  display: flex;
  flex-direction: column;
  /* Воздух между карточкой мастера и строкой «Подробнее» (operator 2026-06-04:
   * было space-1=4px, стрелка прилипала). --space-3 = 14px. */
  gap: var(--space-3);
}

.master-card {
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-white);
  border-radius: var(--radius-md);
  /* Figma: base card height 104 (avatar xl=80 + padding-y 12+12). min-height
   * (not fixed height) so many wrapped method tags grow the card instead of
   * spilling out of it; with the usual 3-4 tags it stays at 104. */
  min-height: var(--velo-card-height-list);
  padding: 12px var(--space-3);
  display: flex;
  align-items: center;
  /* Figma: tags start at x=111 от card left = 14 padding + 80 avatar + 17 gap.
   * Round 17 до space-4=16 — расхождение 1px. */
  gap: var(--space-4);
  box-sizing: border-box;
}

.master-card__info {
  flex: 1;
  min-width: 0;
}

.master-card__name {
  display: flex;
  align-items: center;
  /* Figma: gap name→verified ≈ 12 (233-221). Round до space-2=8. */
  gap: var(--space-2);
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  margin-bottom: var(--space-1);
}

.master-card__verified {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  /* Figma: verified circle r=13 → 26×26 (был 18). */
  width: 26px;
  height: 26px;
  border-radius: var(--radius-full);
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}

.master-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin-top: var(--space-1);
}

/* Footer-кнопка «Подробнее» — отдельным row под card (text label + pill
 * со стрелкой, right-aligned). */
.master-card__more {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  /* Figma: text ends x=259, pill starts x=272.5 → gap 13. */
  gap: 13px;
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.master-card__more:hover {
  opacity: 0.8;
}

.master-card__more-text {
  font-family: var(--font-body);
  font-size: 14px;
  letter-spacing: 0.28px;
  color: var(--velo-text-primary);
}

/* «Подробнее» = тот же белый pill, что VBackButton (63×40, без рамки,
 * фон --velo-bg-card-solid, радиус full) — единая «понятная» кнопка-стрелка
 * на весь проект (operator 2026-06-04). Стрелка вправо = вперёд (в профиль). */
.master-card__more-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 63px;
  height: 40px;
  border-radius: var(--radius-full);
  background: var(--velo-bg-card-solid);
  border: none;
  color: var(--velo-text-primary);
}
</style>
