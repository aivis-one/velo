// =============================================================================
// VELO Frontend -- Vitest global setup (T1 stage 2)
// =============================================================================
//
// Runs before every test file. Resets the API client's module-level state
// (token, 401 callback, in-flight GET dedupe map) so tests don't leak state
// across files -- api/client.ts:91 already ships resetClientState() for
// exactly this (WARNING-13); this is the first place it's wired in.
// =============================================================================

import { beforeEach } from 'vitest'
import { resetClientState } from '@/api/client'

beforeEach(() => {
  resetClientState()
})
