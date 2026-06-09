<!--
  VELO Frontend -- VAvatar Component (Phase F2.1)

  Circular avatar. Shows image if url provided, otherwise initials from name.
  Matches mockup avatar patterns (student-avatar, user-avatar, master-avatar).

  Usage:
    <VAvatar name="Мария К." size="md" />
    <VAvatar name="Alex" url="/avatars/alex.jpg" size="lg" />
-->

<template>
  <div class="v-avatar" :class="`v-avatar--${size}`">
    <img v-if="url" :src="url" :alt="name" class="v-avatar__img" />
    <span v-else class="v-avatar__initials">{{ initials }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    name: string
    url?: string
    size?: 'sm' | 'md' | 'lg' | 'xl'
  }>(),
  {
    url: '',
    size: 'md',
  },
)

const initials = computed(() => {
  const parts = props.name.trim().split(/\s+/)
  const first = (parts[0] ?? '').charAt(0)
  const second = (parts[1] ?? '').charAt(0)
  if (first && second) {
    return (first + second).toUpperCase()
  }
  return (first || '?').toUpperCase()
})
</script>

<style scoped>
.v-avatar {
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--velo-bg-subtle);
  color: var(--velo-primary);
  font-weight: 400;
  flex-shrink: 0;
  overflow: hidden;
}

.v-avatar--sm {
  width: 32px;
  height: 32px;
  font-size: var(--text-12);
}

.v-avatar--md {
  width: 40px;
  height: 40px;
  font-size: 14px;
}

.v-avatar--lg {
  width: 64px;
  height: 64px;
  font-size: 22px;
}

.v-avatar--xl {
  width: 80px;
  height: 80px;
  font-size: 28px;
}

.v-avatar__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.v-avatar__initials {
  line-height: 1;
}
</style>
