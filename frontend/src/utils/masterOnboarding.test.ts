// =============================================================================
// VELO Frontend -- masterOnboarding.ts Unit Tests
// =============================================================================

import { describe, it, expect } from 'vitest'
import {
  isMasterOnboardingCompleted,
  shouldShowMasterOnboarding,
  type MasterOnboardingGateInput,
} from '@/utils/masterOnboarding'

describe('isMasterOnboardingCompleted (defensive read — E15 not yet typed)', () => {
  it('absent field -> false (honest-stub: backend ignores until E15)', () => {
    expect(isMasterOnboardingCompleted({ id: 'u1' })).toBe(false)
  })
  it('null / undefined user -> false', () => {
    expect(isMasterOnboardingCompleted(null)).toBe(false)
    expect(isMasterOnboardingCompleted(undefined)).toBe(false)
  })
  it('explicit false -> false', () => {
    expect(isMasterOnboardingCompleted({ master_onboarding_completed: false })).toBe(false)
  })
  it('explicit true -> true', () => {
    expect(isMasterOnboardingCompleted({ master_onboarding_completed: true })).toBe(true)
  })
})

describe('shouldShowMasterOnboarding (gate)', () => {
  const base: MasterOnboardingGateInput = {
    role: 'master',
    profileStatus: 'verified',
    completed: false,
    shownThisSession: false,
  }

  it('verified master, not completed, not shown -> show', () => {
    expect(shouldShowMasterOnboarding(base)).toBe(true)
  })
  it('non-master role -> hidden', () => {
    expect(shouldShowMasterOnboarding({ ...base, role: 'user' })).toBe(false)
    expect(shouldShowMasterOnboarding({ ...base, role: 'admin' })).toBe(false)
    expect(shouldShowMasterOnboarding({ ...base, role: null })).toBe(false)
  })
  it('not yet verified (pending / rejected / null) -> hidden', () => {
    expect(shouldShowMasterOnboarding({ ...base, profileStatus: 'pending' })).toBe(false)
    expect(shouldShowMasterOnboarding({ ...base, profileStatus: 'rejected' })).toBe(false)
    expect(shouldShowMasterOnboarding({ ...base, profileStatus: null })).toBe(false)
    expect(shouldShowMasterOnboarding({ ...base, profileStatus: undefined })).toBe(false)
  })
  it('already completed (server flag) -> hidden', () => {
    expect(shouldShowMasterOnboarding({ ...base, completed: true })).toBe(false)
  })
  it('dismissed this session -> hidden (loop guard before E15)', () => {
    expect(shouldShowMasterOnboarding({ ...base, shownThisSession: true })).toBe(false)
  })

  it('forced (test role-switch replay) bypasses completed + shownThisSession', () => {
    expect(
      shouldShowMasterOnboarding({
        ...base,
        completed: true,
        shownThisSession: true,
        forced: true,
      }),
    ).toBe(true)
  })

  it('forced still requires a verified master', () => {
    expect(shouldShowMasterOnboarding({ ...base, profileStatus: 'pending', forced: true })).toBe(
      false,
    )
    expect(shouldShowMasterOnboarding({ ...base, role: 'user', forced: true })).toBe(false)
  })
})
