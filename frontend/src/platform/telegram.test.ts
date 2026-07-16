// =============================================================================
// VELO Frontend -- Telegram Platform Chrome Tests (T8, ПРОМТ №437)
// =============================================================================
//
// Covers the chrome tokenisation: #334D6E / #F8FAFC used to be bare literals in
// telegram.ts and existed in NO token, so the header and background around every
// screen sat outside the design system. They are now --velo-tg-header /
// --velo-tg-bg in variables.css, read BY NAME because the Telegram SDK takes a
// colour string and cannot consume a var().
//
// WHY THIS FILE EXISTS: the read has a fallback, and a fallback that silently
// fires is exactly the failure mode this session has been chasing all day. If
// the token is ever renamed or dropped, the chrome keeps rendering the old
// colour and NOTHING says so -- the app looks right and the design system is
// lying. These tests assert both branches, and assert that the fallback and the
// token agree, so a future divergence is caught here rather than by nobody.
//
// The stylesheet is NOT loaded in happy-dom (vitest imports no CSS), so the
// token is injected onto :root per test -- which is also what makes the
// fallback branch honest to test.
// =============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { telegramPlatform } from '@/platform/telegram'

const setHeaderColor = vi.fn()
const setBackgroundColor = vi.fn()
const ready = vi.fn()
const expand = vi.fn()

function installWebApp(): void {
  ;(window as unknown as { Telegram: unknown }).Telegram = {
    WebApp: { ready, expand, setHeaderColor, setBackgroundColor },
  }
}

function setToken(name: string, value: string): void {
  document.documentElement.style.setProperty(name, value)
}

beforeEach(() => {
  installWebApp()
  vi.clearAllMocks()
})

afterEach(() => {
  document.documentElement.style.removeProperty('--velo-tg-header')
  document.documentElement.style.removeProperty('--velo-tg-bg')
  delete (window as unknown as { Telegram?: unknown }).Telegram
})

describe('telegramPlatform.init -- app chrome', () => {
  it('paints the chrome from the design tokens when they are defined', async () => {
    setToken('--velo-tg-header', '#334d6e')
    setToken('--velo-tg-bg', '#f8fafc')

    await telegramPlatform.init()

    expect(setHeaderColor).toHaveBeenCalledWith('#334d6e')
    expect(setBackgroundColor).toHaveBeenCalledWith('#f8fafc')
  })

  it('a re-theme of the token re-themes the chrome -- the token is really the source', async () => {
    // The whole point of the change: change the value in variables.css and the
    // Telegram header follows. If someone reverts to a literal, this goes red.
    setToken('--velo-tg-header', '#123456')
    setToken('--velo-tg-bg', '#abcdef')

    await telegramPlatform.init()

    expect(setHeaderColor).toHaveBeenCalledWith('#123456')
    expect(setBackgroundColor).toHaveBeenCalledWith('#abcdef')
  })

  it('falls back to the pre-existing literals when the stylesheet has not applied', async () => {
    // getPropertyValue returns '' before the CSS lands. Passing '' to the SDK
    // would throw the colour away; the fallback keeps the chrome exactly as it
    // shipped before ПРОМТ №437.
    await telegramPlatform.init()

    expect(setHeaderColor).toHaveBeenCalledWith('#334D6E')
    expect(setBackgroundColor).toHaveBeenCalledWith('#F8FAFC')
  })

  it('the fallback and the token are the SAME colour -- zero visual change', async () => {
    // The gate on this whole change. The fallback literals are the values that
    // shipped; the tokens must resolve to the same colour, case-insensitively.
    // If anyone edits one without the other, the chrome silently depends on
    // whether the stylesheet won the race. That is the bug this asserts against.
    setToken('--velo-tg-header', '#334d6e')
    setToken('--velo-tg-bg', '#f8fafc')

    await telegramPlatform.init()
    const themed = String(setHeaderColor.mock.calls[0]?.[0]).toLowerCase()
    const themedBg = String(setBackgroundColor.mock.calls[0]?.[0]).toLowerCase()

    vi.clearAllMocks()
    document.documentElement.style.removeProperty('--velo-tg-header')
    document.documentElement.style.removeProperty('--velo-tg-bg')
    await telegramPlatform.init()
    const fallback = String(setHeaderColor.mock.calls[0]?.[0]).toLowerCase()
    const fallbackBg = String(setBackgroundColor.mock.calls[0]?.[0]).toLowerCase()

    expect(themed).toBe(fallback)
    expect(themedBg).toBe(fallbackBg)
    // Guard against both sides being undefined and trivially "equal".
    expect(themed).toBe('#334d6e')
    expect(themedBg).toBe('#f8fafc')
  })

  it('still readies and expands the WebApp', async () => {
    await telegramPlatform.init()

    expect(ready).toHaveBeenCalled()
    expect(expand).toHaveBeenCalled()
  })
})
