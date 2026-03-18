// =============================================================================
// VELO Frontend -- UI Store (TD-FE-ROLE-SWITCH)
// =============================================================================
//
// Manages UI mode for master/admin users who want to browse the user interface.
// Not persisted -- resets to 'default' on every app open.
// =============================================================================

import { defineStore } from 'pinia'
import { ref } from 'vue'

export type UiMode = 'default' | 'user'

export const useUiStore = defineStore('ui', () => {
  // Not persisted intentionally -- resets on every session start.
  const uiMode = ref<UiMode>('default')

  function setUiMode(mode: UiMode): void {
    uiMode.value = mode
  }

  return { uiMode, setUiMode }
})
