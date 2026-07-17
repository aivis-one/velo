// =============================================================================
// DEPLOY CANARY -- DELETE ME
// =============================================================================
//
// This file is deliberately, permanently red. It exists for exactly one
// purpose: proving on the real TEST server that a failing frontend test
// actually stops `velo update` from deploying -- not "the code reads the
// exit code," watched stopping a real deploy.
//
// This run also proves the 2026-07-17 downtime fix: this time, unlike the
// first canary run, `velo status` right after the abort should still list
// velo-frontend as running, on its PREVIOUS image -- the site must stay up
// through a failed deploy, not just report that it did.
//
// It is added in one commit and removed by `git revert`-ing that exact
// commit in the very next one. If you are reading this on a branch where it
// has lived for more than a few minutes, something went wrong with that
// revert -- delete this file and its describe block, nothing else needs to
// change.
// =============================================================================

import { describe, it, expect } from 'vitest'

describe('deploy canary (DELETE ME)', () => {
  it('is deliberately red to prove a broken build stops `velo update`', () => {
    expect(true).toBe(false)
  })
})
