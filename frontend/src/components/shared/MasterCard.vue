<!--
  VELO Frontend -- MasterCard (shared)

  Master info card used on practice/booking detail screens (Figma 15 / 18 /
  Calendar frame 4):
    - Avatar: real photo (master_avatar_url) when present, IconMeditation
      placeholder otherwise (TD-FE-AVATAR remains only for the null case).
    - Name + verified check
    - Method tags (VTag, cycling blue / pink / sand)
    - "Подробнее" arrow -> master public profile (/user/masters/:id)

  Extracted from PracticeDetailView so screens 15 / 18 / frame 4 share one card.
-->

<template>
  <div class="master-card">
    <div class="master-card__avatar">
      <img
        v-if="avatarUrl"
        :src="avatarUrl"
        :alt="masterName ?? 'Мастер'"
        class="master-card__avatar-img"
      />
      <IconMeditation v-else :size="32" />
    </div>
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
    <button
      class="master-card__arrow"
      aria-label="Профиль мастера"
      @click="onMore"
    >
      <IconArrowRight :size="20" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { VTag } from '@/components/ui'
import { IconMeditation, IconCheck, IconArrowRight } from '@/components/icons'
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
.master-card {
  background: var(--velo-bg-card-solid);
  border: 1px solid #ffffff;
  border-radius: var(--radius-md);
  padding: var(--space-3);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  position: relative;
}

.master-card__avatar {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
  border-radius: var(--radius-full);
  flex-shrink: 0;
  overflow: hidden;
}

.master-card__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-full);
}

.master-card__info {
  flex: 1;
  min-width: 0;
}

.master-card__name {
  display: flex;
  align-items: center;
  gap: var(--space-1);
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
  width: 18px;
  height: 18px;
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

.master-card__arrow {
  position: absolute;
  bottom: var(--space-3);
  right: var(--space-3);
  background: var(--velo-glass-blue-15);
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--velo-text-primary);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.master-card__arrow:hover {
  opacity: 0.8;
}
</style>
