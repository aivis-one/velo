// =============================================================================
// VELO Frontend -- keyboardViewportState.ts Unit Tests (dancing-bg #4, item 6)
// =============================================================================

import { describe, it, expect, beforeEach } from 'vitest'
import { resetKeyboardViewportState } from '@/utils/keyboardViewportState'

describe('resetKeyboardViewportState', () => {
  beforeEach(() => {
    document.documentElement.className = ''
    document.documentElement.style.removeProperty('--velo-vvh')
    document.body.innerHTML = ''
  })

  it('resets bg-shift to 0px, drops is-keyboard-open, clears --velo-vvh', () => {
    const app = document.createElement('div')
    app.id = 'app'
    app.style.setProperty('--velo-bg-shift', '120px')
    document.body.appendChild(app)
    document.documentElement.classList.add('is-keyboard-open')
    document.documentElement.style.setProperty('--velo-vvh', '540px')

    resetKeyboardViewportState()

    expect(app.style.getPropertyValue('--velo-bg-shift')).toBe('0px')
    expect(document.documentElement.classList.contains('is-keyboard-open')).toBe(false)
    expect(document.documentElement.style.getPropertyValue('--velo-vvh')).toBe('')
  })

  it('is a no-op on an already at-rest document (idempotent)', () => {
    const app = document.createElement('div')
    app.id = 'app'
    document.body.appendChild(app)

    resetKeyboardViewportState()

    expect(app.style.getPropertyValue('--velo-bg-shift')).toBe('0px')
    expect(document.documentElement.classList.contains('is-keyboard-open')).toBe(false)
    expect(document.documentElement.style.getPropertyValue('--velo-vvh')).toBe('')
  })

  it('does not throw when #app is absent (only clears root state)', () => {
    document.documentElement.classList.add('is-keyboard-open')

    expect(() => resetKeyboardViewportState()).not.toThrow()
    expect(document.documentElement.classList.contains('is-keyboard-open')).toBe(false)
  })
})
