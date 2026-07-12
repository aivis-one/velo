<!--
  VELO Frontend -- VModal Component (Phase F4.1)

  Reusable modal dialog with overlay, close on Escape/overlay click,
  enter/leave transitions. Content via default slot.

  Mobile: bottom sheet (slides up from bottom).
  Desktop (>640px): centered dialog.

  Used by: BookingPopup, CancelBookingPopup, and future modals.

  Usage:
    <VModal :open="showModal" @close="showModal = false">
      <h2>Title</h2>
      <p>Content</p>
    </VModal>
-->

<template>
  <Teleport to="body">
    <Transition name="v-modal">
      <div v-if="open" class="v-modal__overlay" @click.self="onOverlayClick">
        <div class="v-modal__container" role="dialog" aria-modal="true">
          <button
            v-if="showClose"
            class="v-modal__close"
            aria-label="Закрыть"
            @click="$emit('close')"
          >
            <IconClose :size="16" />
          </button>
          <div class="v-modal__scroll velo-kbd-scroll">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import { IconClose } from '@/components/icons'

const props = withDefaults(
  defineProps<{
    open: boolean
    closeOnOverlay?: boolean
    showClose?: boolean
  }>(),
  {
    closeOnOverlay: true,
    showClose: true,
  },
)

const emit = defineEmits<{
  close: []
}>()

function onOverlayClick(): void {
  if (props.closeOnOverlay) {
    emit('close')
  }
}

function onKeydown(e: KeyboardEvent): void {
  if (e.key === 'Escape' && props.open) {
    emit('close')
  }
}

// Lock body scroll when modal is open.
watch(
  () => props.open,
  (isOpen) => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
  },
)

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  // Ensure scroll is restored if component unmounts while open.
  document.body.style.overflow = ''
})
</script>

<style scoped>
.v-modal__overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: var(--velo-scrim);
  padding: var(--space-4);
}

.v-modal__container {
  position: relative;
  width: 100%;
  max-width: 420px;
  max-height: 85vh;
  /* Clip the scrollbar to the rounded corners so it never pokes above the
     sheet. The actual scrolling happens on .v-modal__scroll inside. */
  overflow: hidden;
  background: var(--velo-bg-card-solid);
  border: 1px solid var(--velo-border-card);
  /* Плавающая шторка (overlay даёт отступ со всех сторон) -> скругляем ВСЕ
     углы. Радиус из DS-токена (--radius-md=15), а не сырой 20px. */
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-xl);
}

/* Inner scroll area: holds the padding and owns the vertical scroll, so the
   scrollbar stays within the container's rounded clip. */
.v-modal__scroll {
  max-height: 85vh;
  overflow-y: auto;
  padding: var(--space-5);
}

.v-modal__close {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  z-index: 1;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: var(--velo-bg-subtle);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.v-modal__close:hover {
  background: var(--velo-border);
  color: var(--velo-text-primary);
}

/* -- Transitions -- */
.v-modal-enter-active,
.v-modal-leave-active {
  transition: opacity var(--transition-slow);
}

.v-modal-enter-active .v-modal__container,
.v-modal-leave-active .v-modal__container {
  transition: transform var(--transition-slow);
}

.v-modal-enter-from,
.v-modal-leave-to {
  opacity: 0;
}

.v-modal-enter-from .v-modal__container {
  transform: translateY(100%);
}

.v-modal-leave-to .v-modal__container {
  transform: translateY(100%);
}

/* Desktop: centered modal instead of bottom sheet */
@media (min-width: 640px) {
  .v-modal__overlay {
    align-items: center;
  }

  .v-modal__container {
    border-radius: var(--radius-md);
  }

  .v-modal-enter-from .v-modal__container {
    transform: translateY(20px);
  }

  .v-modal-leave-to .v-modal__container {
    transform: translateY(20px);
  }
}
</style>
