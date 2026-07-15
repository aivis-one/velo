// =============================================================================
// VELO Frontend -- router/guards.ts Unit Tests (T1 stage 3 -- seam + guards)
// =============================================================================
//
// Uses the REAL @/composables/useAuth module (unlike stage 2, which mocked it
// wholesale to avoid the isReady singleton entirely) -- that singleton and
// waitUntilReady() are exactly what stage 3 exists to make testable. The seam
// is __setReadyForTest() (useAuth.ts, test-only, additive): forces isReady
// without running the real initAuth() bootstrap. The not-ready/timeout path
// uses fake timers to fast-forward waitUntilReady()'s 10s race instead of
// leaving isReady unset and waiting for real time (well past testTimeout).
//
// @/stores/auth is the REAL Pinia store (setActivePinia per test) so
// role/allowedRoles/masterApplication computeds are exercised for real, not
// re-implemented in a mock. @/stores/master is mocked wholesale -- its
// fetchMyProfile() would otherwise hit the network.
// =============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import {
  roleRedirect,
  roleGuard,
  masterNoProfileGuard,
  masterStatusGuard,
  masterPendingGuard,
} from '@/router/guards'
import { useAuthStore } from '@/stores/auth'
import { resetAuthState, __setReadyForTest, pendingDeepLink } from '@/composables/useAuth'
import { MASTER_APPLIED_KEY, masterRejectionSeenKey } from '@/utils/constants'
import type { UserResponse } from '@/api/types'

// Guards ignore (to, from, next) entirely at runtime -- call bare, matching
// how vue-router actually invokes them. NavigationGuardWithThis's declared
// 3-required-param signature is a vue-router typing convenience, not a real
// runtime requirement here; cast through unknown rather than pass dummy args.
type BareGuardResult = { path: string } | { name: string; params?: Record<string, string> } | true
function call(guard: unknown): Promise<BareGuardResult> {
  return (guard as () => Promise<BareGuardResult>)()
}

const masterStoreState: { profileMissing: boolean; profile: { status: string } | null } = {
  profileMissing: false,
  profile: null,
}
const fetchMyProfile = vi.fn().mockResolvedValue(undefined)
vi.mock('@/stores/master', () => ({
  useMasterStore: () => ({
    get profileMissing() {
      return masterStoreState.profileMissing
    },
    get profile() {
      return masterStoreState.profile
    },
    fetchMyProfile,
  }),
}))

function setAuthUser(overrides: Partial<UserResponse> & Record<string, unknown> = {}): void {
  const store = useAuthStore()
  store.token = 'tok'
  store.user = {
    id: 'user_1',
    role: 'user',
    first_name: 'Test',
    last_name: null,
    onboarding_completed: true,
    ...overrides,
  } as UserResponse
}

