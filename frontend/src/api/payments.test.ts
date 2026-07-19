// =============================================================================
// VELO Frontend -- payments.ts Unit Tests (T1 stage 1 -- money-path wrapper)
// =============================================================================
//
// createTopup is the single narrowest, highest-stakes function in the app: it
// either (stub mode) instantly credits balance server-side, or (real mode)
// creates a Stripe Checkout Session. The wrapper itself has no branching --
// both modes return the same TopupResponse shape -- so these tests cover the
// request-building contract and pass-through of both response shapes, plus
// error propagation. Client mocked at the seam (@/api/client); ApiResponseError
// kept real via importOriginal so rejection tests assert on the real class.
// =============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createTopup } from '@/api/payments'
import { api, ApiResponseError, ApiNetworkError } from '@/api/client'

vi.mock('@/api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/api/client')>()
  return {
    ...actual,
    api: {
      get: vi.fn(),
      post: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
    },
  }
})

describe('createTopup', () => {
  beforeEach(() => {
    vi.mocked(api.post).mockReset()
  })

  it('POSTs to /api/v1/payments/topup with amount_cents in the body', async () => {
    vi.mocked(api.post).mockResolvedValue({
      payment_id: 'pay_1',
      checkout_url: '/topup/success',
      amount_cents: 5000,
      currency: 'eur',
    })

    await createTopup(5000)

    expect(api.post).toHaveBeenCalledWith('/api/v1/payments/topup', { amount_cents: 5000 })
  })

  it('stub mode: resolves with an instantly-confirmed payment (non-Stripe checkout_url)', async () => {
    const stubResponse = {
      payment_id: 'pay_stub_1',
      checkout_url: '/topup/success',
      amount_cents: 2000,
      currency: 'eur',
    }
    vi.mocked(api.post).mockResolvedValue(stubResponse)

    const result = await createTopup(2000)

    expect(result).toEqual(stubResponse)
  })

  it('real mode: resolves with a Stripe Checkout Session URL', async () => {
    const stripeResponse = {
      payment_id: 'pay_stripe_1',
      checkout_url: 'https://checkout.stripe.com/c/pay/cs_test_abc123',
      amount_cents: 10000,
      currency: 'eur',
    }
    vi.mocked(api.post).mockResolvedValue(stripeResponse)

    const result = await createTopup(10000)

    expect(result).toEqual(stripeResponse)
  })

  it('propagates a backend rejection (e.g. invalid amount) as ApiResponseError', async () => {
    vi.mocked(api.post).mockRejectedValue(
      new ApiResponseError(400, 'Amount must be positive', 'invalid_amount'),
    )

    await expect(createTopup(-100)).rejects.toBeInstanceOf(ApiResponseError)
    await expect(createTopup(-100)).rejects.toMatchObject({ code: 'invalid_amount' })
  })

  it('propagates a network failure as ApiNetworkError', async () => {
    vi.mocked(api.post).mockRejectedValue(new ApiNetworkError())

    await expect(createTopup(1000)).rejects.toBeInstanceOf(ApiNetworkError)
  })
})
