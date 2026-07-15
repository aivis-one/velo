// =============================================================================
// VELO Frontend -- bookings.ts Unit Tests (T1 stage 1 -- money-path wrapper)
// =============================================================================
//
// Covers the two money-moving wrappers: purchasePractice (creates Booking +
// Purchase + ledger entries -- not wrapped by stores/bookings.ts, called
// directly from views) and cancelBooking (triggers the backend's
// refund-by-deadline policy). Client mocked at the seam (@/api/client);
// ApiResponseError kept real via importOriginal for realistic error-path tests.
// =============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { purchasePractice, cancelBooking } from '@/api/bookings'
import { api, ApiResponseError } from '@/api/client'

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

describe('purchasePractice', () => {
  beforeEach(() => {
    vi.mocked(api.post).mockReset()
  })

  it('POSTs to the practice purchase endpoint with no body when promoCode is omitted', async () => {
    vi.mocked(api.post).mockResolvedValue({ id: 'purch_1' })

    await purchasePractice('practice_1')

    expect(api.post).toHaveBeenCalledWith('/api/v1/practices/practice_1/purchase', undefined)
  })

  it('includes promo_code in the body when provided', async () => {
    vi.mocked(api.post).mockResolvedValue({ id: 'purch_2' })

    await purchasePractice('practice_1', 'SUMMER10')

    expect(api.post).toHaveBeenCalledWith('/api/v1/practices/practice_1/purchase', {
      promo_code: 'SUMMER10',
    })
  })

  it('resolves with the Booking + Purchase + ledger response from the backend', async () => {
    const purchaseResponse = {
      id: 'purch_3',
      user_id: 'user_1',
      practice_id: 'practice_1',
      booking_id: 'booking_1',
      promo_id: null,
      amount_cents: 5000,
      discount_cents: 0,
      paid_cents: 5000,
      currency: 'eur',
    }
    vi.mocked(api.post).mockResolvedValue(purchaseResponse)

    const result = await purchasePractice('practice_1')

    expect(result).toEqual(purchaseResponse)
  })

  it('propagates a backend rejection (e.g. insufficient balance)', async () => {
    vi.mocked(api.post).mockRejectedValue(
      new ApiResponseError(400, 'Insufficient balance', 'insufficient_balance'),
    )

    await expect(purchasePractice('practice_1')).rejects.toBeInstanceOf(ApiResponseError)
    await expect(purchasePractice('practice_1')).rejects.toMatchObject({
      code: 'insufficient_balance',
    })
  })

  it('propagates a backend rejection for an invalid promo code', async () => {
    vi.mocked(api.post).mockRejectedValue(
      new ApiResponseError(400, 'Promo code not found', 'promo_invalid'),
    )

    await expect(purchasePractice('practice_1', 'BOGUS')).rejects.toMatchObject({
      code: 'promo_invalid',
    })
  })
})

describe('cancelBooking', () => {
  beforeEach(() => {
    vi.mocked(api.delete).mockReset()
  })

  it('DELETEs the booking by id', async () => {
    vi.mocked(api.delete).mockResolvedValue(undefined)

    await cancelBooking('booking_1')

    expect(api.delete).toHaveBeenCalledWith('/api/v1/bookings/booking_1')
  })

  it('resolves with no value on success (refund policy is applied server-side)', async () => {
    vi.mocked(api.delete).mockResolvedValue(undefined)

    await expect(cancelBooking('booking_1')).resolves.toBeUndefined()
  })

  it('propagates a backend rejection (e.g. booking not found / already cancelled)', async () => {
    vi.mocked(api.delete).mockRejectedValue(
      new ApiResponseError(404, 'Booking not found', 'not_found'),
    )

    await expect(cancelBooking('booking_1')).rejects.toBeInstanceOf(ApiResponseError)
    await expect(cancelBooking('booking_1')).rejects.toMatchObject({ code: 'not_found' })
  })
})