describe('router/guards', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    resetAuthState()
    sessionStorage.clear()
    localStorage.clear()
    masterStoreState.profileMissing = false
    masterStoreState.profile = null
    fetchMyProfile.mockClear()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('roleRedirect', () => {
    it('admin -> /admin/dashboard', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'admin' })
      expect(await call(roleRedirect)).toEqual({ path: '/admin/dashboard' })
    })

    it('master -> /master/dashboard', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'master' })
      expect(await call(roleRedirect)).toEqual({ path: '/master/dashboard' })
    })

    it('user -> /user/dashboard (default case)', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'user' })
      expect(await call(roleRedirect)).toEqual({ path: '/user/dashboard' })
    })

    it('a pending deep link is consumed and cleared instead of the role dashboard', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'master' })
      pendingDeepLink.value = { name: 'practice-detail', params: { id: 'p1' } }

      const result = await call(roleRedirect)

      expect(result).toEqual({ name: 'practice-detail', params: { id: 'p1' } })
      expect(pendingDeepLink.value).toBeNull()
    })

    it('timeout with role still null -> /auth-error', async () => {
      vi.useFakeTimers()
      // isReady never set -- waitUntilReady() races the 10s timeout.
      const promise = call(roleRedirect)
      await vi.advanceTimersByTimeAsync(10_000)
      expect(await promise).toEqual({ path: '/auth-error' })
    })

    it('timeout but role already resolved -> falls through to normal role routing, not auth-error', async () => {
      vi.useFakeTimers()
      setAuthUser({ role: 'master' })
      const promise = call(roleRedirect)
      await vi.advanceTimersByTimeAsync(10_000)
      expect(await promise).toEqual({ path: '/master/dashboard' })
    })

    // -- Bug 1 (ПРОМТ №405): rejected applicant routing --------------------
    it('rejected applicant, not yet seen -> routed to /master/pending', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'user', master_application: { status: 'rejected' } })
      expect(await call(roleRedirect)).toEqual({ path: '/master/pending' })
    })

    it('rejected applicant, already seen -> /user/dashboard like an ordinary user', async () => {
      __setReadyForTest(true)
      setAuthUser({ id: 'user_1', role: 'user', master_application: { status: 'rejected' } })
      localStorage.setItem(masterRejectionSeenKey('user_1'), '1')
      expect(await call(roleRedirect)).toEqual({ path: '/user/dashboard' })
    })

    it('rejected applicant with a pending deep link -> the deep link wins', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'user', master_application: { status: 'rejected' } })
      pendingDeepLink.value = { name: 'practice-detail', params: { id: 'p1' } }

      const result = await call(roleRedirect)

      expect(result).toEqual({ name: 'practice-detail', params: { id: 'p1' } })
      expect(pendingDeepLink.value).toBeNull()
    })

    it('a plain user with no application is unaffected -> /user/dashboard', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'user' })
      expect(await call(roleRedirect)).toEqual({ path: '/user/dashboard' })
    })

    it('the seen key is scoped per user -- user B still gets routed after user A is marked seen', async () => {
      __setReadyForTest(true)
      localStorage.setItem(masterRejectionSeenKey('user_a'), '1')

      setAuthUser({ id: 'user_b', role: 'user', master_application: { status: 'rejected' } })

      expect(await call(roleRedirect)).toEqual({ path: '/master/pending' })
    })
  })

  describe('roleGuard', () => {
    it("roleGuard('admin'): admin passes", () => {
      setAuthUser({ role: 'admin' })
      expect(call(roleGuard('admin'))).toBe(true)
    })

    it("roleGuard('admin'): master is redirected to /user/dashboard", () => {
      setAuthUser({ role: 'master' })
      expect(call(roleGuard('admin'))).toEqual({ path: '/user/dashboard' })
    })

    it("roleGuard('admin'): user is redirected to /user/dashboard", () => {
      setAuthUser({ role: 'user' })
      expect(call(roleGuard('admin'))).toEqual({ path: '/user/dashboard' })
    })

    it("roleGuard('master'): master passes", () => {
      setAuthUser({ role: 'master' })
      expect(call(roleGuard('master'))).toBe(true)
    })

    it("roleGuard('master'): admin also passes (admin outranks master)", () => {
      setAuthUser({ role: 'admin' })
      expect(call(roleGuard('master'))).toBe(true)
    })

    it("roleGuard('master'): user is redirected to /user/dashboard", () => {
      setAuthUser({ role: 'user' })
      expect(call(roleGuard('master'))).toEqual({ path: '/user/dashboard' })
    })
  })

  describe('masterNoProfileGuard', () => {
    it('non-master role: passes without touching the master store', async () => {
      setAuthUser({ role: 'user' })
      expect(await call(masterNoProfileGuard)).toBe(true)
      expect(fetchMyProfile).not.toHaveBeenCalled()
    })

    it('master with no profile at all: redirects to /master/apply', async () => {
      setAuthUser({ role: 'master' })
      masterStoreState.profileMissing = true
      expect(await call(masterNoProfileGuard)).toEqual({ path: '/master/apply' })
    })

    it('master with a profile: passes', async () => {
      setAuthUser({ role: 'master' })
      masterStoreState.profileMissing = false
      expect(await call(masterNoProfileGuard)).toBe(true)
    })
  })

  describe('masterStatusGuard', () => {
    it('no profile at all: redirects to /master/apply (delegates to the no-profile check)', async () => {
      setAuthUser({ role: 'master' })
      masterStoreState.profileMissing = true
      expect(await call(masterStatusGuard)).toEqual({ path: '/master/apply' })
    })

    it('profile exists but not verified: redirects to /master/pending', async () => {
      setAuthUser({ role: 'master' })
      masterStoreState.profile = { status: 'pending' }
      expect(await call(masterStatusGuard)).toEqual({ path: '/master/pending' })
    })

    it('profile verified: passes', async () => {
      setAuthUser({ role: 'master' })
      masterStoreState.profile = { status: 'verified' }
      expect(await call(masterStatusGuard)).toBe(true)
    })
  })

  describe('masterPendingGuard', () => {
    it('timeout with role still null -> /auth-error', async () => {
      vi.useFakeTimers()
      const promise = call(masterPendingGuard)
      await vi.advanceTimersByTimeAsync(10_000)
      expect(await promise).toEqual({ path: '/auth-error' })
    })

    it('admin -> redirected to /admin/dashboard (admins never apply)', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'admin' })
      expect(await call(masterPendingGuard)).toEqual({ path: '/admin/dashboard' })
    })

    it('master -> allowed (masterStatusGuard is what sent them here)', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'master' })
      expect(await call(masterPendingGuard)).toBe(true)
    })

    it('user with the fresh-submit session marker -> allowed', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'user' })
      sessionStorage.setItem(MASTER_APPLIED_KEY, '1')
      expect(await call(masterPendingGuard)).toBe(true)
    })

    it('user with master in allowedRoles (approved capability) -> allowed', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'user', role_switch: { allowed_roles: ['user', 'master'] } })
      expect(await call(masterPendingGuard)).toBe(true)
    })

    it('user with a rejected application -> allowed (sees the rejection screen)', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'user', master_application: { status: 'rejected' } })
      expect(await call(masterPendingGuard)).toBe(true)
    })

    it('plain user who never applied -> redirected to /user/dashboard', async () => {
      __setReadyForTest(true)
      setAuthUser({ role: 'user' })
      expect(await call(masterPendingGuard)).toEqual({ path: '/user/dashboard' })
    })
  })
})
